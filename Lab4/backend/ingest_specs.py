# ==============================================================================
# ingest_specs.py - Ingestion pipeline for the Lab 4 chatbot knowledge base
# Author: Thomas Chen | AI Technologist Course
#
# Reuses the Lab 3 DocumentLoader (front-matter metadata, overlap chunking,
# content-hash dedup) and writes into the Lab 4 text_chunks table so the chatbot
# can cite sources.
#
# Usage (run from Lab4\backend):
#   python ingest_specs.py                # incremental - duplicates skipped
#   python ingest_specs.py --refresh      # purge each source, then re-insert
#   python ingest_specs.py --folder .\data
#
# Pipeline: load + chunk -> batch embed -> map metadata -> upsert -> index
# ==============================================================================

import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Optional

from utils.utils import Utils
from utils.vectordb import VectorDB
from utils.document_loader import DocumentLoader
from utils.audit_logger import logger, audit_event


# ==============================================================================
# SECTION 1 - METADATA MAPPING
# ==============================================================================

CATEGORY_TO_DOC_TYPE = {
    "GOAT": "Data Dictionary",
    "LANID": "Business Rule",
    "CASH": "SOP",
    "CAPACITY": "Business Overview",
    "INVENTORY": "Data Dictionary",
    "DELINQUENCY": "SOP",
    "GENERAL": "Reference",
}


def parse_effective_date(value: Optional[str]):
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%b-%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    logger.warning(f"Unrecognized effective_date '{value}' - storing NULL.")
    return None


def to_lab4_record(rec: Dict, embedding: List[float]) -> Dict:
    # Maps a Lab 3 loader record onto the Lab 4 text_chunks schema.
    #   source -> source_document    category -> doc_type
    #   owner  -> owner              content_hash reused for dedup consistency
    category = (rec.get("category") or "GENERAL").upper()

    return {
        "text": rec["text"],
        "embedding": embedding,
        "source_document": rec["source"],
        "doc_type": CATEGORY_TO_DOC_TYPE.get(category, category.title()),
        "owner": rec.get("owner") or "Unassigned",
        "effective_date": parse_effective_date(rec.get("effective_date")),
        "chunk_index": rec.get("chunk_index", 0),
        "content_hash": rec.get("content_hash"),
    }


# ==============================================================================
# SECTION 2 - INGESTION
# ==============================================================================

def ingest(folder: str, refresh: bool = False,
           chunk_size: int = 1024, overlap: int = 150,
           batch_size: int = 64) -> None:

    if not os.path.isdir(folder):
        logger.error(f"Folder not found: {folder}")
        sys.exit(1)

    db = VectorDB()
    util = Utils()
    loader = DocumentLoader(folder)

    # Step 1 - ensure schema and citation columns exist
    db.init_db(build_index=False)
    db.add_metadata_columns()

    # Step 2 - load and chunk (front-matter parsed, cross-file dedup applied)
    records = loader.load(chunk_size=chunk_size, overlap=overlap)
    if not records:
        logger.warning("Nothing to ingest. Add .txt/.md files to the data folder.")
        sys.exit(0)

    # Step 3 - optional full refresh so superseded values cannot be retrieved
    # alongside current ones
    if refresh:
        for src in sorted({r["source"] for r in records}):
            db.purge_source(src)

    # Step 4 - batch embed (one API call per batch, not per chunk)
    logger.info(f"Embedding {len(records)} chunk(s) in batches of {batch_size}...")
    lab4_records: List[Dict] = []
    for start in range(0, len(records), batch_size):
        batch = records[start:start + batch_size]
        vectors = util.batch_embedding_generator([r["text"] for r in batch])
        for rec, vec in zip(batch, vectors):
            lab4_records.append(to_lab4_record(rec, vec))

    # Step 5 - upsert (content_hash dedup applied inside)
    inserted = db.save_embeddings_in_postgres(lab4_records)

    # Step 6 - build the index after loading, so it learns valid centroids
    db.create_ann_index()

    audit_event("ingest",
                files=sorted({r["source"] for r in records}),
                chunks=len(lab4_records),
                inserted=inserted,
                refresh=refresh)

    # Step 7 - summary
    print("\n" + "=" * 78)
    print(f"Ingest complete. {inserted} new / {len(lab4_records)} processed.")
    print(f"Knowledge base now holds {db.count_chunks()} chunk(s).")
    print("=" * 78)
    for s in db.list_sources():
        print(f"  {s['source_document']:<26} {s['doc_type']:<20} "
              f"{s['chunk_count']:>3} chunks   {s['owner']}")

    unassigned = [s for s in db.list_sources() if s["owner"] == "Unassigned"]
    if unassigned:
        print("\nWARNING: these documents have no owner in their front-matter. "
              "Add an 'owner:' line before relying on them.")
        for s in unassigned:
            print(f"  - {s['source_document']}")


# ==============================================================================
# SECTION 3 - CLI
# ==============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest capacity/inventory specs into the Lab 4 knowledge base."
    )
    parser.add_argument(
        "--folder",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"),
        help="Folder containing .txt/.md spec documents (default: ./data)",
    )
    parser.add_argument("--refresh", action="store_true",
                        help="Purge each source before re-inserting.")
    parser.add_argument("--chunk-size", type=int, default=1024)
    parser.add_argument("--overlap", type=int, default=150)
    args = parser.parse_args()

    ingest(folder=args.folder, refresh=args.refresh,
           chunk_size=args.chunk_size, overlap=args.overlap)
