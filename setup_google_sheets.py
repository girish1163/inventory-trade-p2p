#!/usr/bin/env python3
"""
Setup script for Google Sheets integration
This script helps you set up Google Sheets for the inventory management system
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

def create_sample_credentials():
    """Create a sample credentials file for demonstration"""
    sample_credentials = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
    }
    
    with open('credentials.json', 'w') as f:
        json.dump(sample_credentials, f, indent=2)
    
    print("✅ Created sample credentials.json file")
    print("⚠️  You need to replace the sample values with your actual Google Cloud credentials")

def setup_instructions():
    """Print setup instructions"""
    print("""
🔧 Google Sheets Setup Instructions:

1. Create a Google Cloud Project:
   - Go to https://console.cloud.google.com/
   - Create a new project or use an existing one

2. Enable APIs:
   - Go to "APIs & Services" > "Library"
   - Enable "Google Sheets API"
   - Enable "Google Drive API"

3. Create Service Account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the details and create
   - Download the JSON credentials file
   - Rename it to 'credentials.json' and place it in the project root

4. Create Google Sheet:
   - Go to https://sheets.google.com
   - Create a new spreadsheet
   - Share the spreadsheet with your service account email
   - Copy the spreadsheet ID from the URL (between /d/ and /edit)

5. Update .env file:
   - Set GOOGLE_SHEETS_SPREADSHEET_ID to your spreadsheet ID
   - The credentials file should already be set as 'credentials.json'

6. Run the application:
   - pip install -r requirements.txt
   - python main.py

The system will automatically create the required worksheets:
- Users (for user accounts)
- Inventory (for inventory items)
- Transactions (for stock movements)

Default Login Credentials:
- User ID: 743663
- Password: girish7890@A
""")

if __name__ == "__main__":
    print("🚀 Google Sheets Setup for Inventory Management System")
    print("=" * 50)
    
    if not os.path.exists('credentials.json'):
        create_sample_credentials()
    else:
        print("✅ credentials.json already exists")
    
    setup_instructions()
