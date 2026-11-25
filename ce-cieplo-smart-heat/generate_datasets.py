"""Generator danych syntetycznych dla Contoso Energia Ciepło Smart Heat Optimizer.

Dane są w 100% fikcyjne. Scenariusz wiodący: fikcyjne Miasto Alfa, parametry syntetyczne.
Jednostka energii w szeregach: MWh ciepła; przelicznik 1 MWh = 3,6 GJ.
Seed=42, czas Europe/Warsaw z prawidłowym offsetem DST.
"""
from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
rng = np.random.default_rng(SEED)
BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
TZ = "Europe/Warsaw"
CITY = "Miasto Alfa"
D0 = pd.Timestamp("2026-02-10 06:00", tz=TZ)
START = pd.Timestamp("2025-01-01 00:00", tz=TZ)
END = pd.Timestamp("2027-01-01 00:00", tz=TZ)
AS_OF_DATE = "2026-08-21"


def utc_iso(ts: pd.Timestamp) -> str:
    return ts.tz_convert("UTC").isoformat()


def local_iso(ts: pd.Timestamp) -> str:
    return ts.isoformat()


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = fields or list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)


def write_jsonl(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")


def meta(ts: pd.Timestamp, source: str, interval="PT1H", q="good") -> dict:
    return {
        "event_timestamp_utc": utc_iso(ts),
        "local_timezone": TZ,
        "settlement_interval": interval,
        "source_system": source,
        "quality_flag": q,
        "ingestion_timestamp": utc_iso(ts + pd.Timedelta(minutes=7)),
        "data_version": "smart-heat-demo-v1",
    }


def main() -> None:
    DATA.mkdir(exist_ok=True); DERIVED.mkdir(exist_ok=True)
    for old in list(DATA.glob("*.csv")) + list(DATA.glob("*.jsonl")) + list(DERIVED.glob("*.csv")) + list(DERIVED.glob("*.json")) + list(DERIVED.glob("*.jsonl")):
        old.unlink()

    hours = pd.date_range(START, END, freq="h", inclusive="left", tz=TZ)
    source_rows = [
        {"heat_source_id":"SRC-CHP-GAS-01","source_name":"EC Alfa-SH A","source_type":"chp_gas","city":CITY,"installed_capacity_mwt":150,"available_capacity_mwt":138,"electrical_capacity_mwe":72,"min_stable_load_mwt":35,"heat_efficiency_pct":88,"power_to_heat_ratio_mwe_per_mwt":0.46,"fuel_cost_pln_per_mwh_fuel":210,"emission_tco2_per_mwh_fuel":0.202,"variable_om_pln_per_mwh_heat":8,"as_of_date":AS_OF_DATE},
        {"heat_source_id":"SRC-CHP-BIO-02","source_name":"EC Alfa-SH B","source_type":"chp_biomass","city":CITY,"installed_capacity_mwt":80,"available_capacity_mwt":68,"electrical_capacity_mwe":24,"min_stable_load_mwt":14,"heat_efficiency_pct":82,"power_to_heat_ratio_mwe_per_mwt":0.30,"fuel_cost_pln_per_mwh_fuel":145,"emission_tco2_per_mwh_fuel":0.035,"variable_om_pln_per_mwh_heat":11,"as_of_date":AS_OF_DATE},
        {"heat_source_id":"SRC-BOILER-GAS-03","source_name":"Kotly Szczytowe Wschod","source_type":"peak_gas_boiler","city":CITY,"installed_capacity_mwt":205,"available_capacity_mwt":185,"electrical_capacity_mwe":0,"min_stable_load_mwt":0,"heat_efficiency_pct":91,"power_to_heat_ratio_mwe_per_mwt":0,"fuel_cost_pln_per_mwh_fuel":220,"emission_tco2_per_mwh_fuel":0.202,"variable_om_pln_per_mwh_heat":6,"as_of_date":AS_OF_DATE},
                {"heat_source_id":"SRC-BOILER-OIL-04","source_name":"Kotly Rezerwowe Poludnie","source_type":"reserve_oil_boiler","city":CITY,"installed_capacity_mwt":145,"available_capacity_mwt":130,"electrical_capacity_mwe":0,"min_stable_load_mwt":0,"heat_efficiency_pct":88,"power_to_heat_ratio_mwe_per_mwt":0,"fuel_cost_pln_per_mwh_fuel":360,"emission_tco2_per_mwh_fuel":0.267,"variable_om_pln_per_mwh_heat":9,"as_of_date":AS_OF_DATE},
    ]
    write_csv(DATA / "heat_sources.csv", source_rows)
    storage = [{"storage_id":"TES-ALF-01","storage_name":"Akumulator Ciepla Rzeczna-SH","city":CITY,"energy_capacity_mwh":720,"max_charge_mwt":75,"max_discharge_mwt":75,"charge_efficiency_pct":96,"discharge_efficiency_pct":96,"standing_loss_pct_per_hour":0.045,"initial_soc_mwh":360,"as_of_date":AS_OF_DATE}]
    write_csv(DATA / "thermal_storage.csv", storage)
    segments=[]
    for i, length in enumerate([2.8,3.6,4.1,5.4,6.7,7.9,3.2,4.9,5.8,6.3,2.5,7.1],1):
        segments.append({"network_segment_id":f"NET-ALF-{i:02d}","segment_name":f"Odcinek SH-{i:02d}","from_node_id":f"HN-{max(1,i-1):03d}","to_node_id":f"HN-{i:03d}","length_km":length,"pipe_diameter_mm":int(rng.choice([350,450,500,600,700,800])),"insulation_class":rng.choice(["A","B","C"]),"heat_loss_coeff_mwh_per_km_h_c":round(float(rng.uniform(0.0011,0.0024)),5),"transport_time_h":round(length / float(rng.uniform(2.0,3.8)),2),"as_of_date":AS_OF_DATE})
    write_csv(DATA / "network_segments.csv", segments)
    nodes=[]
    districts=["Polnoc","Poludnie","Wschod","Zachod","Centrum","Przemyslowa","Parkowa","Lesna","Ogrodowa","Rzeczna","Nowe Osiedle","Stare Miasto"]
    for i,d in enumerate(districts,1):
        nodes.append({"heat_node_id":f"HN-{i:03d}","node_name":f"Wezel {d}-SH","district":d,"city":CITY,"node_type":rng.choice(["distribution","exchange","monitoring"]),"design_supply_temp_c":110,"design_return_temp_c":60,"transport_delay_h":round(float(rng.uniform(0.8,3.7)),2),"as_of_date":AS_OF_DATE})
    write_csv(DATA / "heat_nodes.csv", nodes)
    customers=[]
    for i,d in enumerate(districts,1):
        customers.append({"customer_zone_id":f"CZ-{i:03d}","heat_node_id":f"HN-{i:03d}","zone_name":f"Strefa {d}-SH","customer_mix":rng.choice(["residential","mixed","public_services"]),"heated_area_thousand_m2":round(float(rng.uniform(260,780)),1),"dhw_share_pct":round(float(rng.uniform(12,22)),1),"comfort_min_temp_c":20.0,"as_of_date":AS_OF_DATE})
    write_csv(DATA / "customer_zones.csv", customers)

    weather=[]; weather_forecast=[]; prices=[]; demand=[]
    inertia_temp = -1.0
    forecast_inertia_temp = -1.0
    lagged_demands=[]
    behavior_state = 0.0
    forecast_temp_bias = 0.0
    for idx, ts in enumerate(hours):
        day_of_year = ts.dayofyear
        hour = ts.hour
        season = math.cos(2*math.pi*(day_of_year-15)/365.25)
        cold_wave = -11.5 * math.exp(-(((ts - D0).total_seconds()/3600)/44)**2)
        temp = 6 - 13*season + cold_wave + 2.5*math.sin(2*math.pi*(hour-14)/24) + rng.normal(0,1.0)
        inertia_temp = 0.88*inertia_temp + 0.12*temp
        wind = max(0.5, rng.normal(12 + 7*season + (5 if abs((ts-D0).total_seconds()/3600)<70 else 0), 4))
        solar = max(0, math.sin(math.pi*(hour-6)/12)) * max(0.18, -season+0.7) * rng.uniform(120,620)
        forecast_temp_bias = 0.82*forecast_temp_bias + rng.normal(0, 0.45)
        forecast_temp = temp + forecast_temp_bias + rng.normal(0, 2.6)
        forecast_wind = max(0.5, wind + rng.normal(0, 6.5))
        forecast_solar = max(0, solar * rng.normal(1.0, 0.32) + rng.normal(0, 60))
        forecast_inertia_temp = 0.86*forecast_inertia_temp + 0.14*forecast_temp
        is_weekend = ts.weekday()>=5
        behavior_state = 0.90*behavior_state + rng.normal(0, 7.5)
        dhw = 28 + 8*math.sin(2*math.pi*(hour-7)/24)**2 + (4 if is_weekend else 0) + rng.normal(0, 7.0)
        if rng.random() < 0.018:
            dhw += rng.choice([-1, 1]) * rng.uniform(10, 28)
        dhw = max(12, dhw)
        degree = max(0, 16 - inertia_temp)
        wind_chill_extra = max(0, wind - 18) * rng.uniform(0.25, 0.65)
        solar_gain_variability = -0.018*solar + rng.normal(0, max(1.5, solar/120))
        demand_raw = 62 + 10.8*degree + 0.9*wind + wind_chill_extra + dhw + solar_gain_variability + behavior_state + (12 if hour in [6,7,8,17,18,19] else 0) + rng.normal(0,12)
        demand_mwh = max(55, demand_raw)
        if idx>0:
            demand_mwh = 0.58*(lagged_demands[-1]) + 0.42*demand_mwh + rng.normal(0, 5.5)
        lagged_demands.append(demand_mwh)
        price = 350 + 95*math.sin(2*math.pi*(hour-17)/24) + 70*season - 0.23*solar + rng.normal(0,35)
        if 10 <= hour <= 14 and solar > 430 and rng.random()<0.18:
            price -= rng.uniform(280,520)
        weather.append({**meta(ts,"weather_api"),"local_timestamp":local_iso(ts),"city":CITY,"temperature_c":round(temp,2),"inertia_temperature_c":round(inertia_temp,2),"wind_kmh":round(wind,2),"solar_irradiance_w_m2":round(solar,2),"is_frost_wave":abs((ts-D0).total_seconds()/3600)<=84})
        weather_forecast.append({**meta(ts - pd.Timedelta(hours=6),"weather_forecast_api"),"forecast_issue_local_timestamp":local_iso(ts - pd.Timedelta(hours=6)),"target_local_timestamp":local_iso(ts),"forecast_horizon_h":6,"city":CITY,"forecast_temperature_c":round(forecast_temp,2),"forecast_inertia_temperature_c":round(forecast_inertia_temp,2),"forecast_wind_kmh":round(forecast_wind,2),"forecast_solar_irradiance_w_m2":round(forecast_solar,2),"is_frost_wave_forecast":abs((ts-D0).total_seconds()/3600)<=84})
        prices.append({**meta(ts,"market_data"),"local_timestamp":local_iso(ts),"market":"RDN","price_pln_per_mwh":round(price,2),"volume_mwh":round(float(rng.uniform(1400,3600)),1),"balancing_area":"PL","pob_id":"POB-SH-SYN","settlement_status":"final"})
        demand.append({**meta(ts,"billing_heat_metering"),"local_timestamp":local_iso(ts),"city":CITY,"heat_demand_mwh":round(demand_mwh,3),"dhw_demand_mwh":round(dhw,3),"space_heating_mwh":round(max(0,demand_mwh-dhw),3),"weighted_transport_time_h":round(float(np.average([s["transport_time_h"] for s in segments], weights=[s["length_km"] for s in segments])),2)})
    write_jsonl(DATA / "weather_hourly.jsonl", weather)
    write_jsonl(DATA / "weather_forecast_hourly.jsonl", weather_forecast)
    write_jsonl(DATA / "electricity_prices_hourly.jsonl", prices)
    write_jsonl(DATA / "heat_demand_hourly.jsonl", demand)

    # Baseline dispatch and telemetry.
    demand_by_ts = {r["local_timestamp"]: r["heat_demand_mwh"] for r in demand}
    temp_by_ts = {r["local_timestamp"]: r["temperature_c"] for r in weather}
    price_by_ts = {r["local_timestamp"]: r["price_pln_per_mwh"] for r in prices}
    soc=360.0
    telemetry=[]; storage_events=[]; network_rows=[]
    src_caps={r["heat_source_id"]:r for r in source_rows}
    for ts in hours:
        key=local_iso(ts); dem=demand_by_ts[key]; temp=temp_by_ts[key]
        supply_temp=92 + max(0, -temp)*0.85 + (4 if dem>235 else 0)
        total_loss_coeff=sum(s["length_km"]*s["heat_loss_coeff_mwh_per_km_h_c"] for s in segments)
        losses=max(6, total_loss_coeff*(supply_temp-temp)*1.08)
        price=price_by_ts[key]
        cold=abs((ts-D0).total_seconds()/3600)<96
        target_soc=610 if cold and ts < D0 else 260
        charge=0.0; discharge=0.0
        if soc < target_soc and dem < 245 and price > 260:
            charge=min(45, target_soc-soc)
        if dem > 270 and soc > 120:
            discharge=min(55, dem-250, (soc-80)*0.96)
        required=dem+losses+charge-discharge
        remaining=required
        gen={sid:0.0 for sid in src_caps}
        order=["SRC-CHP-BIO-02","SRC-CHP-GAS-01","SRC-BOILER-GAS-03","SRC-BOILER-OIL-04"] if price>120 else ["SRC-BOILER-GAS-03","SRC-CHP-BIO-02","SRC-CHP-GAS-01","SRC-BOILER-OIL-04"]
        for sid in order:
            cap=src_caps[sid]["available_capacity_mwt"]
            val=min(cap, max(0, remaining)); gen[sid]=val; remaining-=val
        if remaining>0:
            gen["SRC-BOILER-OIL-04"] += remaining
        prev_soc=soc
        soc=max(0,min(720, soc + charge*0.96 - discharge/0.96 - soc*0.00045))
        storage_events.append({**meta(ts,"scada_historian"),"local_timestamp":key,"storage_id":"TES-ALF-01","charge_mwh":round(charge,3),"discharge_mwh":round(discharge,3),"soc_mwh":round(soc,3),"standing_loss_mwh":round(prev_soc*0.00045,3),"roundtrip_efficiency_pct":92.16})
        prod=sum(gen.values())
        residual=prod-(dem+losses+charge-discharge)
        for sid,g in gen.items():
            src=src_caps[sid]; electric=g*src["power_to_heat_ratio_mwe_per_mwt"]
            fuel=g/(src["heat_efficiency_pct"]/100) if src["heat_efficiency_pct"] else 0
            telemetry.append({**meta(ts,"scada_historian"),"local_timestamp":key,"heat_source_id":sid,"heat_production_mwh":round(g,3),"electricity_generation_mwh":round(electric,3),"fuel_energy_mwh":round(fuel,3),"emissions_tco2":round(fuel*src["emission_tco2_per_mwh_fuel"],4),"operating_mode":"chp" if src["electrical_capacity_mwe"]>0 and g>0 else "heat_only" if g>0 else "standby","supply_temp_c":round(supply_temp,2),"return_temp_c":round(supply_temp-38-rng.normal(0,1.2),2),"balance_residual_mwh":round(residual,6)})
        for s in segments:
            seg_loss=losses*(s["length_km"]*s["heat_loss_coeff_mwh_per_km_h_c"])/total_loss_coeff
            network_rows.append({**meta(ts,"scada_historian"),"local_timestamp":key,"network_segment_id":s["network_segment_id"],"supply_temp_c":round(supply_temp-rng.uniform(0,2.5),2),"return_temp_c":round(supply_temp-38-rng.uniform(0,2.5),2),"ambient_temp_c":round(temp,2),"heat_loss_mwh":round(seg_loss,5),"flow_m3_h":round(float(rng.uniform(900,2200)),1),"pressure_bar":round(float(rng.uniform(5.5,9.5)),2)})
    write_jsonl(DATA / "source_telemetry_hourly.jsonl", telemetry)
    write_jsonl(DATA / "storage_telemetry_hourly.jsonl", storage_events)
    write_jsonl(DATA / "network_telemetry_hourly.jsonl", network_rows)

    metadata={"scenario":"Contoso Energia Cieplo S.A. — Smart Heat Optimizer","city":CITY,"synthetic":True,"seed":SEED,"d0":local_iso(D0),"period_start":local_iso(START),"period_end_exclusive":local_iso(END),"energy_unit":"MWh heat","conversion":"1 MWh = 3.6 GJ","forecast_horizon_h":6,"notes":"Nazwy aktywów i parametry są syntetyczne; nie są danymi Contoso Energia Ciepło. Prognoza popytu używa prognozy pogody z błędem, nie pomiaru z przyszłości."}
    (DATA / "dataset_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    dq={"rows_weather":len(weather),"rows_weather_forecast":len(weather_forecast),"rows_prices":len(prices),"rows_demand":len(demand),"rows_source_telemetry":len(telemetry),"rows_storage_telemetry":len(storage_events),"rows_network_telemetry":len(network_rows),"dst_hours_total":len(hours),"max_abs_balance_residual_mwh":max(abs(r["balance_residual_mwh"]) for r in telemetry),"negative_price_hours":sum(1 for r in prices if r["price_pln_per_mwh"]<0)}
    pd.DataFrame([dq]).to_csv(DERIVED / "data_quality_checks.csv", index=False)
    print(json.dumps(dq, ensure_ascii=False))

if __name__ == "__main__":
    main()
