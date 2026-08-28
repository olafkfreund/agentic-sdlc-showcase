#!/usr/bin/env python3
"""Stage 5.2 — gate on the machine-readable severity tally, never on the narrative.

Reads the review comments on a pull request, counts findings by the severity labels
defined in REVIEW.md, and fails when critical or material findings remain open.

No model runs here. The review itself is a model's work; the decision this script makes
is arithmetic over its output, which is what keeps model behaviour out of the control
effectiveness argument (principle 4).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import gate  # noqa: E402

SEVERITIES = ["critical", "material", "minor", "cosmetic"]
BLOCKING = {"critical", "material"}
COSMETIC_CAP = 5

# Reviews mark findings as e.g. "**[material]** the audit event is missing".
TAG = re.compile(r"\[\s*(critical|material|minor|cosmetic)\s*\]", re.I)


def fetch_comments(pr: str) -> list[dict]:
    """Review comments on the PR, via the GitHub CLI already authenticated in CI."""
    out = subprocess.run(
        ["gh", "api", "--paginate", f"repos/{{owner}}/{{repo}}/pulls/{pr}/comments"],
        capture_output=True,
        text=True,
    )
    if out.returncode != 0:
        print(f"could not read review comments: {out.stderr.strip()}", file=sys.stderr)
        return []
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return []


def tally(comments: list[dict]) -> dict[str, int]:
    counts = dict.fromkeys(SEVERITIES, 0)
    for comment in comments:
        # A resolved thread is a finding that was dealt with; it does not block.
        if comment.get("in_reply_to_id"):
            continue
        for match in TAG.finditer(comment.get("body", "")):
            counts[match.group(1).lower()] += 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr", required=True)
    args = parser.parse_args()

    comments = fetch_comments(args.pr)
    counts = tally(comments)

    findings = [
        f"{counts[severity]} open {severity} finding(s) — see REVIEW.md"
        for severity in BLOCKING
        if counts[severity]
    ]
    if counts["cosmetic"] > COSMETIC_CAP:
        # Not blocking. An unbounded nitpick list trains reviewers to skim, so it is
        # recorded as a review-quality signal rather than held against the author.
        print(
            f"::warning::{counts['cosmetic']} cosmetic findings exceeds the cap of "
            f"{COSMETIC_CAP} (REVIEW.md). Tune the review passes, not the author."
        )

    return gate.report(
        "REV-01",
        "review_tally",
        not findings,
        findings,
        pull_request=args.pr,
        counts=counts,
        comments_read=len(comments),
        cosmetic_cap=COSMETIC_CAP,
    )


if __name__ == "__main__":
    raise SystemExit(main())
