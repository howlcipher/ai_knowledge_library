---
name: "data_analyst"
description: "Explicit methodologies for pandas data wrangling, jupyter notebooks, and scikit-learn machine learning pipelines."
triggers:
  - "pandas"
  - "dataframe"
  - "jupyter"
  - "notebook"
  - "scikit-learn"
  - "data analysis"
tier: 2
---

# Data Analyst Skill

This skill defines and enforces core engineering standards, best practices, and methodologies for all data science, machine learning, and data analytics tasks.

## General Principles

1. **Reproducibility**: Always enforce determinism by setting a fixed random seed (e.g., `random_state=42` or `np.random.seed(42)`) for all machine learning models, train-test splits, bootstrapping, and synthetic data generation.
2. **Immutability**: Avoid modifying DataFrames in-place unless memory constraints strictly demand it. Prefer method chaining or assigning to new variables (e.g., `df_clean = df.dropna()`) to maintain a clear lineage of data transformations.
3. **Documentation**: Every Jupyter Notebook or Python analytics script must begin with a structured header (Markdown cell or module-level docstring) explaining the analytical objective, data sources, inputs, and expected outputs.

## Pandas Data Wrangling

- **Indexing and Assignment**: Always use `.loc` and `.iloc` explicitly for all slicing, filtering, and value assignments to prevent the `SettingWithCopyWarning` and ensure predictable behavior.
- **Vectorization**: Prioritize vectorized operations using pandas built-ins, NumPy functions, or `np.where()`. Avoid row-based iterations via `.iterrows()` or `.itertuples()` unless vectorization is mathematically or structurally impossible.
- **Data Quality**: Explicitly check for, document, and handle missing values (`NaN`), duplicates, and data type inconsistencies at the ingestion layer of the pipeline.

## Machine Learning and Statistical Modeling

- **Pipelines and Feature Engineering**: Enforce the use of `sklearn.pipeline.Pipeline` or `sklearn.pipeline.make_pipeline` to encapsulate data preprocessing (e.g., scaling, encoding) and estimation. Preprocessing transformations must be fit strictly on the training partition to avoid data leakage. Maintain standardized feature engineering transformation steps.
- **Validation**: Utilize cross-validation techniques (e.g., `cross_val_score`, `KFold`, `GridSearchCV`) for model evaluation and hyperparameter tuning. For time-series analysis or backtesting, employ specialized cross-validation (e.g., walk-forward optimization or purged cross-validation) and point-in-time data to avoid look-ahead and survivorship bias.
- **Evaluation Metrics**: Evaluate classification models using comprehensive metrics including Precision, Recall, F1-Score, and Confusion Matrices. For regression, compute and report RMSE, MAE, and R-squared. For financial or risk models, track metrics such as Value at Risk (VaR), Expected Shortfall (ES), and maximum drawdown thresholds.
- **Model Drift and Fairness**: Implement monitoring pipelines to log performance metrics over time and regularly check for data/model drift and subgroup bias.

## Jupyter Notebooks

- **Version Control**: Clear all output cells before committing notebook `.ipynb` files to version control. This prevents the exposure of sensitive data, reduces file size, and avoids large git diff noise.
- **Structure**: Keep notebook cells small, modular, and single-purpose. Consolidate all package imports, environment configurations, and global constants in the first code cell.
