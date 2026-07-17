---
name: "baseball_analytics"
description: "Sabermetrics, statistical modeling, and baseball strategy."
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

### 2. Pandas Data Wrangling for Sabermetrics
- **Vectorization**: Calculate complex sabermetric formulas (like wOBA and FIP) using vectorized pandas and NumPy operations. Avoid row-based `.iterrows()` iterations to optimize performance on large Statcast datasets.
- **Immutability and Indexing**: Avoid modifying DataFrames in-place. Use method chaining to build data transformations, and apply `.loc` and `.iloc` explicitly to filter plate appearances and avoid `SettingWithCopyWarning`.
- **Data Quality**: Explicitly check for and handle missing Statcast metrics (such as missing launch angles or velocities) at the data ingestion layer.

### 3. Predictive Modeling and Projection Systems
- **Rigor and Reproducibility**: Enforce determinism in all performance projections, train-test splits, and bootstrapping routines by setting a fixed random seed (e.g., `random_state=42`).
- **Machine Learning Pipelines**: Encapsulate player preprocessing steps (such as park factor adjustments and normalization) inside Scikit-learn pipelines to prevent data leakage from test partitions.
- **Validation and Evaluation**: Evaluate projection systems using cross-validation. Report domain-aligned regression metrics (e.g., RMSE and MAE for ERA or runs projected) and classification metrics (e.g., Precision, Recall, and F1-Score for binary outcomes like injury prediction).
- **Environment and Model Drift**: Monitor projections for drift caused by changes in league run-scoring environments, rule changes, or ball composition.

### 4. Strategic Optimization
- Leverage platoon splits, defensive positioning vectors, pitch sequencing patterns, and base-running value calculations to optimize in-game decision making and roster construction.
