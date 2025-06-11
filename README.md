# Job Application Tracker Chrome Extension

A Chrome extension that helps you track your job applications by automatically saving them to a Google Sheet.

## Setup Instructions

### 1. Environment Setup

1. Create a Python virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your Google OAuth2 credentials

### 2. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Sheets API and Google Drive API
4. Create OAuth2 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application" as the application type
   - Add authorized JavaScript origins:
     - `http://localhost:5000`
     - `chrome-extension://YOUR_EXTENSION_ID`
   - Add authorized redirect URIs:
     - `http://localhost:5000/oauth2callback`
     - `https://YOUR_EXTENSION_ID.chromiumapp.org/`
5. Download the credentials JSON file
6. Copy the credentials file to your project root as `credentials.json`
   - Use `example.credentials.json` as a template
   - Replace all placeholder values with your actual credentials

### 3. Extension Setup

1. Load the extension in Chrome:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the `chrome_extension` directory
   - Copy your extension ID from the extensions page

2. Install the native messaging host:
   - Windows: Create a registry key at:
     ```
     HKEY_CURRENT_USER\Software\Google\Chrome\NativeMessagingHosts\com.jobtracker.server
     ```
   - Set the default value to the path of your native host manifest

### 4. Usage

1. Click the extension icon when viewing a job posting
2. The job details will be automatically scraped
3. Review and edit the details if needed
4. Click "Submit" to save to your Google Sheet

## Development

- `server.py`: Main Flask server
- `job_tracker_gui.py`: GUI for manual job entry
- `chrome_extension/`: Chrome extension files
- `chrome_extension/native_host/`: Native messaging host for server management

## License

MIT License

