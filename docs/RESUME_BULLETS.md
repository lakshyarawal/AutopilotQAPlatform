# Resume-Ready Bullets

## One-line project summary
Built a production-style perception data tooling platform for autonomous driving workflows with ingestion lineage, dataset discovery, label QA analytics, and streaming ingestion patterns.

## Bullets (choose 3-5)

- Designed and implemented a FastAPI + SQLAlchemy metadata platform for perception assets (camera/lidar/radar) with ingestion lineage, checksum-based sharding, and object-store placement.
- Built dataset discovery and QA tooling with scenario/weather search, class-distribution drift visibility, annotator disagreement analysis, and hard-example surfacing.
- Implemented dual-mode search architecture with SQL fallback and OpenSearch integration for scalable metadata retrieval.
- Added streaming patterns including event-based ingest APIs, Kafka micro-batch consumer flow, and Spark Structured Streaming curation templates.
- Created deterministic preflight and smoke validation workflows (`make preflight`, `make smoke`) to improve local reliability and onboarding.

## Suggested stack line
Python, FastAPI, SQLAlchemy, Streamlit, OpenSearch, Kafka, Spark Structured Streaming, Docker
