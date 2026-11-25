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
profiles = pd.read_csv(DATA / "customer_profiles_d0_15min_wide.csv")
prices = pd.read_csv(DATA / "market_prices_15min.csv")
price = prices[prices.local_timestamp.str.startswith(ass["d0"])].price_pln_per_mwh.to_numpy(float)
load = profiles[[c for c in profiles.columns if c.startswith("load_q")]].to_numpy(float)
pv = profiles[[c for c in profiles.columns if c.startswith("pv_q")]].to_numpy(float)
eta_rt = ass["storage_round_trip_efficiency"]; eta_c = math.sqrt(eta_rt); eta_d = math.sqrt(eta_rt)
low_thr, high_thr = np.quantile(price, .25), np.quantile(price, .75)
rows=[]; errors=[]
for idx, c in customers[customers.has_storage.astype(bool)].iterrows():
    cap=float(c.storage_capacity_kwh); max_kw=min(5.0, cap/2); soc=cap*.35
    grid_total=grid_load=pv_self=pv_export=ch_grid=ch_pv=dis=0.0; base_cost=opt_cost=0.0
    for q in range(96):
        l=float(load[idx,q]); p=float(pv[idx,q]); pr=float(price[q])/1000
        base_import=max(l-p,0); base_export=max(p-l,0); base_cost += base_import*pr - base_export*max(pr*.70,-.10)
        direct=min(l,p); rem=l-direct; surplus=max(p-l,0)
        cpv=min(surplus,max_kw/4,max(0,cap-soc)/eta_c); soc += cpv*eta_c; ch_pv += cpv; surplus -= cpv
        d=0.0
        if price[q] >= high_thr and rem > 0:
            d=min(rem,max_kw/4,soc*eta_d); soc -= d/eta_d; rem -= d; dis += d
        cg=0.0
        if price[q] <= low_thr and soc < cap*.95:
            cg=min(max_kw/4,(cap-soc)/eta_c); soc += cg*eta_c; ch_grid += cg
        gl=max(rem,0); grid_load += gl; grid_total += gl + cg; pv_self += direct; pv_export += surplus
        opt_cost += (gl+cg)*pr - surplus*max(pr*.70,-.10)
    total=load[idx].sum(); physical=grid_load + pv_self + dis; err=total-physical; errors.append(abs(err))
    rows.append({"customer_id":c.customer_id,"storage_capacity_kwh":cap,"baseline_energy_cost_pln":round(base_cost,2),"optimized_energy_cost_pln":round(opt_cost,2),"storage_value_pln":round(base_cost-opt_cost,2),"grid_import_total_kwh":round(grid_total,4),"grid_import_for_load_kwh":round(grid_load,4),"pv_self_consumption_kwh":round(pv_self,4),"charged_from_grid_kwh":round(ch_grid,4),"charged_from_pv_kwh":round(ch_pv,4),"discharged_to_load_kwh":round(dis,4),"cycle_losses_kwh":round(max(0,ch_grid+ch_pv-dis),4),"pv_export_kwh":round(pv_export,4),"energy_balance_error_kwh":round(err,6)})
res=pd.DataFrame(rows); res.to_csv(DERIVED / "storage_customer_optimization.csv", index=False)
summary=pd.DataFrame([{"storage_customers_count":len(res),"round_trip_efficiency":eta_rt,"avg_storage_value_pln":round(float(res.storage_value_pln.mean()),2),"total_storage_value_pln":round(float(res.storage_value_pln.sum()),2),"total_cycle_losses_mwh":round(float(res.cycle_losses_kwh.sum()/1000),4),"max_energy_balance_error_kwh":round(float(np.max(errors)),8),"pv_export_mwh_after_storage":round(float(res.pv_export_kwh.sum()/1000),4)}])
summary.to_csv(DERIVED / "storage_optimization_summary.csv", index=False)
print(summary.to_dict(orient="records")[0])
