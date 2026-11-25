"""Generate deterministic synthetic data for Contoso Energia Sprzedaz customer flexibility demo.
All data is fictional; no personal data. Seed=42.
"""
from __future__ import annotations

import json, math, random
from datetime import datetime, timedelta, timezone
from pathlib import Path
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
TZ = timezone(timedelta(hours=2))
D0 = datetime(2026, 6, 18, 0, 0, tzinfo=TZ)
START = D0 - timedelta(days=30)
END = D0 + timedelta(days=1, hours=23, minutes=45)
N = 36000
MIN_GROUP_SIZE = 100
ROUND_TRIP_EFFICIENCY = 0.88

VOIV = [("51", "region_polnocny"), ("53", "region_zachodni"), ("55", "region_centralny"), ("57", "region_gorski"), ("59", "region_nadrzeczny"), ("61", "region_jeziorny")]
GMINAS = [{"gmina_code": f"{vc}{i:02d}{(i*7)%1000:03d}"[:7], "voivodeship_code": vc, "voivodeship_name": vn, "gmina_name": f"gmina_syntetyczna_{vn}_{i:02d}"} for vc, vn in VOIV for i in range(1, 16)]
pd.DataFrame(GMINAS).to_csv(DATA / "dim_gmina.csv", index=False)

ARCH = {
    "pv_midday_exporter": (.22, (2.8, 5.8), .92, .18, .08, .05),
    "storage_optimizer": (.08, (3.6, 7.2), .80, .95, .20, .10),
    "ev_evening_peak": (.12, (4.2, 8.5), .25, .10, .92, .12),
    "electric_heating": (.14, (5.5, 10.5), .30, .08, .12, .88),
    "flat_profile": (.24, (2.1, 4.6), .10, .03, .04, .08),
    "evening_family": (.20, (2.8, 6.0), .18, .05, .10, .10),
}

def iso(dt): return dt.isoformat(timespec="minutes")
def solar(h):
    sunrise, sunset = 4.5, 20.75
    if h < sunrise or h > sunset: return 0.0
    return max(0.0, math.sin(math.pi * (h - sunrise) / (sunset - sunrise)) ** 1.55)
def shape(a):
    h = np.arange(96) / 4
    morning = np.exp(-((h - 7.0) / 1.7) ** 2); evening = np.exp(-((h - 19.5) / 2.2) ** 2)
    night = np.exp(-((h - 2.0) / 3.2) ** 2); midday = np.exp(-((h - 13.0) / 3.0) ** 2)
    s = {"flat_profile": .75 + .12*morning + .14*evening + .05*np.sin(2*np.pi*h/24),
         "evening_family": .45 + .25*morning + 1.05*evening + .08*night,
         "ev_evening_peak": .40 + .20*morning + .75*evening + 1.05*np.exp(-((h-22)/1.6)**2),
         "electric_heating": .70 + .32*morning + .52*evening + .35*night,
         "pv_midday_exporter": .42 + .20*morning + .48*evening + .12*midday,
         "storage_optimizer": .43 + .18*morning + .45*evening + .08*midday}[a]
    s = np.maximum(.05, s + rng.normal(0, .015, 96))
    return s / s.sum()

def price_at(ts):
    h = ts.hour + ts.minute / 60
    if ts.date() == D0.date():
        return round(390 - 620*math.exp(-((h-12.7)/2.4)**2) + 820*math.exp(-((h-19)/1.55)**2) + rng.normal(0, 16), 2)
    day = (ts.date() - D0.date()).days
    rare = -260*math.exp(-((h-12.5)/2.2)**2) if day in {-25, -12, -4} else 0
    return round(385 + 70*math.exp(-((h-8)/2.3)**2) + 110*math.exp(-((h-19)/2.0)**2) - 145*math.exp(-((h-13)/3.3)**2) + rare + rng.normal(0, 18), 2)

