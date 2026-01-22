# Architecture - Ising Quant System

This document describes the system architecture and data flow.

## Overview

The Ising Quant System is a hybrid architecture combining Google Sheets as a user-facing interface with Python backend services for automation and analysis.

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                          │
│                    (Google Sheets)                           │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
│  │  Ising     │ │  Daily     │ │ Portfolio  │              │
│  │Thermometer │ │   Data     │ │  Summary   │    + 3 more  │
│  └────────────┘ └────────────┘ └────────────┘              │
└─────────────────────────────────────────────────────────────┘
          │                    ▲
          │ Real-time          │ Formulas & Updates
          │ Calculations       │
          ▼                    │
┌─────────────────────────────────────────────────────────────┐
│                   APPS SCRIPT LAYER                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Custom Functions (Google Apps Script)              │   │
│  │  - TESOURO_DIRETO(nome_titulo)                      │   │
│  │  - CALC_VOL(prices_range)                           │   │
│  │  - Z_SCORE(current_price, history_range)            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
          │                    ▲
          │ External APIs      │ Read/Write
          │ (Tesouro, etc)     │ via Sheets API
          ▼                    │
┌─────────────────────────────────────────────────────────────┐
│                    PYTHON BACKEND                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  CLI Tool (isingctl)                                │   │
│  │  - init-sheet: Create spreadsheet                   │   │
│  │  - push-formulas: Apply formulas                    │   │
│  │  - pull: Download data                              │   │
│  │  - report: Generate reports                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ sheets_      │  │    sync.py   │  │   risk.py    │     │
│  │ builder.py   │  │              │  │              │     │
│  │ (Create &    │  │ (Download    │  │ (Calculate   │     │
│  │  Configure)  │  │  to SQLite)  │  │  Metrics)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ google_      │  │  report.py   │                        │
│  │ auth.py      │  │              │                        │
│  │ (OAuth/SA)   │  │ (Generate    │                        │
│  │              │  │  HTML/CSV)   │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
          │                    ▲
          │ Persist            │ Query
          ▼                    │
