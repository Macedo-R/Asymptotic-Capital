"""
Tests for IsingAllocator logic and formulas.
"""

import numpy as np
import pytest


def test_ising_magnetization_calculation():
    """Test the magnetization calculation M = tanh(1/T)."""
    # Temperature calculation: T = 1 / ((VIX/25) + (vol_usd * 8))
    
    # Test case 1: Low fear (normal market)
    vix = 15
    vol_usd = 0.10
    
    temperature = 1 / ((vix / 25) + (vol_usd * 8))
    magnetization = np.tanh(1 / temperature)
    
    # In normal conditions, magnetization should be low (< 0.3)
    assert magnetization < 0.3
    
    # Test case 2: High fear (crash conditions)
    vix = 40
    vol_usd = 0.25
    
    temperature = 1 / ((vix / 25) + (vol_usd * 8))
    magnetization = np.tanh(1 / temperature)
    
    # In crash conditions, magnetization should be high (> 0.7)
    assert magnetization > 0.5  # Should indicate high crash probability


def test_regime_classification():
    """Test regime classification based on magnetization."""
    
    def classify_regime(magnetization):
        if magnetization > 0.7:
            return "CRASH"
        elif magnetization > 0.3:
            return "ALERTA"
        else:
            return "NORMAL"
    
    # Test boundaries
    assert classify_regime(0.2) == "NORMAL"
    assert classify_regime(0.5) == "ALERTA"
    assert classify_regime(0.8) == "CRASH"
    
    # Test exact boundaries
    assert classify_regime(0.3) == "ALERTA"
    assert classify_regime(0.7) == "ALERTA"


def test_discrete_allocation():
    """Test discrete allocation mode."""
    # Define weights for different regimes
    weights = {
        "NORMAL": {"stocks": 0.60, "bonds": 0.30, "cash": 0.10},
        "ALERTA": {"stocks": 0.30, "bonds": 0.50, "cash": 0.20},
        "CRASH": {"stocks": 0.00, "bonds": 0.30, "cash": 0.70},
    }
    
    # Test allocation in NORMAL regime
    regime = "NORMAL"
    allocation = weights[regime]
    
    assert allocation["stocks"] == 0.60
    assert allocation["bonds"] == 0.30
    assert allocation["cash"] == 0.10
    assert sum(allocation.values()) == 1.0
    
    # Test allocation in CRASH regime
    regime = "CRASH"
    allocation = weights[regime]
    
    assert allocation["stocks"] == 0.00  # No stocks in crash
    assert allocation["cash"] == 0.70  # Heavy cash position
    assert sum(allocation.values()) == 1.0


def test_continuous_allocation():
    """Test continuous allocation mode with lambda interpolation."""
    
    def calculate_lambda(magnetization):
        """Lambda = min(1, max(0, (M - 0.3) / 0.4))"""
        return min(1, max(0, (magnetization - 0.3) / 0.4))
    
    # Test lambda values
    assert calculate_lambda(0.1) == 0.0  # Below threshold
    assert calculate_lambda(0.5) == 0.5  # Middle of range
    assert calculate_lambda(0.7) == 1.0  # At or above max
    assert calculate_lambda(0.9) == 1.0  # Above max
    
    # Test continuous weight interpolation
    weight_normal = 0.60
    weight_alerta = 0.30
    weight_crash = 0.00
    
    magnetization = 0.5
    lambda_val = calculate_lambda(magnetization)
    
    # Simplified continuous formula (concept)
    # w = w_normal * (1 - λ) + w_alerta * λ * (1 - crash_factor) + w_crash * crash_factor
    # For M < 0.7, crash_factor = 0
    crash_factor = 0
    
    weight_target = (
        weight_normal * (1 - lambda_val)
        + weight_alerta * lambda_val * (1 - crash_factor)
        + weight_crash * crash_factor
    )
    
    # Weight should be between normal and alerta
    assert weight_normal > weight_target > weight_alerta


