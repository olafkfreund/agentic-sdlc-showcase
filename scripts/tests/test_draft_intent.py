"""Stage 6.4 — change id allocation.

Stage 6 failed on three consecutive nights allocating an id that already existed on a
`stage6/*` branch, then being refused the push and losing the finding entirely. The
allocator could not see its own previous output, because every id it had ever issued lived
on a branch that Actions is deliberately not permitted to merge.

So the case worth testing is not "does it increment". It is: **an id that exists nowhere in
the working tree still has to be skipped.**
"""

from __future__ import annotations

import sys

sys.path.insert(0, __file__.rsplit("/", 2)[0])

from draft_intent import (  # noqa: E402
    allocated_change_ids,
    next_change_id,
    reserved_change_ids,
)


def test_increments_past_the_highest_id():
    assert next_change_id({"CHG-2026-014910", "CHG-2026-014911"}) == "CHG-2026-014912"


def test_empty_set_starts_at_one():
    assert next_change_id(set()) == "CHG-2026-000001"


def test_ignores_ids_from_another_year():
    assert next_change_id({"CHG-2025-999999", "CHG-2026-000004"}) == "CHG-2026-000005"


def test_reserved_ids_reads_refs_and_never_raises():
    """Whatever the git situation, this returns a set.

    An allocator that raises because a remote was unreachable is a detector that does not
    run, which is the failure this whole change exists to remove. Degrading to the old
    behaviour is recoverable; refusing to start is not.
    """
    found = reserved_change_ids()
    assert isinstance(found, set)
    assert all(cid.startswith("CHG-") for cid in found)


def test_allocation_covers_ids_that_exist_only_on_a_branch():
    """**The regression.** This is the assertion that would have caught the outage.

    An id on a `stage6/*` branch appears in no artifact on `main`, because Actions is not
    permitted to merge those branches. Allocating from the working tree alone re-issues it,
    the push to the existing branch is rejected, and the issue fallback never runs because
    it sits behind the push.

    Skips rather than fails where there is no remote or no such branch — that is a
    different environment, not a regression. If the branches are triaged away this stops
    asserting anything and should be retired with them; what must not happen quietly is
    `allocated_change_ids` ceasing to consult refs.
    """
    import subprocess

    refs = subprocess.run(
        ["git", "ls-remote", "--heads", "origin", "refs/heads/stage6/*"],
        capture_output=True,
        text=True,
        check=False,
    )
    if refs.returncode != 0 or not refs.stdout.strip():
        return
    on_branches = {
        part
        for line in refs.stdout.splitlines()
        for part in line.split("/")
        if part.startswith("CHG-")
    }
    allocated = allocated_change_ids()
    assert on_branches <= allocated, (
        f"ids on stage6 branches are invisible to the allocator: {on_branches - allocated}"
    )
    # And the id it would hand out must not be one of them.
    assert next_change_id(allocated) not in on_branches
