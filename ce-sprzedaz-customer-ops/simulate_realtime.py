# -*- coding: utf-8 -*-
"""Symulator strumienia kontaktów dla Eventstream/Eventhouse.

Działa bez poświadczeń w trybie --dry-run.
Przykład: python simulate_realtime.py --dry-run --speed 20 --from 2026-03-02 --to 2026-03-30
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="Nie wysyła zdarzeń, tylko wypisuje próbkę JSON.")
    p.add_argument("--speed", type=float, default=10.0, help="Przyspieszenie symulacji; 1 = rytm historyczny.")
    p.add_argument("--from", dest="from_date", default=None, help="Początek okna, np. 2026-03-02.")
    p.add_argument("--to", dest="to_date", default=None, help="Koniec okna, np. 2026-03-30.")
    p.add_argument("--max-events", type=int, default=25, help="Limit w --dry-run.")
    p.add_argument("--endpoint", default=None, help="Custom endpoint Eventstream/Event Hub; nie podawaj sekretów w CLI.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    events = pd.read_csv(DATA / "event_channel_contact.csv")
    events["event_local_timestamp"] = pd.to_datetime(events["event_local_timestamp"], utc=True)
    if args.from_date:
        events = events[events["event_local_timestamp"] >= pd.to_datetime(args.from_date, utc=True)]
    if args.to_date:
        events = events[events["event_local_timestamp"] <= pd.to_datetime(args.to_date, utc=True)]
    events = events.sort_values("event_local_timestamp")

    if not args.dry_run and not args.endpoint:
        raise SystemExit("Brak --endpoint. Użyj --dry-run, jeśli chcesz uruchomić bez poświadczeń.")

    prev = None
    sent = 0
    for _, row in events.iterrows():
        ts = row["event_local_timestamp"]
        if prev is not None and not args.dry_run:
            delay = max(0, (ts - prev).total_seconds() / max(args.speed, 0.1))
            time.sleep(min(delay, 5))
        payload = row.dropna().to_dict()
        payload["event_local_timestamp"] = ts.isoformat()
        if args.dry_run:
            print(json.dumps(payload, ensure_ascii=False))
            sent += 1
            if sent >= args.max_events:
                break
        else:
            # Miejsce integracji: requests.post(args.endpoint, json=payload, timeout=10)
            # Celowo brak implementacji sekretów i nagłówków autoryzacyjnych w repo.
            print(f"would_send endpoint={args.endpoint} event_id={payload.get('event_id')}")
        prev = ts

    print(f"events_selected={len(events)} events_emitted={sent if args.dry_run else len(events)} dry_run={args.dry_run}")


if __name__ == "__main__":
    main()
