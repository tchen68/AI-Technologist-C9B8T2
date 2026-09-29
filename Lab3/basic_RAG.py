"""
================================================================================
Lab 3 - basic_RAG.py

Purpose :
    Interactive Retrieval Augmented Generation (RAG) Chatbot. Learning Materials

    Process Flow:
        1. User enters a question.
        2. Question is converted into an embedding.
        3. pgvector similarity search retrieves relevant content.
        4. Retrieved content is injected as context.
        5. Context + conversation history are sent to the LLM.
        6. Response is displayed.
        7. Conversation history is maintained.

Run :
    From the AITechnologistLabs root folder:

        python -m Lab3.basic_RAG

================================================================================
"""

from Lab3.utils.utils_lab3 import Utils
from Lab3.utils.vectordb_lab3 import VectorDB


def main() -> None:
    """
    Main RAG chatbot execution loop.
    """

    # ------------------------------------------------------------------
    # Initialize OpenAI Utility Class
    # ------------------------------------------------------------------
    util = Utils()

    # ------------------------------------------------------------------
    # Initialize PostgreSQL / pgvector Class
    # ------------------------------------------------------------------
    db = VectorDB()

    # ------------------------------------------------------------------
    # Conversation Memory
    # ------------------------------------------------------------------
    conversation = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant designed to answer user "
                "questions using conversation history and retrieved "
                "context from a vector database."
            )
        }
    ]
    # ------------------------------------------------------------------
    # Main chat loop.
    # ------------------------------------------------------------------
    while True:
        user_input = input("Question: ")

        # (Optional convenience: allow a clean exit.)
        if user_input.strip().lower() in {"exit", "quit"}:
            break

        # --------------------------------------------------------------
        # Step 1: Embed the user's question, then run the similarity
        # search against the embeddings stored in Postgres.
        # --------------------------------------------------------------
        user_prompt_embedding = util.basic_embedding_generator(user_input)
        context = db.get_embedding_from_postgres(user_prompt_embedding)

        # --------------------------------------------------------------
        # Step 2: Append the user's message to the permanent conversation.
        # --------------------------------------------------------------
        user_message = {"role": "user", "content": user_input}
        conversation.append(user_message)

        # --------------------------------------------------------------
        # Step 3: Build a TEMPORARY conversation that also carries the
        # retrieved context, so the main history doesn't grow unbounded.
        #
        # NOTE: The guide writes `conversation_with_context = conversation`,
        # which points both names at the SAME list (so the context would be
        # kept permanently). Using list(conversation) makes a shallow copy so
        # the context is used for THIS turn only.
        # --------------------------------------------------------------
        context_message = {
            "role": "system",
            "content": f"Here is some additional context: {context}",
        }
        conversation_with_context = list(conversation)
        conversation_with_context.append(context_message)

        # --------------------------------------------------------------
        # Step 4: Send to the LLM, print the answer, and store the
        # assistant reply in the permanent conversation history.
        # --------------------------------------------------------------
        llm_response = util.basic_chat_completion(conversation_with_context)
        print(llm_response)

        llm_message = {"role": "assistant", "content": f"{llm_response}"}
        conversation.append(llm_message)


if __name__ == "__main__":
    main()