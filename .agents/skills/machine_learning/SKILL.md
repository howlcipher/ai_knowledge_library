---
name: "machine_learning"
description: "Protocols for building, deploying, and evaluating AI and ML models."
triggers:
  - "machine learning"
  - "model training"
  - "mlops"
  - "inference"
  - "model drift"
tier: 2
---

# Machine Learning Engineering

Protocols for building, evaluating, deploying, and monitoring machine learning and artificial intelligence models with an emphasis on rigor, transparency, and reproducibility.

## Data Management and Preprocessing
- **Data Splitting**: Enforce strict separation between training, validation, and testing datasets before any feature engineering or scaling to prevent data leakage.
- **Feature Engineering**: Standardize preprocessing pipelines using `sklearn.pipeline.Pipeline` or `sklearn.pipeline.make_pipeline`. Fit preprocessing transformations strictly on the training partition. Document transformation steps and maintain feature stores to ensure consistency between offline training and online inference.

## Model Evaluation and Fairness
- **Metrics Selection**: Select evaluation metrics that align with the specific domain objectives (e.g., precision-recall curves for highly imbalanced classification tasks, MAE/RMSE for regression).
- **Bias and Fairness**: Actively test for and mitigate bias across key demographic subgroups. Establish clear baselines and check for model drift regularly.

## Deployment, Reproducibility, and Tooling
- **Reproducibility**: Package execution environments using containers or virtual environment specifications, applying the fixed-seed determinism standards owned by `data_analyst`.
- **Monitoring**: Implement logging for model predictions, inputs, and latency to monitor performance degradation and data drift in production.

## Related Skills
- Defer to `data_analyst` for pandas wrangling, scikit-learn pipelines, cross-validation, and notebook standards.
- Defer to `devops` for the CI/CD pipelines that ship and monitor models in production.
