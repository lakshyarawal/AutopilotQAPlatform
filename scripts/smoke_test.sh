#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8000}"
BASE="http://127.0.0.1:${PORT}"
API="${BASE}/api"

echo "[1/5] Checking health endpoint"
if ! curl -fsS "${BASE}/health" >/dev/null 2>&1; then
  echo "health endpoint unreachable on ${BASE}; running in-process smoke fallback"
  python3 scripts/smoke_test_inprocess.py
  exit $?
fi

echo "[2/5] Ensuring sample metadata exists"
if [[ ! -f data/raw/sample_metadata.jsonl ]]; then
  python3 scripts/generate_sample_dataset.py
fi

echo "[3/5] Ingesting dataset"
curl -fsS -X POST "${API}/ingest" \
  -H "Content-Type: application/json" \
  -d '{"dataset_name":"sample-bdd-like","metadata_file":"data/raw/sample_metadata.jsonl"}' >/dev/null

echo "[4/5] Checking search endpoint"
SEARCH_JSON="$(curl -fsS "${API}/assets/search?limit=5")"
python3 - << 'PY' "$SEARCH_JSON"
import json
import sys
payload = json.loads(sys.argv[1])
if not isinstance(payload, list):
    raise SystemExit("search response is not a list")
print(f"search_count={len(payload)}")
PY

echo "[5/5] Checking QA endpoint"
QA_JSON="$(curl -fsS "${API}/qa/summary")"
python3 - << 'PY' "$QA_JSON"
import json
import sys
payload = json.loads(sys.argv[1])
required = ["total_assets", "total_annotations", "missing_label_assets", "label_distribution", "annotator_disagreement_rate", "hard_examples"]
missing = [k for k in required if k not in payload]
if missing:
    raise SystemExit(f"qa missing keys: {missing}")
if payload["total_assets"] <= 0:
    raise SystemExit("qa total_assets must be > 0")
print(f"qa_total_assets={payload['total_assets']}")
PY

echo "smoke_status=ok"