prices=[]; ts=START; hourly_price_cache={}
while ts <= END:
    hour_ts = ts.replace(minute=0)
    hourly_price_cache.setdefault(hour_ts, price_at(hour_ts))
    prices.append({"event_timestamp_utc": iso(ts.astimezone(timezone.utc)), "local_timestamp": iso(ts), "local_timezone": "Europe/Warsaw", "settlement_interval": "PT15M", "market": "RDN", "market_time_unit": "hourly_price_repeated_to_15m", "price_pln_per_mwh": hourly_price_cache[hour_ts], "volume_mwh": round(float(rng.uniform(1600, 4200)), 2), "source_system": "synthetic_TGE_RDN", "quality_flag": "good", "ingestion_timestamp": iso((ts+timedelta(minutes=5)).astimezone(timezone.utc)), "data_version": "demo-2026-08-v1"})
    ts += timedelta(minutes=15)
pd.DataFrame(prices).to_csv(DATA / "market_prices_15min.csv", index=False)

pd.DataFrame([{"event_id":"DSR-2026-06-18-EVENING-01","event_date":D0.date().isoformat(),"start_local":iso(D0+timedelta(hours=18)),"end_local":iso(D0+timedelta(hours=20)),"notice_hours":6,"requested_reduction_mw":38.0,"rebound_window_hours":4,"rebound_ratio_assumption":0.80,"status":"test_activation","role_note":"Sprzedawca/agregator prowadzi produkt; OSD mierzy i dystrybuuje, OSP bilansuje KSE, POB bilansuje handlowo."}]).to_csv(DATA / "dsr_events.csv", index=False)

names = list(ARCH); weights = np.array([ARCH[a][0] for a in names]); weights /= weights.sum()
customers=[]; load_mat=np.zeros((N,96), dtype=np.float32); pv_mat=np.zeros((N,96), dtype=np.float32)
solar_vec=np.array([solar(q/4) for q in range(96)], dtype=np.float32)
for i in range(N):
    a = rng.choice(names, p=weights); _, annual_rng, ppv, pst, pev, ph = ARCH[a]
    annual = float(rng.uniform(*annual_rng)); daily = annual*1000/365*rng.uniform(.96,1.08)
    load = daily * shape(a)
    has_pv, has_st, has_ev, has_heat = rng.random()<ppv, rng.random()<pst, rng.random()<pev, rng.random()<ph
    pv_kwp = float(rng.uniform(3, 9.5)) if has_pv else 0.0
    pv = pv_kwp * solar_vec * .25 * rng.uniform(.82,1.08)
    storage = float(rng.choice([5,7.5,10,12.5,15])) if has_st else 0.0
    ev_kw = float(rng.uniform(2.2, 7.2)) if has_ev else 0.0; heat_kw = float(rng.uniform(1,4.5)) if has_heat else 0.0
    resp = float(np.clip(rng.normal(.28, .10), .05, .58))
    peak_kw = float(load[72:80].mean() * 4)
    flex_factor = .45 + 2.20*has_ev + 1.60*has_heat + 1.10*has_st + .35*has_pv
    flex = min(peak_kw * flex_factor, 9.0)
    g=random.choice(GMINAS); cid=f"CUST-{i+1:06d}"
    customers.append({"customer_id":cid,"gmina_code":g["gmina_code"],"voivodeship_code":g["voivodeship_code"],"contract_type":rng.choice(["sale","complex"], p=[.28,.72]),"generation_archetype_for_validation":a,"annual_consumption_mwh":round(annual,3),"has_pv":has_pv,"pv_kwp":round(pv_kwp,2),"has_storage":has_st,"storage_capacity_kwh":round(storage,2),"has_ev":has_ev,"ev_charger_kw":round(ev_kw,2),"has_electric_heating":has_heat,"electric_heating_kw":round(heat_kw,2),"price_response_index":round(resp,3),"flexible_power_kw_model":round(flex,3),"source_system":"synthetic_CRM_Billing_AMI","quality_flag":"good","local_timezone":"Europe/Warsaw","data_version":"demo-2026-08-v1"})
    load_mat[i]=load; pv_mat[i]=pv
