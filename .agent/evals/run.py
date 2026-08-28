#!/usr/bin/env python3
"""Non-interactive eval runner (playbook Stage 4.5).

static  — assert the configuration each case depends on is present and correct.
gateway — send each prompt through the routed gateway and check the response.

The gate is the pass rate, not any single case; a suite that must be 100% green gets
its awkward cases deleted rather than fixed.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CASES = pathlib.Path(__file__).resolve().parent / "cases"
MIN_PASS_RATE = 0.90


def flat(text: str) -> str:
    """Collapse whitespace before matching.

    A policy statement does not stop being present because the line wrapped, and an
    eval that fails on a reflow trains people to ignore the suite.
    """
    return " ".join(text.split())


def check_context(requirement: dict) -> tuple[bool, str]:
    """One `context_requires` entry. Deterministic; no model involved."""
    if "file" in requirement:
        path = ROOT / requirement["file"]
        if not path.exists():
            return False, f"missing file {requirement['file']}"
        text = flat(path.read_text())
        for needle in requirement.get("contains", []):
            if flat(needle) not in text:
                return False, f"{requirement['file']} no longer contains {needle!r}"
        for needle in requirement.get("absent", []):
            if flat(needle) in text:
                return False, f"{requirement['file']} unexpectedly contains {needle!r}"
        return True, ""

    if "gate" in requirement:
        gate_path = ROOT / requirement["gate"]
        if not gate_path.exists():
            return False, f"gate {requirement['gate']} no longer exists"
        return True, ""

    if "route" in requirement:
        routes = yaml.safe_load((ROOT / ".agent/routes.yaml").read_text())
        if requirement["route"] not in routes.get("routes", {}):
            return False, f"route {requirement['route']} is not declared"
        return True, ""

    if "skill" in requirement:
        skill = ROOT / ".agent/skills" / requirement["skill"] / "SKILL.md"
        if not skill.exists():
            return False, f"skill {requirement['skill']} is missing"
        text = flat(skill.read_text())
        for needle in requirement.get("contains", []):
            if flat(needle) not in text:
                return False, f"skill {requirement['skill']} no longer covers {needle!r}"
        return True, ""

    return False, f"unrecognised requirement: {requirement}"


def check_response(case: dict, response: str) -> tuple[bool, str]:
    expect = case.get("expect", {})
    for needle in expect.get("must_contain", []):
        if needle.lower() not in response.lower():
            return False, f"response omits {needle!r}"
    for needle in expect.get("must_not_contain", []):
        if needle.lower() in response.lower():
            return False, f"response contains forbidden {needle!r}"
    return True, ""


def ask_gateway(case: dict) -> str:
    """Send the prompt through the routed gateway.

    Deliberately the only place in this repository that talks to a model, and it
    resolves a route rather than naming one (Substitution Test #4, #5).
    """
    import urllib.request

    routes = yaml.safe_load((ROOT / ".agent/routes.yaml").read_text())
    endpoint = routes["gateway"]["endpoint"]
    token = os.environ.get("AI_GATEWAY_TOKEN")
    if not token:
        raise RuntimeError(
            "AI_GATEWAY_TOKEN is not set. In CI this is a short-lived workload identity "
            "token; there are no static provider keys anywhere (§5.1)."
        )
    payload = json.dumps(
        {"route": case["route"], "messages": [{"role": "user", "content": case["prompt"]}]}
    ).encode()
    request = urllib.request.Request(
        f"{endpoint}/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310
        return json.loads(response.read())["choices"][0]["message"]["content"]


def run(mode: str) -> int:
    cases = [yaml.safe_load(p.read_text()) for p in sorted(CASES.glob("*.yaml"))]
    if not cases:
        print("no eval cases found", file=sys.stderr)
        return 1

    results = []
    for case in cases:
        failures = []
        for requirement in case.get("context_requires", []):
            ok, why = check_context(requirement)
            if not ok:
                failures.append(why)

        if mode == "gateway" and not failures:
            try:
                ok, why = check_response(case, ask_gateway(case))
                if not ok:
                    failures.append(why)
            except Exception as exc:  # noqa: BLE001
                failures.append(f"gateway call failed: {exc}")

        results.append({"id": case["id"], "pass": not failures, "failures": failures})
        print(f"  {'PASS' if not failures else 'FAIL'}  {case['id']}")
        for failure in failures:
            print(f"        {failure}")

    passed = sum(r["pass"] for r in results)
    rate = passed / len(results)
    print(
        f"\n  Evals: {passed}/{len(results)} = {rate:.0%} "
        f"(mode={mode}, threshold={MIN_PASS_RATE:.0%})\n"
    )

    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary, "a") as fh:
            fh.write(f"## Evals ({mode}): {passed}/{len(results)} = {rate:.0%}\n\n")
            for r in results:
                if not r["pass"]:
                    fh.write(f"- **{r['id']}** — {'; '.join(r['failures'])}\n")

    sys.path.insert(0, str(ROOT / "scripts"))
    import gate

    return gate.report(
        "TPR-05",
        "evals",
        rate >= MIN_PASS_RATE,
        [f"{r['id']}: {'; '.join(r['failures'])}" for r in results if not r["pass"]],
        mode=mode,
        pass_rate=round(rate, 3),
        threshold=MIN_PASS_RATE,
        cases=len(results),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["static", "gateway"], default="static")
    raise SystemExit(run(parser.parse_args().mode))
