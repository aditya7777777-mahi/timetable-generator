import os
import sys
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, PyMongoError
from bson.objectid import ObjectId
import datetime
from collections import defaultdict

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='../client', static_url_path='/')
CORS(app)

# MongoDB connection
db = None
def init_db():
    global db
    try:
        mongo_uri = os.environ.get('MONGODB_URI', "mongodb+srv://adityabasude13:13777adi@cluster0.4weinpi.mongodb.net/")
        db_name = os.environ.get('DB_NAME', 'timetable_db')
        
        print(f"Connecting to MongoDB at: {mongo_uri}")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Force a connection to verify it works
        client.server_info()
        print("Connected to MongoDB successfully!")
        db = client[db_name]
        return True
    except ServerSelectionTimeoutError:
        print("Failed to connect to MongoDB: Connection timed out")
        return False
    except PyMongoError as e:
        print(f"Failed to connect to MongoDB: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error connecting to MongoDB: {e}")
        return False

# Initialize database connection
if not init_db():
    print("Error: Could not connect to MongoDB. Please check your connection and try again.")
    sys.exit(1)

# Initialize models with the database
def init_models():
    try:
        from api.models.base_model import BaseModel
        from api.models.department import Department
        from api.models.teacher import Teacher
        from api.models.subject import Subject
        from api.models.room import Room
        from api.models.timetable import Timetable
        
        Department.initialize(db)
        Teacher.initialize(db)
        Subject.initialize(db)
        Room.initialize(db)
        Timetable.initialize(db)
        print("Database models initialized successfully!")
    except Exception as e:
        print(f"Error initializing models: {e}")
        sys.exit(1)

# Import routes (after database setup)
from api.routes.departments import departments
from api.routes.teachers import teachers
from api.routes.subjects import subjects
from api.routes.rooms import rooms
from api.routes.timetables import timetables

# Register blueprints
app.register_blueprint(departments)
app.register_blueprint(teachers)
app.register_blueprint(subjects)
app.register_blueprint(rooms)
app.register_blueprint(timetables)

# Home route - serves the frontend
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

@app.route('/api/departments', methods=['GET'])
def get_departments():
    try:
        if db is None:
            return jsonify({'error': 'Database connection not available'}), 500
        departments = list(db.departments.find())
        return jsonify(departments), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/teachers', methods=['GET'])
def get_teachers():
    try:
        if db is None:
            return jsonify({'error': 'Database connection not available'}), 500
        teachers = list(db.teachers.find())
        return jsonify(teachers), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    try:
        if db is None:
            return jsonify({'error': 'Database connection not available'}), 500
        subjects = list(db.subjects.find())
        return jsonify(subjects), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    try:
        if db is None:
            return jsonify({'error': 'Database connection not available'}), 500
        rooms = list(db.rooms.find())
        return jsonify(rooms), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/timetables', methods=['GET'])
def get_timetables():
    try:
        if db is None:
            return jsonify({'error': 'Database connection not available'}), 500
        timetables = list(db.timetables.find())
        return jsonify(timetables), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize models
init_models()

if __name__ == '__main__':
    app.run(debug=True)
