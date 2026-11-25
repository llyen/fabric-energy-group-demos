import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# CELL
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "datasets" / "derived"
parts = {}
for name in ["dataset_counts", "quality_summary", "lineage_validation", "legacy_summary", "finops_summary", "waste_summary", "agent_summary"]:
    with (DERIVED / f"{name}.json").open(encoding="utf-8") as f:
        parts[name] = json.load(f)
(DERIVED / "executive_summary.json").write_text(json.dumps(parts, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(parts, ensure_ascii=False, indent=2))
