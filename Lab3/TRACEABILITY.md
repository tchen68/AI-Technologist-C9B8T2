# Lab 3 → Production Traceability Matrix

**Purpose:** Prove that every Lab 3 concept and every Lab 3 question (Q1–Q4) is
not merely *understood* but *engineered into* the production Capacity/Inventory
RAG assistant. Use this as the review checklist before sign-off.

**Legend:** ✅ Implemented & verified · 🧪 Covered by offline test

---

## Part A — Lab 3 Questions mapped to code

### Q1 — "What is an embedding?" (semantic vectors)
| Requirement from Lab 3 | Where it lives | Status |
|---|---|---|
| 1536-dim semantic vectors | `app_config.EMBEDDING_DIMS = 1536`; `Vector(EMBEDDING_DIMS)` in `utils/pgvector_store.py` | ✅ |
| Normalize text before embedding | `normalize_text()` in `utils/ai_gateway_client.py` | ✅ |
| Dimension actually matches the store | `AiGatewayClient._validate_embedding_dimension()` fails fast at startup | ✅ |
| Efficient vector creation | `AiGatewayClient.embed_batch()` (batched) | ✅ |
| L2 distance → interpretable score | `PgVectorStore._similarity_from_l2()` | 🧪 `test_similarity_mapping` |

### Q2 — "Why implement RAG?" (accuracy, trust, freshness, security)
| Requirement | Where it lives | Status |
|---|---|---|
| Answer only from proprietary data | `SYSTEM_PROMPT` + retrieved context in `capacity_rag_assistant.py` | ✅ |
| Reduce hallucination | Confidence gate: `min_similarity` in `RagEngine.answer()` refuses weak matches | ✅ |
| Trust / auditability | `utils/audit_logger.py` writes JSONL of question, chunks, decision, answer | ✅ |
| Citations for every answer | `citations` returned by `RagEngine.answer()` and printed in CLI | ✅ |
| Freshness without retraining | Re-run `spec_ingestion_pipeline.py`; content updates immediately | ✅ |
| Security (data stays in our DB) | pgvector store in your schema; secrets via `.env`/vault | ✅ |
| Example use-case realized | This *is* the capacity/inventory assistant | ✅ |

### Q3 — "Steps to implement context retrieval"
| Lab 3 step | Production implementation | Status |
|---|---|---|
| Capture question | CLI loop / `RagEngine.answer(question)` | ✅ |
| Embed question | `AiGatewayClient.embed_query()` (+ cache) | ✅ |
| Similarity search | `PgVectorStore.hybrid_search()` (semantic + keyword) | ✅ |
| Assemble prompt w/ temporary context | `RagEngine._build_context()`, copied conversation | ✅ |
| Generate answer | `AiGatewayClient.chat()` with retries | ✅ |
| Hardening (pooling, retries, token cap) | pooled engine, `_retry()`, `max_context_chars` | ✅ |

### Q4 — "Areas to improve the RAG pipeline"
| Improvement named in Lab 3 | Production implementation | Status |
|---|---|---|
| Smarter chunking | Paragraph chunking **with overlap** (`document_loader.chunk_text`) | 🧪 `test_chunk_overlap` |
| Top-K + re-ranking | `top_k`/`final_k` + **RRF fusion** (`hybrid_search`) | 🧪 `test_rrf_fusion` |
| Metadata filtering | category/client/site/effective-date (`_apply_filters`) | ✅ |
| Hybrid search | semantic (pgvector) + keyword (tsvector) fused | ✅ |
| Better preprocessing | `normalize_text` + content-hash **dedup** | 🧪 `test_dedup_hash` |
| Grounding + citations | confidence gate + citations | ✅ |
| Better models + caching | config-driven models + query-embedding **cache** | ✅ |
| Performance at scale | **HNSW** vector index + **GIN** text index + batching | ✅ |

---

## Part B — Production concerns beyond Lab 3

| Concern | Implementation | Status |
|---|---|---|
| Fail-fast configuration | `app_config.load_config()` validates every var | ✅ |
| Transient API failures | exponential backoff `_retry()` | ✅ |
| Idempotent re-ingest | unique `content_hash` + `ON CONFLICT DO NOTHING` | ✅ |
| Full refresh option | `spec_ingestion_pipeline.py --refresh` (delete-by-source) | ✅ |
| Connection stability | pooled engine + `pool_pre_ping` | ✅ |
| Reusable core | `RagEngine` can back CLI, API, or agent tool | ✅ |
| Testability | `tests/test_offline.py` (no DB/API needed) | ✅ |
| Least-secret exposure | `.gitignore` excludes `.env`, logs | ✅ |

---

## Part C — Sign-off checklist

- [ ] `.env` created from `sample.env` with real values
- [ ] `python -m tests.test_offline` passes
- [ ] `python -m spec_ingestion_pipeline` completes; audit shows `inserted` count
- [ ] `python -m capacity_rag_assistant` answers a known question **with citations**
- [ ] Ask an out-of-scope question → assistant says "not in the specs" (grounding)
- [ ] Re-run `python -m spec_ingestion_pipeline` → `inserted = 0` (idempotency proven)
- [ ] Review `logs/audit.jsonl` for a complete question/answer trail
