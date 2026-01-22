"""
Ising Quant System - Quantitative Trading System using Ising Model Physics

A complete system for portfolio management that applies concepts from statistical
physics to dynamically adjust allocation based on market regimes.
"""

__version__ = "1.0.0"
__author__ = "Asymptotic Capital"

from ising_quant.config import Config
from ising_quant.google_auth import get_sheets_service
from ising_quant.report import ReportGenerator
from ising_quant.risk import RiskCalculator
from ising_quant.sheets_builder import SheetsBuilder
from ising_quant.sync import DataSync

__all__ = [
    "Config",
    "get_sheets_service",
    "SheetsBuilder",
    "DataSync",
    "RiskCalculator",
    "ReportGenerator",
]
