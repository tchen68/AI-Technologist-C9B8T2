import os
import base64
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Text, MetaData, Table, select
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector

load_dotenv()

class VectorDB:
    def __init__(self):
        self.pg_db_name = os.environ["PG_DB_NAME"]
        self.pg_db_schema = os.environ["PG_DB_SCHEMA"]
        self.DIMS = 1536
        self.engine = self.connect_to_postgres(self.pg_db_name)
        print("[VectorDB] Connected to Postgres database.")
        self.metadata = MetaData(schema=self.pg_db_schema)
        self.text_chunks = Table(
            "text_chunks", self.metadata,
            Column("id", Integer, primary_key=True),
            Column("text_content", Text, nullable=False),
            Column("embedding", Vector(self.DIMS)),
            extend_existing=True
        )
        self.Session = sessionmaker(bind=self.engine)
        print("[VectorDB] Table and sessionmaker initialized.")

    def decode_base64(self, encoded_str):
        decoded_bytes = base64.b64decode(encoded_str)
        password = decoded_bytes.decode('utf-8')
        return password

    def connect_to_postgres(self, db_name: str):
        password = self.decode_base64(os.environ["PG_DB_PASSWORD"])
        conf = {
            "host": os.environ["PG_DB_HOST"],
            "port": os.environ["PG_DB_PORT"],
            "database": db_name,
            "user": os.environ["PG_DB_USERNAME"],
            "password": password
        }
        connection_str = f"postgresql+pg8000://{conf['user']}:{conf['password']}@{conf['host']}:{conf['port']}/{conf['database']}"
        print(f"[VectorDB] Connecting to Postgres with connection string for DB: {db_name} using pg8000 driver")
        return create_engine(connection_str)

    def init_db(self):
        self.metadata.create_all(self.engine)
        print("[VectorDB] DB initialized (tables created if not exist).")

    def save_embeddings_in_postgres(self, text_and_embeds: list[dict]):
        if not all(isinstance(item, dict) for item in text_and_embeds):
            raise ValueError("text_and_embeds must be a list of dicts containing the chunked text and its embedding")
        with self.Session() as session:
            for obj in text_and_embeds:
                stmt = self.text_chunks.insert().values(
                    text_content=obj['text'], embedding=obj['embedding']
                )
                session.execute(stmt)
            session.commit()
        print(f"[VectorDB] Filled db with {len(text_and_embeds)} entries.")

    def get_embedding_from_postgres(self, query_embedding):
        table = self.text_chunks
        stmt = (
            select(table.c.text_content)
            .order_by(table.c.embedding.l2_distance(query_embedding))
            .limit(1)
        )
        with self.Session() as session:
            result = session.execute(stmt).fetchone()
            if result:
                return result[0]
            print("[VectorDB] No results returned for semantic search. Ensure you have filled the db with entries.")
            return None
