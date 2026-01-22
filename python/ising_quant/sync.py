"""
Data synchronization module for Ising Quant System.
Downloads data from Google Sheets and saves to SQLite database.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from googleapiclient.discovery import Resource

from ising_quant.config import Config
from ising_quant.google_auth import get_sheets_service


class DataSync:
    """Synchronize data between Google Sheets and local storage."""

    def __init__(
        self,
        service: Optional[Resource] = None,
        config: Optional[Config] = None,
        spreadsheet_id: Optional[str] = None,
    ):
        """
        Initialize data sync.

        Args:
            service: Authenticated Sheets service. If None, creates from config.
            config: Configuration object. If None, creates new Config.
            spreadsheet_id: ID of spreadsheet to sync. Overrides config value.
        """
        self.config = config or Config()
        self.service = service or get_sheets_service(self.config)
        self.spreadsheet_id = spreadsheet_id or self.config.spreadsheet_id

        if not self.spreadsheet_id:
            raise ValueError("Spreadsheet ID not provided and not in config")

        # Ensure database directory exists
        db_path = Path(self.config.output_db)
        db_path.parent.mkdir(parents=True, exist_ok=True)

    def pull_all_data(self) -> dict[str, pd.DataFrame]:
        """
        Pull all data from spreadsheet.

        Returns:
            Dictionary mapping table names to DataFrames.
        """
        print(f"Syncing data from spreadsheet: {self.spreadsheet_id}")

        data = {}
        data["dailydata"] = self.pull_daily_data()
        data["summary"] = self.pull_portfolio_summary()

        # Save to database
        self.save_to_database(data)

        # Export to CSV
        self.export_to_csv(data)

        print("Data sync complete!")
        return data

    def pull_daily_data(self) -> pd.DataFrame:
        """
        Pull DailyData tab.

        Returns:
            DataFrame with daily transaction data.
        """
        print("Pulling DailyData...")

        result = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=self.spreadsheet_id, range="DailyData!A1:F")
            .execute()
        )

        values = result.get("values", [])

        if not values or len(values) < 2:
            print("No data found in DailyData")
            return pd.DataFrame()

        # First row is header
        df = pd.DataFrame(values[1:], columns=values[0])

        # Clean and convert types
        if not df.empty:
            # Remove completely empty rows
            df = df.dropna(how="all")

            # Convert date column
            if "Data" in df.columns:
                df["Data"] = pd.to_datetime(df["Data"], errors="coerce", dayfirst=True)

            # Convert numeric columns
            numeric_cols = ["Preço Unitário", "Quantidade", "Valor Total"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

        print(f"Pulled {len(df)} rows from DailyData")
        return df

    def pull_portfolio_summary(self) -> pd.DataFrame:
        """
        Pull PortfolioSummary tab.

        Returns:
            DataFrame with portfolio summary data.
        """
        print("Pulling PortfolioSummary...")

        result = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=self.spreadsheet_id, range="PortfolioSummary!A1:F")
            .execute()
        )

        values = result.get("values", [])

        if not values or len(values) < 2:
            print("No data found in PortfolioSummary")
            return pd.DataFrame()

        # First row is header
        df = pd.DataFrame(values[1:], columns=values[0])

        # Clean and convert types
        if not df.empty:
            # Remove completely empty rows
            df = df.dropna(how="all")

            # Convert date column
            if "Data" in df.columns:
                df["Data"] = pd.to_datetime(df["Data"], errors="coerce", dayfirst=True)

            # Convert numeric columns
            numeric_cols = [
                "Patrimônio Bruto",
                "Lucro Diário (R$)",
                "Retorno Log (%)",
                "Lucro Acumulado",
                "Drawdown",
            ]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

        print(f"Pulled {len(df)} rows from PortfolioSummary")
        return df

    def save_to_database(self, data: dict[str, pd.DataFrame]):
        """
        Save DataFrames to SQLite database.

        Args:
            data: Dictionary mapping table names to DataFrames.
        """
        print(f"Saving to database: {self.config.output_db}")

        conn = sqlite3.connect(self.config.output_db)

        try:
            # Save each table
            for table_name, df in data.items():
                if not df.empty:
                    df.to_sql(table_name, conn, if_exists="replace", index=False)
                    print(f"Saved {len(df)} rows to table '{table_name}'")

            # Create snapshot record
            snapshot_data = pd.DataFrame(
                [
                    {
                        "snapshot_date": datetime.now(),
                        "spreadsheet_id": self.spreadsheet_id,
                        "dailydata_rows": len(data.get("dailydata", [])),
                        "summary_rows": len(data.get("summary", [])),
                    }
                ]
            )
            snapshot_data.to_sql("snapshots", conn, if_exists="append", index=False)

            conn.commit()
            print("Database updated successfully")

        finally:
            conn.close()

    def export_to_csv(self, data: dict[str, pd.DataFrame]):
        """
        Export DataFrames to CSV files.

        Args:
            data: Dictionary mapping table names to DataFrames.
        """
        export_dir = Path(self.config.output_db).parent / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for table_name, df in data.items():
            if not df.empty:
                csv_path = export_dir / f"{table_name}_{timestamp}.csv"
                df.to_csv(csv_path, index=False)
                print(f"Exported {table_name} to {csv_path}")

    def get_latest_data(self, table_name: str) -> pd.DataFrame:
        """
        Read latest data from database.

        Args:
            table_name: Name of table to read.

        Returns:
            DataFrame with table data.
        """
        conn = sqlite3.connect(self.config.output_db)
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            return df
        except Exception as e:
            print(f"Error reading {table_name}: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
