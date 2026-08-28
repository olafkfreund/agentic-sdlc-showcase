#!/usr/bin/env python3
"""Generate the derived pages of the site from the repository itself.

The site publishes the playbook and the artifact chain **as they are on disk**, so
the page and the repository cannot drift into disagreeing. Nothing here is a second
source of truth; it only adds the Jekyll front matter that the source files must not
carry — an artifact's §6.2 header is YAML the gates parse, and turning it into
Jekyll front matter would hide the very thing worth showing.

    python site/build_pages.py        # writes site/playbook.md and site/chain/

Idempotent, and the generated files are git-ignored.
"""

from __future__ import annotations

import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

sys.path.insert(0, str(ROOT / "scripts"))
import artifacts  # noqa: E402

STAGE_TITLE = {"intent": "Intent", "spec": "Spec", "plan": "Plan"}
STAGE_ORDER = {"intent": 0, "spec": 1, "plan": 2}


def front_matter(**fields: object) -> str:
    lines = ["---"]
    for key, value in fields.items():
        if value is None:
            continue
        text = str(value).replace('"', "'")
        lines.append(f'{key}: "{text}"' if isinstance(value, str) else f"{key}: {value}")
    lines.append("---\n")
    return "\n".join(lines)


def write_playbook() -> None:
    source = ROOT / "Synechron-Agentic-SDLC-Playbook.md"
    body = source.read_text()
    # The document opens with its own H1; the layout renders the title, so drop it
    # rather than showing the same heading twice.
    if body.startswith("# "):
        body = body.split("\n", 1)[1].lstrip("\n")
    (SITE / "playbook.md").write_text(
        front_matter(
            layout="page",
            title="The Agentic SDLC Playbook",
            permalink="/playbook/",
            lede="The v1.0 text this repository implements, published as it is on disk.",
            source=source.name,
        )
        + body
    )


def write_chain() -> None:
    out = SITE / "chain"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)

    found = [a for a in artifacts.all_artifacts() if a.change_id]
    found.sort(key=lambda a: (a.change_id, STAGE_ORDER.get(a.stage, 9)))

    rows = []
    for artifact in found:
        rel = artifact.path.relative_to(ROOT).as_posix()
        slug = f"{artifact.change_id}-{artifact.stage}".lower()
        header = "\n".join(f"{k}: {v}" for k, v in artifact.header.items())
        body = artifact.body.lstrip("\n")
        if body.startswith("# "):
            body = body.split("\n", 1)[1].lstrip("\n")

        (out / f"{slug}.md").write_text(
            front_matter(
                layout="page",
                title=f"{STAGE_TITLE[artifact.stage]} · {artifact.change_id}",
                permalink=f"/chain/{slug}/",
                lede=f"Stage artifact from {rel}, header and all.",
                source=rel,
            )
            # The §6.2 header is the point of the artifact, so it is rendered rather
            # than consumed as Jekyll front matter.
            + f"```yaml\n{header}\n```\n\n{body}"
        )
        rows.append((artifact, slug, rel))

    index = [
        front_matter(
            layout="page",
            title="The artifact chain",
            permalink="/chain/",
            lede=(
                "intent → spec → plan, each carrying the machine-readable header that "
                "makes the chain queryable rather than merely present."
            ),
        ),
        "Three commits, three authors, three timestamps. **The chain of commits is the "
        "audit trail** — no transcript, no chat window, no vendor's session store.\n",
        "| Change | Stage | Risk | Autonomy | Controls | Source |",
        "|---|---|---|---|---|---|",
    ]
    for artifact, slug, rel in rows:
        controls = ", ".join(f"`{c}`" for c in artifact.header.get("controls", []) or [])
        index.append(
            f"| [{artifact.change_id}]({{{{ site.baseurl }}}}/chain/{slug}/) "
            f"| {STAGE_TITLE[artifact.stage]} "
            f"| `{artifact.header.get('risk_class', '')}` "
            f"| `{artifact.header.get('autonomy_tier', '')}` | {controls} "
            f"| [`{rel}`](https://github.com/olafkfreund/agentic-sdlc-showcase/blob/main/{rel}) |"
        )
    index.append(
        "\n> A chain with a gap is markdown. `scripts/check_artifact_header.py` refuses a "
        "plan whose spec is missing, and a spec whose intent is missing.\n"
    )
    (out / "index.md").write_text("\n".join(index))


def main() -> int:
    write_playbook()
    write_chain()
    pages = list((SITE / "chain").glob("*.md"))
    print(f"generated site/playbook.md and {len(pages)} chain page(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
