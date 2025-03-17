from flask import Blueprint, jsonify, request
from pymongo.errors import PyMongoError
from api.models.department import Department
from bson import ObjectId

departments = Blueprint('departments', __name__)

@departments.route('/api/departments', methods=['GET', 'POST'])
def handle_departments():
    try:
        if request.method == 'POST':
            department_data = request.json
            department_id = Department.create_with_defaults(department_data)
            return jsonify({
                "id": department_id,
                "message": "Department added successfully"
            }), 201
        else:
            departments = Department.find_all()
            return jsonify(Department.to_json_friendly(departments))
    except PyMongoError as e:
        print(f"Database error in departments route: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error in departments route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@departments.route('/api/departments/<department_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_department(department_id):
    try:
        if request.method == 'GET':
            department = Department.find_by_id(department_id)
            if not department:
                return jsonify({"error": "Department not found"}), 404
            return jsonify(Department.to_json_friendly(department))
            
        elif request.method == 'PUT':
            if Department.update_by_id(department_id, request.json):
                return jsonify({"message": "Department updated successfully"})
            return jsonify({"error": "Department not found"}), 404
            
        elif request.method == 'DELETE':
            if Department.delete_by_id(department_id):
                return jsonify({"message": "Department deleted successfully"})
            return jsonify({"error": "Department not found"}), 404
    except PyMongoError as e:
        print(f"Database error in departments route: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error in departments route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500