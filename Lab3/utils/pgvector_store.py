"""
================================================================================
Module      : utils/pgvector_store.py
Purpose     : Production pgvector access layer for the Capacity/Inventory RAG
              assistant. This is where most of the Lab 3 Q4 improvements become
              real engineering:
                  - HYBRID retrieval: semantic (pgvector L2) + keyword (tsvector)
                    fused with Reciprocal Rank Fusion (RRF).
                  - METADATA filtering: category / client / site / effective_date.
                  - IDEMPOTENT ingest: unique content_hash + ON CONFLICT DO NOTHING.
                  - SCALE: HNSW vector index + GIN full-text index.
                  - Similarity SCORING + confidence threshold (Lab 3 Q2 grounding).
Design      : Keeps the Lab 3 connection recipe (pg8000 + base64 password) but
              adds a pooled engine, indexes, and hybrid queries. Reads config
              only from the validated Config object.
Change Log  :
  2026-08-31  T. Chen  Initial production version.
================================================================================
"""

from __future__ import annotations

import base64
from typing import List, Dict, Optional

from sqlalchemy import (
    create_engine, Column, Integer, Text, String, Date,
    MetaData, Table, select, delete, text as sql_text
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert
from pgvector.sqlalchemy import Vector

from app_config import Config, EMBEDDING_DIMS
from utils.audit_logger import logger


class PgVectorStore:
    """Pooled, index-aware pgvector store with hybrid retrieval."""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.engine = self._connect()
        self.metadata = MetaData(schema=cfg.pg_schema)

        # Table definition. Note the metadata columns that power filtering,
        # and content_hash which enforces idempotency/dedup.
        self.specs = Table(
            cfg.table_name, self.metadata,
            Column("id", Integer, primary_key=True),
            Column("spec_id", String(100)),
            Column("category", String(100)),
            Column("client", String(100)),
            Column("site", String(100)),
            Column("effective_date", Date),
            Column("source", String(255)),
            Column("text_content", Text, nullable=False),
            Column("content_hash", String(64), unique=True),
            Column("embedding", Vector(EMBEDDING_DIMS)),
            extend_existing=True,
        )
        self.Session = sessionmaker(bind=self.engine)
        logger.info("PgVectorStore initialized.")

    # -- connection ---------------------------------------------------------
    def _connect(self):
        """Create a POOLED engine using the Lab 3 pg8000 + base64 recipe."""
        password = base64.b64decode(self.cfg.pg_password_b64).decode("utf-8")
        conn_str = (
            f"postgresql+pg8000://{self.cfg.pg_user}:{password}"
            f"@{self.cfg.pg_host}:{self.cfg.pg_port}/{self.cfg.pg_name}"
        )
        # pool_pre_ping recycles dead connections (important for long-running
        # services against corporate DBs that drop idle sessions).
        return create_engine(
            conn_str,
            pool_size=5,
            max_overflow=5,
            pool_pre_ping=True,
        )

    # -- schema / indexes ---------------------------------------------------
    def init_db(self) -> None:
        """Create the extension, table, and performance indexes (idempotent)."""
        with self.engine.begin() as conn:
            # pgvector extension must exist to use the Vector type/operators.
            conn.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector"))

        self.metadata.create_all(self.engine)
        logger.info("Table created/verified.")
        self._create_indexes()

    def _create_indexes(self) -> None:
        """
        Build the HNSW vector index (fast approximate nearest neighbour) and a
        GIN full-text index (fast keyword search). Both are wrapped so that an
        older pgvector build simply logs a warning instead of failing ingest.
        """
        schema = self.cfg.pg_schema
        table = self.cfg.table_name
        hnsw = (
            f"CREATE INDEX IF NOT EXISTS {table}_hnsw_idx "
            f"ON {schema}.{table} USING hnsw (embedding vector_l2_ops)"
        )
        gin = (
            f"CREATE INDEX IF NOT EXISTS {table}_fts_idx "
            f"ON {schema}.{table} USING gin "
            f"(to_tsvector('english', text_content))"
        )
        for label, ddl in (("HNSW vector", hnsw), ("GIN text", gin)):
            try:
                with self.engine.begin() as conn:
                    conn.execute(sql_text(ddl))
                logger.info(f"{label} index ready.")
            except Exception as e:
                logger.warning(f"Could not create {label} index "
                               f"(non-fatal): {e}")

    # -- write --------------------------------------------------------------
    def delete_by_source(self, source: str) -> None:
        """Full-refresh helper: remove all rows from a given source file."""
        with self.Session() as s:
            res = s.execute(delete(self.specs).where(self.specs.c.source == source))
            s.commit()
            logger.info(f"Deleted {res.rowcount} old row(s) for '{source}'.")

    def upsert_records(self, records: List[Dict]) -> int:
        """
        Insert records idempotently. Duplicate content_hash rows are skipped via
        ON CONFLICT DO NOTHING, so re-running ingest never creates duplicates.
        Returns the number of NEW rows inserted.
        """
        inserted = 0
        with self.Session() as s:
            for r in records:
                stmt = pg_insert(self.specs).values(
                    spec_id=r.get("spec_id"),
                    category=r.get("category"),
                    client=r.get("client"),
                    site=r.get("site"),
                    effective_date=r.get("effective_date"),
                    source=r.get("source"),
                    text_content=r["text"],
                    content_hash=r["content_hash"],
                    embedding=r["embedding"],
                ).on_conflict_do_nothing(index_elements=["content_hash"])
                result = s.execute(stmt)
                inserted += result.rowcount or 0
            s.commit()
        logger.info(f"Upsert complete: {inserted} new row(s).")
        return inserted

    # -- filters ------------------------------------------------------------
    def _apply_filters(self, stmt, filters: Optional[Dict]):
        """Attach optional metadata equality filters to a Core select."""
        if not filters:
            return stmt
        c = self.specs.c
        mapping = {
            "category": c.category,
            "client": c.client,
            "site": c.site,
        }
        for key, col in mapping.items():
            if filters.get(key):
                stmt = stmt.where(col == filters[key])
        # effective_date is treated as "on or before" a reporting date.
        if filters.get("as_of_date"):
            stmt = stmt.where(
                (c.effective_date.is_(None)) |
                (c.effective_date <= filters["as_of_date"])
            )
        return stmt

    # -- retrieval ----------------------------------------------------------
    @staticmethod
    def _similarity_from_l2(distance: float) -> float:
        """Map L2 distance (0=identical, larger=worse) to a 0..1 similarity."""
        return 1.0 / (1.0 + float(distance))

    def _semantic_rank(self, query_embedding, k, filters) -> List[Dict]:
        """Return top-k rows by vector L2 distance, with similarity scores."""
        c = self.specs.c
        stmt = (
            select(
                c.id, c.spec_id, c.category, c.client, c.site,
                c.source, c.text_content,
                c.embedding.l2_distance(query_embedding).label("distance"),
            )
            .order_by(c.embedding.l2_distance(query_embedding))
            .limit(k)
        )
        stmt = self._apply_filters(stmt, filters)
        with self.Session() as s:
            rows = s.execute(stmt).fetchall()
        return [
            {
                "id": r.id, "spec_id": r.spec_id, "category": r.category,
                "client": r.client, "site": r.site, "source": r.source,
                "text": r.text_content,
                "similarity": self._similarity_from_l2(r.distance),
            }
            for r in rows
        ]

    def _keyword_rank(self, query: str, k, filters) -> List[Dict]:
        """Return top-k rows by full-text relevance (ts_rank)."""
        c = self.specs.c
        ts_rank = sql_text(
            "ts_rank(to_tsvector('english', text_content), "
            "plainto_tsquery('english', :q))"
        )
        match = sql_text(
            "to_tsvector('english', text_content) @@ "
            "plainto_tsquery('english', :q)"
        )
        stmt = (
            select(
                c.id, c.spec_id, c.category, c.client, c.site,
                c.source, c.text_content, ts_rank.label("rank"),
            )
            .where(match)
            .order_by(sql_text("rank DESC"))
            .limit(k)
        )
        stmt = self._apply_filters(stmt, filters)
        with self.Session() as s:
            rows = s.execute(stmt, {"q": query}).fetchall()
        return [
            {
                "id": r.id, "spec_id": r.spec_id, "category": r.category,
                "client": r.client, "site": r.site, "source": r.source,
                "text": r.text_content,
                "kw_rank": float(r.rank),
            }
            for r in rows
        ]

    def hybrid_search(
        self,
        query_text: str,
        query_embedding: List[float],
        filters: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Retrieve with BOTH methods and fuse with Reciprocal Rank Fusion (RRF):

            score(doc) = Σ  1 / (rrf_k + rank_in_list)

        RRF is robust because it combines *rankings*, not raw scores, so the
        very different scales of vector distance and text rank don't distort
        the result. Returns the top `final_k` fused rows, each carrying the
        semantic similarity (used later for the confidence threshold).
        """
        k = self.cfg.top_k
        rrf_k = self.cfg.rrf_k

        semantic = self._semantic_rank(query_embedding, k, filters)
        keyword = self._keyword_rank(query_text, k, filters)

        # Accumulate RRF scores keyed by row id; keep the richest row payload.
        fused: Dict[int, Dict] = {}

        def _fuse(ranked: List[Dict], score_field: str):
            for rank, row in enumerate(ranked, start=1):
                rid = row["id"]
                entry = fused.setdefault(rid, {"row": row, "rrf": 0.0})
                entry["rrf"] += 1.0 / (rrf_k + rank)
                # Preserve similarity if this list has it.
                if "similarity" in row:
                    entry["row"]["similarity"] = row["similarity"]
                entry["row"][score_field] = True

        _fuse(semantic, "_from_semantic")
        _fuse(keyword, "_from_keyword")

        ordered = sorted(fused.values(), key=lambda e: e["rrf"], reverse=True)
        results = []
        for e in ordered[: self.cfg.final_k]:
            row = e["row"]
            row["rrf_score"] = round(e["rrf"], 6)
            row.setdefault("similarity", 0.0)  # keyword-only hits get 0.0
            results.append(row)

        return results
