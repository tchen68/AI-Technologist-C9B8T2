"""
================================================================================
Script      : spec_ingestion_pipeline.py
Purpose     : Production ingestion pipeline: load specs -> chunk (overlap) ->
              batch-embed -> idempotent upsert -> build indexes.
Run         : From the CapacityRAG root folder:
                  python -m spec_ingestion_pipeline            # incremental
                  python -m spec_ingestion_pipeline --refresh  # full refresh
Change Log  :
  2026-08-31  T. Chen  Initial production version.
================================================================================
"""

from __future__ import annotations

import os
import sys
import argparse

from app_config import load_config
from utils.audit_logger import logger, audit_event
from utils.ai_gateway_client import AiGatewayClient
from utils.document_loader import DocumentLoader
from utils.pgvector_store import PgVectorStore

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CACHE = os.path.join(os.path.dirname(__file__), "logs", "query_cache.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest capacity/inventory specs.")
    parser.add_argument("--refresh", action="store_true",
                        help="Delete existing rows per source before insert.")
    args = parser.parse_args()

    cfg = load_config()
    llm = AiGatewayClient(cfg, cache_path=CACHE)
    loader = DocumentLoader(DATA_DIR)
    db = PgVectorStore(cfg)

    # 1) Ensure schema + indexes exist.
    db.init_db()

    # 2) Load and chunk all documents.
    records = loader.load(chunk_size=1024, overlap=150)
    if not records:
        logger.warning("Nothing to ingest. Add .txt/.md files to ./data.")
        sys.exit(0)

    # 3) Optional full refresh (deterministic re-baseline).
    if args.refresh:
        for src in sorted({r["source"] for r in records}):
            db.delete_by_source(src)

    # 4) Batch-embed all chunks (fast/cheap vs one-by-one).
    logger.info(f"Embedding {len(records)} chunk(s) in batches...")
    vectors = llm.embed_batch([r["text"] for r in records])
    for r, v in zip(records, vectors):
        r["embedding"] = v

    # 5) Idempotent upsert (duplicates skipped by content_hash).
    inserted = db.upsert_records(records)

    audit_event("ingest", files=sorted({r["source"] for r in records}),
                chunks=len(records), inserted=inserted, refresh=args.refresh)

    logger.info(f"Ingest done. {inserted} new / {len(records)} processed.")


if __name__ == "__main__":
    main()
