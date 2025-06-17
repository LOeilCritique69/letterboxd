from flask import Flask, jsonify, render_template
import json

app = Flask(__name__)

# Page principale
@app.route("/")
def home():
    return render_template("index.html")

# API pour récupérer les films notés
@app.route("/api/films")
def films():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
