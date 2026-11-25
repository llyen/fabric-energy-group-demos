import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# CELL
from pathlib import Path
import json
import pandas as pd
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets"
DERIVED = DATA / "derived"

# CELL
products = pd.read_csv(DATA / "data_product.csv")
edges = pd.read_csv(DATA / "lineage_edge.csv")
consumers = pd.read_csv(DATA / "consumer.csv")
G = nx.DiGraph()
G.add_nodes_from(products["data_product_id"])
G.add_edges_from(edges[["source_data_product_id", "target_data_product_id"]].itertuples(index=False, name=None))
is_dag = nx.is_directed_acyclic_graph(G)
missing_sources = sorted(set(edges["source_data_product_id"]) - set(products["data_product_id"]))
missing_targets = sorted(set(edges["target_data_product_id"]) - set(products["data_product_id"]))
missing_consumer_products = sorted(set(consumers["data_product_id"]) - set(products["data_product_id"]))
rows = []
for pid in products["data_product_id"]:
    downstream = sorted(nx.descendants(G, pid))
    affected = consumers[consumers["data_product_id"].isin(downstream + [pid])]
    rows.append({"data_product_id": pid, "downstream_products": len(downstream), "affected_consumers": int(len(affected)), "blast_radius_score": int(len(downstream) * 10 + len(affected)), "affected_domains": ";".join(sorted(products[products["data_product_id"].isin(downstream)]["domain"].unique()))})
blast = pd.DataFrame(rows).merge(products[["data_product_id","data_product_name","domain","owning_company"]], on="data_product_id").sort_values(["blast_radius_score","affected_consumers"], ascending=False)
blast.to_csv(DERIVED / "lineage_blast_radius.csv", index=False, encoding="utf-8")
summary = {
    "lineage_edges": int(len(edges)), "lineage_is_dag": bool(is_dag),
    "missing_edge_sources": missing_sources, "missing_edge_targets": missing_targets,
    "missing_consumer_products": missing_consumer_products,
    "top_blast_product_id": blast.iloc[0]["data_product_id"],
    "top_blast_product_name": blast.iloc[0]["data_product_name"],
    "top_blast_downstream_products": int(blast.iloc[0]["downstream_products"]),
    "top_blast_affected_consumers": int(blast.iloc[0]["affected_consumers"]),
}
(DERIVED / "lineage_validation.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
