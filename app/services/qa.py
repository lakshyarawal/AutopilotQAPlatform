from collections import Counter, defaultdict

from sqlalchemy.orm import Session

from app.db.models import Annotation, Asset


def qa_summary(db: Session) -> dict:
    assets = db.query(Asset).all()
    annotations = db.query(Annotation).all()

    label_counter = Counter(a.label_class for a in annotations)

    anns_by_asset: dict[int, list[Annotation]] = defaultdict(list)
    for ann in annotations:
        anns_by_asset[ann.asset_id].append(ann)

    missing_label_assets = 0
    disagreements = 0
    hard_examples = []

    for asset in assets:
        anns = anns_by_asset.get(asset.id, [])
        if not anns:
            missing_label_assets += 1
            hard_examples.append(asset.id)
            continue

        labels = {a.label_class for a in anns}
        if len(labels) > 1:
            disagreements += 1
            hard_examples.append(asset.id)

        avg_quality = sum(a.quality_score for a in anns) / len(anns)
        if avg_quality < 0.6 and asset.id not in hard_examples:
            hard_examples.append(asset.id)

    total_assets = len(assets)
    disagreement_rate = disagreements / total_assets if total_assets else 0.0

    return {
        "total_assets": total_assets,
        "total_annotations": len(annotations),
        "missing_label_assets": missing_label_assets,
        "label_distribution": dict(label_counter),
        "annotator_disagreement_rate": round(disagreement_rate, 3),
        "hard_examples": hard_examples[:20],
    }
