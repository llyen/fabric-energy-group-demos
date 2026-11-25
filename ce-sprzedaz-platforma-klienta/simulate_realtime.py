from __future__ import annotations

import argparse, csv, json, time
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets"

def parse_args():
    p = argparse.ArgumentParser(description="Simulate DSR portfolio telemetry for Fabric Eventstream.")
    p.add_argument("--from", dest="from_ts", default=None)
    p.add_argument("--to", dest="to_ts", default=None)
    p.add_argument("--speed", type=float, default=60.0)
    p.add_argument("--dry-run", action="store_true", help="Print events; do not use credentials or network.")
    p.add_argument("--limit", type=int, default=20)
    return p.parse_args()

def main():
    args = parse_args(); sent = 0
    with (DATA / "portfolio_profile_d0_15min.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ts = row["local_timestamp"]
            if args.from_ts and ts < args.from_ts: continue
            if args.to_ts and ts > args.to_ts: continue
            event = {"stream": "portfolio_ami_15min", **row}
            if args.dry_run:
                print(json.dumps(event, ensure_ascii=False))
            else:
                raise RuntimeError("Real send disabled in demo. Use Managed Identity and configured Eventstream endpoint in production.")
            sent += 1
            if args.limit and sent >= args.limit: break
            if not args.dry_run and args.speed > 0: time.sleep(900 / args.speed)
    print(f"events_emitted={sent} dry_run={args.dry_run}")

if __name__ == "__main__":
    main()
