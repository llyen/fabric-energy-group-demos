import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# CELL
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets"
DERIVED = DATA / "derived"
agents = pd.read_csv(DATA / "agent.csv")
evals = pd.read_csv(DATA / "agent_evaluation.csv")
inc = pd.read_csv(DATA / "agent_incident.csv")
ag = agents.merge(evals[["agent_id","decision","groundedness_score_pct","safety_score_pct"]], on="agent_id", how="left")
ag["business_owner"] = ag["business_owner"].fillna("")
ag["has_owner"] = ag["business_owner"].str.len() > 0
ag["has_evaluation"] = ag["decision"].notna()
ag["governance_debt"] = (~ag["has_owner"] | ~ag["has_evaluation"]) & (ag["lifecycle_status"] != "retired")
ic = inc.groupby("agent_id").size().reset_index(name="incidents")
ag = ag.merge(ic, on="agent_id", how="left")
ag["incidents"] = ag["incidents"].fillna(0).astype(int)
ag.to_csv(DERIVED / "agent_portfolio_health.csv", index=False, encoding="utf-8")
summary = {
    "agents_total": int(len(ag)),
    "agents_production": int((ag["lifecycle_status"] == "production").sum()),
    "agents_without_owner": int((~ag["has_owner"] & (ag["lifecycle_status"] != "retired")).sum()),
    "agents_without_evaluation": int((~ag["has_evaluation"] & (ag["lifecycle_status"] != "retired")).sum()),
    "governance_debt_agents": int(ag["governance_debt"].sum()),
    "governance_debt_cost_pln": round(float(ag.loc[ag["governance_debt"], "quarterly_cost_pln"].sum()), 2),
    "governance_debt_cost_share_pct": round(float(ag.loc[ag["governance_debt"], "quarterly_cost_pln"].sum() / ag["quarterly_cost_pln"].sum() * 100), 1),
    "agent_incidents": int(len(inc)),
}
(DERIVED / "agent_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
