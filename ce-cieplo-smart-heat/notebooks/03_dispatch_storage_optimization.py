# CELL
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.optimize import linprog

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)
meta = json.loads((DATA / "dataset_metadata.json").read_text(encoding="utf-8"))
D0 = pd.Timestamp(meta["d0"])

# CELL
sources = pd.read_csv(DATA / "heat_sources.csv")
storage = pd.read_csv(DATA / "thermal_storage.csv").iloc[0]
forecast = pd.read_csv(DERIVED / "forecast_window.csv")
prices = pd.read_json(DATA / "electricity_prices_hourly.jsonl", lines=True)
net = pd.read_json(DATA / "network_telemetry_hourly.jsonl", lines=True)
src_tel = pd.read_json(DATA / "source_telemetry_hourly.jsonl", lines=True)
segments = pd.read_csv(DATA / "network_segments.csv")
for frame in [prices, net, src_tel]:
    frame["ts"] = pd.to_datetime(frame["local_timestamp"], utc=True)
start = D0 - pd.Timedelta(days=2); end = D0 + pd.Timedelta(days=5)

window = forecast.copy()
window["ts"] = pd.to_datetime(window["local_timestamp"], utc=True)
window = window[(window["ts"] >= start) & (window["ts"] <= end)].copy().reset_index(drop=True)
window = window.merge(prices[["local_timestamp","price_pln_per_mwh"]], on="local_timestamp")
base_loss_hour = net[(net["ts"] >= start) & (net["ts"] <= end)].groupby("local_timestamp", as_index=False).agg(
    baseline_network_losses_mwh=("heat_loss_mwh","sum"), baseline_supply_temp_c=("supply_temp_c","mean")
)
window = window.merge(base_loss_hour, on="local_timestamp")

# This coefficient is known from asset data before the decision; it is not inferred from actual demand.
total_loss_coeff = float((segments["length_km"] * segments["heat_loss_coeff_mwh_per_km_h_c"]).sum())
units = sources["heat_source_id"].tolist(); U=len(units)
source_by_id = {r["heat_source_id"]: r for _, r in sources.iterrows()}
eta_c = storage["charge_efficiency_pct"]/100; eta_d = storage["discharge_efficiency_pct"]/100; storage_loss = storage["standing_loss_pct_per_hour"]/100
cap_storage = storage["energy_capacity_mwh"]; init_soc = storage["initial_soc_mwh"]


def production_unit_cost(src, price):
    heat_eff=src["heat_efficiency_pct"]/100
    fuel=src["fuel_cost_pln_per_mwh_fuel"]/heat_eff + src["variable_om_pln_per_mwh_heat"]
    eua=src["emission_tco2_per_mwh_fuel"]/heat_eff * 330
    power_credit=src["power_to_heat_ratio_mwe_per_mwt"]*price
    return fuel + eua - power_credit


def fuel_and_emissions(heat_by_unit):
    fuel=0.0; em=0.0; elec=0.0
    for sid,g in heat_by_unit.items():
        src=source_by_id[sid]
        f=g/(src["heat_efficiency_pct"]/100) if src["heat_efficiency_pct"] else 0
        fuel += f
        em += f*src["emission_tco2_per_mwh_fuel"]
        elec += g*src["power_to_heat_ratio_mwe_per_mwt"]
    return fuel, em, elec


def planned_supply_temp(temp_plan, demand_plan, enable_temp):
    baseline = 92 + np.maximum(0, -temp_plan)*0.85 + np.where(demand_plan > 235, 4, 0)
    if not enable_temp:
        return baseline
    reduction = np.where(temp_plan < -14, 3.0, 6.0)
    return baseline - reduction


def loss_from_temp(supply_temp, ambient_temp):
    return np.maximum(6, total_loss_coeff * (supply_temp - ambient_temp) * 1.08)


