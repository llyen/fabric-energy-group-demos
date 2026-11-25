# CELL
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
sources = pd.read_csv(DATA / "heat_sources.csv")
opt = pd.read_csv(DERIVED / "optimization_results_hourly.csv")
src_tel = pd.read_json(DATA / "source_telemetry_hourly.jsonl", lines=True)
summary = pd.read_csv(DERIVED / "optimization_summary.csv").iloc[0].to_dict()
start = summary["window_start"]; end = summary["window_end"]
src_tel = src_tel[(src_tel["local_timestamp"] >= start) & (src_tel["local_timestamp"] <= end)]

# CELL
rows=[]
for _,src in sources.iterrows():
    sid=src["heat_source_id"]
    base = src_tel[src_tel["heat_source_id"]==sid]
    opt_heat = opt["gen_"+sid].sum()
    opt_fuel = opt_heat/(src["heat_efficiency_pct"]/100)
    opt_em = opt_fuel*src["emission_tco2_per_mwh_fuel"]
    rows.append({"heat_source_id":sid,"source_type":src["source_type"],"baseline_heat_mwh":round(base["heat_production_mwh"].sum(),3),"optimized_heat_mwh":round(opt_heat,3),"baseline_emissions_tco2":round(base["emissions_tco2"].sum(),3),"optimized_emissions_tco2":round(opt_em,3),"emissions_delta_tco2":round(base["emissions_tco2"].sum()-opt_em,3)})
out=pd.DataFrame(rows)
out.to_csv(DERIVED / "emissions_by_source.csv", index=False)
print(out.to_string(index=False))
