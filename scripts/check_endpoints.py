#!/usr/bin/env python3
"""SEC-API-01 — the organisation's API security standard, as a gate.

Three rules from .agent/skills/secure-api-review/SKILL.md:
  1. Authentication  — every route except /health takes the gateway token.
  2. Audit           — every state-changing route emits an audit event.
  3. Validation      — every request body is a typed model, not a raw dict.
"""

import ast
import pathlib
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import gate  # noqa: E402

STATE_CHANGING = {"post", "put", "patch", "delete"}
ANONYMOUS_ALLOWED = {"/health"}
TOKEN_PARAM = "x_gateway_token"


def route_of(decorator: ast.expr) -> tuple[str, str] | None:
    """('post', '/payments') for an @app.post("/payments") decorator."""
    if not isinstance(decorator, ast.Call):
        return None
    method = getattr(decorator.func, "attr", "")
    if method not in STATE_CHANGING | {"get", "head", "options"}:
        return None
    if not decorator.args or not isinstance(decorator.args[0], ast.Constant):
        return None
    return method, decorator.args[0].value


def main() -> int:
    findings: list[str] = []
    routes = []
    for path in sorted(pathlib.Path("service").rglob("*.py")):
        if "tests" in path.parts:
            continue
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for decorator in node.decorator_list:
                found = route_of(decorator)
                if not found:
                    continue
                method, url = found
                routes.append(f"{method.upper()} {url}")
                where = f"{path}:{node.lineno} {method.upper()} {url}"
                args = {a.arg for a in node.args.args}
                body = ast.dump(node)

                # 1. Authentication
                if url not in ANONYMOUS_ALLOWED and TOKEN_PARAM not in args:
                    findings.append(
                        f"{where}: no gateway token parameter; only "
                        f"{sorted(ANONYMOUS_ALLOWED)} may be anonymous (rule 1)"
                    )
                # 2. Audit
                if method in STATE_CHANGING and "audit" not in body:
                    findings.append(
                        f"{where}: state-changing route emits no audit event; "
                        "call audit.emit(actor, action, entity) (rule 3)"
                    )
                # 3. Input validation
                if method in STATE_CHANGING:
                    typed = any(
                        isinstance(a.annotation, ast.Name)
                        and a.annotation.id.endswith(("Request", "Model"))
                        for a in node.args.args
                        if a.annotation
                    )
                    if not typed:
                        findings.append(
                            f"{where}: request body is not a typed Pydantic model; "
                            "unknown fields must be rejected (rule 2)"
                        )

    return gate.report("SEC-API-01", "endpoints", not findings, findings, routes=sorted(routes))


if __name__ == "__main__":
    raise SystemExit(main())
