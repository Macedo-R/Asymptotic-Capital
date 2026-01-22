# Apps Script Deployment Guide

This directory contains Google Apps Script code that provides custom functions for the Ising Quant System.

## Custom Functions

The script provides three custom functions:

1. **TESOURO_DIRETO(nome_titulo)** - Fetches Brazilian Treasury bond prices
2. **CALC_VOL(prices_range)** - Calculates annualized volatility
3. **Z_SCORE(current_price, history_range)** - Calculates Z-Score

## Deployment Options

### Option 1: Manual Copy-Paste (Recommended for Beginners)

1. Open your Google Sheet
2. Go to **Extensions** > **Apps Script**
3. Delete any existing code
4. Copy the entire contents of `Code.gs`
5. Paste into the editor
6. Click the **Save** icon (disk icon)
7. Close the Apps Script tab
8. Return to your sheet and refresh

Your custom functions are now available!

### Option 2: Using clasp (Advanced)

[clasp](https://github.com/google/clasp) is Google's command-line tool for Apps Script.

#### Prerequisites

- Node.js and npm installed
- Google account with Apps Script enabled

#### Setup

1. **Install clasp globally**:
```bash
npm install -g @google/clasp
```

2. **Enable Apps Script API**:
   - Go to https://script.google.com/home/usersettings
   - Enable "Google Apps Script API"

3. **Login to clasp**:
```bash
clasp login
```
This opens a browser window for authentication.

#### Deploy to New Project

```bash
cd apps_script
clasp create --title "Ising Quant Functions" --type standalone
clasp push
clasp open
```

#### Deploy to Existing Sheet

If you already have a spreadsheet:

```bash
cd apps_script
# Get the script ID from your sheet: Extensions > Apps Script > Project Settings
clasp clone YOUR_SCRIPT_ID
clasp push
```

#### Update Existing Deployment

After making changes to Code.gs:

```bash
cd apps_script
clasp push
```

## Usage Examples

Once deployed, use the functions in your Google Sheet:

### TESOURO_DIRETO
```
=TESOURO_DIRETO("Tesouro IPCA+ 2035")
=TESOURO_DIRETO("Tesouro Selic 2027")
```

### CALC_VOL
```
=CALC_VOL(A2:A100)
=CALC_VOL(DailyData!C2:C50)
```

### Z_SCORE
```
=Z_SCORE(100; A2:A100)
=Z_SCORE(B2; QUERY(GOOGLEFINANCE(A2; "price"; HOJE()-30; HOJE()); "select Col2"))
```

## Testing

To test the functions from Apps Script editor:

1. Open Apps Script editor
2. Select function `testCustomFunctions` from dropdown
3. Click **Run** (play icon)
4. Check **View** > **Logs** for output

## Troubleshooting

### "Unknown function" error
- Ensure the script is saved
- Refresh your spreadsheet (Ctrl+R or Cmd+R)
- Check for typos in function name

### "Loading..." never finishes
- Check Apps Script execution logs (View > Logs in editor)
- Verify UrlFetchApp has permissions
- Check API endpoint is accessible

### "Authorization required" error
- Run the function once from Apps Script editor
- Grant necessary permissions when prompted
- Return to sheet and try again

### Tesouro Direto returns 0
- Check if the bond name is correct
- Verify Tesouro Direto API is accessible
- Check execution logs for specific errors

### Volatility calculation issues
- Ensure price range contains valid numbers
- Need at least 2 data points
- Check for empty cells or text in range

## Cache Management

The script caches Tesouro Direto prices for 5 minutes to improve performance and reduce API calls.

To clear the cache manually:
1. Open Apps Script editor
2. Select function `clearCache` from dropdown
3. Click **Run**

## Performance Considerations

- **TESOURO_DIRETO**: Cached for 5 minutes, one API call per unique bond
- **CALC_VOL**: Processes data in Apps Script, fast for ranges up to ~1000 rows
- **Z_SCORE**: Lightweight calculation, fast for any reasonable range

## Limitations

- Apps Script has execution time limits (30 seconds for custom functions)
- UrlFetchApp has daily quota limits
- Custom functions cannot make side effects (write to sheets, send emails)
- Functions recalculate when sheet changes

## Files in This Directory

- **Code.gs**: Main script with custom functions
- **appsscript.json**: Project manifest and settings
- **README.md**: This file

## Support

If you encounter issues:

1. Check Apps Script execution logs (View > Logs)
2. Verify the function syntax is correct
3. Ensure necessary permissions are granted
4. Check Google Apps Script status page for outages

## License

Part of the Ising Quant System - MIT License
