"""
================================================================================
Script      : capacity_rag_assistant.py
================================================================================
"""

from __future__ import annotations

import os
import getpass
from datetime import date

from app_config import load_config, Config
from utils.audit_logger import logger, audit_query_turn
from utils.ai_gateway_client import AiGatewayClient
from utils.pgvector_store import PgVectorStore

CACHE = os.path.join(os.path.dirname(__file__), "logs", "query_cache.json")

SYSTEM_PROMPT = (
    "You are the Capacity & Inventory Specifications assistant for a healthcare "
    "revenue-operations team. Answer ONLY from the provided context drawn from "
    "the internal spec database. If the context does not contain the answer, "
    "clearly state that the information is not in the specs rather than "
    "guessing. Be concise, precise, and cite the supporting spec_id/source."
)


class RagEngine:
    """Reusable engine so the same logic can back a CLI, API, or agent tool."""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.llm = AiGatewayClient(cfg, cache_path=CACHE)
        self.db = PgVectorStore(cfg)

    def _build_context(self, results: list[dict]) -> str:
        """
        Concatenate retrieved chunks into a citation-tagged context block,
        capped at cfg.max_context_chars to protect the model's context window.
        """
        block, used = [], 0
        for i, r in enumerate(results, start=1):
            piece = (f"[{i}] (spec_id={r['spec_id']}, category={r['category']}, "
                     f"source={r['source']})\n{r['text']}")
            if used + len(piece) > self.cfg.max_context_chars:
                break
            block.append(piece)
            used += len(piece)
        return "\n\n".join(block)

    def answer(
        self,
        question: str,
        history: list[dict] | None = None,
        filters: dict | None = None,
        user: str = "anonymous",
    ) -> dict:
        """
        Full RAG turn. Returns a dict with the answer, whether it was grounded,
        and the citations used — suitable for a CLI, API response, or agent.
        """
        history = history or [{"role": "system", "content": SYSTEM_PROMPT}]

        # Step 1: embed the question (cached).
        q_vec = self.llm.embed_query(question)

        # Step 2: hybrid retrieve + RRF re-rank.
        results = self.db.hybrid_search(question, q_vec, filters=filters)

        # Step 3: confidence gate (Lab 3 Q2 anti-hallucination).
        best_sim = max((r.get("similarity", 0.0) for r in results), default=0.0)
        if not results or best_sim < self.cfg.min_similarity:
            answer = ("I don't have that information in the current specs. "
                      "Try rephrasing, or confirm the spec has been ingested.")
            audit_query_turn(user, question, (filters or {}).get("category"),
                             results, grounded=False, answer=answer)
            return {"answer": answer, "grounded": False, "citations": []}

        # Step 4: assemble grounded prompt (temporary context, not persisted).
        context = self._build_context(results)
        convo = list(history)
        convo.append({"role": "user", "content": question})
        convo.append({"role": "system",
                      "content": f"Relevant context:\n\n{context}"})

        # Step 5: generate + audit.
        answer = self.llm.chat(convo)
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})

        citations = [
            {"spec_id": r["spec_id"], "category": r["category"],
             "source": r["source"], "similarity": round(r.get("similarity", 0), 4)}
            for r in results
        ]
        audit_query_turn(user, question, (filters or {}).get("category"),
                         results, grounded=True, answer=answer)
        return {"answer": answer, "grounded": True, "citations": citations}


def _parse_inline_filters(text: str) -> tuple[str, dict]:
    """
    Allow inline filters like:
        category:CASH which table is newest to oldest?
        site:CHENNAI what is the parent vendor?
    Returns (clean_question, filters_dict).
    """
    filters: dict = {}
    tokens = text.split()
    keep = []
    for tok in tokens:
        if ":" in tok and tok.split(":", 1)[0].lower() in {"category", "client", "site"}:
            key, val = tok.split(":", 1)
            filters[key.lower()] = val.upper() if key.lower() == "category" else val
        else:
            keep.append(tok)
    return " ".join(keep).strip(), filters


def main() -> None:
    cfg = load_config()
    engine = RagEngine(cfg)
    try:
        user = getpass.getuser()
    except Exception:
        user = "cli-user"

    history = [{"role": "system", "content": SYSTEM_PROMPT}]

    print("\nCapacity & Inventory Specs Assistant (production).")
    print("Filters: prefix tokens like 'category:CASH', 'site:CHENNAI'.")
    print("Type 'exit' to quit.\n")

    while True:
        raw = input("Question: ").strip()
        if raw.lower() in {"exit", "quit"}:
            break
        if not raw:
            continue

        question, filters = _parse_inline_filters(raw)
        if not question:
            print("Please include a question after the filter(s).\n")
            continue
        # As-of date defaults to today for effective-date-aware retrieval.
        filters.setdefault("as_of_date", date.today())

        result = engine.answer(question, history=history,
                               filters=filters, user=user)

        print(f"\nAnswer:\n{result['answer']}\n")
        if result["citations"]:
            print("Sources:")
            for i, c in enumerate(result["citations"], start=1):
                print(f"  [{i}] {c['spec_id']} / {c['category']} / "
                      f"{c['source']} (sim={c['similarity']})")
        print()


if __name__ == "__main__":
    main()
