#!/usr/bin/env python3
import sys
import json
import struct
import subprocess
import os
import signal
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='server_host.log'
)

# Get the directory where this script is located and navigate to project root
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
APP_SCRIPT = PROJECT_ROOT / 'app.py'

def send_message(message):
    """Send a message to Chrome."""
    sys.stdout.buffer.write(struct.pack('I', len(message)))
    sys.stdout.buffer.write(message.encode('utf-8'))
    sys.stdout.buffer.flush()

def read_message():
    """Read a message from Chrome."""
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        return None
    message_length = struct.pack('I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode('utf-8')
    return json.loads(message)

def check_server_running():
    """Check if the Flask server is already running."""
    try:
        import requests
        response = requests.get('http://localhost:5000/health', timeout=2)
        return response.status_code == 200
    except:
        return False

def start_server():
    """Start the Flask server as a subprocess."""
    try:
        # Check if server is already running
        if check_server_running():
            logging.info("Server is already running")
            return True

        logging.info(f"Starting Flask server from {PROJECT_ROOT}")
        
        # Change to project directory
        os.chdir(PROJECT_ROOT)
        
        # Check if virtual environment exists and activate it
        venv_python = PROJECT_ROOT / 'venv' / 'Scripts' / 'python.exe'
        if venv_python.exists():
            python_executable = str(venv_python)
            logging.info("Using virtual environment Python")
        else:
            python_executable = sys.executable
            logging.info("Using system Python")
        
        # Start the server
        server_process = subprocess.Popen(
            [python_executable, str(APP_SCRIPT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW,
            cwd=str(PROJECT_ROOT)
        )
        
        # Wait for server to start
        logging.info("Waiting for server to start...")
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if check_server_running():
                logging.info("Server started successfully")
                return True
        
        logging.error("Server failed to start within timeout")
        return False
            
    except Exception as e:
        logging.error(f"Error starting server: {e}")
        return False

def main():
    """Main loop for native messaging host."""
    logging.info("Native messaging host started")
    
    while True:
        try:
            message = read_message()
            if message is None:
                break
                
            logging.info(f"Received message: {message}")
            
            if message.get('command') == 'start_server':
                success = start_server()
                response = {
                    'success': success,
                    'message': 'Server started successfully' if success else 'Failed to start server'
                }
                logging.info(f"Sending response: {response}")
                send_message(json.dumps(response))
            else:
                # Unknown command
                response = {
                    'success': False,
                    'message': f'Unknown command: {message.get("command")}'
                }
                send_message(json.dumps(response))
                
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            error_response = {
                'success': False,
                'message': f'Error: {str(e)}'
            }
            send_message(json.dumps(error_response))

if __name__ == '__main__':
    main() 