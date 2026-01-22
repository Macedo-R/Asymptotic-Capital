"""
Configuration module for Ising Quant System.
Loads settings from environment variables and .env file.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


class Config:
    """Configuration manager for the Ising Quant System."""

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            env_file: Path to .env file. If None, looks for .env in project root.
        """
        # Find project root (parent of python/ directory)
        self.project_root = Path(__file__).parent.parent.parent

        # Load environment variables
        if env_file:
            env_path = Path(env_file)
        else:
            env_path = self.project_root / ".env"

        if env_path.exists():
            load_dotenv(env_path)

        # Authentication settings
        self.google_auth_mode = os.getenv("GOOGLE_AUTH_MODE", "service_account")
        self.google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

        # Spreadsheet settings
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID", "")

        # Database settings
        self.output_db = os.getenv("OUTPUT_DB", "data/ising.db")

        # Risk settings
        self.risk_free_rate = float(os.getenv("RISK_FREE_RATE", "0.10"))

        # Cache settings
        self.cache_ttl = int(os.getenv("CACHE_TTL", "300"))

        # Ensure paths are absolute
        if self.google_credentials_path and not os.path.isabs(self.google_credentials_path):
            self.google_credentials_path = str(
                self.project_root / self.google_credentials_path
            )

        if not os.path.isabs(self.output_db):
            self.output_db = str(self.project_root / self.output_db)

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check auth mode
        if self.google_auth_mode not in ["service_account", "oauth"]:
            errors.append(
                f"Invalid GOOGLE_AUTH_MODE: {self.google_auth_mode}. "
                "Must be 'service_account' or 'oauth'."
            )

        # Check credentials path for service account
        if self.google_auth_mode == "service_account":
            if not self.google_credentials_path:
                errors.append("GOOGLE_APPLICATION_CREDENTIALS not set for service_account mode.")
            elif not os.path.exists(self.google_credentials_path):
                errors.append(
                    f"Credentials file not found: {self.google_credentials_path}"
                )

        # Check database directory exists
        db_dir = os.path.dirname(self.output_db)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create database directory {db_dir}: {e}")

        return len(errors) == 0, errors

    def __repr__(self) -> str:
        """String representation of config (safe - no secrets)."""
        return (
            f"Config("
            f"auth_mode={self.google_auth_mode}, "
            f"credentials={'***' if self.google_credentials_path else 'None'}, "
            f"spreadsheet_id={self.spreadsheet_id or 'Not set'}, "
            f"db={self.output_db}"
            f")"
        )
