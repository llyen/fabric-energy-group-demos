from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
rng = np.random.default_rng(SEED)
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "datasets"
DERIVED = DATA / "derived"
TZ = "Europe/Warsaw"

COMPANIES = [
    "Contoso Energia Usługi Wspólne", "Contoso Energia Sieci", "Contoso Energia Sprzedaż",
    "Contoso Energia Wytwarzanie", "Contoso Energia Ciepło"
]
DOMAINS = ["platform", "grid", "customer", "generation", "renewables", "heat", "shared_services", "finance"]
PRODUCTS = [
    ("DP-001", "grid_asset_registry", "grid", "Contoso Energia Sieci", "GIS sieciowy", 14, 0.96, 3),
    ("DP-002", "grid_outage_events", "grid", "Contoso Energia Sieci", "DMS / ADMS", 10, 0.94, 6),
    ("DP-003", "ami_quality_profile", "grid", "Contoso Energia Sieci", "AMI/LZO + head-end", 8, 0.90, 7),
    ("DP-004", "customer_contract_360", "customer", "Contoso Energia Sprzedaż", "Billing / CRM", 18, 0.92, 8),
    ("DP-005", "contact_reason_taxonomy", "customer", "Contoso Energia Sprzedaż", "Billing / CRM", 5, 0.89, 5),
    ("DP-006", "generation_unit_availability", "generation", "Contoso Energia Wytwarzanie", "SAP PM / EAM", 11, 0.93, 4),
    ("DP-007", "emission_reporting_basis", "generation", "Contoso Energia Wytwarzanie", "EHS / środowisko", 7, 0.91, 3),
    ("DP-008", "wind_fleet_scada_summary", "renewables", "Contoso Energia Wytwarzanie", "SCADA turbin", 9, 0.95, 5),
    ("DP-009", "bess_market_signal", "renewables", "Contoso Energia Wytwarzanie", "Dane rynkowe PSE/TGE", 6, 0.88, 4),
    ("DP-010", "heat_network_balance", "heat", "Contoso Energia Ciepło", "Historian", 7, 0.90, 4),
    ("DP-011", "overhead_line_inspection", "grid", "Contoso Energia Sieci", "CMMS + inspekcje dronowe", 6, 0.87, 3),
    ("DP-012", "platform_capacity_telemetry", "platform", "Contoso Energia Usługi Wspólne", "FinOps platform telemetry", 16, 0.98, 11),
    ("DP-013", "data_contract_registry", "platform", "Contoso Energia Usługi Wspólne", "manual registry", 4, 0.97, 9),
    ("DP-014", "agent_factory_registry", "platform", "Contoso Energia Usługi Wspólne", "manual registry", 12, 0.86, 10),
    ("DP-015", "legacy_application_portfolio", "platform", "Contoso Energia Usługi Wspólne", "CMDB", 20, 0.84, 7),
    ("DP-016", "ot_boundary_dataflows", "platform", "Contoso Energia Usługi Wspólne", "Bezpieczeństwo OT", 8, 0.93, 6),
    ("DP-017", "corporate_document_index", "platform", "Contoso Energia Usługi Wspólne", "ECM synthetic", 28, 0.78, 2),
    ("DP-018", "shadow_report_archive", "finance", "Contoso Energia Usługi Wspólne", "fileshare synthetic", 22, 0.63, 0),
    ("DP-019", "obsolete_helpdesk_extract", "platform", "Contoso Energia Usługi Wspólne", "legacy export", 19, 0.58, 0),
    ("DP-020", "pilot_ai_prompt_logs", "platform", "Contoso Energia Usługi Wspólne", "AI Gateway telemetry", 17, 0.66, 1),
    ("DP-021", "temporary_csrd_workspace", "finance", "Contoso Energia Usługi Wspólne", "manual upload", 15, 0.69, 0),
    ("DP-022", "replicated_ot_alarm_snapshot", "platform", "Contoso Energia Usługi Wspólne", "SCADA", 25, 0.82, 0),
    ("DP-023", "procurement_spend_cube", "finance", "Contoso Energia Usługi Wspólne", "ERP synthetic", 13, 0.91, 5),
    ("DP-024", "hr_skills_matrix", "platform", "Contoso Energia Usługi Wspólne", "HR synthetic", 10, 0.86, 4),
]


