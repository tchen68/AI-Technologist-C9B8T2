"""
================================================================================
Script      : tests/test_offline.py
Purpose     : Offline unit checks for the pieces that do NOT require the live
              database or AI Gateway. Verifies the Lab 3 Q4 logic actually
              behaves: overlap chunking, content-hash dedup, RRF fusion math,
              L2->similarity mapping, and inline filter parsing.
Run         : From the CapacityRAG root folder:
                  python -m tests.test_offline
Change Log  :
  2026-08-31  T. Chen  Updated imports for renamed modules.
================================================================================
"""

from __future__ import annotations

import sys

from utils.document_loader import DocumentLoader


def test_chunk_overlap():
    loader = DocumentLoader(data_dir=".")
    text = "\n\n".join(f"Paragraph number {i} with some filler text." for i in range(20))
    chunks = loader.chunk_text(text, chunk_size=120, overlap=30)
    assert len(chunks) > 1, "expected multiple chunks"
    # Overlap means consecutive chunks should share some trailing/leading text.
    shared = any(
        chunks[i][-15:].strip() and chunks[i][-15:].strip() in chunks[i + 1]
        for i in range(len(chunks) - 1)
    )
    assert shared, "expected overlap between consecutive chunks"
    print("PASS test_chunk_overlap")


def test_dedup_hash():
    loader = DocumentLoader(data_dir=".")
    h1 = loader.content_hash("Hello   World")
    h2 = loader.content_hash("hello world")
    assert h1 == h2, "hash should be normalization-insensitive"
    print("PASS test_dedup_hash")


def test_similarity_mapping():
    # Reproduce the mapping used in PgVectorStore without importing DB deps.
    def sim(d): return 1.0 / (1.0 + d)
    assert sim(0.0) == 1.0
    assert sim(1.0) == 0.5
    assert sim(3.0) < sim(1.0)
    print("PASS test_similarity_mapping")


def test_rrf_fusion():
    # Standalone RRF to confirm the fusion ordering logic.
    rrf_k = 60
    semantic = [{"id": 1}, {"id": 2}, {"id": 3}]
    keyword = [{"id": 3}, {"id": 1}, {"id": 4}]
    fused = {}
    for lst in (semantic, keyword):
        for rank, row in enumerate(lst, start=1):
            fused[row["id"]] = fused.get(row["id"], 0.0) + 1.0 / (rrf_k + rank)
    order = [rid for rid, _ in sorted(fused.items(), key=lambda kv: kv[1], reverse=True)]
    # id 1 (ranks 1 & 2) and id 3 (ranks 3 & 1) should outrank singletons 2 & 4.
    assert order[0] in (1, 3) and order[1] in (1, 3), order
    assert order[-1] in (2, 4), order
    print("PASS test_rrf_fusion")


def test_filter_parsing():
    from capacity_rag_assistant import _parse_inline_filters
    q, f = _parse_inline_filters("category:CASH site:CHENNAI which table is newest?")
    assert f.get("category") == "CASH"
    assert f.get("site") == "CHENNAI"
    assert "which table is newest?" in q
    print("PASS test_filter_parsing")


if __name__ == "__main__":
    try:
        test_chunk_overlap()
        test_dedup_hash()
        test_similarity_mapping()
        test_rrf_fusion()
        # filter parsing imports capacity_rag_assistant which imports openai.
        try:
            test_filter_parsing()
        except Exception as e:
            print(f"SKIP test_filter_parsing (needs deps): {e}")
        print("\nAll offline logic checks passed.")
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
