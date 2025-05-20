import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import base64

load_dotenv("chatbot.env")

class VectorDB():
    """
    A class for interacting with a PostgreSQL database to store and retrieve vector embeddings.

    Attributes:
        postgres_connection: A connection to the PostgreSQL database.
    """
    def __init__(self):
        """
        Initializes a VectorDB instance with a connection to a PostgreSQL database.

        Args:
            pg_db_name (str): The name of the PostgreSQL database to connect to.
        """
        self.pg_db_name = os.environ["PG_DB_NAME"]
        self.pg_db_schema = os.environ["PG_DB_SCHEMA"]
        self.postgres_connection = self.connect_to_postgres(db_name=self.pg_db_name)
        self.DIMS = 1536

    def decode_base64(self, encoded_str):
        decoded_bytes = base64.b64decode(encoded_str)
        password = decoded_bytes.decode('utf-8')
        return password

    def connect_to_postgres(self, db_name:str):
        """
        Establishes a connection to a PostgreSQL database.

        Args:
            db_name (str): The name of the PostgreSQL database to connect to.

        Returns:
            engine: A connection to the PostgreSQL database.
        """

        encoded_str = os.environ["PG_DB_PASSWORD"]
        password = self.decode_base64(encoded_str)

        conf = {
            "host": os.environ["PG_DB_HOST"],
            "port": os.environ["PG_DB_PORT"],
            "database": db_name,
            "username": os.environ["PG_DB_USERNAME"],
            "password": password
        }
        
        connection_str = 'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}'.format(**conf)
        try:
            conn = create_engine(connection_str, pool_size=10)

            print("Connection to Postgres created..")
            return conn
        except Exception as e:
            raise (f'The following error occurred while connecting to PG: {e}')

    def init_db(self):
        print("Initializing db...")
        DDL = f"""create table if not exists {self.pg_db_schema}.text_chunks (
            id serial primary key,
            text_content text not null,
            embedding vector({self.DIMS})
        );"""
        try:
            rc =  self.postgres_connection.raw_connection()
            cursor = rc.cursor()
            cursor.execute("CREATE EXTENSION if not exists vector;")
            cursor.execute(DDL)
            rc.commit()
            rc.close()
        except Exception as e:
            print(f"Failed to init db using DDL:\n{DDL}")
            raise(e)
        print("DB initialized")



    def save_embeddings_in_postgres(self, text_and_embeds: list[dict], table_name="text_chunks", text_field = 'text_content',vector_field='embedding'):
        """
        Saves a list of text and embedding tuples to a PostgreSQL database.

        Args:
            text_and_embeds (list[dict]): A list of dictionaries containing text and embedding data.
            table_name: The name of the table to insert the data into.
            text_field: The name of the column for the text data. Defaults to 'text_content'.
            vector_field: The name of the column for the embedding data. Defaults to 'embedding'.
        """
        if not all(isinstance(item, dict) for item in text_and_embeds):
            raise ValueError("text_and_embeds must be a list of dicts containing the chunked text and it's embedding")
        if not isinstance(table_name, str) or not table_name.strip():
            raise ValueError("table_name must be a non-empty string")
        if not isinstance(text_field, str) or not text_field.strip():
            raise ValueError("text_field must be a non-empty string")
        if not isinstance(vector_field, str) or not vector_field.strip():
            raise ValueError("vector_field must be a non-empty string")
        
        try:
            with self.postgres_connection.begin() as session:
                for obj in text_and_embeds:
                    try:
                        sql = f"INSERT INTO {self.pg_db_schema}.{table_name} ({text_field}, {vector_field}) VALUES (:text, :embedding)"
                        session.execute(text(sql), {'text': obj['text'], 'embedding': obj['embedding']})
                    except Exception as e:
                        raise (f"{obj} could not be inserted to db: {e}")
            print(f"Filled db with {len(text_and_embeds)} entries")
        except Exception as e:
            raise (f"Failed to populate db due to the following error: {e}")
            


    def get_embedding_from_postgres(self, query_embedding, table_name="text_chunks", text_field='text_content',vector_field='embedding'):
        """
        Retrieves the most relevant text result from a PostgreSQL database based on a query embedding.

        Args:
            query_embedding: The embedding to query the database with.
            query: The original query text.
            table_name: The name of the table to query.
            text_field: The name of the column for the text data. Defaults to 'text_content'.
            vector_field: The name of the column for the embedding data. Defaults to 'embedding'.

        Returns:
            str: The most relevant text result.
        """
                
        q = f"""
        SELECT {text_field}, {vector_field} <=> '{query_embedding}' AS similarity
        FROM {self.pg_db_schema}.{table_name}
        ORDER BY similarity
        LIMIT 1;
        """
        
        try:
            with self.postgres_connection.begin() as session:
                df = pd.read_sql(q, session)
                txt = df.iloc[0][text_field]
                #print(f"Identified as most relevant: {txt}")
                return txt
        except Exception as e:
            print(e)
            raise(e)