#!/usr/bin/env python3
"""FIN-02 — Monetary correctness. Fixed-precision decimal types only.

AGENTS.md states the convention so the agent applies it while working; this gate
proves it held. Write the policy once as guidance and once as a gate (§5.4).
"""

import ast
import pathlib
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import gate  # noqa: E402

MONEY_NAMES = {"amount", "amounts", "balance", "total", "price", "fee", "value_minor", "subtotal"}
BANNED_CALLS = {"round"}


class MoneyVisitor(ast.NodeVisitor):
    """Flag float literals and float()/round() reaching a monetary name."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.findings: list[str] = []

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        target = getattr(node.target, "id", getattr(node.target, "attr", ""))
        if (
            target in MONEY_NAMES
            and isinstance(node.annotation, ast.Name)
            and node.annotation.id == "float"
        ):
            self.findings.append(
                f"{self.path}:{node.lineno}: monetary field `{target}` annotated as float; "
                "use decimal.Decimal (AGENTS.md Conventions)"
            )
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        names = {getattr(t, "id", getattr(t, "attr", "")) for t in node.targets}
        if (
            names & MONEY_NAMES
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, float)
        ):
            self.findings.append(
                f"{self.path}:{node.lineno}: float literal assigned to a monetary name; "
                "use a Decimal built from a string"
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        name = getattr(node.func, "id", "")
        if name in BANNED_CALLS or name == "float":
            for arg in node.args:
                if getattr(arg, "id", getattr(arg, "attr", "")) in MONEY_NAMES:
                    self.findings.append(
                        f"{self.path}:{node.lineno}: `{name}()` applied to a monetary value; "
                        "quantise with Decimal instead (service/app/money.py)"
                    )
        self.generic_visit(node)


def main() -> int:
    findings: list[str] = []
    scanned = 0
    for path in sorted(pathlib.Path("service").rglob("*.py")):
        if "tests" in path.parts:
            continue
        scanned += 1
        visitor = MoneyVisitor(str(path))
        visitor.visit(ast.parse(path.read_text()))
        findings.extend(visitor.findings)

    return gate.report("FIN-02", "money", not findings, findings, files_scanned=scanned)


if __name__ == "__main__":
    raise SystemExit(main())
