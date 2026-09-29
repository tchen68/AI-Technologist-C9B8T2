"""
================================================================================
Module      : utils/audit_logger.py
Purpose     : Structured, append-only audit logging for the RAG assistant.
              Every question, the chunks retrieved (ids + distances), the
              grounding decision, and the final answer are recorded. This is a
              production requirement for a regulated (healthcare) environment
              and directly supports Lab 3 Q2 (trust/auditability of RAG).
Design      : Writes one JSON object per line (JSONL) to ./logs so records are
              easy to ship to Splunk/ELK later. Also mirrors to the standard
              logging module for console visibility.
Change Log  :
  2026-08-31  T. Chen  Initial production version.
================================================================================
"""

from __future__ import annotations

import os
import json
import logging
from datetime import datetime, timezone

# Directory for audit artifacts; created on import so callers never worry.
_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(_LOG_DIR, exist_ok=True)
_AUDIT_PATH = os.path.join(_LOG_DIR, "audit.jsonl")

# Console/file logger for operational messages (separate from the audit trail).
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("capacity_rag")


def _utc_now() -> str:
    """ISO-8601 UTC timestamp for consistent, sortable audit records."""
    return datetime.now(timezone.utc).isoformat()


def audit_event(event_type: str, **fields) -> None:
    """
    Append a single structured event to the JSONL audit trail.

    Args:
        event_type: short label, e.g. 'query', 'retrieval', 'answer', 'ingest'.
        **fields  : any JSON-serializable context to record.
    """
    record = {"ts": _utc_now(), "event": event_type, **fields}
    try:
        with open(_AUDIT_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:  # audit must never crash the main flow
        logger.warning(f"Failed to write audit record: {e}")


def audit_query_turn(
    user: str,
    question: str,
    category_filter: str | None,
    retrieved: list[dict],
    grounded: bool,
    answer: str,
) -> None:
    """
    Convenience wrapper that records a full question/answer turn in one event,
    including which spec chunks were used (ids + similarity) for traceability.
    """
    audit_event(
        "query_turn",
        user=user,
        question=question,
        category_filter=category_filter,
        grounded=grounded,
        retrieved=[
            {
                "spec_id": r.get("spec_id"),
                "category": r.get("category"),
                "source": r.get("source"),
                "similarity": round(r.get("similarity", 0.0), 4),
            }
            for r in retrieved
        ],
        answer_preview=(answer[:280] + "…") if len(answer) > 280 else answer,
    )
