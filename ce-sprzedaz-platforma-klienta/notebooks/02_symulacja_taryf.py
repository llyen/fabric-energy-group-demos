# CELL
from pathlib import Path
import json
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
ass = json.loads((DATA / "assumptions.json").read_text(encoding="utf-8"))
profiles = pd.read_csv(DATA / "customer_profiles_d0_15min_wide.csv")
segments = pd.read_csv(DERIVED / "customer_segments.csv")
prices = pd.read_csv(DATA / "market_prices_15min.csv")
price = prices[prices.local_timestamp.str.startswith(ass["d0"])].price_pln_per_mwh.to_numpy(float)
load = profiles[[c for c in profiles.columns if c.startswith("load_q")]].to_numpy(float)
pv = profiles[[c for c in profiles.columns if c.startswith("pv_q")]].to_numpy(float)
net = np.maximum(load - pv, 0); export = np.maximum(pv - load, 0)
energy_mwh = net.sum(axis=1) / 1000
hours = np.arange(96) / 4
peak = ((hours >= 6) & (hours < 13)) | ((hours >= 15) & (hours < 22))

def energy_component(rate_vec):
    import_energy = (net * (rate_vec / 1000)).sum(axis=1)
    export_credit = (export * (np.maximum(price, -100) * .70 / 1000)).sum(axis=1)
    return import_energy - export_credit

energy_flat = energy_component(np.full(96, ass["flat_energy_price_pln_mwh"]))
energy_multi = energy_component(np.where(peak, ass["multi_zone_peak_pln_mwh"], ass["multi_zone_offpeak_pln_mwh"]))
energy_dyn = energy_component(price)
distribution_fee = energy_mwh * ass["distribution_fee_pln_mwh"]
system_fee = energy_mwh * ass["system_fee_pln_mwh"]
flat = energy_flat + distribution_fee + system_fee
multi = energy_multi + distribution_fee + system_fee
dyn = energy_dyn + distribution_fee + system_fee
res = pd.DataFrame({"customer_id": profiles.customer_id, "energy_component_flat_pln_day": energy_flat.round(2), "energy_component_multizone_pln_day": energy_multi.round(2), "energy_component_dynamic_pln_day": energy_dyn.round(2), "distribution_fee_pln_day": distribution_fee.round(2), "system_fee_pln_day": system_fee.round(2), "bill_flat_pln_day": flat.round(2), "bill_multizone_pln_day": multi.round(2), "bill_dynamic_pln_day": dyn.round(2), "dynamic_vs_flat_energy_component_pln_day": (energy_dyn-energy_flat).round(2), "dynamic_vs_flat_pln_day": (dyn-flat).round(2), "dynamic_vs_multizone_pln_day": (dyn-multi).round(2), "net_import_kwh_day": (energy_mwh*1000).round(3), "export_kwh_day": export.sum(axis=1).round(3), "negative_price_import_kwh_day": net[:, price < 0].sum(axis=1).round(3), "evening_peak_import_kwh_day": net[:, (hours>=18)&(hours<21)].sum(axis=1).round(3)}).merge(segments[["customer_id","segment_name","cluster_id"]], on="customer_id")
res.to_csv(DERIVED / "tariff_customer_results.csv", index=False)
summary = res.groupby("segment_name").agg(customers_count=("customer_id","count"), avg_flat_pln_day=("bill_flat_pln_day","mean"), avg_multizone_pln_day=("bill_multizone_pln_day","mean"), avg_dynamic_pln_day=("bill_dynamic_pln_day","mean"), avg_dynamic_vs_flat_pln_day=("dynamic_vs_flat_pln_day","mean"), avg_dynamic_vs_flat_energy_component_pln_day=("dynamic_vs_flat_energy_component_pln_day","mean"), winners_dynamic_vs_flat=("dynamic_vs_flat_pln_day", lambda s: int((s<0).sum())), losers_dynamic_vs_flat=("dynamic_vs_flat_pln_day", lambda s: int((s>0).sum())), p10_dynamic_vs_flat_pln_day=("dynamic_vs_flat_pln_day", lambda s: s.quantile(.10)), p90_dynamic_vs_flat_pln_day=("dynamic_vs_flat_pln_day", lambda s: s.quantile(.90)), avg_negative_price_import_kwh_day=("negative_price_import_kwh_day","mean"), avg_evening_peak_import_kwh_day=("evening_peak_import_kwh_day","mean")).reset_index()
summary.to_csv(DERIVED / "tariff_summary.csv", index=False)
overall = pd.DataFrame([{"customers_count":len(res),"dynamic_winners_count":int((res.dynamic_vs_flat_pln_day<0).sum()),"dynamic_losers_count":int((res.dynamic_vs_flat_pln_day>0).sum()),"dynamic_winners_pct":round(float((res.dynamic_vs_flat_pln_day<0).mean()*100),2),"dynamic_losers_pct":round(float((res.dynamic_vs_flat_pln_day>0).mean()*100),2),"avg_dynamic_vs_flat_pln_day":round(float(res.dynamic_vs_flat_pln_day.mean()),2),"avg_dynamic_vs_flat_energy_component_pln_day":round(float(res.dynamic_vs_flat_energy_component_pln_day.mean()),2),"p10_dynamic_vs_flat_pln_day":round(float(res.dynamic_vs_flat_pln_day.quantile(.10)),2),"p90_dynamic_vs_flat_pln_day":round(float(res.dynamic_vs_flat_pln_day.quantile(.90)),2),"min_rdn_price_pln_mwh":round(float(price.min()),2),"max_rdn_price_pln_mwh":round(float(price.max()),2)}])
overall.to_csv(DERIVED / "tariff_winners_losers.csv", index=False)
pd.DataFrame([{"horizon":"doba_referencyjna_D0_2026_06_18","currency_scope":"PLN na odbiorcę za dobę referencyjną","tariff_comparison_scope":"Zmienia się składnik energii zależny od wariantu taryfy; distribution_fee_pln_day i system_fee_pln_day są pokazane osobno i w tym modelu nie zmieniają się przez taryfę dynamiczną.","annual_portfolio_value_status":"nie_policzono_bez_ekstrapolacji","annual_portfolio_value_gap":"Do rocznej wyceny potrzeba pełnorocznych profili 15-min, pełnorocznej ścieżki cen RDN/kontraktów, rzeczywistych warunków taryfowych i umownych, taryfy dystrybucyjnej, podatków, mechanizmów osłonowych oraz skalibrowanej historii reakcji klientów."}]).to_csv(DERIVED / "tariff_bill_horizon_summary.csv", index=False)
print(overall.to_dict(orient="records")[0])
