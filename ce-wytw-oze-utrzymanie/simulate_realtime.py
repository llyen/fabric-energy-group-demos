from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
STREAM_FILES = {
    "wind": "wind_scada_10min.csv",
    "pv": "pv_scada_15min.csv",
    "hydro": "hydro_scada_1h.csv",
    "esp": "esp_scada_1h.csv",
}


def parse_time(value: str | None):
    return datetime.fromisoformat(value) if value else None


def iter_csv_events(streams, start=None, end=None, limit=None):
    import pandas as pd
    for stream in streams:
        path = DATA / STREAM_FILES[stream]
        for chunk in pd.read_csv(path, chunksize=5000, parse_dates=["event_timestamp_utc"]):
            chunk["_stream"] = stream
            chunk["event_time"] = chunk["event_timestamp_utc"].astype(str)
            if start:
                chunk = chunk[chunk["event_timestamp_utc"].dt.tz_convert("Europe/Warsaw") >= pd.Timestamp(start)]
            if end:
                chunk = chunk[chunk["event_timestamp_utc"].dt.tz_convert("Europe/Warsaw") <= pd.Timestamp(end)]
            for row in chunk.to_dict(orient="records"):
                for k, v in list(row.items()):
                    if hasattr(v, "isoformat"):
                        row[k] = v.isoformat()
                    elif isinstance(v, float) and pd.isna(v):
                        row[k] = None
                yield row
                if limit is not None:
                    limit -= 1
                    if limit <= 0:
                        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Stream synthetic OZE maintenance telemetry to Fabric Eventstream/Event Hub.")
    parser.add_argument("--stream", action="append", choices=STREAM_FILES.keys(), help="Repeatable stream name. Default: wind.")
    parser.add_argument("--speed", type=float, default=120.0, help="Simulation speed multiplier.")
    parser.add_argument("--from", dest="from_time", help="ISO local start time filter.")
    parser.add_argument("--to", dest="to_time", help="ISO local end time filter.")
    parser.add_argument("--dry-run", action="store_true", help="Offline mode without dependencies or credentials.")
    parser.add_argument("--limit", type=int, default=2000, help="Max events in dry-run sample.")
    args = parser.parse_args()

    streams = args.stream or ["wind"]
    events = list(iter_csv_events(streams, parse_time(args.from_time), parse_time(args.to_time), args.limit if args.dry_run else None))
    events.sort(key=lambda e: e["event_time"])
    if args.dry_run:
        DERIVED.mkdir(parents=True, exist_ok=True)
        out = DERIVED / ("dry_run_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".jsonl")
        with out.open("w", encoding="utf-8") as f:
            for event in events:
                f.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
        print(f"DRY RUN OK: {len(events)} events selected from {streams}; sample written to {out}")
        for event in events[:5]:
            print(json.dumps(event, ensure_ascii=False, default=str))
        return

    from azure.eventhub import EventData, EventHubProducerClient
    producer = EventHubProducerClient.from_connection_string(os.environ["EVENTHUB_CONNECTION_STR"], eventhub_name=os.environ.get("EVENTHUB_NAME"))
    prev = None
    with producer:
        batch = producer.create_batch()
        for event in iter_csv_events(streams, parse_time(args.from_time), parse_time(args.to_time)):
            ts = datetime.fromisoformat(event["event_time"])
            if prev:
                time.sleep(max(0, (ts - prev).total_seconds() / args.speed))
            prev = ts
            payload = json.dumps(event, ensure_ascii=False, default=str)
            try:
                batch.add(EventData(payload))
            except ValueError:
                producer.send_batch(batch)
                batch = producer.create_batch()
                batch.add(EventData(payload))
        if len(batch) > 0:
            producer.send_batch(batch)
    print("SENT OK")


if __name__ == "__main__":
    main()
