"""Audytowalny silnik rekomendacji FLISR dla syntetycznej sieci SN.

Modul nie steruje siecia. Wylicza propozycje izolacji i zasilenia rezerwowego,
ktore dyspozytor moze zatwierdzic poza platforma analityczna zgodnie z IRiESD.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

MAX_VOLTAGE_DROP_PCT = 7.0
SAFETY_MARGIN = 0.92


@dataclass(frozen=True)
class SwitchingCandidate:
    fault_id: str
    tie_switch_id: str
    open_switch_id: str
    close_switch_id: str
    source_feeder_id: str
    target_feeder_id: str
    affected_customers: int
    restored_customers: int
    not_restored_customers: int
    added_current_a: float
    target_current_after_a: float
    target_current_limit_a: float
    voltage_drop_after_pct: float
    feasible: bool
    rejection_reason: str
    switching_steps: str


def _section_downstream(sections: pd.DataFrame, feeder_id: str, fault_order: int) -> pd.DataFrame:
    feeder_sections = sections[sections["feeder_id"] == feeder_id].copy()
    return feeder_sections[feeder_sections["section_order"] >= fault_order]


def evaluate_fault(
    fault: dict,
    feeders: pd.DataFrame,
    sections: pd.DataFrame,
    tie_switches: pd.DataFrame,
) -> list[SwitchingCandidate]:
    """Zwraca kandydatow przelaczen dla jednego uszkodzenia odcinka SN."""
    feeder_id = str(fault["feeder_id"])
    fault_order = int(fault["section_order"])
    fault_section = str(fault["section_id"])
    downstream = _section_downstream(sections, feeder_id, fault_order)
    if downstream.empty:
        return []
    affected_customers = int(downstream["customers_count"].sum())
    affected_current_a = float(downstream["normal_current_a"].sum())
    source = feeders.set_index("feeder_id").loc[feeder_id]
    candidates: list[SwitchingCandidate] = []

    relevant_ties = tie_switches[
        (tie_switches["source_feeder_id"] == feeder_id)
        | (tie_switches["target_feeder_id"] == feeder_id)
    ]
    feeder_by_id = feeders.set_index("feeder_id")
    for _, tie in relevant_ties.iterrows():
        if tie["source_feeder_id"] == feeder_id:
            target_id = tie["target_feeder_id"]
        else:
            target_id = tie["source_feeder_id"]
        target = feeder_by_id.loc[target_id]
        target_after = float(target["current_a"]) + affected_current_a
        limit = float(target["current_limit_a"]) * SAFETY_MARGIN
        voltage_after = float(target["voltage_drop_pct"]) + float(tie["transfer_voltage_drop_pct"])
        feasible = True
        reasons: list[str] = []
        if not bool(tie.get("normally_open", True)):
            feasible = False
            reasons.append("tie_switch_not_normally_open")
        if target_after > limit:
            feasible = False
            reasons.append("current_limit_exceeded")
        if voltage_after > MAX_VOLTAGE_DROP_PCT:
            feasible = False
            reasons.append("voltage_drop_exceeded")
        restored = affected_customers if feasible else 0
        candidates.append(SwitchingCandidate(
            fault_id=str(fault["fault_id"]),
            tie_switch_id=str(tie["tie_switch_id"]),
            open_switch_id=f"OPEN_{fault_section}_UPSTREAM",
            close_switch_id=str(tie["tie_switch_id"]),
            source_feeder_id=feeder_id,
            target_feeder_id=str(target_id),
            affected_customers=affected_customers,
            restored_customers=restored,
            not_restored_customers=affected_customers - restored,
            added_current_a=round(affected_current_a, 1),
            target_current_after_a=round(target_after, 1),
            target_current_limit_a=round(float(target["current_limit_a"]), 1),
            voltage_drop_after_pct=round(voltage_after, 2),
            feasible=feasible,
            rejection_reason=";".join(reasons) if reasons else "",
            switching_steps=(
                f"1. Potwierdz brak napiecia i lokalizacje {fault_section}. "
                f"2. Otworz {fault_section} od strony GPZ. "
                f"3. Zamknij {tie['tie_switch_id']} po zgodzie dyspozytora. "
                "4. Monitoruj prad i napiecie przez 15 minut."
            ),
        ))
    return candidates


def recommend_switching(
    faults: pd.DataFrame,
    feeders: pd.DataFrame,
    sections: pd.DataFrame,
    tie_switches: pd.DataFrame,
) -> pd.DataFrame:
    """Wybiera najlepsza wykonalna propozycje dla kazdej awarii."""
    rows = []
    for _, fault in faults.iterrows():
        candidates = evaluate_fault(fault.to_dict(), feeders, sections, tie_switches)
        if not candidates:
            continue
        candidates = sorted(candidates, key=lambda c: (c.feasible, c.restored_customers, -c.voltage_drop_after_pct), reverse=True)
        rows.append(candidates[0].__dict__)
    return pd.DataFrame(rows)


def interruption_minutes_saved(
    recommendations: pd.DataFrame,
    baseline_duration_min: float | str | pd.Series,
    switching_min: float,
) -> pd.DataFrame:
    """Liczy customer-minutes saved dla rekomendacji wykonalnych.

    `baseline_duration_min` pochodzi z danych o rzeczywistym czasie trwania awarii
    w scenariuszu: jako nazwa kolumny w `recommendations`, seria lub liczba wyliczona
    poza silnikiem. Nie ma tu domyslnej stalej, zeby metryki nie rozjechaly sie po
    zmianie generatora.
    """
    out = recommendations.copy()
    if isinstance(baseline_duration_min, str):
        out["baseline_duration_min"] = out[baseline_duration_min].astype(float)
    elif isinstance(baseline_duration_min, pd.Series):
        out["baseline_duration_min"] = baseline_duration_min.astype(float).to_numpy()
    else:
        out["baseline_duration_min"] = float(baseline_duration_min)
    out["proposed_duration_min"] = out.apply(
        lambda row: float(switching_min) if bool(row["feasible"]) else float(row["baseline_duration_min"]),
        axis=1,
    )
    out["minutes_saved_avg"] = out["baseline_duration_min"] - out["proposed_duration_min"]
    out["customer_minutes_saved"] = out["restored_customers"] * out["minutes_saved_avg"]
    return out
