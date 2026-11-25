from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

STREAM_FILES = {
    "source_telemetry": "source_telemetry_hourly.jsonl",
    "storage_telemetry": "storage_telemetry_hourly.jsonl",
    "network_telemetry": "network_telemetry_hourly.jsonl",
    "weather": "weather_hourly.jsonl",
    "weather_forecast": "weather_forecast_hourly.jsonl",
    "prices": "electricity_prices_hourly.jsonl",
}
BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets"


def parse_time(value: str | None):
    return datetime.fromisoformat(value) if value else None


def event_time(event: dict):
    return parse_time(event.get("local_timestamp") or event["event_timestamp_utc"])


def iter_events(streams, start=None, end=None):
    for stream in streams:
        with (DATA / STREAM_FILES[stream]).open(encoding="utf-8") as f:
            for line in f:
                event = json.loads(line)
                event["_stream"] = stream
                ts = event_time(event)
                if start and ts < start:
                    continue
                if end and ts > end:
                    continue
                yield event


def main() -> None:
    parser = argparse.ArgumentParser(description="Send Smart Heat streams to Fabric Eventstream/Event Hub.")
    parser.add_argument("--stream", action="append", choices=STREAM_FILES.keys(), help="Repeatable stream. Default: all.")
    parser.add_argument("--speed", type=float, default=240.0, help="Simulation speed multiplier.")
    parser.add_argument("--from", dest="from_time", help="ISO local start time filter, e.g. 2026-02-08T00:00:00+01:00")
    parser.add_argument("--to", dest="to_time", help="ISO local end time filter.")
    parser.add_argument("--dry-run", action="store_true", help="Offline mode without dependencies or credentials.")
    args = parser.parse_args()
    streams = args.stream or list(STREAM_FILES)
    events = sorted(iter_events(streams, parse_time(args.from_time), parse_time(args.to_time)), key=event_time)
    if args.dry_run:
        out = DATA / "derived" / ("dry_run_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".jsonl")
        out.parent.mkdir(exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            for event in events[:2000]:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        print(f"DRY RUN OK: {len(events)} events selected from {streams}; sample written to {out}")
        for event in events[:5]:
            print(json.dumps(event, ensure_ascii=False))
        return
    from azure.eventhub import EventData, EventHubProducerClient
    producer = EventHubProducerClient.from_connection_string(os.environ["EVENTHUB_CONNECTION_STR"], eventhub_name=os.environ.get("EVENTHUB_NAME"))
    prev = None; sent = 0
    with producer:
        batch = producer.create_batch()
        for event in events:
            ts = event_time(event)
            if prev:
                time.sleep(max(0, (ts - prev).total_seconds() / args.speed))
            prev = ts
            payload = json.dumps(event, ensure_ascii=False)
            try:
                batch.add(EventData(payload))
            except ValueError:
                producer.send_batch(batch); batch = producer.create_batch(); batch.add(EventData(payload))
            sent += 1
        if len(batch) > 0:
            producer.send_batch(batch)
    print(f"SENT OK: {sent} events")

if __name__ == "__main__":
    main()
