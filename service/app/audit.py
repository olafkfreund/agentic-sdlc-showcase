"""Audit events and PII-safe logging.

Two rules from AGENTS.md live here:
  * every state-changing endpoint emits an audit event;
  * fields classified `personal` never reach a log line.
"""

import json
import logging
import sys
from datetime import UTC, datetime

from .models import PERSONAL_FIELDS

_logger = logging.getLogger("payments")
if not _logger.handlers:  # idempotent under test collection
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(_handler)
    _logger.setLevel(logging.INFO)

# In a real deployment this is an append-only sink with its own identity
# (playbook §8.5, "evidence integrity"). Here it is a list the tests can read.
EVENTS: list[dict] = []


def redact(payload: dict) -> dict:
    """Drop every field classified as personal data."""
    return {k: v for k, v in payload.items() if k not in PERSONAL_FIELDS}


def safe_log(message: str, **fields) -> None:
    """The only sanctioned log path. Redacts before it writes."""
    _logger.info(json.dumps({"message": message, **redact(fields)}, default=str))


def emit(actor: str, action: str, entity: str, **fields) -> dict:
    """Record an audit event for a state-changing operation."""
    event = {
        "actor": actor,
        "action": action,
        "entity": entity,
        "timestamp": datetime.now(UTC).isoformat(),
        **redact(fields),
    }
    EVENTS.append(event)
    safe_log("audit", **event)
    return event
