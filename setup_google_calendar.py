#!/usr/bin/env python3
"""
Google Calendar Setup Script
Sets up OAuth credentials for Google Calendar integration
"""

import os
import sys
from pathlib import Path

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    import pickle
except ImportError:
    print("Error: Google Calendar libraries not installed.")
    print("Run: pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)


SCOPES = ['https://www.googleapis.com/auth/calendar']


def setup_calendar_credentials():
    """Set up Google Calendar API credentials"""
    credentials_file = Path.home() / '.ollama_calendar_credentials.json'
    token_file = Path.home() / '.ollama_calendar_token.pickle'

    print("=" * 70)
    print("Google Calendar Setup for Ollama Multi-Agent Assistant")
    print("=" * 70)
    print()

    # Check if credentials file exists
    if not credentials_file.exists():
        print("⚠️  Credentials file not found!")
        print()
        print("To set up Google Calendar integration, you need to:")
        print()
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create a new project (or select existing)")
        print("3. Enable the Google Calendar API")
        print("4. Go to 'Credentials' → 'Create Credentials' → 'OAuth client ID'")
        print("5. Select 'Desktop app' as application type")
        print("6. Download the credentials JSON file")
        print("7. Save it as: ~/.ollama_calendar_credentials.json")
        print()
        print(f"Expected location: {credentials_file}")
        print()
        return False

    print(f"✓ Found credentials file: {credentials_file}")
    print()
    print("Starting OAuth flow...")
    print("A browser window will open for you to authorize the application.")
    print()

    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_file), SCOPES)
        creds = flow.run_local_server(port=0)

        # Save credentials
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

        print()
        print("=" * 70)
        print("✓ SUCCESS! Google Calendar is now configured.")
        print("=" * 70)
        print()
        print(f"Token saved to: {token_file}")
        print()
        print("You can now use the calendar agent to:")
        print("  - Create events")
        print("  - List upcoming events")
        print("  - Delete events")
        print()
        print("Try asking:")
        print('  "Create a meeting tomorrow at 2pm"')
        print('  "What events do I have this week?"')
        print()
        return True

    except Exception as e:
        print()
        print(f"❌ Error during setup: {e}")
        print()
        return False


def test_calendar_access():
    """Test if calendar access is working"""
    token_file = Path.home() / '.ollama_calendar_token.pickle'

    if not token_file.exists():
        print("No token file found. Run setup first.")
        return False

    try:
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

        service = build('calendar', 'v3', credentials=creds)

        # Try to list calendars
        calendar_list = service.calendarList().list().execute()

        print("✓ Calendar access is working!")
        print()
        print("Available calendars:")
        for calendar in calendar_list.get('items', []):
            print(f"  - {calendar['summary']}")
        print()
        return True

    except Exception as e:
        print(f"❌ Error testing calendar access: {e}")
        return False


def main():
    """Main setup function"""
    print()

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_calendar_access()
    else:
        success = setup_calendar_credentials()
        if success:
            print("Testing calendar access...")
            print()
            test_calendar_access()


if __name__ == "__main__":
    main()
