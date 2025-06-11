from flask import Flask, request, jsonify
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import gspread
import os
import json
import logging
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Enable logging
logging.basicConfig(level=logging.INFO)

# Google Sheets API setup
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_credentials_from_token(token):
    return Credentials(
        token=token,
        refresh_token=None,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        scopes=SCOPES
    )

def create_new_spreadsheet(creds):
    service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Create new spreadsheet
    spreadsheet = {
        'properties': {
            'title': 'Job Application Tracker'
        },
        'sheets': [
            {
                'properties': {
                    'title': 'Applications',
                    'gridProperties': {
                        'rowCount': 1000,
                        'columnCount': 14
                    }
                }
            }
        ]
    }
    
    spreadsheet = service.spreadsheets().create(body=spreadsheet).execute()
    spreadsheet_id = spreadsheet['spreadsheetId']
    
    # Set up headers
    headers = [
        'A', 'Company Name', 'Job Title', 'Location', 'Recruiter',
        'Connections?', 'Email', 'Offered Pay', 'Offered Pay (Duplicate)',
        'Job Link', 'Date Applied', 'Status', 'Cover Letter', 'Notes'
    ]
    
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range='A1:N1',
        valueInputOption='RAW',
        body={'values': [headers]}
    ).execute()
    
    return spreadsheet_id

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/create-spreadsheet', methods=['POST'])
def create_spreadsheet():
    try:
        token = request.json.get('token')
        if not token:
            return jsonify({"error": "No token provided"}), 401
            
        creds = get_credentials_from_token(token)
        spreadsheet_id = create_new_spreadsheet(creds)
        
        return jsonify({"spreadsheetId": spreadsheet_id}), 200
    except Exception as e:
        logging.error(f"Error creating spreadsheet: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/submit-job', methods=['POST'])
def submit_job():
    try:
        data = request.json
        token = data.pop('token', None)
        if not token:
            return jsonify({"error": "No token provided"}), 401
            
        creds = get_credentials_from_token(token)
        client = gspread.authorize(creds)
        
        # Get the spreadsheet ID from the request
        spreadsheet_id = data.get('spreadsheetId')
        if not spreadsheet_id:
            return jsonify({"error": "No spreadsheet ID provided"}), 400
            
        sheet = client.open_by_key(spreadsheet_id).sheet1
        
        # Prepare row data
        row_data = [
            data.get('company_name', ''),
            data.get('job_title', ''),
            data.get('location', ''),
            data.get('recruiter', ''),
            data.get('connections', ''),
            data.get('email', ''),
            data.get('offered_pay', ''),
            data.get('offered_pay', ''),  # Duplicate
            f'=HYPERLINK("{data.get("job_url", "")}", "link")',
            data.get('date_applied', ''),
            data.get('status', ''),
            data.get('cover_letter', ''),
            data.get('notes', '')
        ]
        
        # Append row to sheet
        sheet.append_row(row_data)
        
        return jsonify({"message": "Job added successfully"}), 200
    except Exception as e:
        logging.error(f"Error submitting job: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
