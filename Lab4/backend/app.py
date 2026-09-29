# ==============================================================================
# app.py - Flask REST API for the Capacity Planning RAG Chatbot (Lab 4)
# Author: Thomas Chen | AI Technologist Course
#
#   GET  /health    service status + indexed chunk count
#   GET  /sources   indexed documents with owner (governance view)
#   POST /chat      question -> retrieval -> grounded answer + citations
# ==============================================================================

import os
import time

from flask import Flask, request, jsonify
from flask_cors import CORS

from utils import utils
from utils import vectordb
from utils.audit_logger import logger, audit_event

app = Flask(__name__)

# CORS scoped to specific routes and a single origin. A wildcard would let any
# website call this API from a logged-in user's browser.
ALLOWED_ORIGINS = [
    o.strip() for o in
    os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]
CORS(app, resources={r"/(chat|health|sources)": {"origins": ALLOWED_ORIGINS}})

# Singletons built once at import - avoids rebuilding the DB engine and TLS
# connection on every request.
logger.info("Initializing backend services...")
DB = vectordb.VectorDB()
UTIL = utils.Utils()
logger.info("Backend services ready.")

# Tuning values read from chatbot.env so they change without editing code.
TOP_K = int(os.environ.get("RAG_TOP_K", 4))
MIN_SIMILARITY = float(os.environ.get("RAG_MIN_SIMILARITY", 0.25))
MAX_QUESTION_CHARS = int(os.environ.get("MAX_QUESTION_CHARS", 2000))
DEFAULT_TEMPERATURE = float(os.environ.get("DEFAULT_TEMPERATURE", 0.2))

# Opening words of the system prompt's mandated refusal format.
REFUSAL_PREFIX = "i don't have that documented"


# ==============================================================================
# SECTION 1 - HEALTH
# ==============================================================================

@app.route("/health", methods=["GET"])
def health():
    # Chunk count distinguishes "API down" from "API up, knowledge base empty".
    try:
        return jsonify({
            "status": "ok",
            "knowledge_chunks": DB.count_chunks(),
            "model": UTIL.completions_model,
            "embeddings_model": UTIL.embeddings_model,
            "top_k": TOP_K,
            "min_similarity": MIN_SIMILARITY,
        }), 200
    except Exception as e:
        logger.exception("Health check failed")
        return jsonify({"status": "degraded", "error": str(e)}), 503


# ==============================================================================
# SECTION 2 - SOURCES
# ==============================================================================

@app.route("/sources", methods=["GET"])
def sources():
    # Defines the assistant's approved knowledge scope for review purposes.
    try:
        return jsonify({"sources": DB.list_sources()}), 200
    except Exception:
        logger.exception("Failed to list sources")
        return jsonify({"error": "Unable to list sources."}), 500


# ==============================================================================
# SECTION 3 - CHAT (RAG pipeline)
# ==============================================================================

@app.route("/chat", methods=["POST"])
def chat():
    started = time.time()

    # ---- Step 1: validate payload -------------------------------------------
    payload = request.get_json(silent=True) or {}
    conversation_history = payload.get("messages")

    if not isinstance(conversation_history, list) or not conversation_history:
        return jsonify({"error": "Request must include a non-empty 'messages' array."}), 400

    # Temperature clamped server-side - the UI slider is a convenience, not a control.
    try:
        temperature = float(payload.get("temperature", DEFAULT_TEMPERATURE))
    except (TypeError, ValueError):
        temperature = DEFAULT_TEMPERATURE
    temperature = max(0.0, min(temperature, 1.0))

    # ---- Step 2: locate the newest user question ----------------------------
    # Walk backwards rather than taking [-1], which could be an assistant turn.
    question = ""
    for msg in reversed(conversation_history):
        if msg.get("role") == "user" and str(msg.get("content", "")).strip():
            question = str(msg["content"]).strip()
            break

    if not question:
        return jsonify({"error": "No user message found in the conversation."}), 400

    if len(question) > MAX_QUESTION_CHARS:
        return jsonify({
            "error": f"Question exceeds {MAX_QUESTION_CHARS} characters."
        }), 413

    # ---- Steps 3-4: embed the question and retrieve context -----------------
    retrieved_chunks = []
    try:
        query_embedding = UTIL.basic_embedding_generator(question)
        retrieved_chunks = DB.semantic_search(
            query_embedding=query_embedding,
            top_k=TOP_K,
            min_similarity=MIN_SIMILARITY,
        )
        logger.info(f"Retrieved {len(retrieved_chunks)} chunk(s) for: {question[:80]}")
    except Exception:
        # Degrade rather than fail: answer ungrounded and flag it to the UI.
        logger.exception("Context retrieval failed; continuing ungrounded.")

    # ---- Step 5: build the injection-resistant prompt -----------------------
    safe_messages = utils.build_safe_messages(
        conversation_history=conversation_history,
        retrieved_chunks=retrieved_chunks,
    )

    # ---- Step 6: call the model ---------------------------------------------
    try:
        bot_response = UTIL.basic_chat_completion(safe_messages, temperature=temperature)
    except Exception:
        logger.exception("Chat completion failed")
        audit_event("chat_error", question=question, temperature=temperature)
        # Generic client message; detail stays in the server log so internal
        # URLs, model names and schema names are not exposed.
        return jsonify({"error": "The assistant is temporarily unavailable."}), 502

    # ---- Step 7: return answer with citations -------------------------------

    normalized = (bot_response or "").strip().lower().replace("\u2019", "'")
    refused = normalized.startswith(REFUSAL_PREFIX)

    citations = [] if refused else [
        {
            "source_document": c["source_document"],
            "doc_type": c["doc_type"],
            "owner": c["owner"],
            "effective_date": c["effective_date"],
            "similarity": round(c["similarity"], 3),
        }
        for c in retrieved_chunks
    ]
    grounded = bool(citations)

    elapsed = round(time.time() - started, 2)
    logger.info(f"Answered in {elapsed}s (grounded={grounded}, refused={refused}, "
                f"temp={temperature})")

    # Audit trail - question, sources, scores, token usage, latency.
    audit_event(
        "chat",
        question=question,
        grounded=grounded,
        refused=refused,
        sources=[c["source_document"] for c in citations],
        similarities=[c["similarity"] for c in citations],
        temperature=temperature,
        usage=getattr(UTIL, "last_usage", None),
        elapsed_seconds=elapsed,
    )

    return jsonify({
        "response": bot_response,
        "sources": citations,
        "grounded": grounded,
        "elapsed_seconds": elapsed,
    }), 200


# ==============================================================================
# SECTION 4 - ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    # debug=True enables the Werkzeug debugger, which permits code execution
    # from the browser. Off by default; set FLASK_DEBUG=1 for local development.
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="127.0.0.1", port=5000, debug=debug_mode)
