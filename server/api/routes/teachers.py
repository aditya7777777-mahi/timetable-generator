from flask import Blueprint, jsonify, request
from pymongo.errors import PyMongoError
from api.models.teacher import Teacher
from bson import ObjectId

teachers = Blueprint('teachers', __name__)

@teachers.route('/api/teachers', methods=['GET', 'POST'])
def handle_teachers():
    try:
        if request.method == 'POST':
            teacher_data = request.json
            teacher_id = Teacher.create_with_code(teacher_data)
            return jsonify({
                "id": teacher_id,
                "message": "Teacher added successfully"
            }), 201
        else:
            teachers = Teacher.find_all()
            return jsonify(Teacher.to_json_friendly(teachers))
    except PyMongoError as e:
        print(f"Database error in teachers route: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error in teachers route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@teachers.route('/api/teachers/<teacher_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_teacher(teacher_id):
    try:
        if request.method == 'GET':
            teacher = Teacher.find_by_id(teacher_id)
            if not teacher:
                return jsonify({"error": "Teacher not found"}), 404
            return jsonify(Teacher.to_json_friendly(teacher))
            
        elif request.method == 'PUT':
            if Teacher.update_by_id(teacher_id, request.json):
                return jsonify({"message": "Teacher updated successfully"})
            return jsonify({"error": "Teacher not found"}), 404
            
        elif request.method == 'DELETE':
            if Teacher.delete_by_id(teacher_id):
                return jsonify({"message": "Teacher deleted successfully"})
            return jsonify({"error": "Teacher not found"}), 404
    except PyMongoError as e:
        print(f"Database error in teachers route: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error in teachers route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500