def optimize_plan(label, demand_plan_col, temp_plan_col, enable_storage=True, enable_temp=True):
    df = window.copy()
    df["plan_demand_mwh"] = df[demand_plan_col]
    df["plan_temp_c"] = df[temp_plan_col]
    df["planned_supply_temp_c"] = planned_supply_temp(df["plan_temp_c"], df["plan_demand_mwh"], enable_temp)
    df["planned_network_losses_mwh"] = loss_from_temp(df["planned_supply_temp_c"], df["plan_temp_c"])
    T=len(df)
    def ix_g(t,u): return t*U+u
    off_c=U*T; off_d=off_c+T; off_s=off_d+T; n=off_s+T
    c=np.zeros(n)
    for t,row in df.iterrows():
        price=row["price_pln_per_mwh"]
        for u,(_,src) in enumerate(sources.iterrows()):
            c[ix_g(t,u)] = production_unit_cost(src, price)
        c[off_c+t]=0.7; c[off_d+t]=0.4
    bounds=[]
    for _ in range(T):
        for _,src in sources.iterrows():
            bounds.append((0, src["available_capacity_mwt"]))
    max_charge = storage["max_charge_mwt"] if enable_storage else 0
    max_dis = storage["max_discharge_mwt"] if enable_storage else 0
    for _ in range(T): bounds.append((0, max_charge))
    for _ in range(T): bounds.append((0, max_dis))
    for _ in range(T): bounds.append((60, cap_storage))
    Aeq=[]; beq=[]
    for t,row in df.iterrows():
        a=np.zeros(n)
        for u in range(U): a[ix_g(t,u)]=1
        a[off_d+t]=1; a[off_c+t]=-1
        Aeq.append(a); beq.append(row["plan_demand_mwh"] + row["planned_network_losses_mwh"])
    for t in range(T):
        a=np.zeros(n); a[off_s+t]=1
        if t>0:
            a[off_s+t-1]=-(1-storage_loss); prev=0
        else:
            prev=(1-storage_loss)*init_soc
        a[off_c+t]=-eta_c; a[off_d+t]=1/eta_d
        Aeq.append(a); beq.append(prev)
    res=linprog(c, A_eq=np.vstack(Aeq), b_eq=np.array(beq), bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError(f"{label}: {res.message}")
    x=res.x
    records=[]
    for t,row in df.iterrows():
        plan_gen={units[u]:float(x[ix_g(t,u)]) for u in range(U)}
        charge=float(x[off_c+t]); discharge=float(x[off_d+t]); soc=float(x[off_s+t])
        actual_loss=float(loss_from_temp(row["planned_supply_temp_c"], row["temperature_c"]))
        actual_need=float(row["heat_demand_mwh"] + actual_loss + charge - discharge)
        actual_gen=dict(plan_gen)
        planned_prod=sum(actual_gen.values())
        adjustment=actual_need-planned_prod
        if adjustment > 1e-9:
            for sid in sorted(units, key=lambda s: production_unit_cost(source_by_id[s], row["price_pln_per_mwh"])):
                room=float(source_by_id[sid]["available_capacity_mwt"])-actual_gen[sid]
                add=min(room, adjustment)
                if add>0:
                    actual_gen[sid]+=add; adjustment-=add
                if adjustment <= 1e-9:
                    break
            if adjustment > 1e-6:
                actual_gen["SRC-BOILER-OIL-04"] += adjustment
                adjustment=0.0
        elif adjustment < -1e-9:
            surplus=-adjustment
            for sid in sorted(units, key=lambda s: production_unit_cost(source_by_id[s], row["price_pln_per_mwh"]), reverse=True):
                red=min(actual_gen[sid], surplus)
                if red>0:
                    actual_gen[sid]-=red; surplus-=red
                if surplus <= 1e-9:
                    break
            adjustment=-surplus
        prod=sum(actual_gen.values())
        residual=prod + discharge - charge - row["heat_demand_mwh"] - actual_loss
        fuel, em, elec = fuel_and_emissions(actual_gen)
        rec={
            "scenario": label,
            "local_timestamp": row["local_timestamp"],
            "heat_demand_mwh": row["heat_demand_mwh"],
            "plan_demand_mwh": row["plan_demand_mwh"],
            "forecast_error_mwh": row["heat_demand_mwh"] - row["plan_demand_mwh"],
            "baseline_network_losses_mwh": row["baseline_network_losses_mwh"],
            "optimized_network_losses_mwh": actual_loss,
            "planned_network_losses_mwh": row["planned_network_losses_mwh"],
            "baseline_supply_temp_c": row["baseline_supply_temp_c"],
            "optimized_supply_temp_c": row["planned_supply_temp_c"],
            "charge_mwh": charge,
            "discharge_mwh": discharge,
            "soc_mwh": soc,
            "optimized_production_mwh": prod,
            "fuel_energy_mwh": fuel,
            "emissions_tco2": em,
            "electricity_generation_mwh": elec,
            "balance_residual_mwh": residual,
            "price_pln_per_mwh": row["price_pln_per_mwh"],
        }
        rec.update({"gen_"+k:v for k,v in actual_gen.items()})
        records.append(rec)
    out=pd.DataFrame(records)
    for col in out.columns:
        if col not in ["scenario","local_timestamp"]: out[col]=pd.to_numeric(out[col]).round(6)
    return out

# CELL
base_src=src_tel[(src_tel["ts"] >= start) & (src_tel["ts"] <= end)]
base_prod=base_src["heat_production_mwh"].sum()
base_fuel=base_src["fuel_energy_mwh"].sum()
base_em=base_src["emissions_tco2"].sum()
base_elec=base_src["electricity_generation_mwh"].sum()
base_peak_oil=base_src[base_src["heat_source_id"]=="SRC-BOILER-OIL-04"]["heat_production_mwh"].sum()
base_losses=window["baseline_network_losses_mwh"].sum()

cases = {
    "model_forecast_full": optimize_plan("model_forecast_full", "forecast_mwh", "forecast_temperature_c", True, True),
    "model_forecast_merit_only": optimize_plan("model_forecast_merit_only", "forecast_mwh", "forecast_temperature_c", False, False),
    "model_forecast_merit_storage": optimize_plan("model_forecast_merit_storage", "forecast_mwh", "forecast_temperature_c", True, False),
    "naive_forecast_full": optimize_plan("naive_forecast_full", "baseline_forecast_mwh", "forecast_temperature_c", True, True),
    "perfect_forecast_full": optimize_plan("perfect_forecast_full", "heat_demand_mwh", "temperature_c", True, True),
}

# The headline plan is based on model forecast, not perfect realization.
opt = cases["model_forecast_full"].copy()
opt.to_csv(DERIVED / "optimization_results_hourly.csv", index=False)
pd.concat(cases.values(), ignore_index=True).to_csv(DERIVED / "optimization_sensitivity_hourly.csv", index=False)

# CELL
def summarize_case(label, df):
    opt_fuel=df["fuel_energy_mwh"].sum(); opt_em=df["emissions_tco2"].sum(); opt_prod=df["optimized_production_mwh"].sum()
    opt_losses=df["optimized_network_losses_mwh"].sum(); opt_elec=df["electricity_generation_mwh"].sum(); opt_oil=df["gen_SRC-BOILER-OIL-04"].sum()
    return {
        "scenario": label,
        "baseline_fuel_energy_mwh": round(base_fuel,3),
        "optimized_fuel_energy_mwh": round(opt_fuel,3),
        "fuel_saved_mwh": round(base_fuel-opt_fuel,3),
        "baseline_emissions_tco2": round(base_em,3),
        "optimized_emissions_tco2": round(opt_em,3),
        "emissions_saved_tco2": round(base_em-opt_em,3),
        "baseline_production_mwh": round(base_prod,3),
        "optimized_production_mwh": round(opt_prod,3),
        "production_reduction_mwh": round(base_prod-opt_prod,3),
        "baseline_network_losses_mwh": round(base_losses,3),
        "optimized_network_losses_mwh": round(opt_losses,3),
        "losses_reduced_mwh": round(base_losses-opt_losses,3),
        "baseline_peak_oil_mwh": round(base_peak_oil,3),
        "optimized_peak_oil_mwh": round(opt_oil,3),
        "peak_oil_reduction_pct": round((base_peak_oil-opt_oil)/base_peak_oil*100,3) if base_peak_oil else 0,
        "baseline_chp_electricity_mwh": round(base_elec,3),
        "optimized_chp_electricity_mwh": round(opt_elec,3),
        "max_abs_balance_residual_mwh": round(float(df["balance_residual_mwh"].abs().max()),8),
        "min_storage_soc_mwh": round(df["soc_mwh"].min(),3),
        "max_storage_soc_mwh": round(df["soc_mwh"].max(),3),
        "mean_abs_forecast_error_mwh": round(df["forecast_error_mwh"].abs().mean(),3),
    }

sensitivity = pd.DataFrame([summarize_case(k,v) for k,v in cases.items()])
sensitivity.to_csv(DERIVED / "optimization_sensitivity_summary.csv", index=False)
main = sensitivity[sensitivity["scenario"]=="model_forecast_full"].iloc[0].to_dict()
summary = pd.DataFrame([{**main,
    "window_start": opt["local_timestamp"].min(), "window_end": opt["local_timestamp"].max(), "hours": len(opt),
    "production_reduction_pct": round((base_prod-main["optimized_production_mwh"])/base_prod*100,3),
    "losses_reduced_pct": round((base_losses-main["optimized_network_losses_mwh"])/base_losses*100,3),
    "fuel_saved_pct": round((base_fuel-main["optimized_fuel_energy_mwh"])/base_fuel*100,3),
    "emissions_saved_pct": round((base_em-main["optimized_emissions_tco2"])/base_em*100,3),
}])
summary.to_csv(DERIVED / "optimization_summary.csv", index=False)

merit = sensitivity.loc[sensitivity.scenario=="model_forecast_merit_only", "fuel_saved_mwh"].iloc[0]
merit_storage = sensitivity.loc[sensitivity.scenario=="model_forecast_merit_storage", "fuel_saved_mwh"].iloc[0]
full = sensitivity.loc[sensitivity.scenario=="model_forecast_full", "fuel_saved_mwh"].iloc[0]
naive = sensitivity.loc[sensitivity.scenario=="naive_forecast_full", "fuel_saved_mwh"].iloc[0]
perfect = sensitivity.loc[sensitivity.scenario=="perfect_forecast_full", "fuel_saved_mwh"].iloc[0]
attribution = pd.DataFrame([
    {"benefit_source":"source_merit_order", "fuel_saved_mwh":round(merit,3), "method":"legacy baseline vs optimized source order; no storage and no supply-temperature optimization"},
    {"benefit_source":"thermal_storage", "fuel_saved_mwh":round(merit_storage-merit,3), "method":"incremental benefit of storage over merit order"},
    {"benefit_source":"supply_temperature_losses", "fuel_saved_mwh":round(full-merit_storage,3), "method":"incremental benefit of lower supply temperature and network-loss reduction"},
    {"benefit_source":"better_forecast_vs_naive", "fuel_saved_mwh":round(full-naive,3), "method":"sensitivity: model forecast full optimizer minus naive baseline forecast full optimizer; not additive with rows above"},
    {"benefit_source":"perfect_forecast_headroom", "fuel_saved_mwh":round(perfect-full,3), "method":"sensitivity: perfect forecast full optimizer minus model forecast full optimizer; checks information-leakage headroom"},
])
attribution.to_csv(DERIVED / "optimization_benefit_attribution.csv", index=False)
print(summary.T.to_string())
print("\nSensitivity:")
print(sensitivity[["scenario","fuel_saved_mwh","emissions_saved_tco2","max_abs_balance_residual_mwh","mean_abs_forecast_error_mwh"]].to_string(index=False))
print("\nAttribution:")
print(attribution.to_string(index=False))
