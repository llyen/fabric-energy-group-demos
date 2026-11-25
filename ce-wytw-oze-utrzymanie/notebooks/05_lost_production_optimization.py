# CELL
from pathlib import Path
import json
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / 'datasets'
DERIVED = DATA / 'derived'
DERIVED.mkdir(exist_ok=True)
D0 = pd.Timestamp('2026-09-15T10:00:00+02:00')
TARGET = 'WTG-W02-03'
CONFIG = BASE / 'config.example.json'

# CELL
# Jawny blok założeń modelowych.
# Status wszystkich parametrów poniżej: "założenie modelowe, do kalibracji z ekspertami klienta".
# Wartości nie są faktami o Contoso Energia. Są zapisane w config.example.json, żeby można je było zmienić
# bez edycji kodu notatnika i pokazać ich wpływ w analizie wrażliwości.
config = json.loads(CONFIG.read_text(encoding='utf-8'))
model_assumptions = config['model_assumptions']

def assumption_value(name: str):
    return model_assumptions[name]['value']

LOST_PRODUCTION_DELAY_MULTIPLIER = float(assumption_value('lost_production_delay_multiplier'))
RESIDUAL_RISK_MULTIPLIER = float(assumption_value('residual_risk_multiplier'))
DELAY_NORMALIZATION_DAYS = float(assumption_value('delay_normalization_days'))
OPTIMIZED_PLAN_EARLY_START_DAYS_BEFORE_D0 = int(assumption_value('optimized_plan_early_start_days_before_d0'))
CAPACITY_FACTOR_ASSUMPTIONS = {
    tech: float(spec['value'])
    for tech, spec in model_assumptions['capacity_factor_assumptions'].items()
}
LOST_PRODUCTION_DELAY_MULTIPLIER_SENSITIVITY = [
    float(x) for x in model_assumptions['lost_production_delay_multiplier_sensitivity']
]
assumptions_table = []
for name in ['lost_production_delay_multiplier', 'residual_risk_multiplier', 'delay_normalization_days', 'optimized_plan_early_start_days_before_d0']:
    spec = model_assumptions[name]
    assumptions_table.append({'parameter': name, 'value': spec['value'], 'meaning': spec['meaning'], 'status': spec['status']})
for group in ['capacity_factor_assumptions', 'baseline_operating_capacity_factor', 'baseline_service_cycle_days']:
    for tech, spec in model_assumptions[group].items():
        assumptions_table.append({'parameter': f'{group}.{tech}', 'value': spec['value'], 'meaning': spec['meaning'], 'status': spec['status']})
spec = model_assumptions['risk_alert_threshold_train_non_failure_quantile']
assumptions_table.append({'parameter': 'risk_alert_threshold_train_non_failure_quantile', 'value': spec['value'], 'meaning': spec['meaning'], 'status': spec['status']})
pd.DataFrame(assumptions_table).to_csv(DERIVED / 'model_assumptions.csv', index=False)

# CELL
assets = pd.read_csv(DATA / 'asset_registry.csv')
wo = pd.read_csv(DATA / 'work_orders.csv', parse_dates=['planned_start'])
crew = pd.read_csv(DATA / 'crew_calendar.csv', parse_dates=['date'])
risk = pd.read_csv(DERIVED / 'risk_scores_daily.csv', parse_dates=['date'])

# CELL
value_rows = []
for aid in wo.asset_id.unique():
    asset = assets.loc[assets.asset_id == aid].iloc[0]
    cf = CAPACITY_FACTOR_ASSUMPTIONS[asset.technology]
    expected = float(asset.installed_capacity_mw) * 24 * 30 * cf
    value_rows.append({'asset_id': aid, 'expected_mwh_next_30d': expected, 'capacity_factor_assumption': cf})
value = pd.DataFrame(value_rows)
risk_d = risk[risk.date == (D0 - pd.Timedelta(days=1)).normalize()][['asset_id','risk_score']]
plan = wo.merge(value, on='asset_id', how='left').merge(risk_d, on='asset_id', how='left').merge(assets[['asset_id','technology','installed_capacity_mw']], on='asset_id')
plan['risk_score'] = plan['risk_score'].fillna(0.05)
plan['value_priority_score'] = plan['risk_score'] * plan['expected_mwh_next_30d']

# CELL
def schedule(order: pd.DataFrame, name: str, delay_multiplier: float) -> pd.DataFrame:
    rows = []
    used = {}
    start_min = (D0 - pd.Timedelta(days=OPTIMIZED_PLAN_EARLY_START_DAYS_BEFORE_D0)).normalize()
    for _, r in order.iterrows():
        d = start_min if name == 'value_aware' else max(r.planned_start.normalize(), start_min)
        while True:
            key = (d.date().isoformat(), r.crew_type)
            cap_rows = crew[(crew.date.dt.date == d.date()) & (crew.crew_type == r.crew_type)]
            cap = int(cap_rows.available_crew_days.sum()) if not cap_rows.empty else (0 if d.dayofweek >= 5 else 1)
            if cap > used.get(key, 0):
                used[key] = used.get(key, 0) + 1
                break
            d += pd.Timedelta(days=1)
        days_delayed = max(0, int((d.normalize() - r.planned_start.normalize()).days))
        risk_delay = min(1.0, r.risk_score * days_delayed / DELAY_NORMALIZATION_DAYS)
        residual_risk = RESIDUAL_RISK_MULTIPLIER * r.risk_score
        lost = r.expected_mwh_next_30d * (residual_risk + risk_delay * delay_multiplier)
        rows.append({**r.to_dict(), 'scenario': name, 'scheduled_start': d.isoformat(), 'delay_days': days_delayed, 'expected_lost_mwh': lost, 'lost_production_delay_multiplier': delay_multiplier})
    return pd.DataFrame(rows)

