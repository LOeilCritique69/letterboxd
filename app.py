import os
from flask import Flask, jsonify, send_from_directory
import json

app = Flask(__name__, static_folder='static')

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

@app.route("/api/films")
def films():
    with open('data.json', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
