from flask import Blueprint, jsonify, request
from pymongo.errors import PyMongoError
from api.models.subject import Subject
from bson import ObjectId

subjects = Blueprint('subjects', __name__)

@subjects.route('/api/subjects', methods=['GET', 'POST'])
def handle_subjects():
    try:
        if request.method == 'POST':
            subject_data = request.json
            db = Subject.collection.database
            subject_id = Subject.create_with_validation(subject_data, db.departments, db.teachers)
            
            # Return created subject with proper fields
            created_subject = Subject.find_by_id(subject_id)
            if created_subject:
                created_subject = Subject.to_json_friendly(created_subject)
                
            return jsonify({
                "id": subject_id,
                "message": "Subject added successfully",
                "subject": created_subject
            }), 201
        else:
            subjects = Subject.find_all()
            return jsonify(Subject.to_json_friendly(subjects))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except PyMongoError as e:
        print(f"Database error in subjects route: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error in subjects route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@subjects.route('/api/subjects/<subject_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_subject(subject_id):
    try:
        if request.method == 'GET':
            subject = Subject.find_by_id(subject_id)
            if not subject:
                return jsonify({"error": "Subject not found"}), 404
            return jsonify(Subject.to_json_friendly(subject))
            
        elif request.method == 'PUT':
            # Handle teacher updates for subjects
            if 'teacher_id' in request.json and request.json['teacher_id']:
                db = Subject.collection.database
                teacher = db.teachers.find_one({"_id": ObjectId(request.json['teacher_id'])})
                if not teacher:
                    return jsonify({"error": "Teacher not found"}), 404
                
                # Add teacher details
                request.json['teacher_id'] = ObjectId(request.json['teacher_id'])
                request.json['teacher_id_str'] = str(request.json['teacher_id'])
                request.json['teacher_name'] = teacher.get('name', '')
                request.json['teacher_code'] = teacher.get('code', '')
            
            if Subject.update_by_id(subject_id, request.json):
                return jsonify({"message": "Subject updated successfully"})
            return jsonify({"error": "Subject not found"}), 404
            
        elif request.method == 'DELETE':
            if Subject.delete_by_id(subject_id):
                return jsonify({"message": "Subject deleted successfully"})
            return jsonify({"error": "Subject not found"}), 404
    except PyMongoError as e:
        print(f"Database error in subjects route: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error in subjects route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@subjects.route('/api/subjects/by-department/<department_id>', methods=['GET'])
def get_subjects_by_department(department_id):
    """Get all subjects for a department, organized by year"""
    year = request.args.get('year')  # Optional year filter
    
    try:
        subjects = Subject.find_by_department(department_id, year)
        subjects = Subject.to_json_friendly(subjects)
        
        # Group by year if no specific year requested
        if not year:
            subjects_by_year = {}
            for subject in subjects:
                year = subject.get('year', 'Unknown')
                if year not in subjects_by_year:
                    subjects_by_year[year] = []
                subjects_by_year[year].append(subject)
            return jsonify(subjects_by_year)
        
        return jsonify(subjects)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
@subjects.route('/api/subjects/by-teacher/<teacher_id>', methods=['GET'])
def get_subjects_by_teacher(teacher_id):
    """Get all subjects assigned to a specific teacher"""
    try:
        subjects = Subject.find_by_teacher(teacher_id)
        subjects = Subject.to_json_friendly(subjects)
        return jsonify(subjects)
    except Exception as e:
        return jsonify({"error": str(e)}), 500