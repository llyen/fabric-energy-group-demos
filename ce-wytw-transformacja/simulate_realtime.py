"""Replay synthetic environmental monitoring events to a Fabric Eventstream endpoint.

Dry-run mode requires no credentials and prints a small sample of payloads.
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, time as dt_time, timezone
from pathlib import Path
from urllib import request
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets"
WARSAW = ZoneInfo("Europe/Warsaw")


def parse_window(value: str | None, *, end_of_day: bool = False) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    if len(raw) == 10 and raw[4] == "-" and raw[7] == "-":
        date_value = datetime.fromisoformat(raw).date()
        local_time = dt_time.max if end_of_day else dt_time.min
        return datetime.combine(date_value, local_time, tzinfo=WARSAW).astimezone(timezone.utc)
    parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=WARSAW)
    return parsed.astimezone(timezone.utc)


def load_events(from_time: datetime | None = None, to_time: datetime | None = None, limit: int | None = None):
    path = DATA / "environmental_monitoring_events.jsonl"
    emitted = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            event = json.loads(line)
            event_time = datetime.fromisoformat(event["event_timestamp_utc"].replace("Z", "+00:00")).astimezone(timezone.utc)
            if from_time and event_time < from_time:
                continue
            if to_time and event_time > to_time:
                continue
            if limit is not None and emitted >= limit:
                break
            emitted += 1
            yield event


def post_event(endpoint: str, event: dict) -> None:
    payload = json.dumps(event, ensure_ascii=False).encode("utf-8")
    req = request.Request(endpoint, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=10) as resp:
        if resp.status >= 300:
            raise RuntimeError(f"HTTP {resp.status}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="")
    parser.add_argument("--speed", type=float, default=20.0, help="events per second")
    parser.add_argument("--from", dest="from_time", default=None, help="inclusive replay window start, e.g. 2026-01-01 or 2026-01-01T00:00:00+01:00")
    parser.add_argument("--to", dest="to_time", default=None, help="inclusive replay window end, e.g. 2026-12-31 or 2026-12-31T23:59:59+01:00")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    from_time = parse_window(args.from_time)
    to_time = parse_window(args.to_time, end_of_day=True)
    if from_time and to_time and from_time > to_time:
        raise ValueError("--from must be earlier than or equal to --to")
    delay = 0 if args.speed <= 0 else 1.0 / args.speed
    sent = 0
    for event in load_events(from_time=from_time, to_time=to_time, limit=args.limit):
        if args.dry_run or not args.endpoint:
            print(json.dumps(event, ensure_ascii=True))
        else:
            post_event(args.endpoint, event)
        sent += 1
        if delay:
            time.sleep(delay)
    print(f"events_processed={sent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
