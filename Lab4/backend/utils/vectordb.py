# ==============================================================================
# vectordb.py - PostgreSQL + pgvector data access layer (Lab 4)
# Author: Thomas Chen | AI Technologist Course
# Table name "text_chunks" retained for Lab 3 compatibility.
# ==============================================================================

import os
import base64
import hashlib
from typing import List, Dict, Optional

from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, Text, String, Date,
    MetaData, Table, select, text, func
)
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector

# Load chatbot.env explicitly - load_dotenv() with no argument looks for ".env".
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_BACKEND_DIR, "chatbot.env"))


class VectorDB:

    DIMS = 1536
    TABLE_NAME = "text_chunks"

    # ==========================================================================
    # SECTION 1 - CONSTRUCTION
    # ==========================================================================
    def __init__(self):
        self.pg_db_name = os.environ["PG_DB_NAME"]
        self.pg_db_schema = os.environ["PG_DB_SCHEMA"]

        self.engine = self.connect_to_postgres(self.pg_db_name)
        print("[VectorDB] Connected to Postgres database.")

        self.metadata = MetaData(schema=self.pg_db_schema)

        self.text_chunks = Table(
            self.TABLE_NAME, self.metadata,
            Column("id", Integer, primary_key=True),
            Column("text_content", Text, nullable=False),
            Column("embedding", Vector(self.DIMS)),
            # Metadata columns - nullable so existing Lab 3 rows remain valid.
            Column("source_document", String(400)),   # citation
            Column("doc_type", String(80)),
            Column("owner", String(200)),             # governance
            Column("effective_date", Date),
            Column("chunk_index", Integer),
            Column("content_hash", String(64)),       # dedupe key
            extend_existing=True,
        )

        self.Session = sessionmaker(bind=self.engine)
        print("[VectorDB] Table and sessionmaker initialized.")

    # ==========================================================================
    # SECTION 2 - CONNECTION
    # ==========================================================================
    def decode_base64(self, encoded_str: str) -> str:
        # Base64 is ENCODING, not encryption. Production requires a secret manager.
        return base64.b64decode(encoded_str).decode("utf-8")

    def connect_to_postgres(self, db_name: str):
        password = self.decode_base64(os.environ["PG_DB_PASSWORD"])
        conf = {
            "host": os.environ["PG_DB_HOST"],
            "port": os.environ["PG_DB_PORT"],
            "database": db_name,
            "user": os.environ["PG_DB_USERNAME"],
            "password": password,
        }
        connection_str = (
            f"postgresql+pg8000://{conf['user']}:{conf['password']}"
            f"@{conf['host']}:{conf['port']}/{conf['database']}"
        )
        print(f"[VectorDB] Connecting to DB '{db_name}' via pg8000 driver.")
        return create_engine(
            connection_str,
            pool_size=5,
            max_overflow=5,
            pool_pre_ping=True,     # discards connections dropped by the firewall
            pool_recycle=1800,
        )

    # ==========================================================================
    # SECTION 3 - SCHEMA MANAGEMENT
    # ==========================================================================
    def init_db(self, build_index: bool = False):
        # Check before creating. 
        with self.engine.begin() as conn:
            has_extension = conn.execute(text(
                "SELECT 1 FROM pg_extension WHERE extname = 'vector'"
            )).scalar()
            if not has_extension:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

            has_schema = conn.execute(
                text("SELECT 1 FROM pg_namespace WHERE nspname = :s"),
                {"s": self.pg_db_schema},
            ).scalar()
            if not has_schema:
                conn.execute(text(f'CREATE SCHEMA "{self.pg_db_schema}";'))

        self.metadata.create_all(self.engine)
        print("[VectorDB] DB initialized (tables created if not exist).")

        if build_index:
            self.create_ann_index()

    def add_metadata_columns(self):
        # create_all() only creates missing TABLES, never alters existing ones.
        # Run once to upgrade a Lab 3 table. Safe to re-run.
        cols = {
            "source_document": "VARCHAR(400)",
            "doc_type": "VARCHAR(80)",
            "owner": "VARCHAR(200)",
            "effective_date": "DATE",
            "chunk_index": "INTEGER",
            "content_hash": "VARCHAR(64)",
        }
        with self.engine.begin() as conn:
            for name, sql_type in cols.items():
                conn.execute(text(
                    f'ALTER TABLE "{self.pg_db_schema}"."{self.TABLE_NAME}" '
                    f'ADD COLUMN IF NOT EXISTS {name} {sql_type};'
                ))
        print("[VectorDB] Metadata columns present.")

    def create_ann_index(self, lists: int = 100):
        # IVFFlat clusters vectors so Postgres searches a subset, not every row.
        # Must be built AFTER data is loaded - it learns centroids from rows.
        idx_sql = f"""
        CREATE INDEX IF NOT EXISTS idx_{self.TABLE_NAME}_embedding
        ON "{self.pg_db_schema}"."{self.TABLE_NAME}"
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = {lists});
        """
        try:
            with self.engine.begin() as conn:
                conn.execute(text(idx_sql))
            print("[VectorDB] IVFFlat cosine index ready.")
        except Exception as e:
            print(f"[VectorDB] Index creation skipped: {e}")   # non-fatal

    # ==========================================================================
    # SECTION 4 - WRITE PATH
    # ==========================================================================
    @staticmethod
    def hash_text(t: str) -> str:
        return hashlib.sha256(t.encode("utf-8")).hexdigest()

    def save_embeddings_in_postgres(self, text_and_embeds: List[Dict]) -> int:
        if not all(isinstance(item, dict) for item in text_and_embeds):
            raise ValueError(
                "text_and_embeds must be a list of dicts containing the chunked "
                "text and its embedding"
            )
        if not text_and_embeds:
            return 0

        inserted = 0
        with self.Session() as session:
            # Pull existing hashes once rather than querying per row.
            existing = {
                row[0] for row in session.execute(
                    select(self.text_chunks.c.content_hash)
                ).fetchall() if row[0]
            }

            for obj in text_and_embeds:
                chunk_text = obj["text"]
                # Reuse the loader's hash when supplied so dedup stays consistent
                # with Lab 3's normalized hashing.
                h = obj.get("content_hash") or self.hash_text(chunk_text)
                if h in existing:
                    continue

                session.execute(self.text_chunks.insert().values(
                    text_content=chunk_text,
                    embedding=obj["embedding"],
                    source_document=obj.get("source_document", "Unknown"),
                    doc_type=obj.get("doc_type", "Reference"),
                    owner=obj.get("owner", "Unassigned"),
                    effective_date=obj.get("effective_date"),
                    chunk_index=obj.get("chunk_index", 0),
                    content_hash=h,
                ))
                existing.add(h)
                inserted += 1

            session.commit()

        print(f"[VectorDB] Filled db with {inserted} entries "
              f"({len(text_and_embeds) - inserted} duplicates skipped).")
        return inserted

    # ==========================================================================
    # SECTION 5 - READ PATH (core RAG retrieval)
    # ==========================================================================
    def semantic_search(
        self,
        query_embedding: List[float],
        top_k: int = 4,
        min_similarity: float = 0.25,
        doc_type: Optional[str] = None,
    ) -> List[Dict]:
        # Cosine rather than L2: L2 is sensitive to vector magnitude, which
        # tracks chunk length, so a long chunk can outrank a more relevant one.
        distance = self.text_chunks.c.embedding.cosine_distance(query_embedding)

        stmt = (
            select(
                self.text_chunks.c.text_content,
                self.text_chunks.c.source_document,
                self.text_chunks.c.doc_type,
                self.text_chunks.c.owner,
                self.text_chunks.c.effective_date,
                distance.label("distance"),
            )
            .order_by(distance)
            .limit(top_k * 2)      # over-fetch, then apply the threshold
        )

        if doc_type:
            stmt = stmt.where(self.text_chunks.c.doc_type == doc_type)

        with self.Session() as session:
            rows = session.execute(stmt).fetchall()

        results: List[Dict] = []
        for r in rows:
            similarity = 1.0 - float(r.distance)   # 1.0 = perfect, 0.0 = unrelated
            # Relevance floor: allows the assistant to return nothing, so it can
            # answer "I don't have that documented" instead of using a bad match.
            if similarity < min_similarity:
                continue
            results.append({
                "text_content": r.text_content,
                "source_document": r.source_document or "Unknown source",
                "doc_type": r.doc_type or "Reference",
                "owner": r.owner or "Unassigned",
                "effective_date": str(r.effective_date) if r.effective_date else None,
                "similarity": similarity,
            })
            if len(results) >= top_k:
                break

        if not results:
            print(f"[VectorDB] No chunk cleared the relevance threshold ({min_similarity}).")
        return results

    def get_embedding_from_postgres(self, query_embedding):
        # Legacy shim for Lab 3 compatibility - returns a single string.
        # New code should call semantic_search() to retain metadata and scores.
        results = self.semantic_search(query_embedding, top_k=1)
        if results:
            return results[0]["text_content"]
        print("[VectorDB] No results returned for semantic search. "
              "Ensure you have filled the db with entries.")
        return None

    # ==========================================================================
    # SECTION 6 - OPERATIONS AND GOVERNANCE
    # ==========================================================================
    def count_chunks(self) -> int:
        with self.Session() as session:
            return session.execute(
                select(func.count()).select_from(self.text_chunks)
            ).scalar_one()

    def list_sources(self) -> List[Dict]:
        # Inventory of indexed documents - supports the /sources endpoint.
        stmt = (
            select(
                self.text_chunks.c.source_document,
                self.text_chunks.c.doc_type,
                self.text_chunks.c.owner,
                func.count().label("chunk_count"),
                func.max(self.text_chunks.c.effective_date).label("effective_date"),
            )
            .group_by(
                self.text_chunks.c.source_document,
                self.text_chunks.c.doc_type,
                self.text_chunks.c.owner,
            )
            .order_by(self.text_chunks.c.source_document)
        )
        with self.Session() as session:
            rows = session.execute(stmt).fetchall()

        return [
            {
                "source_document": r.source_document or "Unknown",
                "doc_type": r.doc_type or "Reference",
                "owner": r.owner or "Unassigned",
                "chunk_count": r.chunk_count,
                "effective_date": str(r.effective_date) if r.effective_date else None,
            }
            for r in rows
        ]

    def purge_source(self, source_document: str) -> int:
        # Purge-then-reingest on document revision, so a superseded value cannot
        # be retrieved alongside the current one.
        with self.Session() as session:
            result = session.execute(
                self.text_chunks.delete().where(
                    self.text_chunks.c.source_document == source_document
                )
            )
            session.commit()
        print(f"[VectorDB] Purged {result.rowcount} chunks from '{source_document}'.")
        return result.rowcount
