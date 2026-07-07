#!/usr/bin/env python3
import os
import sys

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("Error: Missing Google API libraries.")
    print("Please run the global install script or 'pip install -r requirements.txt' first.")
    sys.exit(1)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents']

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    
    token_path = os.path.join(repo_root, 'token.json')
    creds_path = os.path.join(repo_root, 'credentials.json')
    
    creds = None
    
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                print("=" * 60)
                print("Error: 'credentials.json' not found!")
                print("=" * 60)
                print("To connect this library to Google Docs, you need an OAuth Client ID.")
                print("Please follow these steps:")
                print("  1. Go to the Google Cloud Console: https://console.cloud.google.com/")
                print("  2. Create a new project (or select an existing one).")
                print("  3. Go to 'APIs & Services' -> 'Library' and enable the 'Google Docs API'.")
                print("  4. Go to 'APIs & Services' -> 'Credentials'.")
                print("  5. Click 'Create Credentials' -> 'OAuth client ID'.")
                print("     (If prompted, configure the OAuth consent screen first)")
                print("  6. Choose Application type: 'Desktop app'.")
                print("  7. Click Create, then Download the JSON file.")
                print(f"  8. Rename it to 'credentials.json' and place it in: {repo_root}")
                print("  9. Run this script again.")
                print("=" * 60)
                sys.exit(1)

            # Initiate OAuth flow
            print("Initiating Google authentication flow. Check your web browser...")
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            
    print("\nAuthentication successful!")
    print(f"Your authorization has been securely saved to: {token_path}")
    print("Your library is now fully connected and authorized to push to Google Docs.")

if __name__ == '__main__':
    main()
