# Ising Quant System

A complete quantitative trading system that uses the Ising model physics concept for portfolio allocation. The system uses Google Sheets as the front-end/ledger and Python as the backend for automation, synchronization, and reporting.

## Overview

The Ising Quant System applies concepts from statistical physics (specifically the Ising model) to portfolio management. The system monitors market "temperature" (liquidity) and "magnetization" (crash probability) to dynamically adjust portfolio allocation between risk-on and risk-off assets.

## Features

- **IsingThermometer**: Real-time market regime detection (NORMAL/ALERTA/CRASH)
- **DailyData**: Automated price tracking for multiple assets including Tesouro Direto
- **PortfolioSummary**: Automatic portfolio aggregation with returns and drawdown tracking
- **Sinais**: Technical signals with Z-Score analysis and Ising regime filtering
- **RiskLab**: Portfolio risk metrics including VaR, Sharpe ratio, and correlation analysis
- **IsingAllocator**: Dynamic asset allocation based on market regime
- **Python CLI**: Automation tools for syncing, reporting, and analysis

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Google Cloud Platform account with Sheets API enabled
- Service account credentials or OAuth credentials

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Macedo-R/Asymptotic-Capital.git
cd Asymptotic-Capital
```

2. Install Python dependencies:
```bash
cd python
pip install -e .
```

3. Configure credentials:
```bash
cp .env.example .env
# Edit .env with your Google credentials path
```

4. Deploy Apps Script functions:
```bash
cd apps_script
# Follow instructions in apps_script/README.md
```

### Usage

#### Create a new spreadsheet:
```bash
isingctl init-sheet --title "My Ising Portfolio"
```

#### Push formulas to existing sheet:
```bash
isingctl push-formulas --spreadsheet-id YOUR_SHEET_ID
```

#### Sync data to local database:
```bash
isingctl pull --spreadsheet-id YOUR_SHEET_ID
```

#### Generate reports:
```bash
isingctl report --spreadsheet-id YOUR_SHEET_ID
```

## Documentation

- [Setup Guide](docs/SETUP.md) - Step-by-step configuration instructions
- [Formulas Reference](docs/FORMULAS.md) - All sheet formulas and calculations
- [Architecture](docs/ARCHITECTURE.md) - System architecture and data flow

## Project Structure

```
ising-quant-system/
├── README.md
├── docs/                      # Documentation
├── apps_script/              # Google Apps Script functions
├── python/                   # Python backend
│   └── ising_quant/         # Main package
├── tests/                    # Test suite
├── data/                     # Local data storage (not committed)
└── .github/workflows/       # CI/CD pipelines
```

## Testing

Run the test suite:
```bash
cd python
pytest tests/
```

## Contributing

This is a personal quantitative trading system. Please use it as reference for your own implementations.

## Disclaimer

This system is for educational and research purposes only. It does not constitute financial advice. Always do your own research and consult with a qualified financial advisor before making investment decisions.

## License

MIT License - See LICENSE file for details

## Author

Created as part of the Asymptotic Capital research project.
