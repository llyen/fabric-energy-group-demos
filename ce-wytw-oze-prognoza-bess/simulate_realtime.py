from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets"
STREAM_FILES = {
    "telemetry": "realtime_telemetry.jsonl",
    "market": "market_prices.csv",
    "storage": "storage_dispatch.csv",
}


def parse_time(value: str | None):
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def iter_jsonl(path: Path):
    with path.open(encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def iter_csv(path: Path):
    import csv
    with path.open(encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f)


def iter_events(streams, start=None, end=None):
    for stream in streams:
        path = DATA / STREAM_FILES[stream]
        source = iter_jsonl(path) if path.suffix == ".jsonl" else iter_csv(path)
        for event in source:
            event = dict(event)
            event["_stream"] = stream
            ts = parse_time(event["event_timestamp_utc"])
            if start and ts < start:
                continue
            if end and ts > end:
                continue
            yield event


def main() -> None:
    parser = argparse.ArgumentParser(description="Send synthetic OZE/BESS/ESP events to Fabric Eventstream/Event Hub.")
    parser.add_argument("--stream", action="append", choices=STREAM_FILES.keys(), help="Repeatable stream name. Default: telemetry.")
    parser.add_argument("--speed", type=float, default=240.0, help="Simulation speed multiplier.")
    parser.add_argument("--from", dest="from_time", help="ISO UTC start time filter.")
    parser.add_argument("--to", dest="to_time", help="ISO UTC end time filter.")
    parser.add_argument("--dry-run", action="store_true", help="Offline mode without dependencies or credentials.")
    args = parser.parse_args()

    streams = args.stream or ["telemetry"]
    events = sorted(iter_events(streams, parse_time(args.from_time), parse_time(args.to_time)), key=lambda e: e["event_timestamp_utc"])
    if args.dry_run:
        out = DATA / "derived" / "dry_run_sample.jsonl"
        out.parent.mkdir(exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            for event in events[:2000]:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        print(f"DRY RUN OK: {len(events)} events selected from {streams}; sample written to {out}")
        for event in events[:5]:
            print(json.dumps(event, ensure_ascii=False))
        return

    from azure.eventhub import EventData, EventHubProducerClient

    producer = EventHubProducerClient.from_connection_string(
        conn_str=os.environ["EVENTHUB_CONNECTION_STR"],
        eventhub_name=os.environ.get("EVENTHUB_NAME"),
    )
    prev = None
    with producer:
        batch = producer.create_batch()
        for event in events:
            ts = parse_time(event["event_timestamp_utc"])
            if prev:
                time.sleep(max(0, (ts - prev).total_seconds() / args.speed))
            prev = ts
            payload = json.dumps(event, ensure_ascii=False)
            try:
                batch.add(EventData(payload))
            except ValueError:
                producer.send_batch(batch)
                batch = producer.create_batch()
                batch.add(EventData(payload))
        if len(batch) > 0:
            producer.send_batch(batch)
    print(f"SENT OK: {len(events)} events")


if __name__ == "__main__":
    main()
