"""The portable artifact chain (playbook §6.1) and its header (§6.2).

One parser, used by every gate that reads an artifact. intent -> spec -> plan,
each carrying the machine-readable header that makes the chain queryable.
"""

from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass, field

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
STAGES = {"intent": "intent", "specs": "spec", "plans": "plan"}

REQUIRED = [
    "change_id",
    "risk_class",
    "autonomy_tier",
    "controls",
    "data_classification",
    "originator",
    "agent_identity",
    "model_route",
]

CHANGE_ID = re.compile(r"^CHG-\d{4}-\d{6}$")
RISK_CLASSES = {"R1", "R2", "R3"}

# Terminal states for a chain that stops before a plan (§6.1). Absent means active.
#
# Without this, "deliberately stopped" and "quietly abandoned" are the same shape on disk,
# and the chain page publishes both as if they were work in progress. The distinction is
# not cosmetic: `blocked` is waiting on a named decision and will resume, `dismissed` never
# will. An auditor asking why a change stopped needs that answered by the artifact, not
# inferred from the absence of a later one.
#
# The convention already existed in prose — CHG-2026-014901's spec opens "STATUS: BLOCKED ON
# POLICY CONFLICT" — used once, enforced nowhere, readable by nothing. This promotes it to a
# header field so it is queryable like the rest of §6.2.
STATUSES = {"blocked", "dismissed"}
TIERS = {"A0", "A1", "A2", "A3"}
CLASSIFICATIONS = {"public", "internal", "confidential", "personal", "restricted"}
# A route, never a raw model name (Appendix C #5). Enforced, not suggested.
MODEL_ROUTE = re.compile(r"^gateway/[a-z0-9-]+$")


@dataclass
class Artifact:
    path: pathlib.Path
    stage: str
    header: dict
    body: str
    errors: list[str] = field(default_factory=list)

    @property
    def change_id(self) -> str:
        return str(self.header.get("change_id", ""))


def parse(path: pathlib.Path) -> Artifact:
    text = path.read_text()
    # The stage is the folder the artifact lives in. Tolerate a path outside the
    # repository so a draft can be validated before it is moved into place.
    stage = STAGES.get(path.parent.name, "unknown")

    if not text.startswith("---\n"):
        return Artifact(path, stage, {}, text, ["missing YAML artifact header"])
    _, _, rest = text.partition("---\n")
    raw, sep, body = rest.partition("\n---\n")
    if not sep:
        return Artifact(path, stage, {}, text, ["artifact header is not terminated by ---"])
    try:
        header = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        return Artifact(path, stage, {}, body, [f"header is not valid YAML: {exc}"])
    if not isinstance(header, dict):
        return Artifact(path, stage, {}, body, ["header must be a YAML mapping"])
    return Artifact(path, stage, header, body, validate(header))


def validate(header: dict) -> list[str]:
    """Validate the §6.2 header. Deterministic; no judgement calls."""
    errors: list[str] = []
    for key in REQUIRED:
        if key not in header or header[key] in (None, "", []):
            errors.append(f"missing required header field: {key}")

    change_id = str(header.get("change_id", ""))
    if change_id and not CHANGE_ID.match(change_id):
        errors.append(f"change_id must match CHG-YYYY-NNNNNN, got {change_id!r}")

    if (rc := header.get("risk_class")) and rc not in RISK_CLASSES:
        errors.append(f"risk_class must be one of {sorted(RISK_CLASSES)}, got {rc!r}")

    if (tier := header.get("autonomy_tier")) and tier not in TIERS:
        errors.append(f"autonomy_tier must be one of {sorted(TIERS)}, got {tier!r}")

    if (dc := header.get("data_classification")) and dc not in CLASSIFICATIONS:
        errors.append(f"data_classification must be one of {sorted(CLASSIFICATIONS)}, got {dc!r}")

    route = str(header.get("model_route", ""))
    if route and not MODEL_ROUTE.match(route):
        errors.append(
            f"model_route must be a gateway route, not a raw model name, got {route!r} "
            "(Substitution Test #5)"
        )

    controls = header.get("controls")
    if controls is not None and not isinstance(controls, list):
        errors.append("controls must be a list of control objective ids")

    if "originator" in header and "@" not in str(header.get("originator", "")):
        errors.append("originator must be an email address")

    # A terminal status must say why. "blocked" with no reason is the gap it exists to close,
    # relabelled — and a reason with no status is a note nothing can query.
    status, reason = header.get("status"), header.get("status_reason")
    if status is not None:
        if status not in STATUSES:
            errors.append(f"status must be one of {sorted(STATUSES)}, got {status!r}")
        if not str(reason or "").strip():
            errors.append(f"status: {status} requires a status_reason saying why")
    elif reason:
        errors.append("status_reason is set without a status")

    return errors


def all_artifacts() -> list[Artifact]:
    found = []
    for folder in STAGES:
        for path in sorted((ROOT / folder).glob("*.md")):
            found.append(parse(path))
    return found


def chain(change_id: str) -> dict[str, Artifact]:
    return {a.stage: a for a in all_artifacts() if a.change_id == change_id}


def claimed_paths() -> dict[str, str]:
    """Every path a plan's `## Files` section claims, mapped to the plan claiming it.

    Read by check_plan_conformance (is this path planned at all?) and by
    check_autonomy (which plan owns this path, so which plan's risk class the
    path floor applies to). One parser, so the two gates cannot disagree.
    """
    claimed: dict[str, str] = {}
    for artifact in all_artifacts():
        if artifact.stage != "plan":
            continue
        section = re.search(r"^##\s+Files\s*$(.*?)(?=^##\s|\Z)", artifact.body, re.M | re.S)
        if not section:
            continue
        for line in section.group(1).splitlines():
            if match := re.match(r"\s*[-*]\s+`([^`]+)`", line):
                claimed[match.group(1)] = artifact.path.name
    return claimed
