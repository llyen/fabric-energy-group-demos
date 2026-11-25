# Fabric notebook: BESS/ESP storage optimization
# CELL
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
TZ = "Europe/Warsaw"
D0 = pd.Timestamp("2026-06-18 00:00", tz=TZ)
START = D0 - pd.Timedelta(days=2)
END = D0 + pd.Timedelta(days=2, hours=23, minutes=45)

# CELL
market = pd.read_csv(DATA / "market_prices.csv", parse_dates=["event_timestamp_utc"])
gen = pd.read_csv(DATA / "generation_assets.csv", parse_dates=["event_timestamp_utc"])
storage_assets = pd.read_csv(DATA / "storage_assets.csv")
market["event_timestamp_utc"] = pd.to_datetime(market["event_timestamp_utc"], utc=True)
gen["event_timestamp_utc"] = pd.to_datetime(gen["event_timestamp_utc"], utc=True)
market["local_time"] = market["event_timestamp_utc"].dt.tz_convert(TZ)
gen["local_time"] = gen["event_timestamp_utc"].dt.tz_convert(TZ)
rdn = market[(market["market"] == "RDN") & (market["local_time"] >= START) & (market["local_time"] <= END)][["event_timestamp_utc", "local_time", "price_pln_per_mwh"]].copy()
curtail = gen[(gen["local_time"] >= START) & (gen["local_time"] <= END)].groupby("event_timestamp_utc", as_index=False)["curtailed_energy_mwh"].sum()
df = rdn.merge(curtail, on="event_timestamp_utc", how="left").fillna({"curtailed_energy_mwh": 0})

# CELL
def optimize_one(asset: dict, price: pd.Series, curtailed: pd.Series) -> pd.DataFrame:
    sid = asset["storage_id"]
    stype = asset["storage_type"]
    cap = float(asset["energy_capacity_mwh"])
    soc = float(asset["initial_soc_mwh"])
    eff = float(asset["round_trip_efficiency"])
    charge_eff = eff ** 0.5
    discharge_eff = eff ** 0.5
    aux_power_mw = float(asset.get("auxiliary_power_mw", 0.0) or 0.0)
    if stype == "BESS":
        charge_power = float(asset["power_mw"])
        discharge_power = float(asset["power_mw"])
    else:
        charge_power = float(asset["pumping_power_mw"])
        discharge_power = float(asset["generating_power_mw"])
    capture_limit_mw = float(asset.get("curtailment_capture_limit_mw", charge_power) or charge_power)
    low = price.quantile(0.25)
    high = price.quantile(0.75)
    rows = []
    for ts, p, c in zip(df["event_timestamp_utc"], price, curtailed):
        mode = "standby"
        charge_mwh = discharge_mwh = curtailment_captured_mwh = revenue_pln = 0.0
        aux_mwh = aux_power_mw * 0.25
        soc = max(0.0, soc - aux_mwh)
        if (p <= low or p < 0) and soc < cap * 0.92:
            mode = "charging" if stype == "BESS" else "pumping"
            charge_mwh = min(charge_power * 0.25, (cap * 0.92 - soc) / charge_eff)
            # Only part of curtailed energy is electrically reachable by this storage asset.
            curtailment_captured_mwh = min(max(c, 0.0), capture_limit_mw * 0.25, charge_mwh)
            soc += charge_mwh * charge_eff
            revenue_pln = -charge_mwh * p
        elif p >= high and soc > cap * 0.14:
            mode = "discharging" if stype == "BESS" else "generation"
            discharge_mwh = min(discharge_power * 0.25, (soc - cap * 0.10) * discharge_eff)
            soc -= discharge_mwh / discharge_eff
            revenue_pln = discharge_mwh * p
        else:
            soc *= (1 - (0.00001 if stype == "BESS" else 0.00002))
        grid_input_mwh = charge_mwh + aux_mwh
        rows.append({"event_timestamp_utc": ts, "storage_id": sid, "storage_type": stype, "mode": mode, "price_pln_per_mwh": round(float(p), 2), "round_trip_efficiency": eff, "input_mwh": round(grid_input_mwh, 5), "output_mwh": round(discharge_mwh, 5), "net_energy_mwh": round(discharge_mwh - grid_input_mwh, 5), "stored_energy_mwh": round(soc, 5), "auxiliary_consumption_mwh": round(aux_mwh, 5), "curtailment_captured_mwh": round(curtailment_captured_mwh, 5), "arbitrage_revenue_pln_synthetic": round(revenue_pln, 2)})
    return pd.DataFrame(rows)

