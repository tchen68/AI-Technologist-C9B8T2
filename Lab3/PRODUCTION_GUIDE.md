# Capacity & Inventory RAG Assistant — Production Guide

**Author:** Thomas Chen — Business Project Lead Analyst
**Built on:** AITechnologist Lab 3 (RAG + pgvector), hardened for production
**Date:** 2026-08-31

---

## 1. Executive Summary (non-technical)

This is a production-ready AI assistant that answers questions about your
**capacity and inventory specifications** (GOAT, LANID, CASH, capacity KPIs)
using **only your approved documents**, and shows the **source** for every
answer. If it isn't confident the specs contain the answer, it says so instead
of guessing — a must-have for a regulated healthcare environment.

It is the same Lab 3 idea (embeddings + vector database + retrieval) taken to
production quality: hybrid search, re-ranking, metadata filters, dedup, indexes,
retries, caching, a confidence guardrail, and a full audit trail.

---

## 2. What "in depth / production" adds over the Lab 3 prototype

| Dimension | Prototype | Production (this build) |
|---|---|---|
| Retrieval | vector only | **Hybrid** vector + keyword, **RRF** re-rank |
| Trust | citations | citations **+ confidence gate + audit log** |
| Ingest | append | **idempotent** (content-hash) + `--refresh` |
| Chunking | paragraph | paragraph **+ overlap** |
| Filtering | category | category / client / site / **effective-date** |
| Reliability | none | **retries**, pooling, `pool_pre_ping`, fail-fast config |
| Performance | none | **HNSW** + **GIN** indexes, **batch** embeddings, **cache** |
| Testing | none | offline unit tests (no DB/API needed) |

Full item-by-item proof is in **`LAB3_TRACEABILITY.md`**.

---

## 3. Architecture

```
INGEST (offline)                         QUERY (online)
data/*.md ─► DocumentLoader              user question
             (front-matter meta,              │
              overlap chunking,               ▼
              hash dedup)               AiGatewayClient.embed_query (cached)
             │                               │
             ▼                               ▼
   AiGatewayClient.embed_batch      PgVectorStore.hybrid_search
             │                       ├─ semantic (pgvector L2)  ─┐
             ▼                       └─ keyword  (tsvector)     ─┤ RRF fuse
    PgVectorStore.upsert_records                                 ▼
     (ON CONFLICT DO NOTHING)                          confidence gate
             │                                          (min_similarity)
             ▼                                                 │
 ┌───────────────────────────┐                      grounded? ─┴─ no ─► "not in specs"
 │ Postgres (pgvector)       │                             │ yes
 │ capacity_specs            │                             ▼
 │  meta + text + vector     │◄──────────────  build capped context + citations
 │  HNSW idx, GIN idx        │                             │
 └───────────────────────────┘                             ▼
                                          AiGatewayClient.chat ─► answer + sources
                                                             │
                                                             ▼
                                                    audit.jsonl (full trail)
```

---

## 4. Project Structure

```
CapacityRAG/
├── app_config.py                  # validated, immutable configuration
├── spec_ingestion_pipeline.py     # load→chunk→embed→upsert→index
│                                  #   run: python -m spec_ingestion_pipeline
├── capacity_rag_assistant.py      # RagEngine + interactive CLI
│                                  #   run: python -m capacity_rag_assistant
├── requirements.txt
├── sample.env                     # copy to .env
├── .gitignore
├── data/                          # spec documents (.md/.txt, optional front-matter)
├── logs/                          # audit.jsonl + query_cache.json (gitignored)
├── tests/
│   └── test_offline.py            # python -m tests.test_offline
└── utils/
    ├── audit_logger.py            # structured audit + logging
    ├── ai_gateway_client.py       # embeddings + chat (retries, batch, cache, validation)
    ├── document_loader.py         # metadata parsing, overlap chunking, dedup
    └── pgvector_store.py          # pooled pgvector store, hybrid search, RRF, indexes
```

---

## 5. Setup & Run

```powershell
# 1) Environment
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2) Credentials
Copy-Item .\sample.env .\.env      # then fill in real values
#    EMBEDDINGS_MODEL must be a 1536-dim model (e.g. text-embedding-3-small)

# 3) Verify logic (no DB/API needed)
python -m tests.test_offline

# 4) Ingest your specs
python -m spec_ingestion_pipeline            # incremental
python -m spec_ingestion_pipeline --refresh  # full rebaseline

# 5) Ask
python -m capacity_rag_assistant
```

Example questions:
```
How is SITE_NM derived when the LAN_ID is not in the map?
category:CASH which table is sorted newest to oldest?
site:CHENNAI what is the parent vendor?
What signals under-capacity in the capacity metric?
```

---

## 6. Document format (drives metadata filtering)

```
---
spec_id: INV-CASH-003
category: CASH
client: ACME            # optional
site: CHENNAI           # optional
effective_date: 2026-01-01
---
<the spec text ...>
```
Missing keys default sensibly (spec_id ← filename, category ← GENERAL).

---

## 7. Key tunables (`app_config.py`)

| Setting | Default | Effect |
|---|---|---|
| `top_k` | 5 | candidates per retrieval method |
| `final_k` | 3 | chunks kept after RRF |
| `rrf_k` | 60 | RRF smoothing constant |
| `min_similarity` | 0.20 | below → assistant refuses (anti-hallucination) |
| `max_context_chars` | 6000 | context-window safety cap |
| `embed_batch_size` | 64 | ingest throughput |
| `llm_max_retries` | 4 | transient-failure resilience |

Tune `min_similarity` during pilot: raise it if you see loose answers, lower it
if valid questions get refused.

---

## 8. Operations & governance

- **Audit:** every turn is appended to `logs/audit.jsonl` (question, retrieved
  spec_ids + similarity, grounded flag, answer preview). Ship to Splunk/ELK.
- **Idempotency:** re-running ingest inserts 0 duplicates (content-hash unique).
- **Secrets:** `.env` and logs are gitignored; move secrets to a vault for prod.
- **Access control (next step):** filter retrieval by `client`/`site` per user
  entitlement; add per-category authorization.
- **Persistence (next step):** migrate from the cohort schema to a durable
  enterprise Postgres; request a long-lived project API key.
- **Source sync (next step):** point `DocumentLoader` at a SharePoint/CADDy
  export folder so specs sync automatically.
- **Agentization (next step):** expose `RagEngine.answer()` as a tool an AI
  agent can call, aligning with your SharePoint-hub + AI-agent roadmap.

---

## 9. Known limitations

- Full-text search uses the English config; adjust for other languages.
- HNSW/GIN index creation is best-effort; on an older pgvector build it logs a
  warning and falls back to sequential scan (still correct, just slower).
- The query cache is a local JSON file (fine for a single-node pilot); use Redis
  for multi-instance deployments.
