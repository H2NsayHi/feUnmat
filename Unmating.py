import webbrowser
from flask import Flask, send_from_directory
import time


app = Flask(__name__, static_folder='browser', static_url_path='')

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':

    webbrowser.open_new('http://localhost:5000')


    app.run(debug=True)