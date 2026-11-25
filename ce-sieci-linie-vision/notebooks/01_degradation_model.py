# CELL
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets"
DER = DATA / "derived"
DER.mkdir(exist_ok=True)
THRESHOLD = 68.0

# CELL
wire = pd.read_csv(DATA / "fact_conductor_condition.csv", parse_dates=["month"])
sections = pd.read_csv(DATA / "dim_line_section.csv")
rows = []
for sid, grp in wire.groupby("section_id"):
    grp = grp.sort_values("month").reset_index(drop=True)
    x = np.arange(len(grp)).reshape(-1, 1)
    y = grp["degradation_pct"].to_numpy()
    model = LinearRegression().fit(x, y)
    slope = max(float(model.coef_[0]), 0.0001)
    current = float(grp[grp["month"] <= "2026-10-01"].iloc[-1]["degradation_pct"])
    rows.append({
        "section_id": sid,
        "current_degradation_pct": round(current, 3),
        "monthly_degradation_slope_pct": round(slope, 4),
        "months_to_replacement_threshold": round(max(0.0, (THRESHOLD - current) / slope), 2),
        "threshold_degradation_pct": THRESHOLD,
    })
forecast = pd.DataFrame(rows).merge(sections, on="section_id")
forecast["degradation_priority_rank"] = forecast["months_to_replacement_threshold"].rank(method="first").astype(int)
forecast.to_csv(DER / "section_degradation_forecast.csv", index=False)

# CELL
violations = []
for sid, grp in wire.sort_values(["section_id", "month"]).groupby("section_id"):
    prev = None
    for _, r in grp.iterrows():
        if int(r.get("replacement_event", 0)) == 1:
            prev = None
        if prev is not None and r["degradation_pct"] + 1e-9 < prev:
            violations.append({"section_id": sid, "month": r["month"].date().isoformat(), "prev_degradation_pct": prev, "degradation_pct": r["degradation_pct"]})
        prev = r["degradation_pct"]
pd.DataFrame(violations).to_csv(DER / "monotonic_degradation_violations.csv", index=False)
metrics = {
    "threshold_degradation_pct": THRESHOLD,
    "monotonic_violations": len(violations),
    "sections_above_threshold": int((forecast["current_degradation_pct"] >= THRESHOLD).sum()),
    "median_months_to_threshold": round(float(forecast["months_to_replacement_threshold"].median()), 1),
}
(DER / "degradation_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
print(metrics)
