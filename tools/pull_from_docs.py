#!/usr/bin/env python3
import os
import sys

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("Error: Missing Google API libraries.")
    print("Please run 'pip install -r requirements.txt' first.")
    sys.exit(1)

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.readonly",
]


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    token_path = os.path.join(repo_root, "token.json")
    personal_docs_dir = os.path.join(repo_root, "personal_docs")

    if not os.path.exists(personal_docs_dir):
        os.makedirs(personal_docs_dir)

    if not os.path.exists(token_path):
        print("Error: 'token.json' not found. You must authenticate first.")
        print("Please run 'python scripts/setup_google_docs_auth.py'")
        sys.exit(1)

    creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    try:
        drive_service = build("drive", "v3", credentials=creds)

        print("Fetching your most recent Google Docs...")
        # Search for Google Docs only
        query = "mimeType='application/vnd.google-apps.document'"
        results = (
            drive_service.files()
            .list(
                q=query,
                pageSize=10,
                fields="nextPageToken, files(id, name)",
                orderBy="modifiedTime desc",
            )
            .execute()
        )

        items = results.get("files", [])

        if not items:
            print("No Google Docs found.")
            return

        print(f"Found {len(items)} documents. Syncing to 'personal_docs/' directory...")

        for item in items:
            doc_id = item["id"]
            doc_name = item["name"].replace("/", "_")

            # Export the document as plain text
            request = drive_service.files().export_media(
                fileId=doc_id, mimeType="text/plain"
            )
            content = request.execute()

            file_path = os.path.join(personal_docs_dir, f"{doc_name}.txt")
            with open(file_path, "wb") as f:
                f.write(content)

            print(f"  ✓ Synced: {doc_name}")

        print(
            f"\nSuccess! Your documents have been safely synced to {personal_docs_dir}/"
        )
        print(
            "This folder is explicitly git-ignored to guarantee your personal data is never pushed to GitHub."
        )

    except HttpError as error:
        print(f"An error occurred: {error}")
        print(
            "If you recently updated scopes, you may need to delete 'token.json' and re-authenticate."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