cust=pd.DataFrame(customers); cust.to_csv(DATA / "customers.csv", index=False)
profile_cols = {"customer_id": cust.customer_id}
profile_cols.update({f"load_q{q:02d}_kwh": load_mat[:, q].round(5) for q in range(96)})
profile_cols.update({f"pv_q{q:02d}_kwh": pv_mat[:, q].round(5) for q in range(96)})
pd.DataFrame(profile_cols).to_csv(DATA / "customer_profiles_d0_15min_wide.csv", index=False)

sample=[]
for idx in range(0, N, 6):
    cid=customers[idx]["customer_id"]
    for q in range(96):
        ts=D0+timedelta(minutes=15*q)
        sample.append({"event_timestamp_utc":iso(ts.astimezone(timezone.utc)),"local_timestamp":iso(ts),"customer_id":cid,"gross_load_kwh":round(float(load_mat[idx,q]),5),"pv_generation_kwh":round(float(pv_mat[idx,q]),5),"settlement_interval":"PT15M","source_system":"synthetic_AMI_LZO","quality_flag":"good","data_version":"demo-2026-08-v1"})
pd.DataFrame(sample).to_csv(DATA / "meter_profile_d0_15min_sample.csv", index=False)
agg=[]
for q in range(96):
    ts=D0+timedelta(minutes=15*q)
    agg.append({"event_timestamp_utc":iso(ts.astimezone(timezone.utc)),"local_timestamp":iso(ts),"gross_load_mwh":round(float(load_mat[:,q].sum()/1000),5),"pv_generation_mwh":round(float(pv_mat[:,q].sum()/1000),5),"customers_count":N,"settlement_interval":"PT15M","source_system":"synthetic_AMI_LZO","quality_flag":"good","data_version":"demo-2026-08-v1"})
pd.DataFrame(agg).to_csv(DATA / "portfolio_profile_d0_15min.csv", index=False)
assumptions={"seed":SEED,"customer_count":N,"minimum_group_size":MIN_GROUP_SIZE,"d0":D0.date().isoformat(),"response_rates_tested":[0.10,0.20,0.35],"rebound_ratio":0.80,"rebound_window_quarters":16,"storage_round_trip_efficiency":ROUND_TRIP_EFFICIENCY,"dynamic_tariff_basis":"synthetic hourly RDN price repeated to 15-minute intervals","flat_energy_price_pln_mwh":520,"multi_zone_peak_pln_mwh":690,"multi_zone_offpeak_pln_mwh":360,"distribution_fee_pln_mwh":310,"system_fee_pln_mwh":95,"dsr_economic_assumptions":{"value_per_kw_event_pln":{"value":280,"description":"Syntetyczna wartość brutto 1 kW zweryfikowanej redukcji DSR w jednym zdarzeniu; proxy wartości portfelowej, nie taryfa Contoso Energia.","status":"założenie modelowe, do kalibracji z danymi handlowymi klienta, rozliczeniami POB i historią programu"},"participant_incentive_pln_event":{"value":4,"description":"Syntetyczna zachęta przypisana do jednego odbiorcy objętego programem w jednym zdarzeniu DSR; modeluje koszt dostępności/udziału, nie tylko faktyczną reakcję.","status":"założenie modelowe, do kalibracji testami akceptacji oferty i regulaminem programu"},"program_fixed_cost_pln_per_event":{"value":65000,"description":"Syntetyczny koszt stały jednego zdarzenia: kampania, operacje, rozliczenia, wsparcie i koszt pracy platformy.","status":"założenie modelowe, do kalibracji z docelowym modelem operacyjnym i zakresem integracji"},"fixed_cost_sensitivity_pln_event":[40000,65000,100000]},"price_response_elasticity_status":"założenie modelowe; wymaga kalibracji na uprawnionych danych AMI i historii programu"}
(DATA / "assumptions.json").write_text(json.dumps(assumptions, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"generated customers={N}, sample_rows={len(sample)}, prices={len(prices)}")
