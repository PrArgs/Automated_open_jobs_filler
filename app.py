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

app = Flask(__name__)
CORS(app)  # <-- Allow cross-origin requests

# Enable logging
logging.basicConfig(level=logging.INFO)

# Google Sheets setup
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SERVICE_ACCOUNT_FILE = "credentials.json"

try:
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open("Visual Job Tracker").sheet1
except Exception as e:
    logging.error(f"Google Sheets setup failed: {e}")
    sheet = None



@app.route("/submit-url", methods=["POST"])
def submit_url():
    data = request.json
    job_url = data.get("url", "")

    try:
        # Call the GUI app and pass the URL as a command line argument
        subprocess.Popen([sys.executable, "job_tracker_gui.py", job_url], cwd=os.getcwd())
        return jsonify({"message": "GUI launched"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"Failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
