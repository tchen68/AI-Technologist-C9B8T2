"""
================================================================================
Module      : app_config.py
Purpose     : Single source of truth for all configuration and a fail-fast
              startup validator. Nothing else in the app reads os.environ
              directly, which keeps configuration auditable and testable.
Design      : Loads .env from the project root, exposes a frozen Config object,
              and validates that every required value is present and sane
              BEFORE any network/DB call is attempted.
Change Log  :
  2026-08-31  T. Chen  Initial production version.
================================================================================
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv

# Load environment once, from the project root, regardless of CWD.
load_dotenv(find_dotenv())

# The embedding vector width MUST match the pgvector column definition.
# Changing this requires re-ingesting all data, so it is a constant, not env.
EMBEDDING_DIMS = 1536


@dataclass(frozen=True)
class Config:
    """Immutable, validated application configuration."""

    # --- AI Gateway (OpenAI-compatible) -----------------------------------
    ai_api_key: str
    ai_base_url: str
    completions_model: str
    embeddings_model: str

    # --- PostgreSQL / pgvector --------------------------------------------
    pg_user: str
    pg_password_b64: str          # base64-encoded, decoded at connect time
    pg_host: str
    pg_port: str
    pg_name: str
    pg_schema: str

    # --- Retrieval / generation tunables ----------------------------------
    top_k: int = 5                # candidates pulled per retrieval method
    final_k: int = 3              # chunks kept after fusion/re-rank
    rrf_k: int = 60               # Reciprocal Rank Fusion constant
    max_context_chars: int = 6000 # cap injected context (token safety)
    min_similarity: float = 0.20  # below this, treat as "no confident match"
    embed_batch_size: int = 64    # batch size for ingest embedding calls
    llm_max_retries: int = 4      # transient-failure retries for API calls

    # --- Table name (kept configurable for blue/green re-ingests) ---------
    table_name: str = "capacity_specs"


def _require(name: str) -> str:
    """Return a required env var or raise a clear, actionable error."""
    val = os.environ.get(name)
    if val is None or val.strip() == "":
        raise EnvironmentError(
            f"Missing required environment variable '{name}'. "
            f"Copy sample.env to .env and fill it in."
        )
    return val.strip()


def load_config() -> Config:
    """
    Build and validate the Config. Fail fast with a helpful message if the
    environment is incomplete, so we never make a half-configured API/DB call.
    """
    cfg = Config(
        ai_api_key=_require("AI_GW_API_KEY"),
        ai_base_url=_require("AI_GW_BASE_URL"),
        completions_model=_require("COMPLETIONS_MODEL"),
        embeddings_model=_require("EMBEDDINGS_MODEL"),
        pg_user=_require("PG_DB_USERNAME"),
        pg_password_b64=_require("PG_DB_PASSWORD"),
        pg_host=_require("PG_DB_HOST"),
        pg_port=_require("PG_DB_PORT"),
        pg_name=_require("PG_DB_NAME"),
        pg_schema=_require("PG_DB_SCHEMA"),
    )

    # Basic sanity checks (cheap guards that catch common mistakes).
    if not cfg.pg_port.isdigit():
        raise EnvironmentError(f"PG_DB_PORT must be numeric, got '{cfg.pg_port}'.")
    if cfg.final_k > cfg.top_k:
        raise ValueError("final_k cannot exceed top_k.")

    return cfg
