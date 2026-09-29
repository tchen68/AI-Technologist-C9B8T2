"""
================================================================================
Module      : utils/ai_gateway_client.py
Purpose     : Production OpenAI/AI-Gateway client wrapper for embeddings + chat.
              Adds the resilience/performance features a real product needs:
                  - Startup validation of the embedding dimension (Lab 3 Q1).
                  - Exponential-backoff RETRIES for transient API failures.
                  - BATCH embedding for fast, cheap ingestion (Lab 3 Q4).
                  - A query-embedding CACHE so repeat questions skip the API
                    call entirely (Lab 3 Q4 "caching for FAQs").
Design      : Configuration comes only from the validated Config object; this
              module never touches os.environ directly.
Change Log  :
  2026-08-31  T. Chen  Initial production version.
================================================================================
"""

from __future__ import annotations

import re
import time
import json
import os
import hashlib
from typing import List

from openai import OpenAI

from app_config import Config, EMBEDDING_DIMS
from utils.audit_logger import logger


# ---------------------------------------------------------------------------
# Text normalization (cleaner input => better, more consistent embeddings).
# ---------------------------------------------------------------------------
def normalize_text(text: str) -> str:
    """Collapse whitespace, fix stray punctuation, strip newlines."""
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\. ,", "", text)
    text = text.replace("..", ".").replace(". .", ".")
    return text.strip()


class AiGatewayClient:
    """Resilient wrapper over the OpenAI-compatible AI Gateway."""

    def __init__(self, cfg: Config, cache_path: str | None = None):
        self.cfg = cfg
        self.client = OpenAI(api_key=cfg.ai_api_key, base_url=cfg.ai_base_url)

        # Simple persistent cache for QUERY embeddings (not ingest chunks).
        # Keyed by a hash of the normalized text. A real product would use
        # Redis; a JSON file is fine for a single-node pilot and is easy to
        # inspect/clear.
        self._cache_path = cache_path
        self._cache: dict[str, list[float]] = {}
        if cache_path and os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except Exception:
                self._cache = {}

        # Fail fast: confirm the configured embedding model returns the exact
        # dimension our vector column expects. Prevents silent corruption.
        self._validate_embedding_dimension()

    # -- internal helpers ---------------------------------------------------
    def _retry(self, fn, what: str):
        """Run fn() with exponential backoff on transient errors."""
        delay = 1.0
        last_err = None
        for attempt in range(1, self.cfg.llm_max_retries + 1):
            try:
                return fn()
            except Exception as e:  # broad: gateway/network/rate-limit
                last_err = e
                logger.warning(f"{what} failed (attempt {attempt}): {e}")
                time.sleep(delay)
                delay = min(delay * 2, 16)  # cap backoff
        raise RuntimeError(f"{what} failed after "
                           f"{self.cfg.llm_max_retries} retries: {last_err}")

    def _validate_embedding_dimension(self) -> None:
        vec = self._embed_raw(["dimension check"])[0]
        if len(vec) != EMBEDDING_DIMS:
            raise ValueError(
                f"Embedding model '{self.cfg.embeddings_model}' returned "
                f"{len(vec)} dims but the vector store expects {EMBEDDING_DIMS}. "
                f"Choose a {EMBEDDING_DIMS}-dim model (e.g. text-embedding-3-small)."
            )
        logger.info(f"Embedding model validated at {EMBEDDING_DIMS} dims.")

    def _embed_raw(self, inputs: List[str]) -> List[List[float]]:
        """Low-level batch embedding call (no cache, no normalization)."""
        def call():
            resp = self.client.embeddings.create(
                input=inputs,
                model=self.cfg.embeddings_model,
                dimensions=EMBEDDING_DIMS,
            )
            return [d.embedding for d in resp.data]
        return self._retry(call, "embeddings.create")

    @staticmethod
    def _key(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    # -- public API ---------------------------------------------------------
    def embed_query(self, text: str) -> List[float]:
        """Embed a single user query, using the persistent cache when possible."""
        cleaned = normalize_text(text)
        k = self._key(cleaned)
        if k in self._cache:
            return self._cache[k]
        vec = self._embed_raw([cleaned])[0]
        self._cache[k] = vec
        self._flush_cache()
        return vec

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed many chunks efficiently for INGEST. Splits into provider-friendly
        batches to reduce round-trips and cost (Lab 3 Q4 performance).
        """
        cleaned = [normalize_text(t) for t in texts]
        out: List[List[float]] = []
        bs = self.cfg.embed_batch_size
        for i in range(0, len(cleaned), bs):
            batch = cleaned[i:i + bs]
            out.extend(self._embed_raw(batch))
        return out

    def chat(self, conversation: list) -> str:
        """Chat completion with retries; returns the assistant text."""
        def call():
            resp = self.client.chat.completions.create(
                model=self.cfg.completions_model,
                messages=conversation,
            )
            return resp.choices[0].message.content
        return self._retry(call, "chat.completions.create")

    def _flush_cache(self) -> None:
        if not self._cache_path:
            return
        try:
            with open(self._cache_path, "w", encoding="utf-8") as f:
                json.dump(self._cache, f)
        except Exception as e:
            logger.warning(f"Could not persist query cache: {e}")
