import argparse
import json
import time

import requests


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay metadata JSONL as streaming API events")
    parser.add_argument("--metadata-file", default="data/raw/sample_metadata.jsonl")
    parser.add_argument("--api-base", default="http://127.0.0.1:8000/api")
    parser.add_argument("--dataset-name", default="stream-replay")
    parser.add_argument("--rate", type=float, default=8.0, help="events per second")
    args = parser.parse_args()

    interval = 1.0 / args.rate if args.rate > 0 else 0.0
    total = 0

    with open(args.metadata_file, "r", encoding="utf-8") as f:
        for raw in f:
            event = json.loads(raw)
            res = requests.post(
                f"{args.api_base}/stream/events",
                params={"dataset_name": args.dataset_name},
                json=event,
                timeout=15,
            )
            res.raise_for_status()
            total += 1
            if total % 10 == 0:
                print(f"streamed {total} events")
            if interval > 0:
                time.sleep(interval)

    print(f"completed replay, total events={total}")


if __name__ == "__main__":
    main()
