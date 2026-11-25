# CELL
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score, adjusted_rand_score
from sklearn.preprocessing import StandardScaler

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)
SEED = 42

# CELL
customers = pd.read_csv(DATA / "customers.csv")
profiles = pd.read_csv(DATA / "customer_profiles_d0_15min_wide.csv")
load_cols = [c for c in profiles.columns if c.startswith("load_q")]
pv_cols = [c for c in profiles.columns if c.startswith("pv_q")]
load = profiles[load_cols].to_numpy(float)
pv = profiles[pv_cols].to_numpy(float)
features = pd.DataFrame({
    "customer_id": profiles.customer_id,
    "daily_kwh": load.sum(axis=1),
    "night_share": load[:, :24].sum(axis=1) / load.sum(axis=1),
    "midday_share": load[:, 40:60].sum(axis=1) / load.sum(axis=1),
    "evening_share": load[:, 68:84].sum(axis=1) / load.sum(axis=1),
    "peak_to_average": load.max(axis=1) / (load.mean(axis=1) + 1e-9),
    "pv_to_load_ratio": pv.sum(axis=1) / (load.sum(axis=1) + 1e-9),
    "noon_export_ratio": np.maximum(pv[:, 40:60] - load[:, 40:60], 0).sum(axis=1) / (load.sum(axis=1) + 1e-9),
    "evening_flex_kw": customers["flexible_power_kw_model"].to_numpy(float),
    "storage_capacity_kwh": customers["storage_capacity_kwh"].to_numpy(float),
})

# CELL
X = features.drop(columns=["customer_id"]).to_numpy(float)
Xs = StandardScaler().fit_transform(X)
rows, models = [], {}
for k in range(2, 9):
    km = KMeans(n_clusters=k, random_state=SEED, n_init=20)
    labels_k = km.fit_predict(Xs)
    rows.append({"model": "kmeans_profile", "k": k, "silhouette": silhouette_score(Xs, labels_k, sample_size=6000, random_state=SEED), "calinski_harabasz": calinski_harabasz_score(Xs, labels_k), "davies_bouldin": davies_bouldin_score(Xs, labels_k)})
    models[k] = labels_k
metrics = pd.DataFrame(rows)
best_k = int(metrics.sort_values(["silhouette", "davies_bouldin"], ascending=[False, True]).iloc[0].k)
labels = models[best_k]
rule = np.select([customers.has_storage.astype(bool), customers.has_ev.astype(bool), customers.has_electric_heating.astype(bool), customers.has_pv.astype(bool)], [0,1,2,3], default=4)
metrics = pd.concat([metrics, pd.DataFrame([{"model": "baseline_rule_assets", "k": len(np.unique(rule)), "silhouette": silhouette_score(Xs, rule, sample_size=6000, random_state=SEED), "calinski_harabasz": calinski_harabasz_score(Xs, rule), "davies_bouldin": davies_bouldin_score(Xs, rule), "adjusted_rand_vs_kmeans": adjusted_rand_score(labels, rule)}])], ignore_index=True)

# CELL
summary = features.assign(cluster_id=labels).groupby("cluster_id").agg(customers_count=("customer_id","count"), daily_kwh_mean=("daily_kwh","mean"), night_share=("night_share","mean"), midday_share=("midday_share","mean"), evening_share=("evening_share","mean"), peak_to_average=("peak_to_average","mean"), pv_to_load_ratio=("pv_to_load_ratio","mean"), noon_export_ratio=("noon_export_ratio","mean"), evening_flex_kw=("evening_flex_kw","mean"), storage_capacity_kwh=("storage_capacity_kwh","mean")).reset_index()
def label_row(r):
    if r.storage_capacity_kwh > 3: return "storage_optimizer"
    if r.noon_export_ratio > .12: return "pv_midday_exporter"
    if r.evening_flex_kw > .9 and r.evening_share > .29: return "ev_or_heating_flexible"
    if r.evening_share > .34: return "evening_family"
    if r.peak_to_average < 1.7: return "flat_profile"
    return "mixed_profile"
summary["segment_name"] = summary.apply(label_row, axis=1)
seg = customers[["customer_id","has_pv","has_storage","has_ev","has_electric_heating","flexible_power_kw_model"]].copy()
seg["cluster_id"] = labels
seg = seg.merge(summary[["cluster_id","segment_name"]], on="cluster_id", how="left")
metrics.to_csv(DERIVED / "segmentation_metrics.csv", index=False)
seg.to_csv(DERIVED / "customer_segments.csv", index=False)
summary.to_csv(DERIVED / "segment_summary.csv", index=False)
print(json.dumps({"best_k": best_k, "best_silhouette": float(metrics.query("model=='kmeans_profile' and k==@best_k").iloc[0].silhouette), "baseline_silhouette": float(metrics.query("model=='baseline_rule_assets'").iloc[0].silhouette)}, ensure_ascii=False))
