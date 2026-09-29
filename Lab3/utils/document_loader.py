"""
================================================================================
Module      : utils/document_loader.py
Purpose     : Load spec documents and turn them into clean, overlapping,
              metadata-tagged chunks ready for embedding.
Design      : Directly implements the Lab 3 Q4 "smarter chunking" and
              "preprocessing" improvements:
                  - Optional YAML-style front-matter (spec_id, category,
                    client, site, effective_date) for metadata FILTERING.
                  - Paragraph-preferring chunking WITH configurable OVERLAP so
                    context that straddles a boundary is not lost.
                  - Content-hash per chunk for DEDUP and idempotent ingest.
Change Log  :
  2026-08-31  T. Chen  Initial production version.
================================================================================
"""

from __future__ import annotations

import os
import re
import glob
import hashlib
from typing import List, Dict

from utils.audit_logger import logger


class DocumentLoader:
    """Reads .txt/.md specs and produces enriched chunk records."""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    # -- metadata -----------------------------------------------------------
    def _parse_front_matter(self, raw: str, path: str) -> Dict:
        """
        Extract an optional '--- key: value ---' header. Recognized keys:
        spec_id, category, client, site, effective_date. Missing keys get
        sensible defaults derived from the filename.
        """
        meta = {
            "spec_id": os.path.splitext(os.path.basename(path))[0],
            "category": "GENERAL",
            "client": None,
            "site": None,
            "effective_date": None,
        }
        body = raw
        m = re.match(r"^---\s*(.*?)\s*---\s*(.*)$", raw, re.DOTALL)
        if m:
            header, body = m.group(1), m.group(2)
            for line in header.splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    key, val = key.strip().lower(), val.strip()
                    if key in meta and val:
                        meta[key] = val.upper() if key == "category" else val
        meta["body"] = body.strip()
        return meta

    # -- chunking -----------------------------------------------------------
    def chunk_text(
        self, text: str, chunk_size: int = 1024, overlap: int = 150
    ) -> List[str]:
        """
        Paragraph-preferring chunker with character overlap.

        - Packs whole paragraphs until chunk_size is reached.
        - Carries the last `overlap` characters of the previous chunk into the
          next one so a fact split across a boundary is still retrievable.
        - Hard-splits any single oversized paragraph.
        """
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        chunks: List[str] = []
        current = ""

        def _emit(buf: str):
            if buf.strip():
                chunks.append(buf.strip())

        for para in paragraphs:
            if len(para) > chunk_size:
                _emit(current)
                current = ""
                for i in range(0, len(para), chunk_size):
                    _emit(para[i:i + chunk_size])
                continue

            if len(current) + len(para) + 2 > chunk_size:
                _emit(current)
                # Start the next chunk with a tail of the previous one (overlap).
                tail = current[-overlap:] if overlap and current else ""
                current = (tail + "\n\n" + para).strip() if tail else para
            else:
                current = f"{current}\n\n{para}" if current else para

        _emit(current)
        return chunks

    # -- content hash -------------------------------------------------------
    @staticmethod
    def content_hash(text: str) -> str:
        """Stable hash of normalized text, used for dedup and idempotency."""
        norm = re.sub(r"\s+", " ", text).strip().lower()
        return hashlib.sha256(norm.encode("utf-8")).hexdigest()

    # -- public load --------------------------------------------------------
    def load(self, chunk_size: int = 1024, overlap: int = 150) -> List[Dict]:
        """
        Return a de-duplicated list of chunk records:
            {spec_id, category, client, site, effective_date,
             source, text, content_hash}
        """
        files: List[str] = []
        for pat in ("*.txt", "*.md"):
            files.extend(glob.glob(os.path.join(self.data_dir, pat)))

        records: List[Dict] = []
        seen_hashes: set[str] = set()

        for path in sorted(files):
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()
            meta = self._parse_front_matter(raw, path)
            source = os.path.basename(path)
            chunks = self.chunk_text(meta["body"], chunk_size, overlap)

            kept = 0
            for chunk in chunks:
                h = self.content_hash(chunk)
                if h in seen_hashes:      # cross-file exact-duplicate guard
                    continue
                seen_hashes.add(h)
                records.append({
                    "spec_id": meta["spec_id"],
                    "category": meta["category"],
                    "client": meta["client"],
                    "site": meta["site"],
                    "effective_date": meta["effective_date"],
                    "source": source,
                    "text": chunk,
                    "content_hash": h,
                })
                kept += 1

            logger.info(f"{source}: {kept} chunk(s) kept "
                        f"(category={meta['category']}).")

        if not records:
            logger.warning(f"No .txt/.md files found in '{self.data_dir}'.")
        return records
