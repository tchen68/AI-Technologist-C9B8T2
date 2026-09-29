# ==============================================================================
# document_loader.py - Spec loader and chunker (ported from Lab 3)
# Author: Thomas Chen | AI Technologist Course
#
# Source: Lab3/utils/document_loader.py
# Lab 4 changes (2 only):
#   1. audit_logger import now resolves to the Lab 4 copy (no cross-lab import).
#   2. Front-matter gained "owner"; records gained "chunk_index". Both feed
#      Lab 4 citations.
# All chunking, metadata parsing, and dedup logic is unchanged from Lab 3.
# ==============================================================================

from __future__ import annotations

import os
import re
import glob
import hashlib
from typing import List, Dict

from utils.audit_logger import logger


class DocumentLoader:

    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    # ==========================================================================
    # SECTION 1 - METADATA
    # ==========================================================================
    def _parse_front_matter(self, raw: str, path: str) -> Dict:
        # Recognized keys: spec_id, category, client, site, effective_date, owner.
        # Missing keys fall back to filename-derived defaults.
        meta = {
            "spec_id": os.path.splitext(os.path.basename(path))[0],
            "category": "GENERAL",
            "client": None,
            "site": None,
            "effective_date": None,
            "owner": "Unassigned",      # Lab 4 addition - shown in citations
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

    # ==========================================================================
    # SECTION 2 - CHUNKING
    # ==========================================================================
    def chunk_text(
        self, text: str, chunk_size: int = 1024, overlap: int = 150
    ) -> List[str]:
        # Packs whole paragraphs until chunk_size, carries an overlap tail into
        # the next chunk, and hard-splits any single oversized paragraph.
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
                tail = current[-overlap:] if overlap and current else ""
                current = (tail + "\n\n" + para).strip() if tail else para
            else:
                current = f"{current}\n\n{para}" if current else para

        _emit(current)
        return chunks

    # ==========================================================================
    # SECTION 3 - CONTENT HASH
    # ==========================================================================
    @staticmethod
    def content_hash(text: str) -> str:
        # Normalized hash - dedup survives whitespace and casing differences.
        norm = re.sub(r"\s+", " ", text).strip().lower()
        return hashlib.sha256(norm.encode("utf-8")).hexdigest()

    # ==========================================================================
    # SECTION 4 - PUBLIC LOAD
    # ==========================================================================
    def load(self, chunk_size: int = 1024, overlap: int = 150) -> List[Dict]:
        files: List[str] = []
        for pat in ("*.txt", "*.md"):
            files.extend(glob.glob(os.path.join(self.data_dir, pat)))

        # Skip helper files. A leading underscore marks anything that is notes,
        # templates, or scratch rather than knowledge - it must never reach the
        # knowledge base, or the bot will cite a template as a source.
        files = [f for f in files if not os.path.basename(f).startswith("_")]

        records: List[Dict] = []
        seen_hashes: set[str] = set()

        for path in sorted(files):
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()
            meta = self._parse_front_matter(raw, path)
            source = os.path.basename(path)
            chunks = self.chunk_text(meta["body"], chunk_size, overlap)

            kept = 0
            for idx, chunk in enumerate(chunks):
                h = self.content_hash(chunk)
                if h in seen_hashes:            # cross-file duplicate guard
                    continue
                seen_hashes.add(h)
                records.append({
                    "spec_id": meta["spec_id"],
                    "category": meta["category"],
                    "client": meta["client"],
                    "site": meta["site"],
                    "effective_date": meta["effective_date"],
                    "owner": meta["owner"],
                    "source": source,
                    "text": chunk,
                    "chunk_index": idx,         # Lab 4 addition - traceability
                    "content_hash": h,
                })
                kept += 1

            logger.info(f"{source}: {kept} chunk(s) kept "
                        f"(category={meta['category']}, owner={meta['owner']}).")

        if not records:
            logger.warning(f"No .txt/.md files found in '{self.data_dir}'.")
        return records
