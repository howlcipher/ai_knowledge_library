---
name: data_analyst
description: Explicit methodologies for pandas data wrangling, jupyter notebooks, and scikit-learn machine learning pipelines.
---

# Data Analyst Skill

This skill enforces best practices for any data science, machine learning, or analytics task within the library.

## General Principles
1. **Reproducibility**: Always set a random seed (`random_state=42`) for reproducibility across all machine learning models, train-test splits, and synthetic data generation.
2. **Immutability**: Avoid modifying dataframes in place unless strictly necessary for memory efficiency. Prefer chaining methods or assigning to new variables (e.g., `df_clean = df.dropna()`).
3. **Documentation**: Every Jupyter Notebook or Python analytics script must start with a markdown block or docstring explaining the objective, inputs, and expected outputs.

## Pandas Data Wrangling
*   Use `.loc` and `.iloc` explicitly for all slicing and indexing to avoid `SettingWithCopyWarning`.
*   Vectorize operations using `.apply()`, `np.where()`, or native pandas mathematical operations rather than iterating through rows with `.iterrows()`.
*   Always check for and explicitly handle missing values (`NaN`) and duplicates early in the pipeline.

## Machine Learning (Scikit-Learn)
*   **Pipelines**: Always use `sklearn.pipeline.Pipeline` to bundle preprocessing (e.g., `StandardScaler`, `OneHotEncoder`) with estimators. Never fit the scaler on the entire dataset before splitting.
*   **Validation**: Use `cross_val_score` or `GridSearchCV` for hyperparameter tuning. Never tune hyperparameters based on the hold-out test set performance.
*   **Evaluation**: Beyond accuracy, always evaluate models using Precision, Recall, F1-Score, and Confusion Matrices for classification, and RMSE/MAE for regression.

## Jupyter Notebooks
*   If writing `.ipynb` files, ensure output cells are cleared before committing to GitHub to prevent exposing sensitive data and to minimize git diff noise.
*   Keep cells small and modular. Import all libraries in the very first cell.
