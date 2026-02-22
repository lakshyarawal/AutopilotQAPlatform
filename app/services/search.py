import json

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Asset

try:
    from opensearchpy import OpenSearch
except Exception:  # pragma: no cover
    OpenSearch = None


class SearchService:
    def __init__(self) -> None:
        self.client = None
        if settings.opensearch_url and OpenSearch is not None:
            self.client = OpenSearch(settings.opensearch_url)
            self._ensure_index()

    def _ensure_index(self) -> None:
        if not self.client.indices.exists(index=settings.opensearch_index):
            self.client.indices.create(
                index=settings.opensearch_index,
                body={
                    "mappings": {
                        "properties": {
                            "weather": {"type": "keyword"},
                            "scenario": {"type": "keyword"},
                            "sensor_type": {"type": "keyword"},
                            "captured_at": {"type": "date"},
                            "metadata": {"type": "text"},
                        }
                    }
                },
            )

    def upsert_asset(self, asset: Asset) -> None:
        if not self.client:
            return
        self.client.index(
            index=settings.opensearch_index,
            id=str(asset.id),
            body={
                "weather": asset.weather,
                "scenario": asset.scenario,
                "sensor_type": asset.sensor_type,
                "captured_at": asset.captured_at.isoformat(),
                "metadata": asset.metadata_json,
            },
            refresh=True,
        )

    def search_assets(self, db: Session, q: str | None, weather: str | None, scenario: str | None, limit: int) -> list[Asset]:
        if self.client:
            must = []
            if q:
                must.append({"query_string": {"query": q}})
            if weather:
                must.append({"term": {"weather": weather}})
            if scenario:
                must.append({"term": {"scenario": scenario}})

            body = {"query": {"bool": {"must": must or [{"match_all": {}}]}}, "size": limit}
            res = self.client.search(index=settings.opensearch_index, body=body)
            ids = [int(hit["_id"]) for hit in res["hits"]["hits"]]
            return db.query(Asset).filter(Asset.id.in_(ids)).all() if ids else []

        filters = []
        if weather:
            filters.append(Asset.weather == weather)
        if scenario:
            filters.append(Asset.scenario == scenario)

        query = db.query(Asset)
        if filters:
            for f in filters:
                query = query.filter(f)

        if q:
            query = query.filter(
                or_(
                    Asset.source_uri.ilike(f"%{q}%"),
                    Asset.sensor_type.ilike(f"%{q}%"),
                    Asset.metadata_json.ilike(f"%{q}%"),
                )
            )

        return query.order_by(Asset.captured_at.desc()).limit(limit).all()


search_service = SearchService()
