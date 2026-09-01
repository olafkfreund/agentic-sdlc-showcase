---
change_id: CHG-2026-014919
risk_class: R1
autonomy_tier: A2
controls: [TRC-01, CHG-04]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-balanced
supersedes: null
---

# Intent: the accent belongs in the words, not in a stripe

## Problem

Three containers in the stylesheet carry a 3px coloured border down one side: `blockquote`
(orange), `pre` (grey) and `.disclaimer` (yellow). A design linter flags all three as the
side-tab pattern — a thick coloured edge on one side of a card, which has become a
recognisable tell of generated interfaces.

The flag is worth acting on rather than suppressing. It is not that the pattern is wrong in
principle; it is that it does decoration's job while the content does none. A callout on this
site nearly always opens `**Like this.**`, and that lead is what tells the reader what kind
of callout it is. The stripe repeats the message in paint.

Suppressing the rule file-wide was the alternative and it is worse: it would silence the
check for every future edit to this stylesheet, including a genuine instance.

## Who is affected

Every page. Blockquotes are the site's primary callout device — roughly forty across the
published pages, and ten in the playbook alone.

## Success criteria

1. No 3px coloured side border remains on a container.
2. The three boxes stay visually distinct from each other and from body text. Removing the
   tell must not flatten the hierarchy.
3. Nothing about the content changes.

## Out of scope

- `.stage`, whose 2px left border is a timeline rail joining stage markers, terminated by
  `border-left-color: transparent` on the last child. It is a connector, not a card accent,
  and the linter does not flag it.
- `.audio-card`, which already uses a full 1px border.
