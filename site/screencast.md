---
layout: page
title: Watch it run
permalink: /screencast/
lede: >-
  Two recordings: the control layer on a laptop, and the same control layer running
  in CI on a real change. Both are recordings of the actual session — nothing is
  re-typed, simulated, spliced or replayed.
casts: true
---

## The control layer, in nine acts

Sixteen seconds. The chapter markers jump to each act.

<div class="cast" data-cast="control-layer"
     data-title="The control layer, in nine acts"></div>

The act to watch is **the gates refuse**. Each gate has the thing it protects
deliberately broken and must go red — twelve of them, one at a time. A gate verified
only by passing is indistinguishable from a gate that cannot fail, so the passing run
is the less interesting half.

The last act changes the agent vendor four ways and re-scores the repository under each.
Identical every time, because none of what produced the scores belongs to a vendor.

---

## The same control layer, running in CI

This is the half a laptop cannot show: the gates reporting as **required status checks**
on a real pull request, a detector firing with no human in the invocation path, and a
code-owner rule refusing a merge.

<div class="cast" data-cast="pipeline"
     data-title="The same control layer, running in CI"></div>

It triggers a Stage 6 run and watches it to completion with `gh run watch`. That is a run
happening while the recording is made, not one read back from history.

---

## Why these are asciicasts and not a video

Three recorders were available. The better-looking one, `vhs`, types commands into a
*simulated* terminal at a controlled pace and renders a polished GIF.

It was rejected, and the reason is recorded in
[the spec]({{ site.baseurl }}/chain/chg-2026-014908-spec/) so it survives the next person
who notices the GIF would look nicer:

> What it produces is a reconstruction of a session that never happened. A recording of a
> simulated terminal is exactly the artefact that reads as evidence while being a
> performance — the failure mode named in `REVIEW.md`, in the gates, and in the
> Substitution Test.

`asciinema` records the real session. **If a gate fails during a recording, the recording
shows it** — and `record.sh` keeps the cast when the session exits non-zero, because the
recording of a failure is the most useful recording there is.

The casts are **asciicast v2**: plain text, one JSON array per line. Two recordings diff
against each other, and a reviewer can read what was on screen without playing anything:

```bash
git diff site/assets/casts/            # what changed between takes
asciinema cat site/assets/casts/control-layer.cast   # the session as text
```

## Record them yourself

```bash
nix develop
just record              # both casts
just record local        # just the nine acts
just record pipeline     # just the CI half — triggers one Stage 6 run
just record --gif        # also render GIFs (git-ignored; the casts are the artifact)
just play control-layer  # play one back in your terminal
```

The chapter markers are **derived by scanning the banners the run actually printed**,
never from a list kept in the recorder. A hand-maintained chapter list is a second
description of the demo, and it would drift from the first.

<div class="disclaimer">
  <strong>One bug worth mentioning</strong>, because it is the kind this whole repository
  is about. The first recording truncated silently at three seconds, right as act 3 began.
  Act 3 is <code>make negative</code>, which stages the tree with <code>git add -A</code>
  and restores it with <code>git checkout -- .</code> — so the in-progress cast was staged
  and then overwritten by its own three-second-old copy while asciinema still held the file
  open. The recorder now writes outside the working tree and moves the finished cast in.
  A recording tool that quietly produces a shorter recording is the same failure as a gate
  that quietly passes.
</div>