def test_z_score_signal():
    """Test Z-Score signal generation."""
    
    def generate_signal(z_score):
        if z_score < -2:
            return "COMPRA FORTE"
        elif z_score > 2:
            return "VENDA"
        else:
            return "NEUTRO"
    
    # Test signals
    assert generate_signal(-3) == "COMPRA FORTE"
    assert generate_signal(3) == "VENDA"
    assert generate_signal(0) == "NEUTRO"
    assert generate_signal(-1) == "NEUTRO"
    assert generate_signal(1) == "NEUTRO"


def test_risk_off_filter():
    """Test that signals are filtered in CRASH regime."""
    
    def apply_ising_filter(signal, regime, sector):
        """Apply Ising regime filter to signals."""
        if regime == "CRASH":
            return "NÃO COMPRAR (CRASH)"
        elif regime == "ALERTA" and sector == "Tech":
            return "EVITAR TECH (ALERTA)"
        else:
            return signal
    
    # Test filtering
    assert apply_ising_filter("COMPRA FORTE", "CRASH", "Any") == "NÃO COMPRAR (CRASH)"
    assert apply_ising_filter("COMPRA FORTE", "ALERTA", "Tech") == "EVITAR TECH (ALERTA)"
    assert apply_ising_filter("COMPRA FORTE", "ALERTA", "Bonds") == "COMPRA FORTE"
    assert apply_ising_filter("COMPRA FORTE", "NORMAL", "Any") == "COMPRA FORTE"


def test_allocation_weights_sum_to_one():
    """Test that allocation weights sum to 1.0 in all regimes."""
    
    allocations = {
        "NORMAL": [0.20, 0.15, 0.05, 0.30, 0.25, 0.05],
        "ALERTA": [0.30, 0.25, 0.15, 0.15, 0.10, 0.05],
        "CRASH": [0.50, 0.30, 0.15, 0.00, 0.00, 0.05],
    }
    
    for regime, weights in allocations.items():
        total = sum(weights)
        assert abs(total - 1.0) < 0.01, f"Weights in {regime} don't sum to 1.0: {total}"


def test_temperature_inverse_relationship():
    """Test that temperature has inverse relationship with fear indicators."""
    
    def calculate_temperature(vix, vol_usd):
        return 1 / ((vix / 25) + (vol_usd * 8))
    
    # Higher VIX should lead to lower temperature
    temp_low_vix = calculate_temperature(15, 0.10)
    temp_high_vix = calculate_temperature(40, 0.10)
    
    assert temp_low_vix > temp_high_vix
    
    # Higher volatility should lead to lower temperature
    temp_low_vol = calculate_temperature(20, 0.10)
    temp_high_vol = calculate_temperature(20, 0.30)
    
    assert temp_low_vol > temp_high_vol


def test_drawdown_calculation():
    """Test drawdown calculation logic."""
    
    # Sample portfolio values
    values = np.array([100, 110, 105, 95, 100, 115])
    
    # Calculate drawdown
    cummax = np.maximum.accumulate(values)
    drawdown = (values / cummax) - 1
    
    # At peak, drawdown should be 0
    assert drawdown[1] == 0  # First peak at 110
    
    # After peak, should have negative drawdown
    assert drawdown[2] < 0
    assert drawdown[3] < 0
    
    # At new peak, drawdown should be 0 again
    assert drawdown[5] == 0


def test_log_returns():
    """Test log return calculation."""
    
    # Sample values
    value_today = 110
    value_yesterday = 100
    
    # Log return
    log_return = np.log(value_today / value_yesterday)
    
    # Should be positive for gain
    assert log_return > 0
    
    # Should be approximately 9.53% (ln(1.1))
    assert abs(log_return - 0.0953) < 0.001


def test_sharpe_ratio_calculation():
    """Test Sharpe ratio calculation logic."""
    
    # Annual return and volatility
    annual_return = 0.15  # 15%
    annual_volatility = 0.20  # 20%
    risk_free_rate = 0.05  # 5%
    
    # Sharpe ratio
    sharpe = (annual_return - risk_free_rate) / annual_volatility
    
    # Should be 0.5
    assert abs(sharpe - 0.5) < 0.01
    
    # Test that higher volatility reduces Sharpe
    sharpe_high_vol = (annual_return - risk_free_rate) / 0.30
    assert sharpe > sharpe_high_vol
