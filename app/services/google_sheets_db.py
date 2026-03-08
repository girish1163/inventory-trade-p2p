import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

load_dotenv()

class GoogleSheetsDB:
    def __init__(self):
        self.scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.credentials = None
        self.client = None
        self.spreadsheet = None
        self.worksheets = {}
        
    async def connect(self):
        """Initialize connection to Google Sheets"""
        try:
            # Try to load credentials from file
            credentials_file = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE")
            
            if os.path.exists(credentials_file):
                self.credentials = Credentials.from_service_account_file(
                    credentials_file, scopes=self.scope
                )
            else:
                # For demo purposes, create a simple credentials structure
                # In production, you need proper Google Cloud credentials
                print("⚠️  Google Sheets credentials file not found. Using mock mode.")
                return False
                
            self.client = gspread.authorize(self.credentials)
            
            spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
            if spreadsheet_id == "your_spreadsheet_id_here":
                print("⚠️  Please set GOOGLE_SHEETS_SPREADSHEET_ID in .env file")
                return False
                
            self.spreadsheet = self.client.open_by_key(spreadsheet_id)
            
            # Initialize worksheets
            await self._init_worksheets()
            
            print("✅ Connected to Google Sheets successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error connecting to Google Sheets: {e}")
            return False
    
    async def _init_worksheets(self):
        """Initialize required worksheets if they don't exist"""
        try:
            # List of required worksheets
            required_worksheets = ['Users', 'Inventory', 'Transactions']
            
            existing_worksheets = [worksheet.title for worksheet in self.spreadsheet.worksheets()]
            
            for worksheet_name in required_worksheets:
                if worksheet_name not in existing_worksheets:
                    worksheet = self.spreadsheet.add_worksheet(title=worksheet_name, rows="1000", cols="20")
                    await self._setup_worksheet_headers(worksheet, worksheet_name)
                    print(f"✅ Created worksheet: {worksheet_name}")
                else:
                    self.worksheets[worksheet_name] = self.spreadsheet.worksheet(worksheet_name)
                    print(f"✅ Found existing worksheet: {worksheet_name}")
                    
        except Exception as e:
            print(f"❌ Error initializing worksheets: {e}")
    
    async def _setup_worksheet_headers(self, worksheet, worksheet_name):
        """Setup headers for different worksheets"""
        if worksheet_name == 'Users':
            headers = ['id', 'username', 'email', 'password_hash', 'role', 'created_at']
        elif worksheet_name == 'Inventory':
            headers = ['id', 'name', 'sku', 'description', 'category', 'quantity', 
                      'min_stock_level', 'max_stock_level', 'unit_price', 'supplier', 
                      'location', 'status', 'created_at', 'last_updated']
        elif worksheet_name == 'Transactions':
            headers = ['id', 'inventory_item_id', 'type', 'quantity', 'reference', 
                      'notes', 'user_id', 'created_at']
        else:
            return
            
        worksheet.append_row(headers)
        self.worksheets[worksheet_name] = worksheet
    
    def get_worksheet(self, name: str):
        """Get a worksheet by name"""
        return self.worksheets.get(name)
    
    async def get_all_records(self, worksheet_name: str) -> List[Dict[str, Any]]:
        """Get all records from a worksheet"""
        try:
            worksheet = self.get_worksheet(worksheet_name)
            if not worksheet:
                return []
                
            records = worksheet.get_all_records()
            return records
        except Exception as e:
            print(f"❌ Error getting records from {worksheet_name}: {e}")
            return []
    
    async def get_record_by_id(self, worksheet_name: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific record by ID"""
        try:
            worksheet = self.get_worksheet(worksheet_name)
            if not worksheet:
                return None
                
            records = worksheet.get_all_records()
            for record in records:
                if str(record.get('id')) == str(record_id):
                    return record
            return None
        except Exception as e:
            print(f"❌ Error getting record {record_id} from {worksheet_name}: {e}")
            return None
    
    async def add_record(self, worksheet_name: str, record: Dict[str, Any]) -> bool:
        """Add a new record to a worksheet"""
        try:
            worksheet = self.get_worksheet(worksheet_name)
            if not worksheet:
                return False
                
            # Convert record to row format
            headers = worksheet.row_values(1)
            row = []
            for header in headers:
                row.append(record.get(header, ''))
                
            worksheet.append_row(row)
            return True
        except Exception as e:
            print(f"❌ Error adding record to {worksheet_name}: {e}")
            return False
    
    async def update_record(self, worksheet_name: str, record_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update an existing record"""
        try:
            worksheet = self.get_worksheet(worksheet_name)
            if not worksheet:
                return False
                
            records = worksheet.get_all_records()
            headers = worksheet.row_values(1)
            
            for i, record in enumerate(records, start=2):  # Start from row 2 (after headers)
                if str(record.get('id')) == str(record_id):
                    # Update the record
                    for j, header in enumerate(headers):
                        if header in updated_data:
                            worksheet.update_cell(i, j + 1, updated_data[header])
                    return True
                    
            return False
        except Exception as e:
            print(f"❌ Error updating record {record_id} in {worksheet_name}: {e}")
            return False
    
    async def delete_record(self, worksheet_name: str, record_id: str) -> bool:
        """Delete a record by ID"""
        try:
            worksheet = self.get_worksheet(worksheet_name)
            if not worksheet:
                return False
                
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, start=2):  # Start from row 2 (after headers)
                if str(record.get('id')) == str(record_id):
                    worksheet.delete_rows(i)
                    return True
                    
            return False
        except Exception as e:
            print(f"❌ Error deleting record {record_id} from {worksheet_name}: {e}")
            return False

# Global instance
db = GoogleSheetsDB()

async def get_db():
    """Get database instance"""
    return db
