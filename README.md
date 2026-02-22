# Autopilot Dataset Discovery + Label QA

A production-style data tooling project for autonomous-driving workflows.

## What This Demonstrates

- Perception data pipelines: schema-driven ingestion, checksum sharding, object-store placement, lineage tracking.
- Dataset discovery: scenario/weather metadata search with SQL fallback and optional OpenSearch indexing.
- Annotation QA analytics: disagreement rate, missing labels, class distribution, hard-example surfacing.
- Streaming patterns: event APIs, Kafka micro-batches, and Spark Structured Streaming curation template.

## System Overview

- API: `FastAPI` (`app/main.py`)
- Catalog: `SQLite + SQLAlchemy` (`app/db/models.py`)
- Services: ingestion, search, QA (`app/services/*`)
- UI: `Streamlit` dashboard (`dashboard/app.py`)
- Streaming scripts: replay/Kafka/Spark (`scripts/*`)

Detailed docs:
- Architecture: `docs/ARCHITECTURE.md`
- API reference: `docs/API_REFERENCE.md`
- Resume bullets: `docs/RESUME_BULLETS.md`

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 scripts/generate_sample_dataset.py
```

Start API:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Ingest sample metadata:

```bash
curl -X POST http://127.0.0.1:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"dataset_name":"sample-bdd-like","metadata_file":"data/raw/sample_metadata.jsonl"}'
```

Run dashboard:

```bash
streamlit run dashboard/app.py
```

## Reliability Commands

Preflight checks:

```bash
python3 scripts/preflight_check.py
curl "http://127.0.0.1:8000/api/system/preflight"
```

Smoke test:

```bash
bash scripts/smoke_test.sh
```

If local port binding is blocked in your environment, `scripts/smoke_test.sh` automatically falls back to in-process validation.

## Make Targets

```bash
make setup
make preflight
make api
make ingest
make dashboard
make smoke
```

## Streaming Extensions

Local stream replay:

```bash
python3 scripts/stream_replay.py --rate 10
```

Kafka producer/consumer flow:

```bash
docker compose up -d redpanda
python3 scripts/kafka_producer.py --bootstrap-servers localhost:9092 --topic perception-events
python3 scripts/kafka_consumer_to_api.py --bootstrap-servers localhost:9092 --topic perception-events --batch-size 25
```

Spark Structured Streaming template:

```bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3 scripts/spark_structured_streaming.py
```

## Why This Is Resume-Strong

- Shows end-to-end ownership: APIs, data model, ingestion runtime, analytics UI, and streaming patterns.
- Uses reliability practices expected in senior environments: preflight checks, smoke tests, CI workflow, deterministic Make targets.
- Maps directly to autonomous-driving data tooling responsibilities (catalog, QA loops, edge-case discovery, data flywheel patterns).

## License

MIT (`LICENSE`)
