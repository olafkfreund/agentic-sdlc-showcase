---
layout: home
title: Overview
heading: The operating model, as code that runs.
lede: >-
  A runnable reference implementation of the Agentic SDLC Playbook — seven stages,
  five planes, a portable artifact chain, an autonomy matrix, and the Substitution
  Test. Gates that refuse, and evidence that is a by-product rather than a
  reconstruction.
scores:
  - { value: "12/12", label: "Substitution Test", note: "portable — scored from the repository" }
  - { value: "12/12", label: "Deterministic gates", note: "each proven to refuse, not just to pass" }
  - { value: "24/24", label: "Configuration evals", note: "non-interactive regression suite" }
  - { value: "1 line", label: "To change agent vendor", note: "Copilot, Claude, Gemini or Codex" }
  - { value: "0", label: "Models in the gate", note: "the decision is arithmetic over policy" }
casts: true
---

## The whole argument, on one whiteboard

<figure class="infographic">
  <a href="{{ '/assets/img/governing-software-in-the-age-of-ai.webp' | relative_url }}">
    <img src="{{ '/assets/img/governing-software-in-the-age-of-ai.webp' | relative_url }}"
         width="2752" height="1536" loading="lazy" decoding="async"
         alt="Hand-drawn whiteboard infographic titled 'The Agentic SDLC: Governing Software in the
              Age of AI'. Across the top, traditional SDLC and human review as promises and
              checklists are crossed out and replaced by system verification, drawn as a turnstile a
              robot must pass. To the right, the portable architecture runs intent, spec, plan and
              code along a chain into git, labelled an immutable automatic audit trail, beside
              vendor-neutral standards AGENTS.md and MCP. Lower left, the Substitution Test asks
              whether you could switch AI vendors over a weekend and have identical audit evidence by
              Monday morning, next to a productivity J-curve showing AI as an amplifier. Lower right,
              a table maps planes of architecture to their role and key asset, and an autonomy matrix
              grids risk against environment.">
  </a>
  <figcaption>
    Click through for full resolution.
    <strong>AI-generated with Google NotebookLM</strong> from the playbook text, and one thing in it
    is wrong: it maps <em>three</em> planes, and
    <a href="{{ '/playbook/' | relative_url }}">§5</a> has <strong>five</strong> — Agent Runtime and
    Evidence are missing. Published with the gap named rather than quietly reproduced. The playbook
    is the source of truth; this is a way in.
  </figcaption>
</figure>

## Sixteen seconds, and nothing in it is staged

The nine acts of the control layer, recorded as they ran. The act to watch is **the gates
refuse** — each gate has the thing it protects deliberately broken, and must go red.

<div class="cast" data-cast="control-layer"></div>

<p class="cast-note">
  A recording of the real session, not a simulated terminal. If a gate had failed during
  the take, the recording would show it.
  <a href="{{ '/screencast/' | relative_url }}">The CI half is here →</a>
</p>

## The claim

Most agentic-SDLC material describes a workflow. This describes a **control layer**, and
then runs it. Three things follow from that, and each one is checkable on this site:

<div class="cards">
  <div class="card">
    <span class="tag">Principle 4</span>
    <h3>No model in the gate</h3>
    <p>Models diagnose, propose, draft and review. The decision to allow or block is
    arithmetic over version-controlled YAML — the same tables governance signed off.</p>
  </div>
  <div class="card">
    <span class="tag">Principle 5</span>
    <h3>Evidence as a by-product</h3>
    <p>Every gate writes a JSON record as it runs. Nothing is reconstructed at audit
    time, because a reconstruction is a story about a control, not the control.</p>
  </div>
  <div class="card">
    <span class="tag">Appendix C</span>
    <h3>Survives a change of vendor</h3>
    <p><code>make swap RUNTIME=claude</code> — one line of diff, and the gates, evals
    and Substitution Test re-score identically under every vendor. Executed, not claimed.</p>
  </div>
</div>

## Try it in two minutes

```bash
git clone https://github.com/olafkfreund/agentic-sdlc-showcase
cd agentic-sdlc-showcase
python -m venv .venv && .venv/bin/pip install -e '.[dev]'

make build test lint gates     # the closed loop plus the control layer
make substitution              # Appendix C, scored from the repository
make eval                      # 24 configuration regression cases
make negative                  # break each protected thing; watch every gate refuse
```

`make negative` is the one that matters.

> A gate verified only by passing is indistinguishable from a gate that cannot fail.

## The question this exists to answer

> *Which production changes touched control `SEC-API-01`, which were agent-authored, at
> what autonomy tier, and who approved each one?*

```bash
python scripts/query_evidence.py --control SEC-API-01
```

Seconds, from the repository. The playbook calls answering that in minutes rather than a
week **the single highest-value output of the whole programme**. It works because every
artifact in [the chain]({{ '/chain/' | relative_url }}) opens with a machine-readable
header, and every gate emits a record keyed to a control id.

## Where to go next

<div class="cards">
  <div class="card">
    <span class="tag">Start here</span>
    <h3><a href="{{ '/story/' | relative_url }}">One change, end to end</a></h3>
    <p>A user story from the sentence someone said in a meeting to a signed artifact —
    and what stays identical when you change vendor.</p>
  </div>
  <div class="card">
    <span class="tag">90 days</span>
    <h3><a href="{{ '/adoption/' | relative_url }}">Two organisations adopt this</a></h3>
    <p>Step by step at a tier-1 bank and a growth-stage payments firm — and why everything
    that differs between them lives in four YAML files.</p>
  </div>
  <div class="card">
    <span class="tag">16 seconds</span>
    <h3><a href="{{ '/screencast/' | relative_url }}">Watch it run</a></h3>
    <p>Two recordings of the real session — the control layer, and the same control
    layer running in CI. Nothing re-typed, simulated or spliced.</p>
  </div>
  <div class="card">
    <span class="tag">Stage by stage</span>
    <h3><a href="{{ '/stages/' | relative_url }}">The seven stages</a></h3>
    <p>What each stage's control point is, and which workflow enforces it.</p>
  </div>
  <div class="card">
    <span class="tag">The control layer</span>
    <h3><a href="{{ '/gates/' | relative_url }}">The gates that refuse</a></h3>
    <p>Twelve deliberate violations and the gate that stops each one.</p>
  </div>
  <div class="card">
    <span class="tag">Appendix C</span>
    <h3><a href="{{ '/substitution/' | relative_url }}">The Substitution Test</a></h3>
    <p>Twelve checks executed against the tree — no marks for a document that claims.</p>
  </div>
  <div class="card">
    <span class="tag">Portability</span>
    <h3><a href="{{ '/runtimes/' | relative_url }}">Switching the agent vendor</a></h3>
    <p>Copilot, Claude, Gemini, Codex — one command, and the proof that nothing else moved.</p>
  </div>
  <div class="card">
    <span class="tag">Source</span>
    <h3><a href="{{ '/playbook/' | relative_url }}">The playbook itself</a></h3>
    <p>The full v1.1 text this repository implements, published as it is on disk.</p>
  </div>
</div>

<div class="disclaimer">
  <strong>Demo data.</strong> The evidence records, attestations and change ids here are
  produced by this repository's own pipeline against a synthetic payments service. They
  are not any institution's audit records, and nothing here should be presented as one.
</div>
