import argparse
import json
from typing import Any

import requests
from kafka import KafkaConsumer


def main() -> None:
    parser = argparse.ArgumentParser(description="Consume Kafka events and ingest micro-batches into API")
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--topic", default="perception-events")
    parser.add_argument("--group-id", default="autopilot-stream-consumer")
    parser.add_argument("--api-base", default="http://127.0.0.1:8000/api")
    parser.add_argument("--dataset-name", default="kafka-stream")
    parser.add_argument("--batch-size", type=int, default=25)
    args = parser.parse_args()

    consumer = KafkaConsumer(
        args.topic,
        bootstrap_servers=args.bootstrap_servers,
        group_id=args.group_id,
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        enable_auto_commit=True,
    )

    batch: list[dict[str, Any]] = []
    for message in consumer:
        batch.append(message.value)
        if len(batch) >= args.batch_size:
            res = requests.post(
                f"{args.api_base}/stream/events/batch",
                json={"dataset_name": args.dataset_name, "events": batch},
                timeout=30,
            )
            res.raise_for_status()
            payload = res.json()
            print(f"ingested batch run_id={payload['run_id']} processed={payload['processed_events']}")
            batch.clear()


if __name__ == "__main__":
    main()
