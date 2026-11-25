# CELL
from pathlib import Path
import json
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
ass = json.loads((DATA / "assumptions.json").read_text(encoding="utf-8"))
customers = pd.read_csv(DATA / "customers.csv")
profiles = pd.read_csv(DATA / "customer_profiles_d0_15min_wide.csv")
segments = pd.read_csv(DERIVED / "customer_segments.csv")
load = profiles[[c for c in profiles.columns if c.startswith("load_q")]].to_numpy(float)
start_q, end_q = 18*4, 20*4
rebound_q = np.arange(end_q, min(96, end_q + ass["rebound_window_quarters"]))
base_curve_mw = load.sum(axis=0) * 4 / 1000
seg_names = segments.segment_name.to_numpy()
rows=[]; curve=[]
for rr in ass["response_rates_tested"]:
    red_kw = customers.flexible_power_kw_model.to_numpy(float) * customers.price_response_index.to_numpy(float) * rr
    red_kwh_q = red_kw / 4
    event_mwh = red_kwh_q.sum() * (end_q - start_q) / 1000
    rebound_mwh = event_mwh * ass["rebound_ratio"]
    shifted = base_curve_mw.copy(); reduction_mw = red_kw.sum()/1000
    shifted[start_q:end_q] -= reduction_mw
    shifted[rebound_q] += (rebound_mwh / len(rebound_q)) * 4
    for q in range(96): curve.append({"response_rate":rr,"quarter":q,"hour":q/4,"baseline_mw":round(float(base_curve_mw[q]),4),"after_response_mw":round(float(shifted[q]),4),"delta_mw":round(float(shifted[q]-base_curve_mw[q]),4)})
    for name in sorted(set(seg_names)):
        m=seg_names==name
        rows.append({"response_rate":rr,"segment_name":name,"customers_count":int(m.sum()),"peak_reduction_mw":round(float(red_kw[m].sum()/1000),4),"shifted_energy_mwh":round(float(red_kwh_q[m].sum()*(end_q-start_q)/1000),4),"rebound_energy_mwh":round(float(red_kwh_q[m].sum()*(end_q-start_q)*ass["rebound_ratio"]/1000),4),"rebound_ratio":ass["rebound_ratio"]})
summary=pd.DataFrame(rows); summary.to_csv(DERIVED / "dsr_sensitivity.csv", index=False)
pd.DataFrame(curve).to_csv(DERIVED / "dsr_event_curve_15min.csv", index=False)
overall=summary.groupby("response_rate").agg(customers_count=("customers_count","sum"),peak_reduction_mw=("peak_reduction_mw","sum"),shifted_energy_mwh=("shifted_energy_mwh","sum"),rebound_energy_mwh=("rebound_energy_mwh","sum")).reset_index()
overall.to_csv(DERIVED / "dsr_overall_sensitivity.csv", index=False)
print(overall.to_dict(orient="records"))
