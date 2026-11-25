# CELL
from pathlib import Path
import json, math
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
ass = json.loads((DATA / "assumptions.json").read_text(encoding="utf-8"))
customers = pd.read_csv(DATA / "customers.csv")
segments = pd.read_csv(DERIVED / "customer_segments.csv")
dsr = pd.read_csv(DERIVED / "dsr_overall_sensitivity.csv")

# CELL
# Jawny blok założeń ekonomicznych DSR.
# Wszystkie wartości są założeniami modelowymi do kalibracji z danymi klienta;
# nie są taryfą Contoso Energia, cennikiem ani obietnicą finansową.
dsr_economics = ass["dsr_economic_assumptions"]
value_kw = dsr_economics["value_per_kw_event_pln"]["value"]
incentive = dsr_economics["participant_incentive_pln_event"]["value"]
fixed = dsr_economics["program_fixed_cost_pln_per_event"]["value"]
fixed_cost_sensitivity = dsr_economics["fixed_cost_sensitivity_pln_event"]
assumption_rows = []
for name, meta in dsr_economics.items():
    if isinstance(meta, dict):
        assumption_rows.append({"parameter": name, "value": meta["value"], "description": meta["description"], "status": meta["status"]})
pd.DataFrame(assumption_rows).to_csv(DERIVED / "dsr_economic_assumptions.csv", index=False)

# CELL
# response_rate oznacza udział bazy programu, który faktycznie reaguje w pojedynczym zdarzeniu.
# Dlatego rozdzielamy: program_customers_base (adresaci programu) i responding_customers (aktywni w zdarzeniu).
program_base_all = ass["customer_count"]
rows=[]; thresholds=[]
for rr in ass["response_rates_tested"]:
    b=dsr[np.isclose(dsr.response_rate, rr)].iloc[0]
    avg_kw_per_program_customer = b.peak_reduction_mw * 1000 / program_base_all
    avg_kw_per_responding_customer = avg_kw_per_program_customer / rr
    margin_per_program_customer = avg_kw_per_program_customer * value_kw - incentive
    margin_per_responding_customer_equivalent = margin_per_program_customer / rr
    threshold_program = math.ceil(fixed / margin_per_program_customer) if margin_per_program_customer > 0 else None
    threshold_responding = math.ceil(threshold_program * rr) if threshold_program is not None else None
    thresholds.append({"response_rate":rr,"break_even_program_customers":threshold_program,"break_even_responding_customers":threshold_responding,"avg_kw_per_program_customer":round(float(avg_kw_per_program_customer),4),"avg_kw_per_responding_customer":round(float(avg_kw_per_responding_customer),4),"value_per_kw_event_pln":value_kw,"incentive_per_program_customer_pln_event":incentive,"program_fixed_cost_pln_event":fixed,"unit_margin_per_program_customer_pln_event":round(float(margin_per_program_customer),4),"unit_margin_per_responding_customer_equivalent_pln_event":round(float(margin_per_responding_customer_equivalent),4)})
    for n in [1000,2500,5000,7500,10000,15000,20000,30000,program_base_all]:
        n=min(n, program_base_all)
        responding=n*rr
        peak_mw=avg_kw_per_program_customer*n/1000
        gross=peak_mw*1000*value_kw
        inc=n*incentive
        net=gross-inc-fixed
        rows.append({"response_rate":rr,"program_customers_base":n,"expected_responding_customers":round(float(responding),1),"peak_reduction_mw":round(float(peak_mw),3),"avg_kw_per_program_customer":round(float(avg_kw_per_program_customer),4),"avg_kw_per_responding_customer":round(float(avg_kw_per_responding_customer),4),"gross_value_pln_event":round(float(gross),2),"program_customer_incentives_pln_event":round(float(inc),2),"fixed_cost_pln_event":fixed,"net_value_pln_event":round(float(net),2),"break_even_program_customers":threshold_program,"break_even_responding_customers":threshold_responding})
pd.DataFrame(rows).drop_duplicates(["response_rate","program_customers_base"]).to_csv(DERIVED / "portfolio_value_by_participants.csv", index=False)
pd.DataFrame(thresholds).to_csv(DERIVED / "portfolio_scale_threshold.csv", index=False)

# CELL
fixed_rows=[]
for rr in ass["response_rates_tested"]:
    b=dsr[np.isclose(dsr.response_rate, rr)].iloc[0]
    avg_kw_per_program_customer = b.peak_reduction_mw * 1000 / program_base_all
    avg_kw_per_responding_customer = avg_kw_per_program_customer / rr
    margin_per_program_customer = avg_kw_per_program_customer * value_kw - incentive
    for fixed_variant in fixed_cost_sensitivity:
        threshold_program = math.ceil(fixed_variant / margin_per_program_customer) if margin_per_program_customer > 0 else None
        threshold_responding = math.ceil(threshold_program * rr) if threshold_program is not None else None
        fixed_rows.append({"response_rate":rr,"program_fixed_cost_pln_event":fixed_variant,"break_even_program_customers":threshold_program,"break_even_responding_customers":threshold_responding,"avg_kw_per_program_customer":round(float(avg_kw_per_program_customer),4),"avg_kw_per_responding_customer":round(float(avg_kw_per_responding_customer),4),"unit_margin_per_program_customer_pln_event":round(float(margin_per_program_customer),4),"value_per_kw_event_pln":value_kw,"incentive_per_program_customer_pln_event":incentive})
pd.DataFrame(fixed_rows).to_csv(DERIVED / "portfolio_threshold_fixed_cost_sensitivity.csv", index=False)

# CELL
seg=customers[["customer_id","has_pv","has_storage","has_ev","has_electric_heating","flexible_power_kw_model","price_response_index"]].merge(segments[["customer_id","segment_name"]], on="customer_id")
segval=seg.groupby("segment_name").apply(lambda g: pd.Series({"program_customers_count":len(g),"expected_responding_customers_at_20pct":len(g)*0.20,"avg_kw_per_program_customer_at_20pct":(g.flexible_power_kw_model*g.price_response_index*0.20).mean(),"avg_kw_per_responding_customer":(g.flexible_power_kw_model*g.price_response_index).mean(),"portfolio_mw_at_20pct":(g.flexible_power_kw_model*g.price_response_index*0.20).sum()/1000}), include_groups=False).reset_index()
segval.to_csv(DERIVED / "flexibility_value_by_segment.csv", index=False)

def asset_group(r):
    if r.has_storage:
        return "storage"
    if r.has_pv:
        return "pv_without_storage"
    if r.has_ev or r.has_electric_heating:
        return "ev_or_electric_heating_no_pv_storage"
    return "no_major_controllable_device"
seg["asset_group"] = seg.apply(asset_group, axis=1)
asset=seg.groupby("asset_group").apply(lambda g: pd.Series({"program_customers_count":len(g),"expected_responding_customers_at_20pct":len(g)*0.20,"avg_kw_per_program_customer_at_20pct":(g.flexible_power_kw_model*g.price_response_index*0.20).mean(),"avg_kw_per_responding_customer":(g.flexible_power_kw_model*g.price_response_index).mean(),"portfolio_mw_at_20pct":(g.flexible_power_kw_model*g.price_response_index*0.20).sum()/1000}), include_groups=False).reset_index()
asset.to_csv(DERIVED / "flexibility_potential_by_asset_group.csv", index=False)
print(pd.DataFrame(thresholds).to_dict(orient="records"))
