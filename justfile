# Agentic SDLC showcase — one command per thing.
#
#   nix develop         (or: devenv shell, or direnv allow)
#   just demo
#
# The Makefile stays the canonical definition of the loop and the gates: it is what
# CI runs and what AGENTS.md tells the agent to run, so these recipes call it rather
# than restating it. A second definition would drift, and the two would disagree on
# the day it mattered.

set shell := ["bash", "-uc"]

py := env_var_or_default("PY", ".venv/bin/python")

# Every recipe.
default:
    @just --list --unsorted

# ---------------------------------------------------------------- the demo

# The whole demo, narrated, pausing between acts.
demo *ARGS:
    @bash scripts/demo/run_demo.sh {{ ARGS }}

# The demo with no pauses — for a recording, or CI.
demo-fast:
    @bash scripts/demo/run_demo.sh --fast

# The demo plus the live pipeline on GitHub. Needs `gh auth login`.
demo-live:
    @bash scripts/demo/run_demo.sh --live

# The same control layer, watched live in CI. Triggers one Stage 6 run.
pipeline *ARGS:
    @bash scripts/demo/pipeline_demo.sh {{ ARGS }}

# Narrate what CI already did, without triggering anything.
pipeline-observe:
    @bash scripts/demo/pipeline_demo.sh --observe

# ---------------------------------------------------------------- screencasts

# Record both casts. `just record local`, `just record pipeline`, `just record --gif`.
record *ARGS:
    @bash scripts/demo/record.sh {{ ARGS }}

# Play a recorded cast back in this terminal.
play NAME="control-layer":
    @asciinema play site/assets/casts/{{ NAME }}.cast

# Render the casts to GIFs. Large, and git-ignored.
record-gif:
    @bash scripts/demo/record.sh all --gif

# ---------------------------------------------------------------- the loop

# Create the virtualenv and install the project. Not needed inside `nix develop`.
setup:
    python3 -m venv .venv
    .venv/bin/pip install -q -e '.[dev]'
    @echo "  ready — try: just check"

# Build, test, lint, gates. The four commands AGENTS.md tells the agent to run.
check:
    @make build test lint gates PY={{ py }}

test:
    @make test PY={{ py }}

lint:
    @make lint PY={{ py }}

# The deterministic control layer. No model is consulted in any of it.
gates:
    @make gates PY={{ py }}

# ---------------------------------------------------------------- the proofs

# Break each protected thing and watch every gate refuse. The honest half of `gates`.
negative:
    @make negative PY={{ py }}

# Appendix C, scored against the repository rather than self-assessed.
substitution:
    @make substitution PY={{ py }}

# The configuration regression suite that gates changes to the agent's steering.
eval:
    @make eval PY={{ py }}

# Change agent vendor four ways and re-score under each. No RUNTIME=? all four.
swap RUNTIME="":
    @make swap RUNTIME={{ RUNTIME }} PY={{ py }}

# Which runtimes are available, and which is selected.
runtimes:
    @{{ py }} scripts/switch_runtime.py --list

# ---------------------------------------------------------------- the questions

# Which changes touched a control, agent-authored or not, at what tier, approved by whom.
evidence CONTROL="SEC-API-01":
    @{{ py }} scripts/query_evidence.py --control {{ CONTROL }}

# Stage 6 detection: Western Electric rules, unit-tested, no model involved.
detect:
    @{{ py }} scripts/detect_anomaly.py

# The artifact chain, as the gates parse it.
chain:
    @{{ py }} -c "import sys; sys.path.insert(0,'scripts'); import artifacts; \
      [print(f'  {a.header.get(\"risk_class\",\"--\"):>3} {a.header.get(\"autonomy_tier\",\"--\"):>3}  {a.stage:6} {a.path.name}') \
       for a in artifacts.all_artifacts()]"

# ---------------------------------------------------------------- the site

# Generate the derived pages the site publishes from this tree.
site-build:
    @{{ py }} site/build_pages.py

# Serve the site locally. Needs ruby + jekyll (both in the dev shell).
site-serve: site-build
    cd site && bundle exec jekyll serve --livereload

# ---------------------------------------------------------------- housekeeping

# Everything CI runs, in CI's order. Run this before pushing.
ci: check eval substitution negative

fmt:
    @{{ py }} -m ruff format .
    @nix fmt 2>/dev/null || true

clean:
    rm -rf .venv .pytest_cache .ruff_cache site/_site site/.jekyll-cache
    rm -f site/playbook.md
    rm -rf site/chain
    find . -name __pycache__ -type d -prune -exec rm -rf {} +
    @echo "  clean"
