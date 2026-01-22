"""
Tests for risk calculation module.
"""

import numpy as np
import pandas as pd
import pytest

from ising_quant.risk import RiskCalculator


@pytest.fixture
def sample_summary_data():
    """Create sample portfolio summary data for testing."""
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    
    # Simulate portfolio values with some volatility and drift
    np.random.seed(42)
    initial_value = 100000
    returns = np.random.normal(0.001, 0.02, 100)  # Daily returns
    values = initial_value * np.exp(np.cumsum(returns))
    
    # Calculate other metrics
    log_returns = np.diff(np.log(values))
    log_returns = np.insert(log_returns, 0, 0)  # First day has no return
    
    daily_profit = np.diff(values)
    daily_profit = np.insert(daily_profit, 0, 0)
    
    cumulative_profit = np.cumsum(daily_profit)
    
    # Calculate drawdown
    cummax = np.maximum.accumulate(values)
    drawdown = (values / cummax) - 1
    
    df = pd.DataFrame({
        "Data": dates,
        "Patrimônio Bruto": values,
        "Lucro Diário (R$)": daily_profit,
        "Retorno Log (%)": log_returns,
        "Lucro Acumulado": cumulative_profit,
        "Drawdown": drawdown,
    })
    
    return df


def test_calculate_metrics_basic(sample_summary_data):
    """Test that calculate_metrics returns expected keys."""
    calc = RiskCalculator()
    metrics = calc.calculate_metrics(sample_summary_data)
    
    # Check that key metrics are present
    assert "current_value" in metrics
    assert "initial_value" in metrics
    assert "total_return" in metrics
    assert "max_drawdown" in metrics
    assert "annual_volatility" in metrics
    assert "sharpe_ratio" in metrics


def test_calculate_metrics_values(sample_summary_data):
    """Test that calculated metrics have reasonable values."""
    calc = RiskCalculator()
    metrics = calc.calculate_metrics(sample_summary_data)
    
    # Initial value should be around 100000
    assert 95000 < metrics["initial_value"] < 105000
    
    # Sharpe ratio should be a reasonable number
    assert -5 < metrics["sharpe_ratio"] < 10
    
    # Max drawdown should be negative
    assert metrics["max_drawdown"] < 0
    
    # Annual volatility should be positive
    assert metrics["annual_volatility"] > 0


def test_calculate_drawdown_series():
    """Test drawdown calculation."""
    calc = RiskCalculator()
    
    # Simple test case: rising then falling values
    values = pd.Series([100, 110, 105, 95, 100])
    drawdown = calc.calculate_drawdown_series(values)
    
    # At peak (index 1), drawdown should be 0
    assert drawdown.iloc[1] == 0
    
    # After peak, drawdown should be negative
    assert drawdown.iloc[2] < 0
    assert drawdown.iloc[3] < 0


def test_calculate_var():
    """Test Value at Risk calculation."""
    calc = RiskCalculator()
    
    # Create sample returns
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.01, 0.05, 1000))
    
    # Calculate VaR at 95% confidence
    var = calc.calculate_var(returns, confidence_level=0.95)
    
    # VaR should be positive
    assert var > 0
    
    # VaR should be less than the worst return in absolute terms
    assert var < abs(returns.min())


def test_empty_dataframe():
    """Test that empty DataFrame is handled gracefully."""
    calc = RiskCalculator()
    empty_df = pd.DataFrame()
    
    metrics = calc.calculate_metrics(empty_df)
    
    # Should return empty dict
    assert metrics == {}


def test_format_metrics(sample_summary_data):
    """Test metrics formatting."""
    calc = RiskCalculator()
    metrics = calc.calculate_metrics(sample_summary_data)
    
    formatted = calc.format_metrics(metrics)
    
    # Should return a string
    assert isinstance(formatted, str)
    
    # Should contain some key information
    assert "Portfolio Risk Metrics" in formatted
    assert "Current Value" in formatted or "Sharpe Ratio" in formatted


def test_win_rate_calculation(sample_summary_data):
    """Test win rate calculation."""
    calc = RiskCalculator()
    metrics = calc.calculate_metrics(sample_summary_data)
    
    # Win rate should be between 0 and 100%
    if "win_rate_pct" in metrics:
        assert 0 <= metrics["win_rate_pct"] <= 100
        
        # With random data, should be around 50%
        assert 30 <= metrics["win_rate_pct"] <= 70


def test_risk_free_rate_impact():
    """Test that risk-free rate affects Sharpe ratio."""
    # Create simple profitable portfolio
    dates = pd.date_range("2024-01-01", periods=252, freq="D")
    returns = np.full(252, 0.001)  # Constant 0.1% daily return
    values = 100000 * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame({
        "Data": dates,
        "Patrimônio Bruto": values,
        "Retorno Log (%)": returns,
    })
    
    # Calculate with different risk-free rates
    from ising_quant.config import Config
    
    config_low = Config()
    config_low.risk_free_rate = 0.05
    calc_low = RiskCalculator(config_low)
    metrics_low = calc_low.calculate_metrics(df)
    
    config_high = Config()
    config_high.risk_free_rate = 0.15
    calc_high = RiskCalculator(config_high)
    metrics_high = calc_high.calculate_metrics(df)
    
    # Higher risk-free rate should result in lower Sharpe ratio
    if "sharpe_ratio" in metrics_low and "sharpe_ratio" in metrics_high:
        assert metrics_low["sharpe_ratio"] > metrics_high["sharpe_ratio"]
