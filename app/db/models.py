from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dataset_name: Mapped[str] = mapped_column(String(120), index=True)
    schema_version: Mapped[str] = mapped_column(String(24), default="v1")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="running")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_uri: Mapped[str] = mapped_column(String(255), index=True)
    object_uri: Mapped[str] = mapped_column(String(255), index=True)
    sensor_type: Mapped[str] = mapped_column(String(32), index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    weather: Mapped[str] = mapped_column(String(32), index=True)
    scenario: Mapped[str] = mapped_column(String(64), index=True)
    shard_id: Mapped[str] = mapped_column(String(64), index=True)
    compression: Mapped[str] = mapped_column(String(32), default="zstd")
    lineage_id: Mapped[int] = mapped_column(ForeignKey("ingestion_runs.id"), index=True)
    checksum: Mapped[str] = mapped_column(String(64), index=True)
    metadata_json: Mapped[str] = mapped_column(Text)

    annotations: Mapped[list["Annotation"]] = relationship(back_populates="asset")


class Annotation(Base):
    __tablename__ = "annotations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    annotator_id: Mapped[str] = mapped_column(String(64), index=True)
    label_class: Mapped[str] = mapped_column(String(64), index=True)
    bbox_json: Mapped[str] = mapped_column(Text)
    quality_score: Mapped[float] = mapped_column(Float, default=1.0)

    asset: Mapped[Asset] = relationship(back_populates="annotations")
