# API Reference

Base URL: `http://127.0.0.1:8000`

## Health

- `GET /health`
- Response: `{"status":"ok"}`

## Batch ingestion

- `POST /api/ingest`
- Body:

```json
{
  "dataset_name": "sample-bdd-like",
  "metadata_file": "data/raw/sample_metadata.jsonl"
}
```

## Search

- `GET /api/assets/search?q=&weather=&scenario=&limit=20`
- Response: list of assets with sensor metadata and lineage id.

## QA summary

- `GET /api/qa/summary`
- Response includes:
  - `total_assets`
  - `total_annotations`
  - `missing_label_assets`
  - `label_distribution`
  - `annotator_disagreement_rate`
  - `hard_examples`

## Streaming

- `POST /api/stream/events?dataset_name=stream-dataset`
- `POST /api/stream/events/batch`

## Preflight

- `GET /api/system/preflight`
- Response:

```json
{
  "status": "ok",
  "checks": {
    "env_file": true,
    "sample_metadata": true,
    "db_writable": true,
    "python_deps": true,
    "optional_kafka": false
  }
}
```
