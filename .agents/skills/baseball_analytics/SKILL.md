---
name: "baseball_analytics"
description: "Sabermetrics, statistical modeling, and baseball strategy."
triggers:
  - "baseball"
  - "sabermetrics"
  - "statcast"
  - "woba"
  - "war"
tier: 3
---

# Baseball Analytics and Sabermetrics

This skill outlines the methodologies for evaluating player performance, team strategy, and predictive modeling using advanced sabermetric principles, Statcast data, and rigorous data science and machine learning pipelines.

## Analytical Methodologies

### 1. Advanced Metrics Evaluation
Prioritize context-adjusted, comprehensive metrics over traditional counting stats (such as runs, RBIs, wins, and ERA):
- **Wins Above Replacement (WAR):** Evaluate overall player contribution relative to a replacement-level baseline.
- **Weighted On-Base Average (wOBA) and Weighted Runs Created Plus (wRC+):** Analyze offensive efficiency, adjusting for league environments and ballpark factors.
- **Fielding Independent Pitching (FIP):** Isolate a pitcher's performance from defense-dependent outcomes.
- **Statcast Metrics:** Utilize granular data including exit velocity, launch angle, barrel rates, expected metrics (xBA, xSLG, xwOBA), and defensive metrics (Outs Above Average).

### 2. Predictive Modeling and Projection Systems
- **Validation and Evaluation**: Report domain-aligned regression metrics (e.g., RMSE and MAE for ERA or run projections) and classification metrics (e.g., Precision, Recall, and F1-Score for binary outcomes like injury prediction), using the cross-validation standards owned by `data_analyst`.
- **Environment and Model Drift**: Monitor projections for drift caused by changes in league run-scoring environments, rule changes, or ball composition.

### 3. Strategic Optimization
- Leverage platoon splits, defensive positioning vectors, pitch sequencing patterns, and base-running value calculations to optimize in-game decision making and roster construction.

## Related Skills
- Defer to `data_analyst` for pandas wrangling, pipeline encapsulation, reproducibility, and data quality standards; this skill adds only the sabermetric deltas (park factors, league environment drift, Statcast handling).
