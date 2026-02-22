import json
import os
import random
from datetime import datetime, timedelta, timezone

OUTPUT_DIR = "data/raw"
META_FILE = os.path.join(OUTPUT_DIR, "sample_metadata.jsonl")


WEATHER = ["clear", "rain", "fog", "night"]
SCENARIOS = ["intersection", "merge", "occlusion", "pedestrian_crossing"]
SENSORS = ["camera", "lidar", "radar"]
LABELS = ["car", "pedestrian", "truck", "bicycle"]


os.makedirs(OUTPUT_DIR, exist_ok=True)

start = datetime.now(timezone.utc) - timedelta(days=2)
rows = []
for i in range(60):
    frame_path = os.path.join(OUTPUT_DIR, f"frame_{i:04d}.bin")
    with open(frame_path, "wb") as f:
        f.write(os.urandom(2048))

    anns = []
    ann_count = random.choice([0, 1, 2, 3])
    for _ in range(ann_count):
        label = random.choice(LABELS)
        anns.append(
            {
                "annotator_id": random.choice(["ann_a", "ann_b", "ann_c"]),
                "label_class": label,
                "bbox": {
                    "x": random.randint(0, 1000),
                    "y": random.randint(0, 700),
                    "w": random.randint(20, 200),
                    "h": random.randint(20, 200),
                },
                "quality_score": round(random.uniform(0.4, 1.0), 2),
            }
        )

    # Inject disagreement on some assets to make QA dashboard meaningful.
    if len(anns) >= 2 and i % 7 == 0:
        anns[0]["label_class"] = "car"
        anns[1]["label_class"] = "pedestrian"

    rows.append(
        {
            "source_uri": frame_path,
            "sensor_type": random.choice(SENSORS),
            "captured_at": (start + timedelta(minutes=3 * i)).isoformat(),
            "weather": random.choice(WEATHER),
            "scenario": random.choice(SCENARIOS),
            "compression": "zstd",
            "annotations": anns,
        }
    )

with open(META_FILE, "w", encoding="utf-8") as f:
    for row in rows:
        f.write(json.dumps(row) + "\n")

print(f"Wrote {len(rows)} samples to {META_FILE}")