baseline = schedule(plan.sort_values(['planned_start','priority_from_cmms']), 'baseline_calendar', LOST_PRODUCTION_DELAY_MULTIPLIER)
optimized = schedule(plan.sort_values('value_priority_score', ascending=False), 'value_aware', LOST_PRODUCTION_DELAY_MULTIPLIER)
result = pd.concat([baseline, optimized], ignore_index=True)
summary = result.groupby('scenario', as_index=False).agg(total_expected_lost_mwh=('expected_lost_mwh','sum'), max_delay_days=('delay_days','max'))
baseline_lost = float(summary.loc[summary.scenario=='baseline_calendar','total_expected_lost_mwh'].iloc[0])
optimized_lost = float(summary.loc[summary.scenario=='value_aware','total_expected_lost_mwh'].iloc[0])
avoided = baseline_lost - optimized_lost
summary['avoided_mwh_vs_baseline'] = summary['total_expected_lost_mwh'].map(lambda x: baseline_lost - x)
result.to_csv(DERIVED / 'service_schedule_comparison.csv', index=False)
summary.to_csv(DERIVED / 'service_schedule_summary.csv', index=False)

# CELL
sensitivity_rows = []
base_order = plan.sort_values(['planned_start','priority_from_cmms'])
value_order = plan.sort_values('value_priority_score', ascending=False)
for multiplier in LOST_PRODUCTION_DELAY_MULTIPLIER_SENSITIVITY:
    base_s = schedule(base_order, 'baseline_calendar', multiplier)
    opt_s = schedule(value_order, 'value_aware', multiplier)
    base_loss = float(base_s.expected_lost_mwh.sum())
    opt_loss = float(opt_s.expected_lost_mwh.sum())
    top_base = '|'.join(base_s.sort_values('scheduled_start').asset_id.head(5).tolist())
    top_opt = '|'.join(opt_s.sort_values('scheduled_start').asset_id.head(5).tolist())
    sensitivity_rows.append({
        'lost_production_delay_multiplier': multiplier,
        'baseline_expected_lost_mwh': round(base_loss, 1),
        'optimized_expected_lost_mwh': round(opt_loss, 1),
        'avoidable_lost_production_mwh': round(base_loss - opt_loss, 1),
        'avoidable_lost_production_pct': round(100 * (base_loss - opt_loss) / base_loss, 1) if base_loss else 0,
        'top5_baseline_order': top_base,
        'top5_value_aware_order': top_opt,
        'target_in_top5_value_aware': TARGET in top_opt.split('|'),
    })
sensitivity = pd.DataFrame(sensitivity_rows)
sensitivity.to_csv(DERIVED / 'lost_production_sensitivity.csv', index=False)

# CELL
pc = json.loads((DERIVED / 'power_curve_metrics.json').read_text(encoding='utf-8'))
temp = json.loads((DERIVED / 'temperature_model_metrics.json').read_text(encoding='utf-8'))
pv_metrics = json.loads((DERIVED / 'pv_metrics.json').read_text(encoding='utf-8'))
risk_metrics = json.loads((DERIVED / 'risk_model_metrics.json').read_text(encoding='utf-8'))
volumes = {}
for name in ['asset_registry.csv','wind_scada_10min.csv','pv_scada_15min.csv','hydro_scada_1h.csv','esp_scada_1h.csv','work_orders.csv']:
    with (DATA / name).open(encoding='utf-8') as f:
        volumes[name] = sum(1 for _ in f) - 1
numbers = {
    'wow_target_asset': TARGET,
    'wow_lead_time_days_power_curve': pc['lead_time_days'],
    'wow_lead_time_days_temperature': temp['temp_lead_time_days'],
    'baseline_expected_lost_mwh': round(baseline_lost, 1),
    'optimized_expected_lost_mwh': round(optimized_lost, 1),
    'avoidable_lost_production_mwh': round(avoided, 1),
    'avoidable_lost_production_pct': round(100 * avoided / baseline_lost, 1),
    'lost_production_delay_multiplier': LOST_PRODUCTION_DELAY_MULTIPLIER,
    'lost_production_sensitivity_min_mwh': round(float(sensitivity.avoidable_lost_production_mwh.min()), 1),
    'lost_production_sensitivity_max_mwh': round(float(sensitivity.avoidable_lost_production_mwh.max()), 1),
    'risk_auc_failure_30d': risk_metrics['risk_auc_failure_30d'],
    'baseline_auc_calendar_cycle': risk_metrics['baseline_auc_calendar_cycle'],
    'precision_at_20_risk': risk_metrics['precision_at_20_risk'],
    'precision_at_20_baseline': risk_metrics['precision_at_20_baseline'],
    'night_pv_generation_mwh': pv_metrics['night_generation_mwh'],
    'worst_pv_asset_id': pv_metrics['worst_pv_asset_id'],
    'volumes': volumes,
}
(DERIVED / 'demo_numbers.json').write_text(json.dumps(numbers, ensure_ascii=False, indent=2), encoding='utf-8')
pd.DataFrame([{k:v for k,v in numbers.items() if k != 'volumes'}]).to_csv(DERIVED / 'demo_numbers.csv', index=False)
print(numbers)
