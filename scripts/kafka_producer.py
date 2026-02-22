import argparse
import json

from kafka import KafkaProducer


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish perception metadata events to Kafka")
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--topic", default="perception-events")
    parser.add_argument("--metadata-file", default="data/raw/sample_metadata.jsonl")
    args = parser.parse_args()

    producer = KafkaProducer(
        bootstrap_servers=args.bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    count = 0
    with open(args.metadata_file, "r", encoding="utf-8") as f:
        for raw in f:
            event = json.loads(raw)
            producer.send(args.topic, value=event)
            count += 1
    producer.flush()
    print(f"published {count} events to topic={args.topic}")


if __name__ == "__main__":
    main()
