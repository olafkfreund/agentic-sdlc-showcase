#!/usr/bin/env python3
"""TPR-05 — Appendix C, the Substitution Test, executed rather than self-assessed.

  "Can you change your agent runtime and your underlying model on a Monday and have
   identical context, identical controls and identical audit evidence on Tuesday?"

Twelve checks. Each inspects the repository for evidence, not for intent. Scoring
honestly is the whole point of the appendix, so nothing here awards a mark for a
document that merely claims a property.

Nine or fewer: a vendor SDLC. Ten or eleven: portable in principle, untested in
practice. Twelve: you can change your mind.
"""

from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import gate  # noqa: E402

ROOT = gate.ROOT

# Filenames that make context legible to exactly one vendor's product.
VENDOR_CONTEXT = [
    "CLAUDE.md",
    ".cursorrules",
    ".windsurfrules",
    ".aider.conf.yml",
    "GEMINI.md",
    ".continuerules",
]

# Raw model names must appear nowhere outside documentation about why they must not.
RAW_MODEL = re.compile(
    r"\b(gpt-[45][\w.-]*|claude-(?:opus|sonnet|haiku|fable)[\w.-]*|gemini-[12]\.\d[\w.-]*"
    r"|llama-?[34][\w.-]*|mistral-large[\w.-]*)\b",
    re.I,
)

SCANNED_SUFFIXES = {".py", ".yaml", ".yml", ".sh", ".toml", ".json"}
SKIP_DIRS = {".git", ".venv", "__pycache__", ".ruff_cache", ".pytest_cache", "evidence"}
# The detector holds the pattern it hunts for, so it cannot scan itself.
SELF = pathlib.Path(__file__).name


def _files() -> list[pathlib.Path]:
    return [
        p
        for p in ROOT.rglob("*")
        if p.is_file()
        and not SKIP_DIRS & set(p.relative_to(ROOT).parts)
        and p.suffix in SCANNED_SUFFIXES
        and p.name != SELF
    ]


def _text(rel: str) -> str:
    path = ROOT / rel
    return path.read_text() if path.exists() else ""


def check_01() -> tuple[bool, str]:
    """Repository context in AGENTS.md rather than a vendor-specific filename."""
    if not (ROOT / "AGENTS.md").exists():
        return False, "no AGENTS.md at repository root"
    present = [f for f in VENDOR_CONTEXT if (ROOT / f).exists()]
    if present:
        return False, f"vendor context files present: {present}"
    pointer = ROOT / ".github/copilot-instructions.md"
    if pointer.exists() and len(pointer.read_text().split()) > 80:
        return False, "copilot-instructions.md holds context; it must be a pointer only"
    return True, "AGENTS.md is the source of truth; the Copilot file is a pointer"


def check_02() -> tuple[bool, str]:
    """Procedures packaged as Agent Skills rather than vendor-proprietary constructs."""
    skills = sorted((ROOT / ".agent/skills").glob("*/SKILL.md"))
    if not skills:
        return False, "no SKILL.md files under .agent/skills/"
    missing = [
        s.parent.name
        for s in skills
        if not all(k in s.read_text() for k in ("name:", "description:", "policy_owner:"))
    ]
    if missing:
        return False, f"skills missing required frontmatter: {missing}"
    return True, f"{len(skills)} skills, each with a named policy owner"


def check_03() -> tuple[bool, str]:
    """Agents reach tools and data through MCP servers on a platform allowlist."""
    allowlist = ROOT / ".agent/mcp-allowlist.yaml"
    if not allowlist.exists():
        return False, "no .agent/mcp-allowlist.yaml"
    doc = gate.load_yaml(".agent/mcp-allowlist.yaml")
    if doc.get("policy") != "deny_by_default":
        return False, "MCP policy is not deny_by_default"
    if doc.get("skills", {}).get("sideloading") != "forbidden":
        return False, "skill sideloading is not forbidden"
    return True, f"{len(doc.get('allowed', []))} servers allowlisted, deny by default"


