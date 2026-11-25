"""Symulator strumieni AI Grid Control do Microsoft Fabric Eventstream.

Tryb `--dry-run` działa offline i nie wymaga `azure-eventhub` ani poświadczeń.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

STREAM_FILES = {
    "scada": "scada_feeder_telemetry.jsonl",
    "recloser": "recloser_events.jsonl",
    "ami": "ami_voltage_events.jsonl",
}
BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
TMP = DATA / "tmp"
DEFAULT_DRY_RUN_LIMIT_PER_STREAM = 1000


def parse_time(value: str | None):
    return datetime.fromisoformat(value) if value else None


def event_time(event: dict):
    return parse_time(event.get("event_timestamp_local") or event.get("event_timestamp_utc"))


def iter_events(streams, start=None, end=None):
    for stream in streams:
        path = DATA / STREAM_FILES[stream]
        if not path.exists():
            raise SystemExit(f"Brak pliku {path}. Uruchom najpierw: python generate_datasets.py")
        with path.open(encoding="utf-8") as f:
            for line in f:
                event = json.loads(line)
                ts = event_time(event)
                if start and ts < start:
                    continue
                if end and ts > end:
                    continue
                event["stream"] = stream
                event["_stream"] = stream
                event["_event_ts"] = ts
                yield event


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay strumieni SCADA, reklozerow i AMI do Eventstream/Event Hub.")
    parser.add_argument("--stream", action="append", choices=list(STREAM_FILES), help="Nazwa strumienia; można powtórzyć. Domyślnie wszystkie.")
    parser.add_argument("--speed", type=float, default=120.0, help="Przyspieszenie czasu scenariusza.")
    parser.add_argument("--from", dest="from_time", help="Początek okna ISO-8601.")
    parser.add_argument("--to", dest="to_time", help="Koniec okna ISO-8601.")
    parser.add_argument("--limit", type=int, help="Limit zdarzen. W --dry-run liczony per strumien; poza --dry-run globalny.")
    parser.add_argument("--full", action="store_true", help="W --dry-run zapisuje cale wybrane okno zamiast domyslnej probki.")
    parser.add_argument("--batch-size", type=int, default=250, help="Rozmiar paczki wysylanej do Event Hub.")
    parser.add_argument("--dry-run", action="store_true", help="Bez wysylki: zapis probki do datasets/tmp/dry_run_<stream>.jsonl")
    args = parser.parse_args()

    streams = args.stream or list(STREAM_FILES)
    events = sorted(iter_events(streams, parse_time(args.from_time), parse_time(args.to_time)), key=lambda e: e["_event_ts"])
    if args.full and not args.dry_run:
        raise SystemExit("--full ma sens tylko z --dry-run. Dla wysylki produkcyjnej uzyj albo pomin --limit swiadomie.")
    if args.dry_run:
        per_stream_limit = None if args.full else (args.limit or DEFAULT_DRY_RUN_LIMIT_PER_STREAM)
        if per_stream_limit is not None:
            counts: dict[str, int] = {s: 0 for s in streams}
            limited = []
            for event in events:
                stream = event["_stream"]
                if counts[stream] >= per_stream_limit:
                    continue
                limited.append(event)
                counts[stream] += 1
            events = limited
    elif args.limit:
        events = events[: args.limit]
    if not events:
        raise SystemExit("Brak zdarzen w podanym oknie.")
    print(f"Strumienie: {', '.join(streams)} | zdarzen: {len(events)} | okno: {events[0]['_event_ts'].isoformat()} .. {events[-1]['_event_ts'].isoformat()}")

    if args.dry_run:
        TMP.mkdir(parents=True, exist_ok=True)
        for stream in streams:
            (TMP / f"dry_run_{stream}.jsonl").unlink(missing_ok=True)
        handles = {s: (TMP / f"dry_run_{s}.jsonl").open("w", encoding="utf-8") for s in streams}
        counts: dict[str, int] = {s: 0 for s in streams}
        try:
            for event in events:
                stream = event.pop("_stream")
                event.pop("_event_ts", None)
                handles[stream].write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
                counts[stream] += 1
        finally:
            for h in handles.values():
                h.close()
        mode = "pelne okno" if args.full else f"probka max {args.limit or DEFAULT_DRY_RUN_LIMIT_PER_STREAM}/strumien"
        print(f"DRY-RUN: {mode}; zapisano do {TMP}")
        print("DRY-RUN counts: " + ", ".join(f"{s}={counts[s]}" for s in streams))
        return

    conn = os.environ.get("EVENTHUB_CONNECTION_STR")
    if not conn:
        raise SystemExit("Brak EVENTHUB_CONNECTION_STR. Uzyj --dry-run albo ustaw zmienna srodowiskowa.")
    from azure.eventhub import EventData, EventHubProducerClient

    producer = EventHubProducerClient.from_connection_string(conn, eventhub_name=os.environ.get("EVENTHUB_NAME"))
    sent, prev_ts = 0, None
    with producer:
        batch = producer.create_batch()
        for event in events:
            ts = event.pop("_event_ts")
            event.pop("_stream", None)
            if prev_ts is not None and args.speed > 0:
                delay = (ts - prev_ts).total_seconds() / args.speed
                if delay > 0:
                    time.sleep(min(delay, 5.0))
            prev_ts = ts
            data = EventData(json.dumps(event, ensure_ascii=False, separators=(",", ":")))
            try:
                batch.add(data)
            except ValueError:
                producer.send_batch(batch)
                batch = producer.create_batch()
                batch.add(data)
            sent += 1
            if len(batch) >= args.batch_size:
                producer.send_batch(batch)
                batch = producer.create_batch()
        if len(batch):
            producer.send_batch(batch)
    print(f"Zakonczono. Wyslano {sent} zdarzen.")


if __name__ == "__main__":
    main()
