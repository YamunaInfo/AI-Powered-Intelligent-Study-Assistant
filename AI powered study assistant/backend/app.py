from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.notes_routes import notes_bp
from routes.ai_routes import ai_bp
from routes.profile_routes import profile_bp
import database
import mysql.connector

app = Flask(__name__)

# Fix CORS - allow requests from Live Server (port 5500) and any localhost
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

@app.route("/")
def home():
    return "Backend is running 🚀"

@app.route("/health")
def health_check():
    return {"status": "ok", "backend": "running"}, 200

@app.route("/health/db")
def health_check_db():
    """Check database connectivity"""
    try:
        db = mysql.connector.connect(
            host='localhost',
