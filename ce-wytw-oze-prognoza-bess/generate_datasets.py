"""Generate deterministic synthetic data for Contoso Energia Wytwarzanie OZE-BESS-ESP demo.

All data is synthetic. It is not operational, commercial, metering or asset data of Contoso Energia.
Seed=42. Time axis covers 2025-01-01..2026-12-31 in Europe/Warsaw at 15-minute grain.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
rng = np.random.default_rng(SEED)
BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DATA.mkdir(exist_ok=True)
DERIVED.mkdir(exist_ok=True)
TZ = ZoneInfo("Europe/Warsaw")
START_LOCAL = pd.Timestamp("2025-01-01 00:00", tz=TZ)
END_LOCAL = pd.Timestamp("2026-12-31 23:45", tz=TZ)
D0 = pd.Timestamp("2026-06-18 00:00", tz=TZ)
SCENARIO_START = D0 - pd.Timedelta(days=2)
SCENARIO_END = D0 + pd.Timedelta(days=2, hours=23, minutes=45)


def clamp_array(a, lo, hi):
    return np.minimum(np.maximum(a, lo), hi)


def solar_factor(index: pd.DatetimeIndex, lat: float, lon: float) -> np.ndarray:
    day = index.dayofyear.to_numpy()
    hour = index.hour.to_numpy() + index.minute.to_numpy() / 60
    decl = np.deg2rad(23.44 * np.sin(np.deg2rad(360 * (284 + day) / 365)))
    lat_r = math.radians(lat)
    solar_noon = 12 - (lon - 19.0) / 15
    h_angle = np.deg2rad(15 * (hour - solar_noon))
    sin_elev = np.sin(lat_r) * np.sin(decl) + np.cos(lat_r) * np.cos(decl) * np.cos(h_angle)
    return np.maximum(0.0, sin_elev) ** 1.35


def wind_pf(speed):
    speed = np.asarray(speed)
    pf = np.zeros_like(speed, dtype=float)
    mask = (speed >= 3.0) & (speed < 12.0)
    pf[mask] = ((speed[mask] - 3.0) / 9.0) ** 3
    pf[(speed >= 12.0) & (speed < 25.0)] = 1.0
    return pf


def add_common(df: pd.DataFrame, index: pd.DatetimeIndex, source: str, version="v2026_15m", interval="PT15M") -> pd.DataFrame:
    utc = index.tz_convert("UTC")
    df.insert(0, "event_timestamp_utc", utc.astype(str))
    df.insert(1, "local_timezone", "Europe/Warsaw")
    df.insert(2, "settlement_interval", interval)
    df.insert(3, "source_system", source)
    df.insert(4, "quality_flag", rng.choice(["good", "estimated", "suspect"], size=len(df), p=[0.982, 0.013, 0.005]))
    df.insert(5, "ingestion_timestamp", (utc + pd.to_timedelta(rng.integers(1, 7, len(df)), unit="m")).astype(str))
    df.insert(6, "data_version", version)
    return df


assets = pd.DataFrame([
    {"asset_id":"WF-01","asset_name":"FW Alfa","asset_type":"wind","lat":52.90,"lon":19.60,"installed_capacity_mw":96,"hub_height_m":120},
    {"asset_id":"WF-02","asset_name":"FW Beta","asset_type":"wind","lat":53.10,"lon":18.70,"installed_capacity_mw":72,"hub_height_m":115},
    {"asset_id":"WF-03","asset_name":"FW Gamma","asset_type":"wind","lat":52.60,"lon":20.40,"installed_capacity_mw":64,"hub_height_m":110},
    {"asset_id":"WF-04","asset_name":"FW Delta","asset_type":"wind","lat":53.30,"lon":17.90,"installed_capacity_mw":88,"hub_height_m":125},
    {"asset_id":"PV-ZCH-001","asset_name":"PV Zachodnia","asset_type":"pv","lat":52.10,"lon":15.80,"installed_capacity_mw":58,"hub_height_m":""},
    {"asset_id":"PV-PLD-002","asset_name":"PV Południowa","asset_type":"pv","lat":50.75,"lon":16.95,"installed_capacity_mw":42,"hub_height_m":""},
    {"asset_id":"PV-CEN-003","asset_name":"PV Centralna","asset_type":"pv","lat":52.55,"lon":19.10,"installed_capacity_mw":52,"hub_height_m":""},
    {"asset_id":"PV-WYZ-004","asset_name":"PV Wyżynna","asset_type":"pv","lat":50.55,"lon":18.20,"installed_capacity_mw":36,"hub_height_m":""},
    {"asset_id":"ROR-GOR-001","asset_name":"EW Przeplywowa Gorska","asset_type":"run_of_river","lat":49.80,"lon":19.10,"installed_capacity_mw":28,"hub_height_m":""},
    {"asset_id":"ROR-NIZ-002","asset_name":"EW Przeplywowa Nizinna","asset_type":"run_of_river","lat":52.70,"lon":17.40,"installed_capacity_mw":18,"hub_height_m":""},
])
storage_assets = pd.DataFrame([
    {"storage_id":"BESS-001","storage_name":"BESS Farma Centralna","storage_type":"BESS","power_mw":80,"energy_capacity_mwh":320,"round_trip_efficiency":0.88,"initial_soc_mwh":80,"auxiliary_power_mw":0.80,"curtailment_capture_limit_mw":6,"generating_power_mw":"","pumping_power_mw":""},
    {"storage_id":"BESS-002","storage_name":"BESS Farma Północ","storage_type":"BESS","power_mw":50,"energy_capacity_mwh":200,"round_trip_efficiency":0.88,"initial_soc_mwh":50,"auxiliary_power_mw":0.50,"curtailment_capture_limit_mw":4,"generating_power_mw":"","pumping_power_mw":""},
    {"storage_id":"ESP-01","storage_name":"ESP-01","storage_type":"ESP","power_mw":"","energy_capacity_mwh":850,"round_trip_efficiency":0.75,"initial_soc_mwh":210,"auxiliary_power_mw":0.75,"curtailment_capture_limit_mw":6,"generating_power_mw":140,"pumping_power_mw":152},
])
assets.to_csv(DATA / "assets.csv", index=False)
storage_assets.to_csv(DATA / "storage_assets.csv", index=False)

idx = pd.date_range(START_LOCAL, END_LOCAL, freq="15min")
n = len(idx)
local = idx
hours = local.hour.to_numpy() + local.minute.to_numpy() / 60
doy = local.dayofyear.to_numpy()
event_hours = (idx - D0).total_seconds().to_numpy() / 3600
seasonal = np.sin(2 * np.pi * (doy - 80) / 365)
wind_noise = rng.normal(0, 1, n)
cloud_noise = rng.normal(0, 1, n)
for i in range(1, n):
    wind_noise[i] = 0.94 * wind_noise[i-1] + 0.34 * wind_noise[i]
    cloud_noise[i] = 0.90 * cloud_noise[i-1] + 0.44 * cloud_noise[i]
wind_noise = (wind_noise - wind_noise.mean()) / wind_noise.std()
cloud_noise = (cloud_noise - cloud_noise.min()) / (cloud_noise.max() - cloud_noise.min())
wind_drop = np.where(np.abs(event_hours) < 72, 0.48 * np.exp(-((event_hours - 16) / 10) ** 2), 0)
cloud = clamp_array(0.28 + 0.42 * cloud_noise - 0.18 * seasonal + rng.normal(0, 0.04, n), 0.02, 0.96)
temp_c = 9 + 11 * seasonal + 5 * np.sin(2 * np.pi * (hours - 7) / 24) + rng.normal(0, 2, n)
wind_ref = clamp_array(4.9 + 1.7 * wind_noise + 0.7 * (1 - seasonal) - 3.2 * wind_drop, 0.4, 24.0)
scenario = (idx >= SCENARIO_START) & (idx <= SCENARIO_END)
noon_event = scenario & (hours >= 10) & (hours < 15)
forecast_wind_error = rng.normal(0, 1.15, n)
forecast_cloud_error = rng.normal(0, 11.0, n)
for i in range(1, n):
    forecast_wind_error[i] = 0.88 * forecast_wind_error[i-1] + 0.48 * forecast_wind_error[i]
    forecast_cloud_error[i] = 0.84 * forecast_cloud_error[i-1] + 0.55 * forecast_cloud_error[i]
forecast_wind = clamp_array(wind_ref + forecast_wind_error + 1.7 * wind_drop, 0.4, 24.0)
forecast_cloud = clamp_array(cloud * 100 + forecast_cloud_error - 6.0 * noon_event.astype(float), 0, 100)
forecast_temp = temp_c + rng.normal(0, 1.8, n)
weather = pd.DataFrame({"wind_speed_10m_ms":np.round(wind_ref,3),"cloud_cover_pct":np.round(cloud*100,2),"temperature_c":np.round(temp_c,2),"forecast_wind_speed_10m_ms":np.round(forecast_wind,3),"forecast_cloud_cover_pct":np.round(forecast_cloud,2),"forecast_temperature_c":np.round(forecast_temp,2),"forecast_horizon":"D-1 synthetic forecast","scenario_marker":np.where(scenario,"D0_wind_drop_negative_prices","seasonal_history")})
weather = add_common(weather, idx, "Prognozy meteo / modele numeryczne", "meteo_v1")
weather.to_csv(DATA / "weather_features.csv", index=False)

gen_frames = []
tele_frames = []
for _, a in assets.iterrows():
    cap = float(a.installed_capacity_mw)
    if a.asset_type == "wind":
        speed_hub = wind_ref * (float(a.hub_height_m) / 10.0) ** 0.14 * rng.normal(1.0, 0.035, n)
        available = cap * wind_pf(speed_hub)
        available_capacity = cap * rng.uniform(0.93, 1.0, n)
        source = "SCADA turbin (IEC 61400-25)"
        solar = np.full(n, np.nan); flow = np.full(n, np.nan); cloud_pct = np.full(n, np.nan)
    elif a.asset_type == "pv":
        solar = solar_factor(idx, float(a.lat), float(a.lon))
        solar = np.where((hours < 4) | (hours >= 22), 0.0, solar)
        available = cap * solar * (1 - 0.78 * cloud) * (1 - np.maximum(0, temp_c - 25) * 0.004) * rng.normal(0.985, 0.018, n)
        available = np.maximum(0, available)
        available_capacity = cap * rng.uniform(0.96, 1.0, n)
        speed_hub = np.full(n, np.nan); flow = np.full(n, np.nan); cloud_pct = cloud * 100
        source = "SCADA PV"
    else:
        flow = clamp_array(0.42 + 0.22 * np.sin(2 * np.pi * (doy - 35) / 365) + rng.normal(0, 0.035, n), 0.16, 0.88)
        available = cap * flow
        available_capacity = cap * rng.uniform(0.88, 0.98, n)
        speed_hub = np.full(n, np.nan); solar = np.full(n, np.nan); cloud_pct = np.full(n, np.nan)
        source = "SCADA hydro przeplywowe"
    available = np.minimum(available, available_capacity)
    curtail_ratio = np.zeros(n)
    reason = np.array(["none"] * n, dtype=object)
    if a.asset_type in {"pv", "wind"}:
        curtail_ratio = np.where(noon_event & (available > 2), clamp_array(0.08 + 0.18 * np.nan_to_num(solar, nan=0.35) + rng.normal(0, 0.025, n), 0, 0.34), 0)
        random_curt = rng.random(n) < 0.004
        curtail_ratio = np.where((curtail_ratio == 0) & random_curt & (available > 0), rng.uniform(0.02, 0.09, n), curtail_ratio)
        reason = np.where(curtail_ratio > 0.09, "negative_price_and_grid_constraint", np.where(curtail_ratio > 0, "local_grid_constraint", "none"))
    curtailed = available * curtail_ratio * 0.25
    scheduled = available * (1 - curtail_ratio) * rng.uniform(0.985, 1.005, n)
    actual = np.maximum(0, np.minimum(available - curtailed / 0.25, scheduled * rng.normal(1.0, 0.014, n)))
    df = pd.DataFrame({"asset_id":a.asset_id,"asset_type":a.asset_type,"installed_capacity_mw":round(cap,3),"available_capacity_mw":np.round(available_capacity,3),"available_generation_mw":np.round(available,4),"scheduled_generation_mw":np.round(scheduled,4),"actual_generation_mw":np.round(actual,4),"actual_generation_mwh":np.round(actual*0.25,5),"curtailed_energy_mwh":np.round(curtailed,5),"curtailment_reason":reason,"wind_speed_hub_ms":np.round(speed_hub,3),"solar_position_factor":np.round(solar,5),"cloud_cover_pct":np.round(cloud_pct,2),"hydro_flow_index":np.round(flow,4),"scenario_marker":np.where(scenario,"D0_wind_drop_negative_prices","seasonal_history")})
    df = add_common(df, idx, source)
    gen_frames.append(df)
    if a.asset_type in {"wind", "pv"}:
        tel = df.loc[scenario, ["event_timestamp_utc","local_timezone","settlement_interval","source_system","quality_flag","ingestion_timestamp","data_version","asset_id"]].copy()
        tel["telemetry_type"] = a.asset_type
        tel["active_power_mw"] = df.loc[scenario, "actual_generation_mw"].to_numpy()
        tel["available_power_mw"] = df.loc[scenario, "available_generation_mw"].to_numpy()
        tel["status_code"] = np.where(df.loc[scenario, "curtailment_reason"].to_numpy() != "none", "limited", "ok")
        tel["alarm_code"] = np.where(tel["status_code"] == "limited", "CURTAILMENT", "")
        tele_frames.append(tel)

gen = pd.concat(gen_frames, ignore_index=True)
gen.to_csv(DATA / "generation_assets.csv", index=False)
tele = pd.concat(tele_frames, ignore_index=True)
with (DATA / "realtime_telemetry.jsonl").open("w", encoding="utf-8") as f:
    for rec in tele.to_dict("records"):
        f.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")

fleet = gen.groupby("event_timestamp_utc", as_index=False).agg(available_generation_mw=("available_generation_mw","sum"), actual_generation_mw=("actual_generation_mw","sum"))
fleet_av = fleet["available_generation_mw"].to_numpy()
pv_av = gen[gen.asset_type == "pv"].groupby("event_timestamp_utc")["available_generation_mw"].sum().to_numpy()
wind_av = gen[gen.asset_type == "wind"].groupby("event_timestamp_utc")["available_generation_mw"].sum().to_numpy()
demand_shape = 1 + 0.12*np.sin(2*np.pi*(hours-18)/24) + 0.08*np.cos(2*np.pi*doy/365)
res_share = (pv_av + wind_av) / max(fleet_av.max(), 1)
rdn = 375*demand_shape - 245*res_share + rng.normal(0,24,n)
rdn = np.where(noon_event & (pv_av > 55), rdn - 250 + rng.normal(0,20,n), rdn)
rdn = np.where(scenario & (hours >=18) & (hours <=21) & (wind_av < 130), rdn + 180 + rng.normal(0,25,n), rdn)
rdn = np.round(clamp_array(rdn, -190, 920),2)
rdb = np.round(clamp_array(rdn + rng.normal(0,32,n), -230, 980),2)
imb = np.round(clamp_array(rdn + 55 + np.abs(rng.normal(0,75,n)), -120, 1250),2)
market_frames = []
for market_name, price in [("RDN", rdn), ("RDB", rdb), ("imbalance_settlement", imb)]:
    unit = np.where(idx < pd.Timestamp("2025-07-01", tz=TZ), "PT60M", "PT15M")
    version = np.where(idx < pd.Timestamp("2025-07-01", tz=TZ), "market_v2025_hourly_reference", "market_v2026_15m_reference")
    m = pd.DataFrame({"trading_date":idx.date.astype(str),"delivery_date":idx.date.astype(str),"market_time_unit":unit,"market":market_name,"price_pln_per_mwh":price,"volume_mwh":np.round((850+160*demand_shape+rng.normal(0,35,n))*0.25,3),"balancing_area":"PL","pob_id":"POB_SYNTH_OZE","settlement_status":"synthetic_final"})
    m = add_common(m, idx, "Dane rynkowe PSE/TGE", version="")
    m["data_version"] = version
    m["settlement_interval"] = unit
    market_frames.append(m)
market = pd.concat(market_frames, ignore_index=True)
market.to_csv(DATA / "market_prices.csv", index=False)

storage_rows = []
for _, s in storage_assets.iterrows():
    sid, stype = s.storage_id, s.storage_type
    cap = float(s.energy_capacity_mwh); soc = float(s.initial_soc_mwh); eff = float(s.round_trip_efficiency)
    ce = eff**0.5; de = eff**0.5; aux = float(s.auxiliary_power_mw)
    if stype == "BESS": ch_power = dis_power = float(s.power_mw)
    else: ch_power = float(s.pumping_power_mw); dis_power = float(s.generating_power_mw)
    for ts, price in zip(idx, rdn):
        mode="standby"; ch=0.0; dis=0.0; aux_mwh = aux * 0.25
        if ts == SCENARIO_START:
            soc = float(s.initial_soc_mwh)
        soc = max(0, soc - aux_mwh)
        if price < 60 and soc < cap*0.96:
            mode = "charging" if stype == "BESS" else "pumping"; ch = min(ch_power, (cap-soc)/0.25/ce); soc += ch*0.25*ce
        elif price > 450 and soc > cap*0.12:
            mode = "discharging" if stype == "BESS" else "generation"; dis = min(dis_power, soc*de/0.25); soc -= dis*0.25/de
        else:
            soc = max(0, soc*(1-(0.00001 if stype=="BESS" else 0.00002)))
        storage_rows.append({"storage_id":sid,"storage_type":stype,"mode":mode,"stored_energy_mwh":round(soc,4),"state_of_charge_pct":round(100*soc/cap,3),"round_trip_efficiency":eff,"auxiliary_consumption_mwh":round(aux_mwh,5),"net_power_mw":round(dis-ch-aux,4),"net_energy_mwh":round((dis-ch)*0.25-aux_mwh,5),"upper_reservoir_level":round(100*soc/cap,3) if stype=="ESP" else "","lower_reservoir_level":round(100*(1-soc/cap),3) if stype=="ESP" else "","generating_power_mw":round(dis if stype=="ESP" else 0,4),"pumping_power_mw":round(ch if stype=="ESP" else 0,4),"charging_power_mw":round(ch if stype=="BESS" else 0,4),"discharging_power_mw":round(dis if stype=="BESS" else 0,4)})
stor = pd.DataFrame(storage_rows)
common_index = pd.DatetimeIndex(np.tile(idx, len(storage_assets)))
stor = add_common(stor, common_index, "SCADA ESP/BESS")
stor.to_csv(DATA / "storage_dispatch.csv", index=False)

# Derived generator checks.
gen_dt = gen.copy(); gen_dt["event_timestamp_utc"] = pd.to_datetime(gen_dt["event_timestamp_utc"], utc=True); gen_dt["local_time"] = gen_dt["event_timestamp_utc"].dt.tz_convert(TZ)
market_dt = market.copy(); market_dt["event_timestamp_utc"] = pd.to_datetime(market_dt["event_timestamp_utc"], utc=True); market_dt["local_time"] = market_dt["event_timestamp_utc"].dt.tz_convert(TZ)
stor_dt = stor.copy(); stor_dt["event_timestamp_utc"] = pd.to_datetime(stor_dt["event_timestamp_utc"], utc=True); stor_dt["local_time"] = stor_dt["event_timestamp_utc"].dt.tz_convert(TZ)
cf = gen_dt.groupby("asset_type").agg(actual_generation_mwh=("actual_generation_mwh","sum")).reset_index().merge(assets.groupby("asset_type", as_index=False)["installed_capacity_mw"].sum(), on="asset_type")
cf["capacity_factor_pct"] = (100*cf.actual_generation_mwh/(cf.installed_capacity_mw*len(idx)*0.25)).round(2)
cf.to_csv(DERIVED / "capacity_factors.csv", index=False)
scen_mask = (gen_dt.local_time >= SCENARIO_START) & (gen_dt.local_time <= SCENARIO_END)
rdn_scen = market_dt[(market_dt.market=="RDN") & (market_dt.local_time >= SCENARIO_START) & (market_dt.local_time <= SCENARIO_END)]
neg = rdn_scen[rdn_scen.price_pln_per_mwh.astype(float)<0]
curtailed_neg = gen_dt[scen_mask].merge(neg[["event_timestamp_utc"]], on="event_timestamp_utc")["curtailed_energy_mwh"].astype(float).sum()
stor_scen = stor_dt[(stor_dt.local_time >= SCENARIO_START) & (stor_dt.local_time <= SCENARIO_END)]
pumping = -stor_scen[(stor_scen["storage_type"]=="ESP") & (stor_scen["mode"]=="pumping")]["net_energy_mwh"].astype(float).sum()
generating = stor_scen[(stor_scen["storage_type"]=="ESP") & (stor_scen["mode"]=="generation")]["net_energy_mwh"].astype(float).sum()
bess_ch = stor_scen[(stor_scen["storage_type"]=="BESS") & (stor_scen["mode"]=="charging")]["charging_power_mw"].astype(float).sum() * 0.25 + stor_scen[stor_scen["storage_type"]=="BESS"]["auxiliary_consumption_mwh"].astype(float).sum()
bess_dis = stor_scen[(stor_scen["storage_type"]=="BESS") & (stor_scen["mode"]=="discharging")]["discharging_power_mw"].astype(float).sum() * 0.25
storage_balance = pd.DataFrame([{"storage_type":"ESP","charged_or_pumped_mwh":round(pumping,3),"generated_or_discharged_mwh":round(generating,3),"observed_output_input_ratio":round(generating/pumping,3) if pumping else 0},{"storage_type":"BESS","charged_or_pumped_mwh":round(bess_ch,3),"generated_or_discharged_mwh":round(bess_dis,3),"observed_output_input_ratio":round(bess_dis/bess_ch,3) if bess_ch else 0}])
storage_balance.to_csv(DERIVED / "storage_energy_balance.csv", index=False)
night_pv = gen_dt[(gen_dt.asset_type=="pv") & (gen_dt.local_time.dt.hour.isin([0,1,2,3,22,23]))]["actual_generation_mwh"].astype(float).max()
summary = {"seed":SEED,"intervals_15m":int(n),"generation_asset_rows":int(len(gen)),"market_price_rows":int(len(market)),"storage_dispatch_rows":int(len(stor)),"realtime_telemetry_rows":int(len(tele)),"scenario_start_local":SCENARIO_START.isoformat(),"scenario_end_local":SCENARIO_END.isoformat(),"negative_price_intervals_scenario":int(len(neg)),"curtailed_energy_during_negative_prices_mwh":round(float(curtailed_neg),3),"max_pv_generation_mwh_at_night":round(float(night_pv),8),"esp_pumped_energy_mwh_scenario":round(float(pumping),3),"esp_generated_energy_mwh_scenario":round(float(generating),3),"bess_charged_energy_mwh_scenario":round(float(bess_ch),3),"bess_discharged_energy_mwh_scenario":round(float(bess_dis),3)}
(DERIVED / "dataset_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
(DATA / "README.md").write_text("# Datasets — ce-wytw-oze-prognoza-bess\n\n> Dane są w 100% syntetyczne, wygenerowane proceduralnie (seed=42). Nie są danymi operacyjnymi, handlowymi, pomiarowymi ani majątkowymi Contoso Energia Wytwarzanie S.A.\n\n## Pliki\n\n- `assets.csv` — syntetyczne farmy wiatrowe, PV i elektrownie przepływowe.\n- `storage_assets.csv` — BESS i ESP (nazwy fikcyjne).\n- `generation_assets.csv` — 15-minutowa generacja, dostępność, harmonogram, produkcja i curtailment.\n- `market_prices.csv` — syntetyczne ceny RDN/RDB i cena rozliczeniowa niezbilansowania jako osobny typ.\n- `storage_dispatch.csv` — praca BESS/ESP z ujemnym bilansem w ładowaniu/pompowaniu.\n- `realtime_telemetry.jsonl` — wycinek D-2..D+2 do Eventstream/Eventhouse.\n- `derived/` — wyniki generatora i notebooków.\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
