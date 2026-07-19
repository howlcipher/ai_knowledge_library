---
name: "quantitative_finance"
description: "Mathematical modeling and algorithmic approaches to finance."
triggers:
  - "quant"
  - "backtest"
  - "algorithmic trading"
  - "time series"
  - "volatility"
tier: 3
---

# Quantitative Finance Methodologies

Standards and protocols for applying mathematical models, statistical analysis, and algorithmic strategies to financial markets, grounded in corporate financial theory and machine learning engineering.

## Modeling and Backtesting Rigor

### Backtesting and Data Preprocessing
- **Data Leakage and Bias**: Avoid look-ahead bias and survivorship bias by strictly partitioning in-sample and out-of-sample data. Use point-in-time datasets where available. Enforce strict data splitting protocols before feature engineering or scaling.
- **Overfitting Mitigation**: Penalize model complexity to prevent overfitting. Implement cross-validation techniques specifically designed for time-series data (e.g., walk-forward optimization, combinatorial purged cross-validation).

### Mathematical and Statistical Modeling
- **Stochastic Calculus and Valuation**: Apply stochastic processes (e.g., Geometric Brownian Motion, Mean-Reversion models) to asset pricing and risk management, integrating core financial theory concepts like the Capital Asset Pricing Model (CAPM) and Discounted Cash Flow (DCF).
- **Time-Series Analysis**: Utilize rigorous time-series methodologies (e.g., GARCH, ARIMA, cointegration testing) to model asset returns, volatility, and correlation structures.

## Strategy Implementation, Risk, and Evaluation
- **Algorithmic Execution**: Design algorithmic trading strategies with strict execution constraints, accounting for transaction costs, market impact, and latency.
- **Risk Control and Portfolio Performance**: Establish continuous risk monitoring, tracking metrics such as Value at Risk (VaR), Conditional Value at Risk (CVaR/Expected Shortfall), and maximum drawdown thresholds. Differentiate systematically between market, credit, liquidity, and operational risks.

## Related Skills
- Defer to `financial_theory` for valuation frameworks (CAPM, DCF) and risk-adjusted performance metrics (Sharpe, Sortino, Treynor).
- Defer to `data_analyst` for reproducibility, data splitting, and pipeline standards.
- Defer to `machine_learning` for production inference pipelines and model drift monitoring.
