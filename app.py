from flask import Flask, request, jsonify
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import logging
from flask_cors import CORS
import subprocess
import sys
import os
from flask import jsonify
import threading
import time

app = Flask(__name__)
CORS(app)  # <-- Allow cross-origin requests

# Enable logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flask_server.log'),
        logging.StreamHandler()
    ]
)

# Google Sheets setup
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SERVICE_ACCOUNT_FILE = "credentials.json"

# Global variable to track if server is starting
server_starting = False

try:
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open("Visual Job Tracker").sheet1
    logging.info("Google Sheets connection established")
except Exception as e:
    logging.error(f"Google Sheets setup failed: {e}")
    sheet = None

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for the extension to verify server is running."""
    logging.info("Health check requested")
    return jsonify({"status": "healthy", "message": "Flask server is running"}), 200

@app.route("/start-server", methods=["POST"])
def start_server():
    """Endpoint to start the Flask server if it's not already running."""
    global server_starting
    
    if server_starting:
        return jsonify({"message": "Server is already starting up"}), 200
    
    try:
        server_starting = True
        logging.info("Server startup requested")
        
        # Start the job tracker GUI in a separate thread
        def start_gui():
            try:
                subprocess.Popen([sys.executable, "job_tracker_gui.py"], 
                               cwd=os.getcwd(),
                               creationflags=subprocess.CREATE_NO_WINDOW)
                logging.info("Job tracker GUI started successfully")
            except Exception as e:
                logging.error(f"Failed to start GUI: {e}")
        
        # Start GUI in background thread
        gui_thread = threading.Thread(target=start_gui, daemon=True)
        gui_thread.start()
        
        return jsonify({"message": "Server startup initiated", "success": True}), 200
        
    except Exception as e:
        server_starting = False
        logging.error(f"Error starting server: {e}")
        return jsonify({"error": f"Failed to start server: {str(e)}"}), 500
    finally:
        # Reset flag after a delay
        def reset_flag():
            time.sleep(5)
            server_starting = False
        
        reset_thread = threading.Thread(target=reset_flag, daemon=True)
        reset_thread.start()

@app.route("/submit-url", methods=["POST"])
def submit_url():
    data = request.json
    job_url = data.get("url", "")
    logging.info(f"Job URL submitted: {job_url}")

    try:
        # Call the GUI app and pass the URL as a command line argument
        subprocess.Popen([sys.executable, "job_tracker_gui.py", job_url], 
                        cwd=os.getcwd(),
                        creationflags=subprocess.CREATE_NO_WINDOW)
        logging.info("Job tracker GUI launched successfully")
        return jsonify({"message": "Job URL submitted successfully! GUI launched."}), 200
    except Exception as e:
        logging.error(f"Error launching GUI: {e}")
        return jsonify({"error": f"Failed: {str(e)}"}), 500

@app.route("/create-spreadsheet", methods=["POST"])
def create_spreadsheet():
    """Create a new spreadsheet for the user."""
    try:
        if sheet is None:
            return jsonify({"error": "Google Sheets not configured"}), 500
        
        # Create a new spreadsheet
        new_sheet = client.create("Job Application Tracker")
        new_sheet.share('', perm_type='anyone', role='writer')
        
        # Set up basic structure
        worksheet = new_sheet.sheet1
        worksheet.update('A1', 'Job URL')
        worksheet.update('B1', 'Date Applied')
        worksheet.update('C1', 'Company')
        worksheet.update('D1', 'Position')
        worksheet.update('E1', 'Status')
        
        logging.info(f"New spreadsheet created: {new_sheet.id}")
        return jsonify({
            "spreadsheetId": new_sheet.id,
            "message": "Spreadsheet created successfully"
        }), 200
        
    except Exception as e:
        logging.error(f"Error creating spreadsheet: {e}")
        return jsonify({"error": f"Failed to create spreadsheet: {str(e)}"}), 500

if __name__ == "__main__":
    logging.info("Starting Flask server...")
    logging.info(f"Server will be available at: http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)
