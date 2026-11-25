from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

STREAM_FILES = {
    "meter_readings": "meter_readings_stream_sample.jsonl",
    "meter_events": "meter_events.jsonl",
}
BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets"


def parse_time(value: str | None):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def event_time(event: dict) -> datetime:
    return parse_time(event["event_timestamp_utc"])


def iter_events(streams, start=None, end=None):
    for stream in streams:
        path = DATA / STREAM_FILES[stream]
        with path.open(encoding="utf-8") as f:
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
    parser = argparse.ArgumentParser(description="Send synthetic AMI meter streams to Fabric Eventstream/Event Hub.")
    parser.add_argument("--stream", action="append", choices=STREAM_FILES.keys(), help="Repeatable stream name. Default: all.")
    parser.add_argument("--speed", type=float, default=600.0, help="Simulation speed multiplier.")
    parser.add_argument("--from", dest="from_time", help="ISO UTC start time filter.")
    parser.add_argument("--to", dest="to_time", help="ISO UTC end time filter.")
    parser.add_argument("--dry-run", action="store_true", help="Offline mode without dependencies or credentials.")
    parser.add_argument("--limit", type=int, default=2000, help="Dry-run sample limit.")
    args = parser.parse_args()

    streams = args.stream or list(STREAM_FILES)
    events = sorted(iter_events(streams, parse_time(args.from_time), parse_time(args.to_time)), key=event_time)
    if args.dry_run:
        out = DATA / "derived" / ("dry_run_meter_events_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".jsonl")
        out.parent.mkdir(exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            for event in events[: args.limit]:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        print(f"DRY RUN OK: {len(events)} events selected from {streams}; sample written to {out}")
        for event in events[:5]:
            print(json.dumps(event, ensure_ascii=False))
        return

    from azure.eventhub import EventData, EventHubProducerClient  # lazy import; not needed for dry-run

    conn = os.environ["EVENTHUB_CONNECTION_STR"]
    eventhub_name = os.environ.get("EVENTHUB_NAME")
    producer = EventHubProducerClient.from_connection_string(conn_str=conn, eventhub_name=eventhub_name)
    previous = None
    sent = 0
    with producer:
        batch = producer.create_batch()
        for event in events:
            ts = event_time(event)
            if previous:
                time.sleep(max(0, (ts - previous).total_seconds() / args.speed))
            previous = ts
            payload = json.dumps(event, ensure_ascii=False)
            try:
                batch.add(EventData(payload))
            except ValueError:
                producer.send_batch(batch)
                batch = producer.create_batch()
                batch.add(EventData(payload))
            sent += 1
        if len(batch) > 0:
            producer.send_batch(batch)
    print(f"SENT OK: {sent} events")


if __name__ == "__main__":
    main()
