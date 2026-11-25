# CELL
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets"
DER = DATA / "derived"
DER.mkdir(exist_ok=True)

# CELL
risk = pd.read_csv(DER / "section_risk_scores.csv")
windows = pd.read_csv(DATA / "fact_planned_outage_window.csv")
work = pd.read_csv(DATA / "fact_work_order.csv")
top = set(risk.nsmallest(18, "risk_priority_rank")["section_id"])
work = work[work["section_id"].isin(top)].merge(risk[["section_id", "line_no", "risk_score", "risk_priority_rank"]], on=["section_id", "line_no"], how="left")
assign = []
remaining = work.sort_values("risk_priority_rank").copy()
for _, win in windows.sort_values(["window_start", "outage_cost_index"]).iterrows():
    candidates = remaining[remaining["line_no"] == win["line_no"]].head(int(win["max_sections"]))
    for _, row in candidates.iterrows():
        assign.append({
            "window_id": win["window_id"],
            "section_id": row["section_id"],
            "line_no": row["line_no"],
            "risk_priority_rank": int(row["risk_priority_rank"]),
            "risk_score": round(float(row["risk_score"]), 4),
            "estimated_duration_h": int(row["estimated_duration_h"]),
            "window_start": win["window_start"],
            "window_end": win["window_end"],
        })
    remaining = remaining[~remaining["section_id"].isin(candidates["section_id"])]
    if remaining.empty:
        break
plan = pd.DataFrame(assign)
plan.to_csv(DER / "optimized_work_window_plan.csv", index=False)
metrics = {
    "risk_sections_to_schedule": int(len(work)),
    "scheduled_sections": int(len(assign)),
    "outage_windows_used": int(plan["window_id"].nunique() if not plan.empty else 0),
    "unscheduled_sections": int(len(remaining)),
}
(DER / "window_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
print(metrics)
