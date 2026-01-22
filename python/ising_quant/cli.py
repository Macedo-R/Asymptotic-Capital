"""
CLI interface for Ising Quant System.
Provides command-line tools for spreadsheet management and data sync.
"""

import webbrowser
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from ising_quant.config import Config
from ising_quant.google_auth import get_sheets_service, test_connection
from ising_quant.report import ReportGenerator
from ising_quant.sheets_builder import SheetsBuilder
from ising_quant.sync import DataSync

app = typer.Typer(
    name="isingctl",
    help="Ising Quant System - CLI tool for quantitative trading system management",
    add_completion=False,
)


@app.command()
def init_sheet(
    title: Annotated[str, typer.Option(help="Title for the new spreadsheet")] = "Ising Quant System",
):
    """
    Create a new Google Sheet with all tabs, formulas, and formatting.

    This command creates a complete spreadsheet configured for the Ising Quant System,
    including all 6 tabs with proper formulas in PT-BR format.
    """
    typer.echo("🚀 Initializing new Ising Quant System spreadsheet...")

    try:
        # Load config and authenticate
        config = Config()
        is_valid, errors = config.validate()

        if not is_valid:
            typer.echo("❌ Configuration errors:", err=True)
            for error in errors:
                typer.echo(f"  - {error}", err=True)
            raise typer.Exit(1)

        service = get_sheets_service(config)

        # Create spreadsheet
        builder = SheetsBuilder(service, config)
        spreadsheet_id = builder.create_spreadsheet(title)

        typer.echo(f"\n✅ Spreadsheet created successfully!")
        typer.echo(f"\n📋 Spreadsheet ID: {spreadsheet_id}")
        typer.echo(f"🔗 URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        typer.echo(f"\n💡 Add this ID to your .env file:")
        typer.echo(f"   SPREADSHEET_ID={spreadsheet_id}")

        if config.google_auth_mode == "service_account":
            typer.echo(f"\n⚠️  Remember to share the spreadsheet with your service account:")
            typer.echo(f"   (Check your service-account.json for the email)")

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def push_formulas(
    spreadsheet_id: Annotated[
        Optional[str], typer.Option(help="Spreadsheet ID (or use SPREADSHEET_ID from .env)")
    ] = None,
):
    """
    Push/reapply formulas and formatting to an existing spreadsheet.

    Use this command to restore formulas if they were accidentally deleted or modified.
    """
    typer.echo("📝 Pushing formulas to spreadsheet...")

    try:
        config = Config()

        # Use provided ID or fall back to config
        sheet_id = spreadsheet_id or config.spreadsheet_id

        if not sheet_id:
            typer.echo(
                "❌ No spreadsheet ID provided. Use --spreadsheet-id or set SPREADSHEET_ID in .env",
                err=True,
            )
            raise typer.Exit(1)

        service = get_sheets_service(config)
        builder = SheetsBuilder(service, config)

        builder.apply_all_formulas(sheet_id)

        typer.echo(f"✅ Formulas applied successfully!")
        typer.echo(f"🔗 View: https://docs.google.com/spreadsheets/d/{sheet_id}")

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def pull(
    spreadsheet_id: Annotated[
        Optional[str], typer.Option(help="Spreadsheet ID (or use SPREADSHEET_ID from .env)")
    ] = None,
):
    """
    Download data from Google Sheets and save to local database.

    Syncs DailyData and PortfolioSummary tabs to SQLite database and exports to CSV.
    """
    typer.echo("⬇️  Pulling data from Google Sheets...")

    try:
        config = Config()
        sheet_id = spreadsheet_id or config.spreadsheet_id

        if not sheet_id:
            typer.echo(
                "❌ No spreadsheet ID provided. Use --spreadsheet-id or set SPREADSHEET_ID in .env",
                err=True,
            )
            raise typer.Exit(1)

        service = get_sheets_service(config)
        sync = DataSync(service, config, sheet_id)

        data = sync.pull_all_data()

        typer.echo(f"\n✅ Data synchronized successfully!")
        typer.echo(f"💾 Database: {config.output_db}")

        # Show summary
        if "dailydata" in data and not data["dailydata"].empty:
            typer.echo(f"   - DailyData: {len(data['dailydata'])} rows")
        if "summary" in data and not data["summary"].empty:
            typer.echo(f"   - Summary: {len(data['summary'])} rows")

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def report(
    spreadsheet_id: Annotated[
        Optional[str], typer.Option(help="Spreadsheet ID (or use SPREADSHEET_ID from .env)")
    ] = None,
    open_browser: Annotated[
        bool, typer.Option("--open/--no-open", help="Open report in browser")
    ] = True,
):
    """
    Generate HTML and CSV reports from portfolio data.

    Downloads latest data, calculates risk metrics, and generates comprehensive reports.
    """
    typer.echo("📊 Generating reports...")

    try:
        config = Config()
        sheet_id = spreadsheet_id or config.spreadsheet_id

        if not sheet_id:
            typer.echo(
                "❌ No spreadsheet ID provided. Use --spreadsheet-id or set SPREADSHEET_ID in .env",
                err=True,
            )
            raise typer.Exit(1)

        # Sync data first
        service = get_sheets_service(config)
        sync = DataSync(service, config, sheet_id)
        data = sync.pull_all_data()

        # Generate reports
        report_gen = ReportGenerator(config)

        # HTML report
        html_path = report_gen.generate_html_report(
            data.get("dailydata", None), data.get("summary", None)
        )

        # CSV exports
        report_gen.generate_csv_exports(data.get("dailydata", None), data.get("summary", None))

        typer.echo(f"\n✅ Reports generated successfully!")
        typer.echo(f"📄 HTML Report: {html_path}")

        # Open in browser
        if open_browser:
            typer.echo("🌐 Opening report in browser...")
            webbrowser.open(f"file://{Path(html_path).absolute()}")

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def test_auth():
    """
    Test Google authentication and connection.

    Verifies that credentials are configured correctly and can connect to Google Sheets API.
    """
    typer.echo("🔐 Testing Google authentication...")

    try:
        config = Config()
        typer.echo(f"Configuration: {config}")

        is_valid, errors = config.validate()

        if not is_valid:
            typer.echo("\n❌ Configuration errors:")
            for error in errors:
                typer.echo(f"  - {error}")
            raise typer.Exit(1)

        typer.echo("✓ Configuration valid")

        # Test connection
        if test_connection(config):
            typer.echo("✅ Authentication successful!")
            typer.echo(f"   Mode: {config.google_auth_mode}")
        else:
            typer.echo("❌ Authentication failed", err=True)
            raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    from ising_quant import __version__

    typer.echo(f"Ising Quant System v{__version__}")
    typer.echo("Quantitative trading system using Ising model physics")


def main():
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
