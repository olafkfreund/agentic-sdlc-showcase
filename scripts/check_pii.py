#!/usr/bin/env python3
"""DP-11 — Personal data never reaches a log line or an error message.

The classification map in service/app/models.py is the source of truth. This gate
catches the two ways it gets bypassed: logging outside audit.safe_log(), and a
personal field interpolated into an exception message.
"""

import ast
import pathlib
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import gate  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from service.app.models import PERSONAL_FIELDS  # noqa: E402

UNSAFE_LOG = {"print", "info", "debug", "warning", "error", "exception", "critical"}
SANCTIONED = {"safe_log", "emit", "redact"}


def _names(node: ast.AST) -> set[str]:
    return {
        getattr(n, "id", getattr(n, "attr", ""))
        for n in ast.walk(node)
        if isinstance(n, ast.Name | ast.Attribute)
    } | {
        n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)
    }


def main() -> int:
    findings: list[str] = []
    scanned = 0
    for path in sorted(pathlib.Path("service").rglob("*.py")):
        if "tests" in path.parts or path.name == "audit.py":
            continue
        scanned += 1
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = getattr(node.func, "id", getattr(node.func, "attr", ""))
            if func in SANCTIONED:
                continue
            # Scan positional args, keyword names AND keyword values. Missing the
            # values is how `detail=request.payer_email` slips through.
            seen: set[str] = set()
            for arg in node.args:
                seen |= _names(arg)
            for keyword in node.keywords:
                seen |= _names(keyword.value)
                if keyword.arg:
                    seen.add(keyword.arg)
            leaked = PERSONAL_FIELDS & seen
            if func in UNSAFE_LOG:
                findings.append(
                    f"{path}:{node.lineno}: logging outside audit.safe_log(); "
                    "the sanctioned path is the only one that redacts"
                )
            elif leaked and func in {"HTTPException", "ValueError", "MoneyError"}:
                findings.append(
                    f"{path}:{node.lineno}: personal field(s) {sorted(leaked)} in an error "
                    "message; classified `personal` in service/app/models.py"
                )

    return gate.report(
        "DP-11",
        "pii",
        not findings,
        findings,
        files_scanned=scanned,
        personal_fields=sorted(PERSONAL_FIELDS),
    )


if __name__ == "__main__":
    raise SystemExit(main())
