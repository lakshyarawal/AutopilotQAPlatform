import importlib
import os
from pathlib import Path

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.schemas.api import AssetOut, IngestRequest, QASummary, StreamBatchRequest, StreamEvent
from app.services.ingestion import create_ingestion_run, finalize_ingestion_run, ingest_record, run_ingestion
from app.services.qa import qa_summary
from app.services.search import search_service

router = APIRouter()


@router.post("/ingest")
def ingest(payload: IngestRequest, db: Session = Depends(get_db)):
    run = run_ingestion(db, dataset_name=payload.dataset_name, metadata_file=payload.metadata_file)
    return {
        "run_id": run.id,
        "dataset_name": run.dataset_name,
        "status": run.status,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
    }


@router.get("/assets/search", response_model=list[AssetOut])
def search_assets(
    q: str | None = Query(default=None),
    weather: str | None = Query(default=None),
    scenario: str | None = Query(default=None),
    limit: int = Query(default=20, le=200),
    db: Session = Depends(get_db),
):
    assets = search_service.search_assets(db=db, q=q, weather=weather, scenario=scenario, limit=limit)
    return [
        AssetOut(
            id=a.id,
            source_uri=a.source_uri,
            object_uri=a.object_uri,
            sensor_type=a.sensor_type,
            captured_at=a.captured_at,
            weather=a.weather,
            scenario=a.scenario,
            shard_id=a.shard_id,
            compression=a.compression,
            lineage_id=a.lineage_id,
        )
        for a in assets
    ]


@router.get("/qa/summary", response_model=QASummary)
def qa(db: Session = Depends(get_db)):
    return qa_summary(db)


@router.post("/stream/events")
def stream_event(payload: StreamEvent, dataset_name: str = "stream-dataset", db: Session = Depends(get_db)):
    run = create_ingestion_run(db=db, dataset_name=dataset_name, schema_version="v1-stream")
    try:
        asset = ingest_record(db=db, run_id=run.id, item=payload.model_dump())
        finalize_ingestion_run(db=db, run=run, status="completed")
        return {"run_id": run.id, "asset_id": asset.id, "status": "completed"}
    except Exception:
        finalize_ingestion_run(db=db, run=run, status="failed")
        raise


@router.post("/stream/events/batch")
def stream_batch(payload: StreamBatchRequest, db: Session = Depends(get_db)):
    run = create_ingestion_run(db=db, dataset_name=payload.dataset_name, schema_version="v1-stream")
    processed = 0
    try:
        for event in payload.events:
            ingest_record(db=db, run_id=run.id, item=event.model_dump())
            processed += 1
        finalize_ingestion_run(db=db, run=run, status="completed")
        return {"run_id": run.id, "processed_events": processed, "status": "completed"}
    except Exception:
        finalize_ingestion_run(db=db, run=run, status="failed")
        raise


@router.get("/system/preflight")
def system_preflight(db: Session = Depends(get_db)):
    root = Path(".")
    checks = {
        "env_file": root.joinpath(".env").exists(),
        "sample_metadata": root.joinpath("data/raw/sample_metadata.jsonl").exists(),
        "db_writable": True,
        "python_deps": True,
        "optional_kafka": True,
    }

    try:
        # DB write probe to catch lock/permission issues before ingestion.
        db.execute(text("SELECT 1"))
    except Exception:
        checks["db_writable"] = False

    for mod in ("fastapi", "uvicorn", "sqlalchemy", "streamlit", "pandas", "requests"):
        try:
            importlib.import_module(mod)
        except Exception:
            checks["python_deps"] = False
            break

    try:
        importlib.import_module("kafka")
    except Exception:
        checks["optional_kafka"] = False

    if settings.database_url.startswith("sqlite:///"):
        db_path = settings.database_url.replace("sqlite:///", "", 1)
        if db_path:
            parent = Path(db_path).resolve().parent
            checks["db_writable"] = checks["db_writable"] and os.access(parent, os.W_OK)

    status = "ok" if checks["env_file"] and checks["sample_metadata"] and checks["db_writable"] and checks["python_deps"] else "degraded"
    return {"status": status, "checks": checks}
