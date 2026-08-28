"""The severity arithmetic that gates a merge (REVIEW.md).

No model runs in the gate, so this is the whole decision — it is worth a test.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import review_tally as rt  # noqa: E402


def comment(body, reply_to=None):
    return {"body": body, "in_reply_to_id": reply_to}


def test_no_comments_is_no_findings():
    assert rt.tally([]) == dict.fromkeys(rt.SEVERITIES, 0)


def test_counts_each_severity():
    counts = rt.tally(
        [
            comment("**[critical]** secret in the diff"),
            comment("[material] no audit event on POST /refunds"),
            comment("[minor] this will break on an empty list"),
            comment("[cosmetic] naming"),
            comment("[cosmetic] spacing"),
        ]
    )
    assert counts == {"critical": 1, "material": 1, "minor": 1, "cosmetic": 2}


def test_severity_tag_is_case_insensitive():
    assert rt.tally([comment("[CRITICAL] boom")])["critical"] == 1


def test_replies_do_not_count():
    """A reply on a thread is discussion, not a second finding."""
    assert rt.tally([comment("[material] x", reply_to=1)])["material"] == 0


def test_several_findings_in_one_comment_all_count():
    counts = rt.tally([comment("[material] one\nand also [material] two\n[minor] three")])
    assert counts["material"] == 2
    assert counts["minor"] == 1


def test_untagged_prose_is_not_a_finding():
    assert rt.tally([comment("Looks good to me, nice work")]) == dict.fromkeys(rt.SEVERITIES, 0)


def test_only_critical_and_material_block():
    assert {"critical", "material"} == rt.BLOCKING
    assert "cosmetic" not in rt.BLOCKING and "minor" not in rt.BLOCKING
