#!/usr/bin/env python3
import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def main():
    print("Push to docs started.")
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/documents'])
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            print("Successfully rotated Google Docs OAuth token!")
    print("Finished push_to_docs simulation.")

if __name__ == "__main__":
    main()
