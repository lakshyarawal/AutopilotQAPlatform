import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app


def main() -> int:
    client = TestClient(app)

    health = client.get("/health")
    if health.status_code != 200:
        print(f"health_fail status={health.status_code}")
        return 1

    with open("data/raw/sample_metadata.jsonl", "r", encoding="utf-8") as f:
        first = f.readline().strip()
    if not first:
        print("metadata_file_empty")
        return 1

    ingest = client.post(
        "/api/ingest",
        json={"dataset_name": "sample-bdd-like", "metadata_file": "data/raw/sample_metadata.jsonl"},
    )
    if ingest.status_code != 200:
        print(f"ingest_fail status={ingest.status_code} body={ingest.text}")
        return 1

    search = client.get("/api/assets/search", params={"limit": 5})
    if search.status_code != 200:
        print(f"search_fail status={search.status_code} body={search.text}")
        return 1

    payload = search.json()
    if not isinstance(payload, list):
        print("search_response_not_list")
        return 1

    qa = client.get("/api/qa/summary")
    if qa.status_code != 200:
        print(f"qa_fail status={qa.status_code} body={qa.text}")
        return 1

    qa_payload = qa.json()
    required = [
        "total_assets",
        "total_annotations",
        "missing_label_assets",
        "label_distribution",
        "annotator_disagreement_rate",
        "hard_examples",
    ]
    missing = [k for k in required if k not in qa_payload]
    if missing:
        print(f"qa_missing_keys={missing}")
        return 1

    print(f"inprocess_search_count={len(payload)}")
    print(f"inprocess_qa_total_assets={qa_payload['total_assets']}")
    print("smoke_status=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
