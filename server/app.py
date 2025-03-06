import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
from timetable_generator import TimetableGenerator

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
            
        # Log for debugging
        print(f"Adding subject with department_id: {subject_data['department_id']}")
        
        # Store both ObjectId and string versions to be safe
        try:
            subject_data['department_id_str'] = str(subject_data['department_id'])
        except:
            subject_data['department_id_str'] = subject_data['department_id']
        
        # Add subject code if not present
        if 'code' not in subject_data and 'name' in subject_data:
            # Generate code from name (e.g. "Machine Learning" -> "ML")
            words = subject_data['name'].split()
            if len(words) == 1:
                # Single word, take first two characters
                subject_data['code'] = words[0][:2].upper()
            else:
                # Multiple words, take first letter of each word
                subject_data['code'] = ''.join([word[0] for word in words if word.lower() not in ['and', 'of', 'the', 'in', 'on', 'a', 'an']])
                subject_data['code'] = subject_data['code'].upper()
        
        result = subjects_collection.insert_one(subject_data)
        return jsonify({"id": str(result.inserted_id), "message": "Subject added successfully"}), 201
    else:
        subjects = list(subjects_collection.find())
        for subject in subjects:
            subject['_id'] = str(subject['_id'])
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
            # Save to database
            result = timetables_collection.insert_one({
                "department_id": ObjectId(department_id),
                "academic_year": academic_year,
                "formatted_timetables": formatted_timetables,
                "type": "formatted"
            })
            return jsonify({
                "message": "Timetable generated successfully", 
                "id": str(result.inserted_id),
                "timetables": formatted_timetables
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

if __name__ == '__main__':
    app.run(debug=True)
