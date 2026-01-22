"""
Risk calculation module for Ising Quant System.
Calculates portfolio risk metrics from historical data.
"""

import numpy as np
import pandas as pd

from ising_quant.config import Config


class RiskCalculator:
    """Calculate portfolio risk metrics."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize risk calculator.

        Args:
            config: Configuration object. If None, creates new Config.
        """
        self.config = config or Config()

    def calculate_metrics(self, summary_df: pd.DataFrame) -> dict:
        """
        Calculate comprehensive risk metrics from portfolio summary.

        Args:
            summary_df: DataFrame with columns including 'Data', 'Patrimônio Bruto', 'Retorno Log (%)', etc.

        Returns:
            Dictionary of calculated metrics.
        """
        if summary_df.empty:
            return {}

        # Ensure data is sorted by date
        if "Data" in summary_df.columns:
            summary_df = summary_df.sort_values("Data").copy()

        metrics = {}

        # Portfolio value metrics
        if "Patrimônio Bruto" in summary_df.columns:
            values = summary_df["Patrimônio Bruto"].dropna()
            if len(values) > 0:
                metrics["current_value"] = float(values.iloc[-1])
                metrics["initial_value"] = float(values.iloc[0])
                metrics["total_return"] = (metrics["current_value"] / metrics["initial_value"]) - 1
                metrics["total_return_pct"] = metrics["total_return"] * 100

        # Drawdown metrics
        if "Drawdown" in summary_df.columns:
            drawdowns = summary_df["Drawdown"].dropna()
            if len(drawdowns) > 0:
                metrics["current_drawdown"] = float(drawdowns.iloc[-1])
                metrics["max_drawdown"] = float(drawdowns.min())
                metrics["current_drawdown_pct"] = metrics["current_drawdown"] * 100
                metrics["max_drawdown_pct"] = metrics["max_drawdown"] * 100

        # Return metrics
        if "Retorno Log (%)" in summary_df.columns:
            log_returns = summary_df["Retorno Log (%)"].dropna()
            if len(log_returns) > 1:
                # Daily volatility
                metrics["daily_volatility"] = float(log_returns.std())

                # Annualized volatility (252 trading days)
                metrics["annual_volatility"] = metrics["daily_volatility"] * np.sqrt(252)
                metrics["annual_volatility_pct"] = metrics["annual_volatility"] * 100

                # Mean daily return
                metrics["mean_daily_return"] = float(log_returns.mean())

                # Annualized return (from log returns)
                metrics["annual_return"] = metrics["mean_daily_return"] * 252
                metrics["annual_return_pct"] = metrics["annual_return"] * 100

        # Sharpe ratio
        if "annual_return" in metrics and "annual_volatility" in metrics:
            if metrics["annual_volatility"] > 0:
                metrics["sharpe_ratio"] = (
                    metrics["annual_return"] - self.config.risk_free_rate
                ) / metrics["annual_volatility"]
            else:
                metrics["sharpe_ratio"] = 0.0

        # Profit metrics
        if "Lucro Acumulado" in summary_df.columns:
            cumulative = summary_df["Lucro Acumulado"].dropna()
            if len(cumulative) > 0:
                metrics["cumulative_profit"] = float(cumulative.iloc[-1])

        if "Lucro Diário (R$)" in summary_df.columns:
            daily_profit = summary_df["Lucro Diário (R$)"].dropna()
            if len(daily_profit) > 0:
                metrics["avg_daily_profit"] = float(daily_profit.mean())
                metrics["total_days"] = len(daily_profit)
                metrics["winning_days"] = int((daily_profit > 0).sum())
                metrics["losing_days"] = int((daily_profit < 0).sum())
                if metrics["total_days"] > 0:
                    metrics["win_rate"] = metrics["winning_days"] / metrics["total_days"]
                    metrics["win_rate_pct"] = metrics["win_rate"] * 100

        # Date range
        if "Data" in summary_df.columns:
            dates = summary_df["Data"].dropna()
            if len(dates) > 0:
                metrics["start_date"] = dates.iloc[0].strftime("%Y-%m-%d")
                metrics["end_date"] = dates.iloc[-1].strftime("%Y-%m-%d")
                metrics["days_elapsed"] = (dates.iloc[-1] - dates.iloc[0]).days

        return metrics

    def calculate_drawdown_series(self, values: pd.Series) -> pd.Series:
        """
        Calculate drawdown series from portfolio values.

        Args:
            values: Series of portfolio values.

        Returns:
            Series of drawdown values (negative percentages).
        """
        cummax = values.expanding().max()
        drawdown = (values / cummax) - 1
        return drawdown

    def calculate_var(
        self, returns: pd.Series, confidence_level: float = 0.95, horizon_days: int = 1
    ) -> float:
        """
        Calculate Value at Risk (VaR) using historical method.

        Args:
            returns: Series of returns (not log returns).
            confidence_level: Confidence level (e.g., 0.95 for 95% VaR).
            horizon_days: Number of days for VaR calculation.

        Returns:
            VaR value (positive number representing potential loss).
        """
        if len(returns) < 2:
            return 0.0

        # Sort returns
        sorted_returns = returns.sort_values()

        # Find percentile
        percentile = 1 - confidence_level
        var = -sorted_returns.quantile(percentile)

        # Adjust for horizon
        if horizon_days > 1:
            var = var * np.sqrt(horizon_days)

        return float(var)

    def format_metrics(self, metrics: dict) -> str:
        """
        Format metrics as readable string.

        Args:
            metrics: Dictionary of calculated metrics.

        Returns:
            Formatted string representation.
        """
        if not metrics:
            return "No metrics available"

        lines = ["Portfolio Risk Metrics", "=" * 50]

        # Value metrics
        if "current_value" in metrics:
            lines.append(f"Current Value: R$ {metrics['current_value']:,.2f}")
        if "initial_value" in metrics:
            lines.append(f"Initial Value: R$ {metrics['initial_value']:,.2f}")
        if "total_return_pct" in metrics:
            lines.append(f"Total Return: {metrics['total_return_pct']:.2f}%")

        lines.append("")

        # Risk metrics
        if "annual_volatility_pct" in metrics:
            lines.append(f"Annual Volatility: {metrics['annual_volatility_pct']:.2f}%")
        if "max_drawdown_pct" in metrics:
            lines.append(f"Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
        if "current_drawdown_pct" in metrics:
            lines.append(f"Current Drawdown: {metrics['current_drawdown_pct']:.2f}%")

        lines.append("")

        # Performance metrics
        if "annual_return_pct" in metrics:
            lines.append(f"Annual Return: {metrics['annual_return_pct']:.2f}%")
        if "sharpe_ratio" in metrics:
            lines.append(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        if "win_rate_pct" in metrics:
            lines.append(f"Win Rate: {metrics['win_rate_pct']:.2f}%")

        lines.append("")

        # Period info
        if "start_date" in metrics and "end_date" in metrics:
            lines.append(f"Period: {metrics['start_date']} to {metrics['end_date']}")
        if "days_elapsed" in metrics:
            lines.append(f"Days: {metrics['days_elapsed']}")

        return "\n".join(lines)


from typing import Optional  # Add missing import at top
