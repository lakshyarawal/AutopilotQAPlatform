import hashlib
import json
import os
import shutil
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Annotation, Asset, IngestionRun
from app.services.search import search_service


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)


def create_ingestion_run(db: Session, dataset_name: str, schema_version: str = "v1") -> IngestionRun:
    run = IngestionRun(dataset_name=dataset_name, schema_version=schema_version, status="running")
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def finalize_ingestion_run(db: Session, run: IngestionRun, status: str = "completed") -> IngestionRun:
    run.status = status
    run.finished_at = datetime.utcnow()
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def ingest_record(db: Session, run_id: int, item: dict[str, Any]) -> Asset:
    src = item["source_uri"]
    checksum = _sha256(src)
    shard_id = checksum[:8]
    ext = os.path.splitext(src)[1] or ".bin"
    dst_dir = os.path.join(settings.object_store_path, shard_id)
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, f"{checksum}{ext}")
    shutil.copy2(src, dst)

    asset = Asset(
        source_uri=src,
        object_uri=dst,
        sensor_type=item["sensor_type"],
        captured_at=_parse_ts(item["captured_at"]),
        weather=item.get("weather", "unknown"),
        scenario=item.get("scenario", "unknown"),
        shard_id=shard_id,
        compression=item.get("compression", "zstd"),
        lineage_id=run_id,
        checksum=checksum,
        metadata_json=json.dumps(item),
    )
    db.add(asset)
    db.flush()

    for ann in item.get("annotations", []):
        db.add(
            Annotation(
                asset_id=asset.id,
                annotator_id=ann["annotator_id"],
                label_class=ann["label_class"],
                bbox_json=json.dumps(ann.get("bbox", {})),
                quality_score=float(ann.get("quality_score", 1.0)),
            )
        )

    db.commit()
    db.refresh(asset)
    search_service.upsert_asset(asset)
    return asset


def run_ingestion(db: Session, dataset_name: str, metadata_file: str) -> IngestionRun:
    run = create_ingestion_run(db, dataset_name=dataset_name, schema_version="v1")
    os.makedirs(settings.object_store_path, exist_ok=True)

    with open(metadata_file, "r", encoding="utf-8") as f:
        for raw in f:
            item = json.loads(raw)
            ingest_record(db=db, run_id=run.id, item=item)

    return finalize_ingestion_run(db=db, run=run, status="completed")
