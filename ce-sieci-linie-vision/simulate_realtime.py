"""Symulator strumieni Eventstream dla scenariusza inspekcji linii napowietrznych. --dry-run nie wymaga poświadczeń."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "datasets"

def iter_jsonl(path: Path):
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--speed", type=float, default=120.0)
    ap.add_argument("--from", dest="from_ts", default=None)
    ap.add_argument("--to", dest="to_ts", default=None)
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()
    events = []
    for name, stream in [
        ("substation_telemetry", DATA / "fact_substation_telemetry.jsonl"),
        ("ai_vision_detection", DATA / "fact_ai_vision_detection.jsonl"),
        ("protection_event", DATA / "fact_protection_event.jsonl"),
    ]:
        if not stream.exists():
            continue
        for row in iter_jsonl(stream):
            ts = row.get("event_timestamp_utc")
            if args.from_ts and ts < args.from_ts:
                continue
            if args.to_ts and ts > args.to_ts:
                continue
            events.append({"stream": name, **row})
    events.sort(key=lambda r: r.get("event_timestamp_utc", ""))
    if args.dry_run:
        print(f"DRY RUN: {len(events)} events selected. Showing first {min(args.limit, len(events))}.")
        for row in events[: args.limit]:
            print(json.dumps(row, ensure_ascii=False))
        return
    raise SystemExit("Real send is intentionally not implemented in demo. Configure Eventstream endpoint and authenticated sender in production.")

if __name__ == "__main__":
    main()
