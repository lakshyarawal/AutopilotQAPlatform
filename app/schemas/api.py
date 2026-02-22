from datetime import datetime
from pydantic import BaseModel


class IngestRequest(BaseModel):
    dataset_name: str
    metadata_file: str


class AssetOut(BaseModel):
    id: int
    source_uri: str
    object_uri: str
    sensor_type: str
    captured_at: datetime
    weather: str
    scenario: str
    shard_id: str
    compression: str
    lineage_id: int


class QASummary(BaseModel):
    total_assets: int
    total_annotations: int
    missing_label_assets: int
    label_distribution: dict[str, int]
    annotator_disagreement_rate: float
    hard_examples: list[int]


class AnnotationIn(BaseModel):
    annotator_id: str
    label_class: str
    bbox: dict = {}
    quality_score: float = 1.0


class StreamEvent(BaseModel):
    source_uri: str
    sensor_type: str
    captured_at: str
    weather: str = "unknown"
    scenario: str = "unknown"
    compression: str = "zstd"
    annotations: list[AnnotationIn] = []


class StreamBatchRequest(BaseModel):
    dataset_name: str = "stream-dataset"
    events: list[StreamEvent]