# CELL
plans = []
for asset in storage_assets.to_dict("records"):
    plans.append(optimize_one(asset, df["price_pln_per_mwh"], df["curtailed_energy_mwh"]))
plan = pd.concat(plans, ignore_index=True)
# Curtailment is a fleet-level pool and not all curtailed energy is electrically reachable.
eligible = df[["event_timestamp_utc", "curtailed_energy_mwh", "price_pln_per_mwh"]].copy()
eligible["eligible_curtailment_mwh"] = eligible["curtailed_energy_mwh"] * 0.62
eligible.loc[eligible["price_pln_per_mwh"] >= 0, "eligible_curtailment_mwh"] = 0.0
raw_by_ts = plan.groupby("event_timestamp_utc")["curtailment_captured_mwh"].sum().rename("raw_capture_mwh")
plan = plan.merge(eligible[["event_timestamp_utc", "eligible_curtailment_mwh"]], on="event_timestamp_utc", how="left").merge(raw_by_ts, on="event_timestamp_utc", how="left")
scale = np.where(plan["raw_capture_mwh"] > 0, np.minimum(1.0, plan["eligible_curtailment_mwh"] / plan["raw_capture_mwh"]), 0.0)
plan["curtailment_captured_mwh"] = plan["curtailment_captured_mwh"] * scale
plan = plan.drop(columns=["eligible_curtailment_mwh", "raw_capture_mwh"])
summary_by_type = plan.groupby("storage_type", as_index=False).agg(
    input_mwh=("input_mwh", "sum"),
    output_mwh=("output_mwh", "sum"),
    captured_curtailment_mwh=("curtailment_captured_mwh", "sum"),
    arbitrage_revenue_pln_synthetic=("arbitrage_revenue_pln_synthetic", "sum"),
    configured_round_trip_efficiency=("round_trip_efficiency", "mean"),
    auxiliary_consumption_mwh=("auxiliary_consumption_mwh", "sum"),
)
summary_by_type["output_input_ratio"] = np.where(summary_by_type["input_mwh"] > 0, summary_by_type["output_mwh"] / summary_by_type["input_mwh"], 0)
summary_by_type = summary_by_type.round({"input_mwh": 3, "output_mwh": 3, "captured_curtailment_mwh": 3, "arbitrage_revenue_pln_synthetic": 2, "configured_round_trip_efficiency": 3, "auxiliary_consumption_mwh": 3, "output_input_ratio": 3})
neg = df[df["price_pln_per_mwh"] < 0]
curtailment_neg = float(neg["curtailed_energy_mwh"].sum())
captured = float(plan["curtailment_captured_mwh"].sum())
summary = {
    "scenario_intervals": int(len(df)),
    "negative_price_intervals": int(len(neg)),
    "curtailment_during_negative_prices_mwh": round(curtailment_neg, 3),
    "curtailment_captured_by_optimized_storage_mwh": round(captured, 3),
    "curtailment_capture_pct": round(100 * captured / curtailment_neg, 2) if curtailment_neg else 0,
    "unserved_curtailment_mwh": round(curtailment_neg - captured, 3),
    "total_arbitrage_revenue_pln_synthetic": round(float(plan["arbitrage_revenue_pln_synthetic"].sum()), 2),
    "storage_by_type": summary_by_type.to_dict("records"),
    "note": "Przychód liczony wyłącznie na syntetycznych cenach RDN scenariusza; nie jest deklaracją oszczędności Contoso Energia.",
}

# CELL
plan.to_csv(DERIVED / "storage_optimization_plan.csv", index=False)
summary_by_type.to_csv(DERIVED / "storage_optimization_by_type.csv", index=False)
(DERIVED / "storage_optimization_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=True, indent=2))
