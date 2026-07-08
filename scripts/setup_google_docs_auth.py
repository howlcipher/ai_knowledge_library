#!/usr/bin/env python3
"""
Google Docs Authentication Setup

This script sets up OAuth authentication for Google Docs API.
It handles creating/refreshing tokens and guides the user through
obtaining credentials if they are missing.
"""

import os
import sys

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("Error: Missing Google API libraries.")
    print(
        "Please run the global install script or 'pip install -r requirements.txt' first."
    )
    sys.exit(1)


class GoogleDocsAuthenticator:
    """Handles Google Docs API OAuth authentication flow."""

    SCOPES = [
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    def __init__(self, repo_root: str):
        """
        Initialize the authenticator with paths.

        Args:
            repo_root (str): The root directory of the repository.
        """
        self.repo_root = repo_root
        self.token_path = os.path.join(repo_root, "token.json")
        self.creds_path = os.path.join(repo_root, "credentials.json")

    def _load_existing_credentials(self) -> Credentials:
        """Load valid credentials from token file if it exists."""
        if os.path.exists(self.token_path):
            return Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        return None

    def _print_instructions(self):
        """Print instructions for setting up Google OAuth credentials."""
        print("=" * 60)
        print("Error: 'credentials.json' not found!")
        print("=" * 60)
        print("To connect this library to Google Docs, you need an OAuth Client ID.")
        print("Please follow these steps:")
        print("  1. Go to the Google Cloud Console: https://console.cloud.google.com/")
        print("  2. Create a new project (or select an existing one).")
        print(
            "  3. Go to 'APIs & Services' -> 'Library' and enable the 'Google Docs API'."
        )
        print(
            "  4. In the left sidebar under 'Google Auth Platform', click on 'Audience'."
        )
        print(
            "  5. Under the 'Test users' section, click '+ ADD USERS' and add your email address."
        )
        print("  6. Go to 'APIs & Services' -> 'Credentials'.")
        print("  7. Click 'Create Credentials' -> 'OAuth client ID'.")
        print("  8. Choose Application type: 'Desktop app'.")
        print("  9. Click Create, then Download the JSON file.")
        print(
            f"  10. Rename it to 'credentials.json' and place it in: {self.repo_root}"
        )
        print("  11. Run this script again.")
        print("=" * 60)

    def _perform_auth_flow(self) -> Credentials:
        """Perform the OAuth installed app flow."""
        if not os.path.exists(self.creds_path):
            self._print_instructions()
            sys.exit(1)

        print("Initiating Google authentication flow. Check your web browser...")
        flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, self.SCOPES)
        return flow.run_local_server(port=0)

    def authenticate(self):
        """Ensure valid credentials exist, prompting for login if necessary."""
        creds = self._load_existing_credentials()

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                creds = self._perform_auth_flow()

            # Save the credentials for the next run
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        print("\nAuthentication successful!")
        print(f"Your authorization has been securely saved to: {self.token_path}")
        print(
            "Your library is now fully connected and authorized to push to Google Docs."
        )


def main():
    """Main execution point for authentication script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)

    authenticator = GoogleDocsAuthenticator(repo_root)
    authenticator.authenticate()


if __name__ == "__main__":
    main()
