"""
================================================================================
Lab 3 - basic_vectorization.py

Purpose : 
    Learning materials.
    Build a simple embedding pipeline that reads text from Lab3/data,
    chunks the text, generates embeddings, and stores them in
    PostgreSQL (pgvector).

Run :
    From the AITechnologistLabs root folder:

        python -m Lab3.basic_vectorization

================================================================================
"""

from Lab3.utils.utils_lab3 import Utils
from Lab3.utils.vectordb_lab3 import VectorDB


def main() -> None:
    """
    Main execution flow.
    """

    # ------------------------------------------------------------------
    # Step 1 : Initialize Utilities
    # ------------------------------------------------------------------
    util = Utils()

    # ------------------------------------------------------------------
    # Step 2 : Read source text file
    # File expected in:
    # Lab3/data/test.txt
    # ------------------------------------------------------------------
    text_data = util.read_text_file("test.txt")

    # ------------------------------------------------------------------
    # Step 3 : Split text into chunks
    # ------------------------------------------------------------------
    chunks = util.basic_character_chunker(
        text=text_data,
        chunk_size=1024
    )

    print(f"Created {len(chunks)} chunks")

    # ------------------------------------------------------------------
    # Step 4 : Generate embeddings
    # ------------------------------------------------------------------
    text_and_embeddings = []

    for i, text in enumerate(chunks):

        embedding = util.basic_embedding_generator(
            input=text
        )

        text_and_embeddings.append(
            {
                "text": text,
                "embedding": embedding
            }
        )

        print(
            f"Chunk {i + 1}/{len(chunks)} "
            f"Embedding Dimensions = {len(embedding)}"
        )

    # ------------------------------------------------------------------
    # Review generated data
    # ------------------------------------------------------------------
    for i, item in enumerate(text_and_embeddings):

        print(
            f"Chunk {i}: "
            f"text={item['text'][:100]!r} "
            f"... embedding_dims={len(item['embedding'])}"
        )

    # ------------------------------------------------------------------
    # Step 5 : Initialize PostgreSQL / pgvector
    # ------------------------------------------------------------------
    db = VectorDB()

    db.init_db()

    # ------------------------------------------------------------------
    # Step 6 : Persist embeddings
    # ------------------------------------------------------------------
    db.save_embeddings_in_postgres(
        text_and_embeds=text_and_embeddings
    )

    print(
        "\nVectorization complete."
        "\nEmbeddings successfully saved to PostgreSQL."
    )


if __name__ == "__main__":
    main()