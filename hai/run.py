import subprocess
import threading
import time
import os
import webbrowser
from flask import Flask, send_from_directory
import sys

# Update these paths to use relative paths based on the executable location
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the current directory of the script
FRONTEND_BUILD_DIR = os.path.join(CURRENT_DIR, 'browser')  # Point to the 'browser' directory in the executable
CONFIG_FILE_PATH = os.path.join(CURRENT_DIR, 'config.json')  # Path to 'config.json'

# Command to run the backend API using Python
BACKEND_API_COMMAND = [sys.executable, os.path.join(CURRENT_DIR, 'api.py')]  # Use sys.executable to get the Python interpreter
FRONTEND_URL = 'http://localhost:5000'

# Create Flask app to serve the Angular build
app = Flask(__name__, static_folder=FRONTEND_BUILD_DIR)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

def run_frontend():
    print("Starting the Flask server to serve the Angular frontend...")
    app.run(host='0.0.0.0', port=5000)

def run_backend():
    print("Starting the backend API server...")
    subprocess.Popen(BACKEND_API_COMMAND)  # Run api.py using the Python interpreter

if __name__ == '__main__':
    # Create threads to run both frontend and backend concurrently
    frontend_thread = threading.Thread(target=run_frontend)
    backend_thread = threading.Thread(target=run_backend)

    # Start the frontend and backend servers
    frontend_thread.start()
    time.sleep(2)  # Optional delay to ensure the frontend starts before backend
    backend_thread.start()

    # Open the web browser explicitly to a known path
    try:
        # Specify the path for Google Chrome
        chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
        webbrowser.get(chrome_path).open(FRONTEND_URL)
    except Exception as e:
        print(f"Error opening the web browser: {e}")
        # Fallback to another known browser if necessary

    # Keep the main thread alive to allow servers to run
    frontend_thread.join()
    backend_thread.join()
