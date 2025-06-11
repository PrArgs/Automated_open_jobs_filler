#!/usr/bin/env python3
import sys
import json
import struct
import subprocess
import os
import signal
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='server_host.log'
)

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()
SERVER_SCRIPT = SCRIPT_DIR.parent.parent / 'server.py'

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
    message_length = struct.unpack('I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode('utf-8')
    return json.loads(message)

def start_server():
    """Start the Flask server as a subprocess."""
    try:
        # Check if server is already running
        try:
            import requests
            response = requests.get('http://localhost:5000/health')
            if response.status_code == 200:
                return True
        except:
            pass

        # Start the server
        server_process = subprocess.Popen(
            [sys.executable, str(SERVER_SCRIPT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Wait a bit for the server to start
        import time
        time.sleep(2)
        
        # Check if server started successfully
        try:
            import requests
            response = requests.get('http://localhost:5000/health')
            if response.status_code == 200:
                return True
        except:
            return False
            
    except Exception as e:
        logging.error(f"Error starting server: {e}")
        return False

def main():
    """Main loop for native messaging host."""
    while True:
        message = read_message()
        if message is None:
            break
            
        if message.get('command') == 'start_server':
            success = start_server()
            send_message(json.dumps({
                'success': success,
                'message': 'Server started successfully' if success else 'Failed to start server'
            }))

if __name__ == '__main__':
    main() 