def check_04() -> tuple[bool, str]:
    """All model calls traverse a gateway you control."""
    doc = gate.load_yaml(".agent/routes.yaml")
    if not doc.get("gateway", {}).get("endpoint"):
        return False, "no gateway endpoint declared in .agent/routes.yaml"
    offenders = [
        str(p.relative_to(ROOT))
        for p in _files()
        if re.search(r"api\.(openai|anthropic)\.com|generativelanguage\.googleapis", p.read_text())
    ]
    if offenders:
        return False, f"direct provider endpoints referenced in {offenders}"
    return True, "one gateway; no direct provider endpoint anywhere in the tree"


def check_05() -> tuple[bool, str]:
    """Model choices expressed as routes rather than hard-coded model names."""
    offenders = []
    for p in _files():
        for match in RAW_MODEL.finditer(p.read_text()):
            offenders.append(f"{p.relative_to(ROOT)}: {match.group(0)}")
    if offenders:
        return False, f"raw model names found: {offenders[:5]}"
    routes = gate.load_yaml(".agent/routes.yaml").get("routes", {})
    if not routes:
        return False, "no routes declared"
    return True, f"{len(routes)} routes, zero raw model names"


def check_06() -> tuple[bool, str]:
    """Every control that must always hold has a deterministic enforcement point."""
    controls = gate.load_yaml("policy/controls.yaml")["controls"]
    ungated = [c["id"] for c in controls if not c.get("gate")]
    if ungated:
        return False, f"control objectives with no gate: {ungated}"
    missing = [
        c["id"]
        for c in controls
        if c["gate"].startswith("scripts/") and not (ROOT / c["gate"].split()[0]).exists()
    ]
    if missing:
        return False, f"gates named but not present: {missing}"
    return True, f"{len(controls)} control objectives, each with a deterministic gate"


def check_07() -> tuple[bool, str]:
    """Telemetry emitted in OpenTelemetry form and normalised at your collector."""
    doc = gate.load_yaml(".agent/routes.yaml")
    telemetry = doc.get("gateway", {}).get("telemetry", "")
    if not telemetry.startswith("otlp://"):
        return False, "gateway telemetry is not an OTLP endpoint"
    if not (ROOT / "ops/otel-collector.yaml").exists():
        return False, (
            "no collector configuration; the GenAI conventions are still at Development "
            "status and must be normalised at the collector (§5.5)"
        )
    return True, "OTLP to a collector that normalises the GenAI attributes"


def check_08() -> tuple[bool, str]:
    """Approval gates in your CI and version control, not a vendor's hosted service."""
    workflows = sorted((ROOT / ".github/workflows").glob("*.yml"))
    if not workflows:
        return False, "no workflows"
    if not (ROOT / "CODEOWNERS").exists():
        return False, "no CODEOWNERS"
    if not any("environment:" in w.read_text() for w in workflows):
        return False, "no environment-gated job; the production approval is not enforced"
    return True, f"{len(workflows)} workflows, CODEOWNERS, environment approval gate"


def check_09() -> tuple[bool, str]:
    """Agent identity distinct from human identity in every log and every record."""
    header_doc = _text("docs/artifact-header.md")
    if "agent_identity" not in header_doc:
        return False, "artifact header does not carry agent_identity"
    import artifacts

    if "agent_identity" not in artifacts.REQUIRED:
        return False, "agent_identity is not a required, validated header field"
    if "originator" not in artifacts.REQUIRED:
        return False, "originator is not a required header field"
    return True, "agent_identity and originator both required and validated separately"


def check_10() -> tuple[bool, str]:
    """An eval suite capable of qualifying a different model in under a day."""
    cases = sorted((ROOT / ".agent/evals/cases").glob("*.yaml"))
    if not (ROOT / ".agent/evals/run.py").exists():
        return False, "no eval runner"
    if len(cases) < 20:
        return False, f"{len(cases)} eval cases; the playbook calls for 20-50 (Stage 4.5)"
    return True, f"{len(cases)} eval cases with a non-interactive runner"