def common_fact_fields(source: str, version: str = "v1") -> dict:
    return {
        "local_timezone": TZ,
        "settlement_interval": "month",
        "source_system": source,
        "quality_flag": "good",
        "ingestion_timestamp": "2026-12-31T22:15:00+01:00",
        "data_version": version,
    }


def write_csv(name: str, rows: list[dict]):
    pd.DataFrame(rows).to_csv(DATA / name, index=False, encoding="utf-8")


def write_jsonl(name: str, rows: list[dict]):
    with (DATA / name).open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def generate():
    DATA.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    products = []
    for i, (pid, name, domain, owner, source, base_cu, quality, consumers) in enumerate(PRODUCTS, 1):
        products.append({
            "data_product_id": pid, "data_product_name": name, "domain": domain,
            "owning_company": owner, "data_owner_role": f"{domain}_data_owner",
            "technical_owner": f"team_{domain}",
            "business_criticality": ["medium", "high", "critical"][i % 3],
            "classification": ["internal", "confidential", "restricted"][i % 3],
            "expected_freshness_h": [1, 4, 12, 24][i % 4],
            "consumer_count": consumers,
            "created_date": (datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(days=i * 9)).date().isoformat(),
            "status": "active" if i not in (18, 19, 21) else "candidate",
            "notes": "synthetic demo record; not a confirmed Contoso Energia system",
        })
    write_csv("data_product.csv", products)

    contracts = [{
        "contract_id": "DC-" + p["data_product_id"].split("-")[1],
        "data_product_id": p["data_product_id"],
        "schema_version": "1.0" if p["data_product_id"] not in ("DP-017", "DP-018", "DP-019", "DP-021") else "0.8",
        "freshness_sla_h": p["expected_freshness_h"],
        "completeness_sla_pct": 97 if p["business_criticality"] == "critical" else 94,
        "accuracy_sla_pct": 96 if p["business_criticality"] == "critical" else 93,
        "owner_approved": p["consumer_count"] > 0 and p["data_product_id"] != "DP-020",
        "consumer_approved": p["consumer_count"] >= 2,
        "review_cycle": "quarterly",
        "last_review_date": "2026-10-15" if p["consumer_count"] >= 2 else "2026-04-15",
    } for p in products]
    write_csv("data_contract.csv", contracts)

    consumers, cid = [], 1
    for p in products:
        for j in range(p["consumer_count"]):
            consumers.append({
                "consumer_id": f"C-{cid:03d}", "data_product_id": p["data_product_id"],
                "consumer_name": f"consumer_{p['domain']}_{j+1}",
                "consumer_type": ["report", "notebook", "agent", "app"][j % 4],
                "owning_company": COMPANIES[(cid + j) % len(COMPANIES)],
                "access_purpose": "demo decision support",
                "last_access_date": (datetime(2026, 12, 20) - timedelta(days=(j * 3 + cid) % 45)).date().isoformat(),
            })
            cid += 1
    write_csv("consumer.csv", consumers)

    check_types = ["freshness", "completeness", "accuracy", "schema_compatibility"]
    write_csv("quality_check.csv", [{
        "quality_check_id": f"QC-{p['data_product_id']}-{c[:3].upper()}",
        "data_product_id": p["data_product_id"], "check_type": c,
        "threshold_pct": 95 if c != "freshness" else 90,
        "severity": "critical" if p["business_criticality"] == "critical" else "major",
        "enabled": True,
    } for p in products for c in check_types])

    months = pd.period_range("2025-01", "2026-12", freq="M").astype(str).tolist()
    quality_rows = []
    for p in products:
        base = next(x[6] for x in PRODUCTS if x[0] == p["data_product_id"])
        for mi, m in enumerate(months):
            for ct in check_types:
                drift = -0.014 * max(0, mi - 15) if p["data_product_id"] in ("DP-017", "DP-018", "DP-019", "DP-020", "DP-021", "DP-022") else 0.001 * mi
                score = min(0.995, max(0.45, base + drift + {"freshness": -0.015, "completeness": .005, "accuracy": 0, "schema_compatibility": -.004}[ct] + rng.normal(0, .018)))
                quality_rows.append({
                    "quality_result_id": f"QR-{p['data_product_id']}-{m}-{ct}",
                    "event_timestamp_utc": pd.Timestamp(m + "-28T12:00:00Z").isoformat(),
                    "month": m, "quality_check_id": f"QC-{p['data_product_id']}-{ct[:3].upper()}", "data_product_id": p["data_product_id"], "check_type": ct,
                    "score_pct": round(score * 100, 2), "passed": score >= .9,
                    **common_fact_fields(p["notes"].split(';')[0] if False else next(x[4] for x in PRODUCTS if x[0] == p["data_product_id"]))
                })
    write_csv("quality_result.csv", quality_rows)

    edges = [("DP-001","DP-002","schema"),("DP-001","DP-003","reference"),("DP-002","DP-012","usage"),("DP-003","DP-004","feature"),("DP-004","DP-005","semantic"),("DP-006","DP-007","csrd"),("DP-008","DP-009","feature"),("DP-012","DP-014","finops"),("DP-012","DP-018","archive"),("DP-013","DP-014","governance"),("DP-014","DP-020","telemetry"),("DP-015","DP-023","cost"),("DP-016","DP-022","ot"),("DP-017","DP-020","rag"),("DP-021","DP-023","finance"),("DP-023","DP-012","allocation"),("DP-024","DP-014","skill"),("DP-010","DP-012","usage"),("DP-011","DP-012","usage"),("DP-005","DP-014","agent_input")]
    write_csv("lineage_edge.csv", [{"lineage_edge_id": f"LE-{i:03d}", "source_data_product_id": s, "target_data_product_id": t, "edge_type": k, "change_breaking_risk": ["low", "medium", "high"][i % 3]} for i, (s, t, k) in enumerate(edges, 1)])

    agents = [("AG-001","contract_quality_copilot","Contoso Energia Usługi Wspólne","production","platform_data_owner",5200,True),("AG-002","grid_incident_triage","Contoso Energia Sieci","pilot","grid_ops",7400,True),("AG-003","customer_response_drafter","Contoso Energia Sprzedaż","pilot","customer_ops",6800,False),("AG-004","legacy_modernization_advisor","Contoso Energia Usługi Wspólne","production","enterprise_architecture",9100,True),("AG-005","csrd_evidence_collector","Contoso Energia Wytwarzanie","pilot","esg_office",4300,True),("AG-006","ot_alert_summarizer","Contoso Energia Usługi Wspólne","pilot","",8400,False),("AG-007","procurement_clause_checker","Contoso Energia Usługi Wspólne","retired","procurement",1200,False),("AG-008","data_catalog_assistant","Contoso Energia Usługi Wspólne","production","data_office",3900,True),("AG-009","temporary_prompt_playground","Contoso Energia Usługi Wspólne","pilot","",7100,False),("AG-010","finops_explainability_agent","Contoso Energia Usługi Wspólne","pilot","finops",4600,True),("AG-011","maintenance_knowledge_agent","Contoso Energia Ciepło","pilot","heat_ops",5100,False),("AG-012","line_inspection_agent","Contoso Energia Sieci","pilot","grid_ops",3600,True)]
    write_csv("agent.csv", [{"agent_id": a, "agent_name": n, "owning_company": c, "lifecycle_status": s, "business_owner": o, "quarterly_cost_pln": cost, "has_production_exception": (not ev and s != "retired"), "primary_data_products": "DP-014;DP-013" if "catalog" in n or "quality" in n else "DP-012;DP-015", "notes": "synthetic AI agent registry entry"} for a,n,c,s,o,cost,ev in agents])
    write_csv("agent_evaluation.csv", [{"evaluation_id": f"EV-{a}", "agent_id": a, "evaluation_date": "2026-11-30", "groundedness_score_pct": int(rng.integers(82,96)), "safety_score_pct": int(rng.integers(86,99)), "cost_per_1000_actions_pln": round(cost / max(100, int(rng.integers(900,2600))) * 1000, 2), "decision": "approved" if s == "production" else "pilot_continue"} for a,n,c,s,o,cost,ev in agents if ev])
    incidents = []
    incident_start = datetime(2026, 10, 1, tzinfo=timezone.utc)
    for i in range(384):
        agent_idx = int(rng.integers(0, len(agents)))
        ts = incident_start + timedelta(hours=i * 6 + int(rng.integers(0, 4)))
        incidents.append({
            "incident_id": f"AIINC-{i+1:04d}", "event_timestamp_utc": ts.isoformat(),
            "agent_id": agents[agent_idx][0], "severity": ["low","medium","medium","high"][i % 4],
            "incident_type": ["hallucination","policy_refusal","tool_error","cost_spike","latency_spike","grounding_gap"][i % 6],
            "resolved": i % 11 != 0, **{**common_fact_fields("AI Gateway telemetry"), "settlement_interval": "event"}
        })
    write_csv("agent_incident.csv", incidents); write_jsonl("agent_incident_stream.jsonl", incidents)

    techs = ["Oracle Forms","Java 8",".NET Framework","Lotus Notes","Access","COBOL","VB6","PowerBuilder","SAP custom","SharePoint legacy"]
    legacy = []
    for i in range(1, 37):
        age = int(rng.integers(3,24)); risk = int(min(100, age*3 + rng.integers(5,40))); maintain = int(rng.integers(80,950))*1000; deps = int(rng.integers(1,9))
        recommendation = "retain" if risk < 35 else "rehost" if risk < 45 else "replatform" if risk < 60 else "refactor" if risk < 75 else "retire" if deps < 3 else "replace"
        legacy.append({"legacy_app_id": f"LA-{i:03d}", "app_name": f"synthetic_legacy_app_{i:02d}", "owning_company": COMPANIES[i % len(COMPANIES)], "business_domain": DOMAINS[i % len(DOMAINS)], "technology": techs[i % len(techs)], "age_years": age, "risk_score": risk, "annual_maintenance_cost_pln": maintain, "dependency_count": deps, "criticality": ["low","medium","high","critical"][i%4], "recommended_6r": recommendation, "personal_data": i % 5 == 0, "ot_dependency": i % 6 == 0})
    write_csv("legacy_app.csv", legacy)
    write_csv("dependency.csv", [{"dependency_id": f"DEP-{i:03d}", "source_app_id": f"LA-{(i%36)+1:03d}", "target_app_id": f"LA-{((i*5)%36)+1:03d}", "dependency_type": ["database","file_export","api","manual_process"][i%4], "criticality": ["low","medium","high"][i%3]} for i in range(1,73)])

    telemetry = []
    hourly_index = pd.date_range("2025-01-01T00:00:00Z", "2026-12-31T23:00:00Z", freq="h")
    for h_idx, ts in enumerate(hourly_index):
        month = ts.strftime("%Y-%m")
        hour = ts.hour
        day_factor = 1.0 + 0.22 * np.sin((hour - 7) / 24 * 2 * np.pi)
        weekday_factor = 0.88 if ts.weekday() >= 5 else 1.0
        month_idx = (ts.year - 2025) * 12 + ts.month - 1
        seasonal = 1 + 0.08 * np.sin(month_idx / 3.0)
        for p in products:
            base_cu = next(x[5] for x in PRODUCTS if x[0] == p["data_product_id"])
            waste = 1.8 if p["consumer_count"] == 0 else 1.15 if p["consumer_count"] <= 1 else 1.0
            cu = round(max(0.01, base_cu * waste * seasonal * day_factor * weekday_factor * (0.90 + rng.random() * 0.20)), 4)
            telemetry.append({
                "event_timestamp_utc": ts.isoformat(), "month": month, "data_product_id": p["data_product_id"],
                "workspace_domain": p["domain"], "owning_company": p["owning_company"], "capacity_name": "F64-demo-shared",
                "cu_hours": cu, "interactive_cu_hours": round(cu*.37,4), "background_cu_hours": round(cu*.63,4),
                "synthetic_cost_pln": round(cu * 0.42, 4), **{**common_fact_fields("FinOps platform telemetry"), "settlement_interval": "hour"}
            })
    write_jsonl("capacity_telemetry.jsonl", telemetry)

    usage_df = pd.DataFrame(telemetry).groupby(["month", "data_product_id", "workspace_domain", "owning_company", "capacity_name"], as_index=False).agg(
        cu_hours=("cu_hours", "sum"), interactive_cu_hours=("interactive_cu_hours", "sum"),
        background_cu_hours=("background_cu_hours", "sum"), synthetic_cost_pln=("synthetic_cost_pln", "sum")
    )
    usage = []
    alloc = []
    for _, row in usage_df.iterrows():
        usage_row = {
            "event_timestamp_utc": pd.Timestamp(row["month"] + "-28T23:00:00Z").isoformat(),
            "month": row["month"], "data_product_id": row["data_product_id"], "workspace_domain": row["workspace_domain"],
            "owning_company": row["owning_company"], "capacity_name": row["capacity_name"],
            "cu_hours": round(float(row["cu_hours"]), 2), "interactive_cu_hours": round(float(row["interactive_cu_hours"]), 2),
            "background_cu_hours": round(float(row["background_cu_hours"]), 2), "synthetic_cost_pln": round(float(row["synthetic_cost_pln"]), 2),
            **common_fact_fields("FinOps platform telemetry")
        }
        usage.append(usage_row)
        alloc.append({
            "allocation_id": f"ALLOC-{row['data_product_id']}-{row['month']}", "month": row["month"],
            "data_product_id": row["data_product_id"], "owning_company": row["owning_company"],
            "allocated_cost_pln": usage_row["synthetic_cost_pln"], "allocation_method": "cu_hours_weighted",
            "showback_status": "published", "chargeback_ready": int(products[[p["data_product_id"] for p in products].index(row["data_product_id"])]["consumer_count"]) > 0
        })
    write_csv("capacity_usage.csv", usage); write_csv("cost_allocation.csv", alloc)
    ca = pd.DataFrame(alloc); charge = []
    for (m, comp), g in ca.groupby(["month","owning_company"]):
        charge.append({"chargeback_id": f"CB-{m}-{comp.replace(' ', '_')}", "month": m, "owning_company": comp, "allocated_cost_pln": round(float(g["allocated_cost_pln"].sum()), 2), "billing_mode": "showback", "approval_status": "pending" if m >= "2026-10" else "published"})
    write_csv("chargeback.csv", charge)

    write_csv("ot_dataflow.csv", [{"ot_dataflow_id": a, "source_zone": b, "target_zone": c, "direction": d, "control_pattern": e, "data_scope": f, "approval_status": g, "nis2_relevance": True} for a,b,c,d,e,f,g in [("OTF-001","SCADA","Eventstream","OT_to_IT","one_way_replica","status telemetry only","approved"),("OTF-002","Historian","Eventhouse","OT_to_IT","dmz_replica","aggregated time series","approved"),("OTF-003","IEC 61850","Eventstream","OT_to_IT","event_broker","station events, no commands","review"),("OTF-004","AI recommendation","SCADA","IT_to_OT","blocked","control not allowed from analytics platform","blocked"),("OTF-005","SOC/SIEM","Eventhouse","OT_to_IT","security_log_export","OT security events","approved")]])
    write_csv("security_control.csv", [{"security_control_id": a, "control_name": b, "control_domain": c, "applies_to_entity": d, "implementation_status": e} for a,b,c,d,e in [("SC-001","Purview sensitivity labels","classification","data_product","implemented"),("SC-002","RLS per company and domain","access","semantic_model","designed"),("SC-003","No analytical control to OT","segmentation","ot_dataflow","implemented"),("SC-004","Agent owner required","ai_governance","agent","partial"),("SC-005","Evaluation before production","ai_governance","agent_evaluation","partial"),("SC-006","Chargeback approval workflow","finops","chargeback","designed"),("SC-007","Schema change impact review","data_contract","lineage_edge","implemented"),("SC-008","NIS2 incident escalation","security","agent_incident","designed")]])

    counts = {p.name: int(len(pd.read_csv(p))) for p in DATA.glob("*.csv")}
    counts.update({p.name: sum(1 for _ in p.open(encoding="utf-8")) for p in DATA.glob("*.jsonl")})
    (DERIVED / "dataset_counts.json").write_text(json.dumps(counts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(counts, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    generate()
