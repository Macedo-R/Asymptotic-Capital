# Setup Guide - Ising Quant System

This guide walks you through setting up the Ising Quant System from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Google Cloud Setup](#google-cloud-setup)
3. [Python Environment](#python-environment)
4. [Apps Script Deployment](#apps-script-deployment)
5. [Running the System](#running-the-system)

## Prerequisites

- Python 3.11 or higher
- Google Account with access to Google Sheets
- Google Cloud Platform project
- Node.js and npm (for clasp deployment)

## Google Cloud Setup

### Option A: Service Account (Recommended for Automation)

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Note your Project ID

2. **Enable Google Sheets API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

3. **Create Service Account**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in name (e.g., "ising-quant-bot")
   - Click "Create and Continue"
   - Grant "Editor" role (or custom role with Sheets access)
   - Click "Done"

4. **Generate Key**:
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Select JSON format
   - Save the file as `service-account.json` in project root

5. **Share Spreadsheet**:
   - When you create a spreadsheet, share it with the service account email
   - Email format: `your-service-account@your-project.iam.gserviceaccount.com`
   - Give "Editor" permissions

### Option B: OAuth (For Local Development)

1. **Create OAuth Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Configure consent screen if prompted
   - Choose "Desktop app" as application type
   - Download credentials as `credentials.json`
   - Place in project root

2. **First Run**:
   - The system will open a browser for authentication
   - Authorize the application
   - Token will be saved as `token.json`

## Python Environment

1. **Create Virtual Environment**:
```bash
cd Asymptotic-Capital/python
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Package**:
```bash
pip install -e .
```

3. **Configure Environment**:
```bash
cd ..
cp .env.example .env
```

4. **Edit .env**:
```bash
# For Service Account
GOOGLE_AUTH_MODE=service_account
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json

# For OAuth
# GOOGLE_AUTH_MODE=oauth
# Place credentials.json in project root

# Will be filled after creating spreadsheet
SPREADSHEET_ID=

OUTPUT_DB=data/ising.db
RISK_FREE_RATE=0.10
```

## Apps Script Deployment

The Apps Script provides custom functions (TESOURO_DIRETO, CALC_VOL, Z_SCORE) for use in Google Sheets.

### Option 1: Manual Copy-Paste (Simplest)

1. Create or open your Google Sheet
2. Go to "Extensions" > "Apps Script"
3. Copy contents of `apps_script/Code.gs` into the editor
4. Click "Save" (disk icon)
5. Return to your sheet and use the custom functions

### Option 2: Using clasp (Advanced)

1. **Install clasp**:
```bash
npm install -g @google/clasp
```

2. **Login to Google**:
```bash
clasp login
```

3. **Create Apps Script Project**:
```bash
cd apps_script
clasp create --title "Ising Quant Functions" --type sheets
```

4. **Push Code**:
```bash
clasp push
```

5. **Open in Browser**:
```bash
clasp open
```

6. **Link to Spreadsheet**:
   - In Apps Script editor, go to "Project Settings"
   - Note the Script ID
   - Or manually connect via "Resources" > "Libraries"

### Verify Apps Script Functions

Test in your sheet:
```
=TESOURO_DIRETO("Tesouro IPCA+ 2035")
=CALC_VOL(A1:A100)
=Z_SCORE(100; A1:A100)
```

## Running the System

### 1. Create Initial Spreadsheet

```bash
isingctl init-sheet --title "Ising Quant Portfolio"
```

This will:
- Create a new Google Sheet with proper locale (pt_BR)
- Set timezone to America/Sao_Paulo
- Create all 6 tabs
- Apply all formulas
- Set formatting (frozen headers, number formats)
- Output the SPREADSHEET_ID

### 2. Update .env

Add the SPREADSHEET_ID to your `.env` file:
```
SPREADSHEET_ID=your_spreadsheet_id_here
```

### 3. Configure Apps Script

Follow the Apps Script deployment steps above to add custom functions.

### 4. Start Using the System

**Pull data to local database**:
```bash
isingctl pull --spreadsheet-id YOUR_SHEET_ID
```

**Generate reports**:
```bash
isingctl report --spreadsheet-id YOUR_SHEET_ID
```

**Re-apply formulas** (if you accidentally deleted them):
```bash
isingctl push-formulas --spreadsheet-id YOUR_SHEET_ID
```

## Troubleshooting

### "Permission denied" errors
- Verify service account has access to the spreadsheet
- Check that Sheets API is enabled in GCP

### Custom functions not working
- Ensure Apps Script is deployed and saved
- Refresh the spreadsheet
- Check Apps Script execution logs

### Import errors in Python
- Ensure virtual environment is activated
- Run `pip install -e .` from python/ directory

### Database errors
- Ensure data/ directory exists
- Check write permissions
- Delete `data/ising.db` and try again

## Next Steps

- See [FORMULAS.md](FORMULAS.md) for detailed formula reference
- See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Read the main [README.md](../README.md) for usage examples

## Support

For issues, please check:
1. Apps Script execution logs (View > Logs)
2. Python error messages
3. Google Sheets formula errors (red corners)

Remember: This is an educational system. Always verify calculations manually.
