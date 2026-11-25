# Miary DAX

```DAX
Sections = DISTINCTCOUNT(dim_line_section[section_id])

High Risk Sections =
COUNTROWS(FILTER(section_risk_scores, section_risk_scores[risk_priority_rank] <= 18))

Age Baseline Sections =
COUNTROWS(FILTER(risk_vs_age_priority, risk_vs_age_priority[selected_by_age] = 1))

Priority Changed Sections =
COUNTROWS(FILTER(risk_vs_age_priority, risk_vs_age_priority[selected_by_risk] = 1 && risk_vs_age_priority[selected_by_age] = 0))

Priority Changed % = DIVIDE([Priority Changed Sections], [Age Baseline Sections])

Avoidable Outage Risk kCM = SUM(risk_metrics[risk_avoidable_impact_kcm])

Avoidable Outage Age kCM = SUM(risk_metrics[age_avoidable_impact_kcm])

Avoidable Outage Uplift kCM = [Avoidable Outage Risk kCM] - [Avoidable Outage Age kCM]

High Confidence AI Detections =
COUNTROWS(FILTER(fact_ai_vision_candidate, fact_ai_vision_candidate[detected_by_model] = 1 && fact_ai_vision_candidate[confidence] >= 0.60))

AI Detections Outside Age Plan =
COUNTROWS(FILTER(risk_vs_age_priority, risk_vs_age_priority[ai_detections] > 0 && risk_vs_age_priority[selected_by_age] = 0))

Sections Above Degradation Threshold =
COUNTROWS(FILTER(section_degradation_forecast, section_degradation_forecast[current_degradation_pct] >= section_degradation_forecast[threshold_degradation_pct]))

Total Customer Minutes k = SUM(outage_impact_by_section[customer_minutes_k_total])
```
