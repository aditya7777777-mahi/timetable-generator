from flask import Blueprint, jsonify, request
from pymongo.errors import PyMongoError
from api.models.timetable import Timetable
from api.models.department import Department
from api.services.timetable_generator import TimetableGeneratorService

timetables = Blueprint('timetables', __name__)

@timetables.route('/api/timetables', methods=['GET'])
def get_timetables():
    try:
        timetables = Timetable.find_all()
        return jsonify(Timetable.to_json_friendly(timetables))
    except PyMongoError as e:
        print(f"Database error in timetables route: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error in timetables route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@timetables.route('/api/timetables/<timetable_id>', methods=['GET', 'DELETE'])
def handle_timetable(timetable_id):
    try:
        if request.method == 'GET':
            timetable = Timetable.find_by_id(timetable_id)
            if not timetable:
                return jsonify({"error": "Timetable not found"}), 404
            return jsonify(Timetable.to_json_friendly(timetable))
            
        elif request.method == 'DELETE':
            if Timetable.delete_by_id(timetable_id):
                return jsonify({"message": "Timetable deleted successfully"})
            return jsonify({"error": "Timetable not found"}), 404
    except PyMongoError as e:
        print(f"Database error in timetables route: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error in timetables route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@timetables.route('/api/timetables/<timetable_id>/formatted', methods=['GET'])
def get_formatted_timetable(timetable_id):
    try:
        # Get formatted timetable
        result = Timetable.get_formatted(timetable_id)
        if not result:
            return jsonify({"message": "Timetable not found"}), 404
            
        # Get department details if available
        department = None
        if 'department_id' in result:
            department = Department.find_by_id(str(result['department_id']))
            if department:
                department = Department.to_json_friendly(department)
        
        return jsonify({
            "timetable": Timetable.to_json_friendly(result),
            "department": department
        })
    except PyMongoError as e:
        print(f"Database error formatting timetable: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Error formatting timetable: {str(e)}")
        return jsonify({"error": str(e)}), 500

@timetables.route('/api/generate-timetable', methods=['POST'])
def generate_timetable():
    try:
        data = request.json
        department_id = data.get('department_id')
        academic_year = data.get('academic_year')
        
        if not department_id or not academic_year:
            return jsonify({
                "error": "Department ID and academic year are required"
            }), 400
            
        generator = TimetableGeneratorService()
        timetables = generator.generate_timetable(department_id, academic_year)
        
        if not timetables:
            return jsonify({
                "error": "Failed to generate timetable. Check constraints and try again."
            }), 500
            
        return jsonify({
            "message": "Timetable generated successfully",
            "timetables": Timetable.to_json_friendly(timetables)
        })
    except PyMongoError as e:
        print(f"Database error generating timetable: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Error generating timetable: {str(e)}")
        return jsonify({"error": str(e)}), 500

@timetables.route('/api/timetables/import', methods=['POST'])
def import_timetable():
    try:
        data = request.json
        department_id = data.get('department_id')
        timetable_data = data.get('timetable')
        
        if not department_id or not timetable_data:
            return jsonify({
                "error": "Department ID and timetable data are required"
            }), 400
            
        # Add department ID to timetable data
        timetable_data['department_id'] = department_id
        
        timetable_id = Timetable.create(timetable_data)
        return jsonify({
            "message": "Timetable imported successfully",
            "id": timetable_id
        }), 201
    except PyMongoError as e:
        print(f"Database error importing timetable: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Error importing timetable: {str(e)}")
        return jsonify({"error": str(e)}), 500