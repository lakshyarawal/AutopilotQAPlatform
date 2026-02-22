PYTHON ?= python3
VENV ?= .venv
ACTIVATE = . $(VENV)/bin/activate

.PHONY: help setup preflight api dashboard ingest smoke

help:
	@echo "Targets:"
	@echo "  make setup      - create venv, install deps, bootstrap .env, run preflight"
	@echo "  make preflight  - run local preflight checks"
	@echo "  make api        - start FastAPI server"
	@echo "  make ingest     - generate sample data and call /api/ingest"
	@echo "  make dashboard  - start Streamlit dashboard"
	@echo "  make smoke      - run smoke test (socket + in-process fallback)"

setup:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && python -m pip install --upgrade pip
	$(ACTIVATE) && pip install -r requirements.txt
	cp -n .env.example .env || true
	$(ACTIVATE) && python scripts/preflight_check.py

preflight:
	$(ACTIVATE) && python scripts/preflight_check.py

api:
	$(ACTIVATE) && uvicorn app.main:app --host 127.0.0.1 --port 8000

dashboard:
	$(ACTIVATE) && streamlit run dashboard/app.py

ingest:
	$(ACTIVATE) && python3 scripts/generate_sample_dataset.py
	curl -X POST http://127.0.0.1:8000/api/ingest \
	  -H "Content-Type: application/json" \
	  -d '{"dataset_name":"sample-bdd-like","metadata_file":"data/raw/sample_metadata.jsonl"}'

smoke:
	$(ACTIVATE) && bash scripts/smoke_test.sh