def check_11() -> tuple[bool, str]:
    """The artifact chain in your repositories rather than a vendor's session store."""
    import artifacts

    found = artifacts.all_artifacts()
    if not found:
        return False, "no artifacts in intent/, specs/ or plans/"
    broken = [str(a.path.name) for a in found if a.errors]
    if broken:
        return False, f"artifacts with invalid headers: {broken}"
    complete = [
        cid
        for cid in {a.change_id for a in found}
        if set(artifacts.chain(cid)) >= {"intent", "spec", "plan"}
    ]
    if not complete:
        return False, "no change has a complete intent -> spec -> plan chain"
    return True, f"{len(found)} artifacts, {len(complete)} complete chain(s), all headers valid"


def check_12() -> tuple[bool, str]:
    """Could you produce, today, a signed evidence trail without asking a vendor?"""
    if not (ROOT / "scripts/query_evidence.py").exists():
        return False, "no evidence query tool"
    release = _text(".github/workflows/05-release.yml")
    if "attest-build-provenance" not in release:
        return False, "the release workflow produces no signed provenance attestation"
    if "id-token: write" not in release:
        return False, "no OIDC identity for signing; attestations would be unverifiable"
    return True, "signed in-toto provenance from your own CI, queryable locally"


CHECKS = [
    (1, "Context in AGENTS.md, not a vendor filename", check_01),
    (2, "Procedures as Agent Skills", check_02),
    (3, "Tools via MCP on a platform allowlist", check_03),
    (4, "All model calls traverse your gateway", check_04),
    (5, "Model choices are routes, not model names", check_05),
    (6, "Every must-hold control has a deterministic gate", check_06),
    (7, "Telemetry in OTel, normalised at your collector", check_07),
    (8, "Approval gates in your CI and VCS", check_08),
    (9, "Agent identity distinct from human identity", check_09),
    (10, "Eval suite can qualify a new model in a day", check_10),
    (11, "Artifact chain in your repository", check_11),
    (12, "Signed evidence trail without asking a vendor", check_12),
]

VERDICTS = [
    (9, "VENDOR SDLC — you have a vendor's SDLC, not an agentic one."),
    (11, "PORTABLE IN PRINCIPLE, UNTESTED — run the substitution in a branch."),
    (12, "PORTABLE — you can change your mind, which is the only durable position."),
]


def main() -> int:
    results, findings = [], []
    for number, title, check in CHECKS:
        try:
            passed, detail = check()
        except Exception as exc:  # a check that cannot run has not passed
            passed, detail = False, f"check raised {type(exc).__name__}: {exc}"
        results.append({"n": number, "title": title, "pass": passed, "detail": detail})
        print(f"  {'PASS' if passed else 'FAIL'}  {number:2d}. {title}")
        print(f"        {detail}")
        if not passed:
            findings.append(f"#{number} {title}: {detail}")

    score = sum(r["pass"] for r in results)
    verdict = next(v for threshold, v in VERDICTS if score <= threshold)
    print(f"\n  Substitution Test: {score}/12 — {verdict}\n")

    if summary := __import__("os").environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary, "a") as fh:
            fh.write(f"## Substitution Test: {score}/12\n\n{verdict}\n\n")
            fh.write("| | Check | Detail |\n|---|---|---|\n")
            for r in results:
                mark = "PASS" if r["pass"] else "FAIL"
                fh.write(f"| {mark} | {r['n']}. {r['title']} | {r['detail']} |\n")

    return gate.report(
        "TPR-05",
        "substitution_test",
        score == 12,
        findings,
        score=score,
        max_score=12,
        verdict=verdict,
        checks=results,
    )


if __name__ == "__main__":
    raise SystemExit(main())
