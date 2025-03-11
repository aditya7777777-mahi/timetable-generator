import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
from timetable_generator import TimetableGenerator
import datetime
from collections import defaultdict

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='../client', static_url_path='/')
CORS(app)

# Connect to MongoDB - use the Atlas URI directly
mongo_uri = "mongodb+srv://adityabasude13:13777adi@cluster0.4weinpi.mongodb.net/"
db_name = os.environ.get('DB_NAME', 'timetable_db')

try:
    print(f"Connecting to MongoDB at: {mongo_uri}")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    # Force a connection to verify it works
    client.server_info()
    print("Connected to MongoDB successfully!")
    db = client[db_name]
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    print("Using fallback in-memory data structures")
    # Create fallback in-memory data structures
    class InMemoryDB:
        def __init__(self):
            self.departments = InMemoryCollection([])
            self.teachers = InMemoryCollection([])
            self.subjects = InMemoryCollection([])
            self.rooms = InMemoryCollection([])
            self.timetables = InMemoryCollection([])
            self.programs = InMemoryCollection([])
            self.academic_years = InMemoryCollection([])
            self.divisions = InMemoryCollection([])
            self.batches = InMemoryCollection([])
    
    class InMemoryCollection:
        def __init__(self, initial_data):
            self.data = initial_data
            self._id_counter = 1
        
        def find(self, query=None):
            if not query:
                return self.data
            
            # Simple filtering implementation
            result = []
            for item in self.data:
                matches = True
                for key, value in query.items():
                    if key not in item or item[key] != value:
                        matches = False
                        break
                if matches:
                    result.append(item)
            return result
        
        def find_one(self, query):
            items = self.find(query)
            if items:
                return items[0]
            return None
        
        def insert_one(self, item):
            # Add ID if not present
            if '_id' not in item:
                item['_id'] = str(self._id_counter)
                self._id_counter += 1
            
            self.data.append(item)
            
            class Result:
                def __init__(self, inserted_id):
                    self.inserted_id = inserted_id
            
            return Result(item['_id'])

        def update_one(self, query, update_data):
            for item in self.data:
                matches = True
                for key, value in query.items():
                    if key not in item or item[key] != value:
                        matches = False
                        break
                
                if matches:
                    # Apply updates from $set operator
                    if "$set" in update_data:
                        for key, value in update_data["$set"].items():
                            item[key] = value
                    
                    # Apply other update operations as needed
                    class Result:
                        def __init__(self, matched_count=1, modified_count=1):
                            self.matched_count = matched_count
                            self.modified_count = modified_count
                    
                    return Result()
            
            return Result(0, 0)
        
        def delete_one(self, query):
            for i, item in enumerate(self.data):
                matches = True
                for key, value in query.items():
                    if key not in item or item[key] != value:
                        matches = False
                        break
                
                if matches:
                    del self.data[i]
                    class Result:
                        def __init__(self, deleted_count=1):
                            self.deleted_count = deleted_count
                    
                    return Result()
            
            return Result(0)
    
    # Use in-memory DB
    db = InMemoryDB()

# Collections
departments_collection = db.departments
teachers_collection = db.teachers
subjects_collection = db.subjects
rooms_collection = db.rooms
timetables_collection = db.timetables
programs_collection = db.programs
academic_years_collection = db.academic_years
divisions_collection = db.divisions
batches_collection = db.batches

# Home route - serves the frontend
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# API routes
@app.route('/api/departments', methods=['GET', 'POST'])
def handle_departments():
    if request.method == 'POST':
        department_data = request.json
        
        # Initialize year structure if not present
        if 'years' not in department_data:
            department_data['years'] = {
                'SE': {'num_batches': 3},
                'TE': {'num_batches': 3},
                'BE': {'num_batches': 3}
            }
            
        # Add additional metadata
        department_data['batch_prefix'] = 'B'  # Default batch prefix
        department_data['breaks'] = [
            "11:00 am - 11:15 am",
            "1:15 pm - 1:45 pm"
        ]
        
        result = departments_collection.insert_one(department_data)
        return jsonify({"id": str(result.inserted_id), "message": "Department added successfully"}), 201
    else:
        departments = list(departments_collection.find())
        for dept in departments:
            dept['_id'] = str(dept['_id'])
        return jsonify(departments)

