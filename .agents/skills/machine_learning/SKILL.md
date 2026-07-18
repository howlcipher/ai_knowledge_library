---
name: "machine_learning"
description: "Protocols for building, deploying, and evaluating AI and ML models."
tier: 2
---

# Machine Learning Engineering

Protocols for building, evaluating, deploying, and monitoring machine learning and artificial intelligence models with an emphasis on rigor, transparency, and reproducibility.

## Data Management and Preprocessing
* **Data Splitting**: Enforce strict separation between training, validation, and testing datasets before any feature engineering or scaling to prevent data leakage.
* **Feature Engineering**: Standardize preprocessing pipelines using `sklearn.pipeline.Pipeline` or `sklearn.pipeline.make_pipeline`. Fit preprocessing transformations strictly on the training partition. Document transformation steps and maintain feature stores to ensure consistency between offline training and online inference.
* **Pandas and Data Wrangling**: When preprocessing data, avoid in-place DataFrame modifications to maintain a clear lineage of data transformations. Use `.loc` and `.iloc` explicitly for all slicing and filtering to prevent `SettingWithCopyWarning` and ensure predictable data preparation.

## Model Evaluation and Fairness
* **Metrics Selection**: Select evaluation metrics that align with the specific domain objectives (e.g., precision-recall curves for highly imbalanced classification tasks, MAE/RMSE for regression).
* **Bias and Fairness**: Actively test for and mitigate bias across key demographic subgroups. Establish clear baselines and check for model drift regularly.
* **Validation**: Utilize cross-validation techniques (e.g., `cross_val_score`, `GridSearchCV`) for model evaluation and hyperparameter tuning instead of hold-out test partitions.

## Deployment, Reproducibility, and Tooling
* **Reproducibility**: Enforce determinism by setting fixed random seeds (e.g., `random_state=42` or `np.random.seed(42)`) for all machine learning models, train-test splits, and synthetic data generation. Package execution environments using containers or virtual environment specifications.
* **Monitoring**: Implement logging for model predictions, inputs, and latency to monitor performance degradation and data drift in production.
* **Jupyter Notebook Standards**: Clear all output cells before committing notebook `.ipynb` files to version control. Consolidate package imports and environment variables in the first cell, keeping subsequent cells small, modular, and single-purpose.
