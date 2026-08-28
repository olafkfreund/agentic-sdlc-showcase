# The closed loop (playbook Stage 4.1): one command each, non-zero on failure.
.PHONY: install build test lint gates eval substitution negative all clean

PY ?= python3

install:
	$(PY) -m pip install -q -e '.[dev]'

build:
	@$(PY) -c "import service.app.main" && echo "Build succeeded"

test:
	$(PY) -m pytest -q

lint:
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .

# The deterministic control layer (playbook §5.4). Advisory layer is AGENTS.md + skills.
gates:
	@$(PY) scripts/check_money.py
	@$(PY) scripts/check_pii.py
	@bash scripts/check_endpoints.sh
	@$(PY) scripts/check_frozen_paths.py
	@$(PY) scripts/check_codeowners.py
	@$(PY) scripts/check_artifact_header.py
	@$(PY) scripts/check_autonomy.py
	@$(PY) scripts/check_plan_conformance.py
	@$(PY) scripts/bundle_evidence.py
	@echo "All gates passed"

eval:
	$(PY) .agent/evals/run.py

# Appendix C, scored against this repository rather than self-assessed.
substitution:
	$(PY) scripts/substitution_test.py

# Prove the gates refuse. A gate verified only by passing is not verified.
negative:
	bash scripts/demo/negative/run_all.sh

all: build test lint gates
