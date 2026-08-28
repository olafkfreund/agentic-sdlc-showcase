"""The README's headline numbers must be true.

The repository's argument is that a control which reads as operating while it is
not is the failure mode worth fearing. A README claiming 23 evals over a suite of
24 is the same failure in miniature, so the claim is checked rather than trusted.
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
README = (ROOT / "README.md").read_text()
SOCIAL_CARD = (ROOT / "site/assets/social-card.svg").read_text()


def _claim(label: str) -> int:
    match = re.search(rf"^\s*{label}\s+(\d+)/(\d+)\s+—", README, re.M)
    assert match, f"README no longer states a {label} score"
    scored, total = int(match.group(1)), int(match.group(2))
    assert scored == total, f"README claims {label} {scored}/{total}"
    return total


def test_eval_case_count_matches_readme():
    cases = list((ROOT / ".agent/evals/cases").glob("*.yaml"))
    assert _claim("Evals") == len(cases)
    assert f"# {len(cases)} configuration regression cases" in README


def test_negative_test_count_matches_readme():
    script = (ROOT / "scripts/demo/negative/run_all.sh").read_text()
    refusals = len(re.findall(r"^expect_red ", script, re.M))
    assert _claim("Deterministic gates") == refusals


def test_substitution_check_count_matches_readme():
    source = (ROOT / "scripts/substitution_test.py").read_text()
    assert _claim("Substitution Test") == len(re.findall(r"^def check_\d+\(", source, re.M))


def test_social_card_scores_match_the_repository():
    """The link preview is the claim the most people see, and the fewest verify."""
    negative = (ROOT / "scripts/demo/negative/run_all.sh").read_text()
    substitution = (ROOT / "scripts/substitution_test.py").read_text()

    cases = len(list((ROOT / ".agent/evals/cases").glob("*.yaml")))
    refusals = len(re.findall(r"^expect_red ", negative, re.M))
    checks = len(re.findall(r"^def check_\d+\(", substitution, re.M))

    for score, label in (
        (f"{refusals}/{refusals}", "gates proven to refuse"),
        (f"{checks}/{checks}", "Substitution Test"),
        (f"{cases}/{cases}", "configuration evals"),
    ):
        assert score in SOCIAL_CARD, f"social card no longer claims {score} for {label}"