┌─────────────────────────────────────────────────────────────┐
│                   PERSISTENCE LAYER                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  SQLite Database (data/ising.db)                    │   │
│  │  Tables: dailydata, summary, snapshots              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  File Exports                                       │   │
│  │  - exports/*.csv                                    │   │
│  │  - reports/*.html                                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### 1. Google Sheets Layer (User Interface)

**Purpose**: Interactive front-end for data entry, visualization, and real-time calculations.

**Components**:
- **IsingThermometer**: Monitors market regime (NORMAL/ALERTA/CRASH)
- **DailyData**: Manual entry of transactions and positions
- **PortfolioSummary**: Automatic aggregation of portfolio value by date
- **Sinais**: Technical signals with Z-Score analysis
- **RiskLab**: Portfolio risk metrics (VaR, Sharpe, correlation)
- **IsingAllocator**: Dynamic allocation based on market regime

**Key Features**:
- Locale: pt_BR (Brazilian Portuguese)
- Timezone: America/Sao_Paulo
- Formulas use `;` separator and PT-BR function names
- Real-time updates via GOOGLEFINANCE
- Frozen headers for better navigation

**Data Flow**:
- User enters data manually in DailyData
- Formulas automatically calculate derived metrics
- Apps Script custom functions provide additional data sources
- Python backend reads data via Sheets API

### 2. Apps Script Layer (Custom Functions)

**Purpose**: Extend Google Sheets with custom data sources and calculations.

**Components**:
- **TESOURO_DIRETO(nome_titulo)**: Fetches Brazilian treasury bond prices
  - Uses UrlFetchApp to call Tesouro Direto API
  - Returns current unit price
  - Includes caching to reduce API calls

- **CALC_VOL(prices_range)**: Calculates annualized volatility
  - Computes log returns from price series
  - Annualizes using √252 factor
  - Returns standard deviation

- **Z_SCORE(current_price, history_range)**: Statistical deviation
  - Calculates mean and std dev from history
  - Returns (current - mean) / std dev
  - Used for mean reversion signals

**Implementation Details**:
- Written in Google Apps Script (JavaScript)
- Deployed via manual copy-paste or clasp
- Uses CacheService for performance
- Includes error handling and logging

**Data Flow**:
- Called from sheet formulas
- Fetches external data (Tesouro API)
- Returns values to cells
- Updates on recalculation

### 3. Python Backend Layer (Automation & Analysis)

**Purpose**: Automate spreadsheet creation, sync data locally, perform advanced analysis.

**Architecture**:

```
ising_quant/
├── __init__.py          # Package initialization
├── config.py            # Configuration from .env
├── google_auth.py       # Authentication (OAuth/Service Account)
├── sheets_builder.py    # Create and configure spreadsheets
├── sync.py              # Download data to SQLite
├── risk.py              # Calculate risk metrics
├── report.py            # Generate HTML/CSV reports
└── cli.py               # CLI interface (Typer)
```

**Module Responsibilities**:

**config.py**:
- Reads .env file
- Validates configuration
- Provides settings object

**google_auth.py**:
- Supports two auth modes:
  - Service Account (recommended for automation)
  - OAuth (for local development)
- Returns authenticated Google Sheets service

**sheets_builder.py**:
- Creates new spreadsheet with proper locale/timezone
- Creates all 6 tabs
- Applies headers and formulas
- Sets formatting (number formats, frozen rows)
- Can reapply formulas to existing sheets

**sync.py**:
- Reads DailyData and PortfolioSummary ranges
- Converts to pandas DataFrames
- Saves to SQLite database
- Exports to CSV for backup

**risk.py**:
- Calculates additional metrics:
  - Sharpe ratio
  - Maximum drawdown
  - Daily volatility
  - Cumulative returns
- Uses pandas for calculations
- Returns metrics dictionary

**report.py**:
- Generates HTML reports with:
  - Portfolio summary table
  - Risk metrics
  - Performance charts (via Jinja2 templates)
- Exports CSV files
- Saves to reports/ directory

**cli.py**:
- Typer-based CLI tool
- Commands:
  - `init-sheet`: Create new spreadsheet
  - `push-formulas`: Reapply formulas
  - `pull`: Download data to SQLite
  - `report`: Generate reports
- Handles argument parsing and execution

**Data Flow**:
1. User runs CLI command
2. Authenticates with Google
3. Operates on spreadsheet via Sheets API
4. Downloads data to local storage
5. Generates reports and exports

### 4. Persistence Layer (Local Storage)

**Purpose**: Store historical data locally for analysis and reporting.

**Components**:

**SQLite Database** (data/ising.db):
- **dailydata** table: All transactions and positions
  - Columns: date, asset, unit_price, quantity, total_value, notes
- **summary** table: Aggregated portfolio values
  - Columns: date, gross_equity, daily_profit, log_return, cumulative_profit, drawdown
- **snapshots** table: Point-in-time captures
  - Columns: snapshot_date, data (JSON)

**File Exports**:
- **exports/*.csv**: Data dumps for backup
- **reports/*.html**: Human-readable reports
- **.gitignore**: Excludes from version control

**Data Flow**:
- Python sync.py writes to database
- Python risk.py/report.py read from database
- SQLite provides local query capabilities
- CSV exports for external analysis

## Authentication Flows

### Service Account Flow (Recommended)

```
1. Create service account in Google Cloud Console
2. Download JSON key → service-account.json
3. Enable Sheets API
4. Share spreadsheet with service account email
5. Python reads credentials from JSON
6. Authenticates via google-auth library
7. Makes API calls with service account identity
```

**Pros**:
- No user interaction needed
- Works in automated scripts
- Consistent credentials

**Cons**:
- Requires GCP project
- Must share each sheet manually

### OAuth Flow (Local Development)

```
1. Create OAuth client ID in Google Cloud Console
2. Download credentials.json
3. First run: Opens browser for user consent
4. User authorizes application
5. Token saved to token.json
6. Subsequent runs: Uses saved token
7. Token auto-refreshes when expired
```

**Pros**:
- Easy for local development
- No need to share sheets
- Uses user's own permissions

**Cons**:
- Requires user interaction
- Token expires
- Not suitable for automation

## Data Flow Examples

### Creating a New Spreadsheet

```
User runs: isingctl init-sheet --title "My Portfolio"
    │
    ├─> cli.py parses arguments
    │
    ├─> google_auth.py authenticates
    │
    ├─> sheets_builder.py:
    │   ├─> Creates spreadsheet with pt_BR locale
    │   ├─> Creates 6 tabs
    │   ├─> Writes headers
    │   ├─> Applies formulas (PT-BR with ;)
    │   ├─> Sets number formatting
    │   └─> Freezes header rows
    │
    └─> Returns spreadsheet ID to user
```

### Syncing Data

```
User runs: isingctl pull --spreadsheet-id ABC123
    │
    ├─> cli.py parses arguments
    │
    ├─> google_auth.py authenticates
    │
    ├─> sync.py:
    │   ├─> Reads DailyData range (A:F)
    │   ├─> Converts to pandas DataFrame
    │   ├─> Reads PortfolioSummary range (A:F)
    │   ├─> Converts to DataFrame
    │   ├─> Opens SQLite connection
    │   ├─> Writes to dailydata table
    │   ├─> Writes to summary table
    │   ├─> Exports to CSV
    │   └─> Closes connection
    │
    └─> Confirms success to user
```

### Generating Reports

```
User runs: isingctl report --spreadsheet-id ABC123
    │
    ├─> cli.py parses arguments
    │
    ├─> sync.py: Downloads latest data
    │
    ├─> risk.py:
    │   ├─> Reads from SQLite
    │   ├─> Calculates Sharpe ratio
    │   ├─> Calculates max drawdown
    │   ├─> Calculates volatility
    │   └─> Returns metrics dict
    │
    ├─> report.py:
    │   ├─> Loads Jinja2 template
    │   ├─> Renders HTML with metrics
    │   ├─> Saves to reports/report_YYYY-MM-DD.html
    │   ├─> Exports summary CSV
    │   └─> Exports detailed CSV
    │
    └─> Opens report in browser
```

## Technology Stack

### Frontend
- **Google Sheets**: UI and real-time calculations
- **Apps Script**: Custom functions (JavaScript)

### Backend
- **Python 3.11+**: Core language
- **google-api-python-client**: Sheets API client
- **google-auth**: Authentication
- **gspread**: Alternative Sheets wrapper (optional)
- **pandas**: Data manipulation
- **numpy**: Numerical calculations
- **typer**: CLI framework
- **python-dotenv**: Environment variables
- **jinja2**: Template rendering
- **pytest**: Testing framework

### Storage
- **SQLite**: Local relational database
- **CSV**: Data exports
- **HTML**: Report outputs

### DevOps
- **GitHub Actions**: CI/CD
- **clasp**: Apps Script deployment tool
- **pytest**: Automated testing

## Security Considerations

### Credentials Management
- Never commit credentials to git
- Use .env for configuration
- .gitignore excludes sensitive files
- Service account keys require secure storage

### API Access
- Use minimum required scopes
- Service account limits access to shared sheets only
- OAuth requires explicit user consent

### Data Privacy
- Local database not shared
- Reports stored locally
- No data sent to external services (except Google APIs)

### Best Practices
- Rotate service account keys regularly
- Use separate credentials for dev/prod
- Audit API access logs
- Review sharing permissions on sheets

## Scaling Considerations

### Current Architecture
- Suitable for personal use
- Single-user focused
- Local storage
- Synchronous operations

### Future Enhancements (if needed)
- **Multi-user**: Add user authentication
- **Cloud Database**: Replace SQLite with PostgreSQL
- **Web UI**: Add Flask/FastAPI web interface
- **Real-time**: WebSocket updates from sheets
- **Async**: Use asyncio for concurrent operations
- **Caching**: Redis for frequently accessed data
- **Queue**: Celery for background jobs

## Deployment

### Local Development
1. Clone repository
2. Install Python dependencies
3. Configure .env
4. Run CLI commands

### Production/Automation
1. Deploy to server (VPS, cloud instance)
2. Use service account authentication
3. Schedule with cron:
   ```
   # Daily sync at 6 PM
   0 18 * * * cd /path/to/repo && isingctl pull --spreadsheet-id ABC123
   
   # Weekly report on Sunday
   0 9 * * 0 cd /path/to/repo && isingctl report --spreadsheet-id ABC123
   ```
4. Monitor logs
5. Set up alerts for failures

## Monitoring

### Apps Script
- View execution logs in Apps Script editor
- Monitor quota usage (UrlFetchApp calls)
- Set up error notifications

### Python
- Use logging module
- Write logs to files
- Monitor disk usage (SQLite growth)
- Track API quota (Sheets API has daily limits)

### Alerts
- Email on job failures
- Slack/Discord webhooks for notifications
- Dashboard for key metrics

## Testing Strategy

### Unit Tests
- Test individual functions
- Mock external dependencies
- Fast execution

### Integration Tests
- Test API interactions
- Use test spreadsheet
- Slower but comprehensive

### Manual Testing
- Create test spreadsheet
- Run through workflows
- Verify formulas calculate correctly

## Maintenance

### Regular Tasks
- Update dependencies
- Review and rotate credentials
- Archive old reports
- Vacuum SQLite database
- Check for formula errors in sheets

### Backup Strategy
- SQLite database backed up daily
- CSV exports provide redundancy
- Google Sheets has version history
- Consider offsite backup for critical data

## Documentation

- **README.md**: Quick start and overview
- **docs/SETUP.md**: Step-by-step configuration
- **docs/FORMULAS.md**: All sheet formulas
- **docs/ARCHITECTURE.md**: This document
- **apps_script/README.md**: Apps Script deployment
- **Code comments**: Inline documentation
- **Docstrings**: Python function documentation

## Support and Troubleshooting

### Common Issues
1. **Authentication errors**: Check credentials and permissions
2. **Formula errors**: Verify PT-BR syntax with `;`
3. **API quota exceeded**: Wait or request increase
4. **Database locked**: Close other connections
5. **Import errors**: Check Python environment

### Debug Mode
- Enable logging in Python
- Check Apps Script execution logs
- Use `--verbose` flag in CLI
- Test with minimal dataset first

## Conclusion

The Ising Quant System combines the flexibility of Google Sheets with the power of Python automation. The layered architecture allows for:
- User-friendly interface (Sheets)
- Real-time calculations (formulas + Apps Script)
- Advanced analysis (Python)
- Local persistence (SQLite)
- Automated workflows (CLI + cron)

This architecture is suitable for individual traders and small teams managing quantitative portfolios.
