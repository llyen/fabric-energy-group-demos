from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import argparse
import json
import time
from datetime import datetime, time as dt_time, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "datasets"
DERIVED = DATA / "derived"


def parse_time(value: str | None, end_of_day: bool = False) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    if len(raw) == 10:
        d = datetime.fromisoformat(raw).date()
        return datetime.combine(d, dt_time.max if end_of_day else dt_time.min, tzinfo=timezone.utc)
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def event_time(event: dict) -> datetime:
    return datetime.fromisoformat(str(event["event_timestamp_utc"]).replace("Z", "+00:00"))


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def main():
    parser = argparse.ArgumentParser(description="Dry-run replay for Fabric Eventstream demo telemetry.")
    parser.add_argument("--stream", choices=["capacity", "agent"], default="capacity")
    parser.add_argument("--speed", type=float, default=100.0, help="Replay speed multiplier for dry-run output.")
    parser.add_argument("--from", dest="from_time", default=None, help="Inclusive replay start, e.g. 2026-10-01 or 2026-10-01T00:00:00+00:00.")
    parser.add_argument("--to", dest="to_time", default=None, help="Inclusive replay end, e.g. 2026-12-31 or 2026-12-31T23:59:59+00:00.")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true", help="Print events locally; no credentials required.")
    args = parser.parse_args()
    if not args.dry_run:
        raise SystemExit("Ten symulator demo obsługuje tylko --dry-run; produkcyjną wysyłkę skonfiguruj w Fabric Eventstream.")
    start = parse_time(args.from_time)
    end = parse_time(args.to_time, end_of_day=True)
    if start and end and start > end:
        raise SystemExit("--from musi być wcześniejsze albo równe --to.")
    source = DATA / ("capacity_telemetry.jsonl" if args.stream == "capacity" else "agent_incident_stream.jsonl")
    out = DERIVED / f"realtime_{args.stream}_dry_run.jsonl"
    DERIVED.mkdir(exist_ok=True)
    delay = max(0.0, 1.0 / max(args.speed, 1.0))
    count = 0
    scanned = 0
    with out.open("w", encoding="utf-8") as sink:
        for event in read_jsonl(source):
            scanned += 1
            ts = event_time(event)
            if start and ts < start:
                continue
            if end and ts > end:
                continue
            sink.write(json.dumps(event, ensure_ascii=False) + "\n")
            print(json.dumps(event, ensure_ascii=False))
            count += 1
            if count >= args.limit:
                break
            time.sleep(delay)
    print(f"Dry-run zapisany: {out} ({count} zdarzen, przeskanowano {scanned})")


if __name__ == "__main__":
    main()