@app.route('/api/departments/<department_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_department(department_id):
    if request.method == 'GET':
        department = departments_collection.find_one({"_id": ObjectId(department_id)})
        if not department:
            return jsonify({"message": "Department not found"}), 404
        department['_id'] = str(department['_id'])
        return jsonify(department)
    elif request.method == 'PUT':
        update_data = request.json
        result = departments_collection.update_one({"_id": ObjectId(department_id)}, {"$set": update_data})
        if result.matched_count:
            return jsonify({"message": "Department updated successfully"})
        return jsonify({"message": "Department not found"}), 404
    elif request.method == 'DELETE':
        result = departments_collection.delete_one({"_id": ObjectId(department_id)})
        if result.deleted_count:
            return jsonify({"message": "Department deleted successfully"})
        return jsonify({"message": "Department not found"}), 404

@app.route('/api/teachers', methods=['GET', 'POST'])
def handle_teachers():
    if request.method == 'POST':
        teacher_data = request.json
        # Add teacher code if not present
        if 'code' not in teacher_data and 'name' in teacher_data:
            # Generate code from name (e.g., "Dr. Sandeep B. Raskar" -> "SBR")
            name_parts = teacher_data['name'].split()
            if len(name_parts) >= 3:
                # Handle cases like "Dr. Sandeep B. Raskar"
                if name_parts[0] in ["Dr.", "Prof.", "Mr.", "Mrs.", "Ms."]:
                    teacher_data['code'] = name_parts[1][0] + name_parts[2][0] + name_parts[3][0]
                else:
                    # Handle cases without title
                    teacher_data['code'] = name_parts[0][0] + name_parts[1][0] + name_parts[2][0]
            else:
                # Fallback for shorter names
                teacher_data['code'] = ''.join([word[0] for word in name_parts])
            
            teacher_data['code'] = teacher_data['code'].upper()
            
        result = teachers_collection.insert_one(teacher_data)
        return jsonify({"id": str(result.inserted_id), "message": "Teacher added successfully"}), 201
    else:
        teachers = list(teachers_collection.find())
        for teacher in teachers:
            teacher['_id'] = str(teacher['_id'])
            
            # Convert ObjectId in departments list to strings
            if 'departments' in teacher:
                teacher['departments'] = [str(dept) if isinstance(dept, ObjectId) else dept 
                                         for dept in teacher['departments']]
                
        return jsonify(teachers)

@app.route('/api/teachers/<teacher_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_teacher(teacher_id):
    if request.method == 'GET':
        teacher = teachers_collection.find_one({"_id": ObjectId(teacher_id)})
        if not teacher:
            return jsonify({"message": "Teacher not found"}), 404
        teacher['_id'] = str(teacher['_id'])
        return jsonify(teacher)
    elif request.method == 'PUT':
        update_data = request.json
        result = teachers_collection.update_one({"_id": ObjectId(teacher_id)}, {"$set": update_data})
        if result.matched_count:
            return jsonify({"message": "Teacher updated successfully"})
        return jsonify({"message": "Teacher not found"}), 404
    elif request.method == 'DELETE':
        result = teachers_collection.delete_one({"_id": ObjectId(teacher_id)})
        if result.deleted_count:
            return jsonify({"message": "Teacher deleted successfully"})
        return jsonify({"message": "Teacher not found"}), 404

@app.route('/api/subjects', methods=['GET', 'POST'])
def handle_subjects():
    if request.method == 'POST':
        subject_data = request.json
        
        # Validate department_id
        if 'department_id' not in subject_data or not subject_data['department_id']:
            return jsonify({"message": "Department ID is required"}), 400
            
        # Get department to validate
        department = departments_collection.find_one({"_id": ObjectId(subject_data['department_id'])})
        if not department:
            return jsonify({"message": "Department not found"}), 400
        
        # Validate year field
        if 'year' not in subject_data or subject_data['year'] not in ['SE', 'TE', 'BE']:
            return jsonify({"message": "Valid year (SE/TE/BE) is required"}), 400
            
        # Validate subject type
        if 'type' not in subject_data or subject_data['type'] not in ['lecture', 'practical']:
            return jsonify({"message": "Valid type (lecture/practical) is required"}), 400
            
        # Store both ObjectId and string versions
        subject_data['department_id'] = ObjectId(subject_data['department_id'])
        subject_data['department_id_str'] = str(subject_data['department_id'])
        subject_data['department_name'] = department.get('name', '')
            
        # Add lectures/practicals per week and duration based on type
        if subject_data['type'] == 'lecture':
            subject_data['lectures_per_week'] = 3  # Theory subjects 3 times per week
            subject_data['duration_hours'] = 1     # 1 hour duration
        else:  # practical
            subject_data['practicals_per_week'] = 1  # Once per week
            subject_data['duration_hours'] = 2       # 2 hours duration
            
            # For practicals, ensure consecutive slots requirement is set
            subject_data['consecutive_slots'] = 2  # 2-hour practicals
        
        result = subjects_collection.insert_one(subject_data)
        
        # Return created subject with proper fields
        created_subject = subjects_collection.find_one({"_id": result.inserted_id})
        if created_subject:
            created_subject['_id'] = str(created_subject['_id'])
            if 'department_id' in created_subject:
                created_subject['department_id'] = str(created_subject['department_id'])
                
        return jsonify({
            "id": str(result.inserted_id), 
            "message": "Subject added successfully",
            "subject": created_subject
        }), 201
    else:
        subjects = list(subjects_collection.find())
        for subject in subjects:
            subject['_id'] = str(subject['_id'])
            if 'department_id' in subject:
                subject['department_id'] = str(subject['department_id'])
        return jsonify(subjects)

@app.route('/api/subjects/<subject_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_subject(subject_id):
    if request.method == 'GET':
        subject = subjects_collection.find_one({"_id": ObjectId(subject_id)})
        if not subject:
            return jsonify({"message": "Subject not found"}), 404
        subject['_id'] = str(subject['_id'])
        return jsonify(subject)
    elif request.method == 'PUT':
        update_data = request.json
        result = subjects_collection.update_one({"_id": ObjectId(subject_id)}, {"$set": update_data})
        if result.matched_count:
            return jsonify({"message": "Subject updated successfully"})
        return jsonify({"message": "Subject not found"}), 404
    elif request.method == 'DELETE':
        result = subjects_collection.delete_one({"_id": ObjectId(subject_id)})
        if result.deleted_count:
            return jsonify({"message": "Subject deleted successfully"})
        return jsonify({"message": "Subject not found"}), 404

@app.route('/api/subjects/by-department/<department_id>', methods=['GET'])
def get_subjects_by_department(department_id):
    """Get all subjects for a department, organized by year"""
    year = request.args.get('year')  # Optional year filter
    
    try:
        # Base query with both ObjectId and string versions of department_id
        query = {
            "$or": [
                {"department_id": ObjectId(department_id)},
                {"department_id_str": str(department_id)}
            ]
        }
        
        # Add year filter if provided
        if year:
            query["year"] = year
            
        subjects = list(subjects_collection.find(query))
        
        # Convert ObjectId to string for JSON response
        for subject in subjects:
            subject['_id'] = str(subject['_id'])
            if 'department_id' in subject:
                subject['department_id'] = str(subject['department_id'])
        
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

@app.route('/api/rooms', methods=['GET', 'POST'])
def handle_rooms():
    if request.method == 'POST':
        room_data = request.json
        # Set number field to match the room number input
        if 'number' not in room_data and 'room_number' in room_data:
            room_data['number'] = room_data['room_number']
        
        result = rooms_collection.insert_one(room_data)
        return jsonify({"id": str(result.inserted_id), "message": "Room added successfully"}), 201
    else:
        rooms = list(rooms_collection.find())
        for room in rooms:
            room['_id'] = str(room['_id'])
        return jsonify(rooms)

@app.route('/api/rooms/<room_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_room(room_id):
    if request.method == 'GET':
        room = rooms_collection.find_one({"_id": ObjectId(room_id)})
        if not room:
            return jsonify({"message": "Room not found"}), 404
        room['_id'] = str(room['_id'])
        return jsonify(room)
    elif request.method == 'PUT':
        update_data = request.json
        result = rooms_collection.update_one({"_id": ObjectId(room_id)}, {"$set": update_data})
        if result.matched_count:
            return jsonify({"message": "Room updated successfully"})
        return jsonify({"message": "Room not found"}), 404
    elif request.method == 'DELETE':
        result = rooms_collection.delete_one({"_id": ObjectId(room_id)})
        if result.deleted_count:
            return jsonify({"message": "Room deleted successfully"})
        return jsonify({"message": "Room not found"}), 404

@app.route('/api/programs', methods=['GET', 'POST'])
def handle_programs():
    if request.method == 'POST':
        program_data = request.json
        result = programs_collection.insert_one(program_data)
        return jsonify({"id": str(result.inserted_id), "message": "Program added successfully"}), 201
    else:
        programs = list(programs_collection.find())
        for program in programs:
            program['_id'] = str(program['_id'])
        return jsonify(programs)

@app.route('/api/programs/<program_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_program(program_id):
    if request.method == 'GET':
        program = programs_collection.find_one({"_id": ObjectId(program_id)})
        if not program:
            return jsonify({"message": "Program not found"}), 404
        program['_id'] = str(program['_id'])
        return jsonify(program)
    elif request.method == 'PUT':
        update_data = request.json
        result = programs_collection.update_one({"_id": ObjectId(program_id)}, {"$set": update_data})
        if result.matched_count:
            return jsonify({"message": "Program updated successfully"})
        return jsonify({"message": "Program not found"}), 404
    elif request.method == 'DELETE':
        result = programs_collection.delete_one({"_id": ObjectId(program_id)})
        if result.deleted_count:
            return jsonify({"message": "Program deleted successfully"})
        return jsonify({"message": "Program not found"}), 404

@app.route('/api/academic-years', methods=['GET', 'POST'])
def handle_academic_years():
    if request.method == 'POST':
        academic_year_data = request.json
        result = academic_years_collection.insert_one(academic_year_data)
        return jsonify({"id": str(result.inserted_id), "message": "Academic year added successfully"}), 201
    else:
        academic_years = list(academic_years_collection.find())
        for year in academic_years:
            year['_id'] = str(year['_id'])
        return jsonify(academic_years)

@app.route('/api/academic-years/<year_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_academic_year(year_id):
    if request.method == 'GET':
        year = academic_years_collection.find_one({"_id": ObjectId(year_id)})
        if not year:
            return jsonify({"message": "Academic year not found"}), 404
        year['_id'] = str(year['_id'])
        return jsonify(year)
    elif request.method == 'PUT':
        update_data = request.json
        result = academic_years_collection.update_one({"_id": ObjectId(year_id)}, {"$set": update_data})
        if result.matched_count:
            return jsonify({"message": "Academic year updated successfully"})
        return jsonify({"message": "Academic year not found"}), 404
    elif request.method == 'DELETE':
        result = academic_years_collection.delete_one({"_id": ObjectId(year_id)})
        if result.deleted_count:
            return jsonify({"message": "Academic year deleted successfully"})
        return jsonify({"message": "Academic year not found"}), 404

@app.route('/api/divisions', methods=['GET', 'POST'])
def handle_divisions():
    if request.method == 'POST':
        division_data = request.json
        result = divisions_collection.insert_one(division_data)
        return jsonify({"id": str(result.inserted_id), "message": "Division added successfully"}), 201
    else:
        divisions = list(divisions_collection.find())
        for division in divisions:
            division['_id'] = str(division['_id'])
        return jsonify(divisions)

@app.route('/api/divisions/<division_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_division(division_id):
    if request.method == 'GET':
        division = divisions_collection.find_one({"_id": ObjectId(division_id)})
        if not division:
            return jsonify({"message": "Division not found"}), 404
        division['_id'] = str(division['_id'])
        return jsonify(division)
    elif request.method == 'PUT':
        update_data = request.json
        result = divisions_collection.update_one({"_id": ObjectId(division_id)}, {"$set": update_data})
        if result.matched_count:
            return jsonify({"message": "Division updated successfully"})
        return jsonify({"message": "Division not found"}), 404
    elif request.method == 'DELETE':
        result = divisions_collection.delete_one({"_id": ObjectId(division_id)})
        if result.deleted_count:
            return jsonify({"message": "Division deleted successfully"})
        return jsonify({"message": "Division not found"}), 404

@app.route('/api/batches', methods=['GET', 'POST'])
def handle_batches():
    if request.method == 'POST':
        batch_data = request.json
        result = batches_collection.insert_one(batch_data)
        return jsonify({"id": str(result.inserted_id), "message": "Batch added successfully"}), 201
    else:
        batches = list(batches_collection.find())
        for batch in batches:
            batch['_id'] = str(batch['_id'])
        return jsonify(batches)

@app.route('/api/batches/<batch_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_batch(batch_id):
    if request.method == 'GET':
        batch = batches_collection.find_one({"_id": ObjectId(batch_id)})
        if not batch:
            return jsonify({"message": "Batch not found"}), 404
        batch['_id'] = str(batch['_id'])
        return jsonify(batch)
    elif request.method == 'PUT':
        update_data = request.json
        result = batches_collection.update_one({"_id": ObjectId(batch_id)}, {"$set": update_data})
        if result.matched_count:
            return jsonify({"message": "Batch updated successfully"})
        return jsonify({"message": "Batch not found"}), 404
    elif request.method == 'DELETE':
        result = batches_collection.delete_one({"_id": ObjectId(batch_id)})
        if result.deleted_count:
            return jsonify({"message": "Batch deleted successfully"})
        return jsonify({"message": "Batch not found"}), 404

@app.route('/api/generate-timetable', methods=['POST'])
def generate_timetable():
    data = request.json
    department_id = data.get('department_id')
    academic_year = data.get('academic_year')
    
    try:
        # Create timetable generator instance
        generator = TimetableGenerator(db)
        
        # Generate timetable using the backtracking algorithm
        timetable = generator.generate_timetable(ObjectId(department_id), academic_year)
        
        if timetable:
            # Save to database
            result = timetables_collection.insert_one({
                "department_id": ObjectId(department_id),
                "academic_year": academic_year,
                "timetable": timetable,
                "type": "raw"
            })
            return jsonify({"message": "Timetable generated successfully", "id": str(result.inserted_id)}), 201
        else:
            return jsonify({"message": "Failed to generate timetable - unable to satisfy all constraints"}), 400
    except ValueError as e:
        # Return specific error messages for missing data
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        print(f"Error generating timetable: {e}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/api/generate-formatted-timetable', methods=['POST'])
def generate_formatted_timetable():
    data = request.json
    department_id = data.get('department_id')
    academic_year = data.get('academic_year')
    
    try:
        # Create timetable generator instance
        generator = TimetableGenerator(db)
        
        # Generate formatted timetable
        formatted_timetables = generator.generate_formatted_timetable(ObjectId(department_id), academic_year)
        
        if formatted_timetables:
            # Save to database with proper format
            result = timetables_collection.insert_one({
                "department_id": ObjectId(department_id),
                "academic_year": academic_year,
                "formatted_timetables": formatted_timetables,
                "type": "formatted",
                "created_at": datetime.datetime.now().isoformat()
            })
            
            # Also create legacy format for backward compatibility
            legacy_format = {}
            for year, timetable_data in formatted_timetables.items():
                # Convert to day-first structure needed for legacy format
                day_first_structure = {}
                
                # Get all the days and time slots
                if timetable_data:
                    first_time_slot = next(iter(timetable_data))
                    days = list(timetable_data[first_time_slot].keys())
                    time_slots = list(timetable_data.keys())
                    
                    # Initialize days
                    for day in days:
                        day_first_structure[day] = {}
                        for time_slot in time_slots:
                            # Copy the data, converting format
                            slot_data = timetable_data[time_slot][day]
                            if slot_data and slot_data != "-":
                                # Parse cell contents into subject, teacher, room
                                cell_parts = slot_data.split(" - ") if isinstance(slot_data, str) else []
                                if len(cell_parts) >= 2:
                                    subject = cell_parts[0]
                                    teacher_room = cell_parts[1]
                                    teacher = teacher_room.split("(")[0].strip() if "(" in teacher_room else "Unknown"
                                    room = teacher_room.split("(")[1].replace(")", "").strip() if "(" in teacher_room else "Unknown"
                                    
                                    day_first_structure[day][time_slot] = {
                                        "subject": subject,
                                        "teacher": teacher,
                                        "room": room,
                                        "type": "lecture" if "B" not in subject else "practical"
                                    }
                                else:
                                    # Simple string, not structured data
                                    day_first_structure[day][time_slot] = slot_data
                            else:
                                day_first_structure[day][time_slot] = {
                                    "subject": None,
                                    "teacher": None,
                                    "room": None,
                                    "type": None
                                }
                
                legacy_format[year] = day_first_structure
            
            # Add legacy format to response for compatibility
            return jsonify({
                "message": "Timetable generated successfully", 
                "id": str(result.inserted_id),
                "timetables": formatted_timetables,
                "legacy_format": legacy_format
            }), 201
        else:
            return jsonify({"message": "Failed to generate timetable"}), 400
    except Exception as e:
        print(f"Error generating formatted timetable: {e}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/api/timetables', methods=['GET'])
def get_timetables():
    department_id = request.args.get('department_id')
    query = {"department_id": ObjectId(department_id)} if department_id else {}
    
    # Option to filter by type (raw or formatted)
    timetable_type = request.args.get('type')
    if timetable_type:
        query["type"] = timetable_type
    
    timetables = list(timetables_collection.find(query))
    for timetable in timetables:
        timetable['_id'] = str(timetable['_id'])
        if 'department_id' in timetable:
            timetable['department_id'] = str(timetable['department_id'])
    
    return jsonify(timetables)

@app.route('/api/timetables/<timetable_id>', methods=['GET'])
def get_timetable(timetable_id):
    timetable = timetables_collection.find_one({"_id": ObjectId(timetable_id)})
    if timetable:
        timetable['_id'] = str(timetable['_id'])
        if 'department_id' in timetable:
            timetable['department_id'] = str(timetable['department_id'])
            
        # Handle different timetable formats
        if 'formatted_timetables' in timetable:
            # New format with time slots as primary keys
            return jsonify({
                "_id": timetable['_id'],
                "department_id": timetable.get('department_id', ''),
                "academic_year": timetable.get('academic_year', ''),
                "timetable": timetable['formatted_timetables']
            })
        elif 'timetable' in timetable:
            # Check if it's branch format
            branch_keys = [key for key in timetable['timetable'] if key.startswith('Branch-')]
            if branch_keys:
                # Handle branch format - combine into a single view
                combined = {}
                for day in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]:
                    combined[day] = {}
                    
                    # Get all time slots from the first branch
                    time_slots = list(timetable['timetable']['Branch-1'][day].keys()) if 'Branch-1' in timetable['timetable'] and day in timetable['timetable']['Branch-1'] else []
                    
                    for time_slot in time_slots:
                        # Skip break slots
                        if "break" in time_slot.lower():
                            continue
                            
                        combined[day][time_slot] = {}
                        
                        # Add data from each branch
                        for branch_key in branch_keys:
                            branch_num = branch_key.split('-')[1]
                            branch_data = timetable['timetable'][branch_key].get(day, {}).get(time_slot, {})
                            
                            if branch_data and branch_data.get('subject'):
                                if combined[day][time_slot].get('subject'):
                                    # Append to existing entry
                                    combined[day][time_slot]['subject'] += f", B{branch_num}: {branch_data['subject']}"
                                    combined[day][time_slot]['teacher'] += f", {branch_data.get('teacher', 'N/A')}"
                                    combined[day][time_slot]['room'] += f", {branch_data.get('room', 'N/A')}"
                                else:
                                    # Create new entry
                                    combined[day][time_slot] = {
                                        'subject': f"B{branch_num}: {branch_data.get('subject', 'N/A')}",
                                        'teacher': branch_data.get('teacher', 'N/A'),
                                        'room': branch_data.get('room', 'N/A'),
                                        'type': branch_data.get('type', 'lecture')
                                    }
                
                return jsonify({
                    "_id": timetable['_id'],
                    "department_id": timetable.get('department_id', ''),
                    "academic_year": timetable.get('academic_year', ''),
                    "timetable": combined
                })
                
        # Default: return as-is
        return jsonify(timetable)
    else:
        return jsonify({"message": "Timetable not found"}), 404

@app.route('/api/timetables/<timetable_id>', methods=['DELETE'])
def delete_timetable(timetable_id):
    result = timetables_collection.delete_one({"_id": ObjectId(timetable_id)})
    if result.deleted_count:
        return jsonify({"message": "Timetable deleted successfully"})
    return jsonify({"message": "Timetable not found"}), 404

@app.route('/api/conflict-check', methods=['POST'])
def check_conflicts():
    data = request.json
    timetable_id = data.get('timetable_id')
    
    try:
        timetable = timetables_collection.find_one({"_id": ObjectId(timetable_id)})
        if not timetable:
            return jsonify({"message": "Timetable not found"}), 404
            
        # Analyze the timetable for conflicts
        conflicts = []
        
        # Teacher conflicts (same teacher in multiple places at once)
        teacher_slots = defaultdict(list)
        
        # Room conflicts (same room used by multiple classes at once)
        room_slots = defaultdict(list)
        
        # For raw timetables, analyze the nested structure
        if timetable.get("type") == "raw":
            raw_data = timetable.get("timetable", {})
            for batch, batch_data in raw_data.items():
                for day, day_data in batch_data.items():
                    for slot, slot_data in day_data.items():
                        if isinstance(slot_data, dict) and slot_data.get("teacher"):
                            teacher_id = slot_data["teacher"]
                            room_id = slot_data.get("room")
                            
                            # Check for teacher conflicts
                            teacher_key = f"{day}_{slot}_{teacher_id}"
                            teacher_slots[teacher_key].append({
                                "batch": batch,
                                "subject": slot_data.get("subject_code", "Unknown"),
                                "day": day,
                                "time": slot
                            })
                            
                            # Check for room conflicts
                            if room_id:
                                room_key = f"{day}_{slot}_{room_id}"
                                room_slots[room_key].append({
                                    "batch": batch,
                                    "subject": slot_data.get("subject_code", "Unknown"),
                                    "day": day,
                                    "time": slot
                                })
        
        # Find conflicts where a teacher is scheduled in multiple places at once
        for key, assignments in teacher_slots.items():
            if len(assignments) > 1:
                conflicts.append({
                    "type": "teacher_conflict",
                    "details": {
                        "teacher_id": key.split("_")[2],
                        "day": assignments[0]["day"],
                        "time": assignments[0]["time"],
                        "assignments": assignments
                    }
                })
        
        # Find conflicts where a room is used by multiple classes at once
        for key, assignments in room_slots.items():
            if len(assignments) > 1:
                conflicts.append({
                    "type": "room_conflict",
                    "details": {
                        "room_id": key.split("_")[2],
                        "day": assignments[0]["day"],
                        "time": assignments[0]["time"],
                        "assignments": assignments
                    }
                })
        
        return jsonify({
            "timetable_id": timetable_id,
            "conflicts": conflicts,
            "has_conflicts": len(conflicts) > 0
        })
    
    except Exception as e:
        print(f"Error checking conflicts: {e}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/api/debug/subjects-by-department/<department_id>', methods=['GET'])
def debug_subjects_by_department(department_id):
    """Debug endpoint to check what subjects exist for a department"""
    try:
        # Get the department
        department = departments_collection.find_one({"_id": ObjectId(department_id)})
        if not department:
            return jsonify({
                "error": "Department not found", 
                "department_id": department_id
            }), 404
            
        # Try different formats of the ID
        dept_id_str = str(department_id)
        dept_id_obj = ObjectId(department_id)
        
        # Query subjects with different formats
        subjects_by_str = list(subjects_collection.find({"department_id": dept_id_str}))
        subjects_by_obj = list(subjects_collection.find({"department_id": dept_id_obj}))
        
        # Also check the department_id_str field we added
        subjects_by_str_field = list(subjects_collection.find({"department_id_str": dept_id_str}))
        
        # Convert ObjectId to string for JSON response
        for subjects in [subjects_by_str, subjects_by_obj, subjects_by_str_field]:
            for subject in subjects:
                if '_id' in subject:
                    subject['_id'] = str(subject['_id'])
        
        return jsonify({
            "department": {
                "id": str(department["_id"]),
                "name": department.get("name", "Unknown")
            },
            "subjects_by_string_id": {
                "count": len(subjects_by_str),
                "subjects": subjects_by_str
            },
            "subjects_by_object_id": {
                "count": len(subjects_by_obj),
                "subjects": subjects_by_obj
            },
            "subjects_by_string_field": {
                "count": len(subjects_by_str_field),
                "subjects": subjects_by_str_field
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/timetables/import', methods=['POST'])
def import_timetable_data():
    try:
        timetable_data = request.json
        
        # Validate required fields
        if not timetable_data.get('department_id') or not timetable_data.get('academic_year') or not timetable_data.get('timetable'):
            return jsonify({"message": "Missing required fields"}), 400
        
        # Convert department_id to ObjectId if it's a string
        if isinstance(timetable_data['department_id'], str):
            try:
                timetable_data['department_id'] = ObjectId(timetable_data['department_id'])
            except:
                pass  # Keep as string if not valid ObjectId
        
        # Add created timestamp
        timetable_data['created_at'] = datetime.datetime.now()
        
        # Insert the timetable
        result = timetables_collection.insert_one(timetable_data)
        
        return jsonify({
            "id": str(result.inserted_id), 
            "message": "Timetable imported successfully"
        }), 201
    except Exception as e:
        return jsonify({"message": f"Error importing timetable: {str(e)}"}), 500

@app.route('/api/timetables/<timetable_id>/formatted', methods=['GET'])
def get_formatted_timetable(timetable_id):
    try:
        # Find the timetable
        timetable = timetables_collection.find_one({"_id": ObjectId(timetable_id)})
        if not timetable:
            return jsonify({"message": "Timetable not found"}), 404
        
        # Convert ObjectId to string for JSON serialization
        timetable['_id'] = str(timetable['_id'])
        if 'department_id' in timetable and isinstance(timetable['department_id'], ObjectId):
            timetable['department_id'] = str(timetable['department_id'])
        
        # If department exists, get department details
        department = None
        if 'department_id' in timetable:
            try:
                department = departments_collection.find_one({"_id": ObjectId(timetable['department_id'])})
                if department:
                    department['_id'] = str(department['_id'])
            except:
                pass
        
        return jsonify({
            "timetable": timetable,
            "department": department
        })
    except Exception as e:
        return jsonify({"message": f"Error retrieving timetable: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
