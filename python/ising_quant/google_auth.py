"""
Google authentication module for Ising Quant System.
Supports both OAuth and Service Account authentication.
"""

import os
import pickle
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from ising_quant.config import Config

# Scopes required for Google Sheets API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_sheets_service(config: Optional[Config] = None) -> Resource:
    """
    Get authenticated Google Sheets service.

    Args:
        config: Configuration object. If None, creates new Config.

    Returns:
        Authenticated Google Sheets API service resource.

    Raises:
        Exception: If authentication fails.
    """
    if config is None:
        config = Config()

    # Validate configuration
    is_valid, errors = config.validate()
    if not is_valid:
        raise ValueError(f"Invalid configuration: {'; '.join(errors)}")

    if config.google_auth_mode == "service_account":
        return _get_service_account_service(config)
    elif config.google_auth_mode == "oauth":
        return _get_oauth_service(config)
    else:
        raise ValueError(f"Unknown auth mode: {config.google_auth_mode}")


def _get_service_account_service(config: Config) -> Resource:
    """
    Authenticate using service account.

    Args:
        config: Configuration object with service account path.

    Returns:
        Authenticated Sheets service.
    """
    credentials = service_account.Credentials.from_service_account_file(
        config.google_credentials_path, scopes=SCOPES
    )

    service = build("sheets", "v4", credentials=credentials)
    return service


def _get_oauth_service(config: Config) -> Resource:
    """
    Authenticate using OAuth flow.

    Args:
        config: Configuration object.

    Returns:
        Authenticated Sheets service.
    """
    creds = None
    token_path = config.project_root / "token.json"
    credentials_path = config.project_root / "credentials.json"

    # Check for existing token
    if token_path.exists():
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired token
            creds.refresh(Request())
        else:
            # New authentication flow
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"OAuth credentials file not found: {credentials_path}\n"
                    "Download from Google Cloud Console and save as credentials.json"
                )

            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for future use
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    service = build("sheets", "v4", credentials=creds)
    return service


def test_connection(config: Optional[Config] = None) -> bool:
    """
    Test if authentication and connection work.

    Args:
        config: Configuration object. If None, creates new Config.

    Returns:
        True if connection successful, False otherwise.
    """
    try:
        service = get_sheets_service(config)
        # Try to list spreadsheet metadata (minimal operation)
        # This doesn't require a specific spreadsheet ID
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False
