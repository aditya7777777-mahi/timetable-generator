"""
Timetable Generator Algorithm using Backtracking
"""
from collections import defaultdict
from bson.objectid import ObjectId

class TimetableGenerator:
    def __init__(self, db):
        self.db = db
        self.days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        # Update time slots to match the image
        self.time_slots = [
            "9:00 am - 10:00 am",
            "10:00 am - 11:00 am",
            "11:00 am - 11:15 am",  # Break
            "11:15 am - 12:15 pm",
            "12:15 pm - 1:15 pm",
            "1:15 pm - 1:45 pm",    # Lunch break
            "1:45 pm - 2:45 pm",
            "2:45 pm - 3:45 pm",
            "3:45 pm - 4:45 pm"
        ]
        
        # Define which slots are breaks
        self.break_slots = [
            "11:00 am - 11:15 am",
            "1:15 pm - 1:45 pm"
        ]
        
        # Subject abbreviations from the image
        self.subject_codes = {
            "ML": "Machine Learning",
            "DAV": "Data Analytics and Visualization",
            "SEPM": "Software Engineering and Project Management",
            "DC": "Distributed Computing",
            "CSS": "Cryptography and System Security",
            "CC": "Cloud Computing",
            "MINI PROJECT": "Mini Project Lab"
        }
        
        # Teacher codes from the image
        self.teacher_codes = {
            "SBR": "Dr. Sandeep B. Raskar",
            "SJN": "Prof. Sayalee Narkhede",
            "SP": "Prof. Smita Pawar",
            "SB": "Mr. Shrikant Bamane",
            "DT": "Mr. Deepak Thorat",
            "KB": "Mr. Kishor Biradar",
            "SE": "Mr. Samsul Ekram"
        }
        
    def generate_timetable(self, department_id, academic_year):
        """
        Main function to generate timetable using backtracking algorithm
        """
        # Get all required data from the database
        department = self.db.departments.find_one({"_id": department_id})
        if not department:
            return None
            
        # Get number of branches
        num_branches = department.get('num_branches', 1)
        
        # Prepare different formats of department ID for matching
        dept_id_str = str(department_id)
        
        # Log diagnostic information
        print(f"Searching for subjects with department_id: {dept_id_str}")
        
        # Try different queries to diagnose the issue
        subjects_by_str = list(self.db.subjects.find({"department_id": dept_id_str}))
        subjects_by_obj = list(self.db.subjects.find({"department_id": department_id}))
        
        print(f"Found {len(subjects_by_str)} subjects using string ID")
        print(f"Found {len(subjects_by_obj)} subjects using ObjectId")
        
        # Use a more comprehensive approach to find subjects
        subjects = []
        if subjects_by_str:
            subjects = subjects_by_str
        elif subjects_by_obj:
            subjects = subjects_by_obj
        else:
            # Last attempt - use a regex search if possible for string matching
            try:
                subjects = list(self.db.subjects.find({"department_id": {"$regex": dept_id_str}}))
            except:
                pass
        
        if not subjects:
            raise ValueError("No subjects found for this department. Please add subjects first.")
            
        # Get teachers and rooms
        teachers = list(self.db.teachers.find())
        if not teachers:
            raise ValueError("No teachers found. Please add teachers first.")
            
        rooms = list(self.db.rooms.find())
        if not rooms:
            raise ValueError("No rooms found. Please add rooms first.")
        
        # Get program and academic year details
        program = self.db.programs.find_one({"_id": ObjectId(department.get('program_id'))}) if 'program_id' in department else None
        acad_year_data = self.db.academic_years.find_one({"_id": ObjectId(academic_year)}) if ObjectId.is_valid(academic_year) else None
        
        # Create empty timetables for each branch and batch
        timetables = {}
        # Main timetable for lectures (common for all branches)
        timetables["Main"] = self._create_empty_timetable()
        
        # Batch timetables for practicals
        for batch_num in range(1, 4):  # B1, B2, B3
            batch_name = f"B{batch_num}"
            timetables[batch_name] = self._create_empty_timetable()
        
        # Get all constraints
        constraints = self._get_constraints(department, program, acad_year_data, subjects, teachers, rooms)
        
        # First schedule lectures - all branches together in the Main timetable
        lecture_success = self._schedule_lectures(timetables, subjects, teachers, rooms, constraints)
        
        if not lecture_success:
            return None
            
        # Then schedule practical sessions - branches separately in their respective timetables
        practical_success = self._schedule_practicals(timetables, subjects, teachers, rooms, constraints)
        
        if practical_success:
            return timetables
        else:
            return None
    
    def _create_empty_timetable(self):
        """Create an empty timetable structure"""
        timetable = {}
        for day in self.days:
            timetable[day] = {}
            for time_slot in self.time_slots:
                # Mark break slots as unavailable
                if time_slot in self.break_slots:
                    timetable[day][time_slot] = {
                        "subject": "BREAK",
                        "teacher": None,
                        "room": None,
                        "type": "break"
                    }
                else:
                    timetable[day][time_slot] = {
                        "subject": None,
                        "teacher": None,
                        "room": None,
                        "type": None  # lecture or practical
                    }
        return timetable
    
    def _get_constraints(self, department, program, acad_year, subjects, teachers, rooms):
        """Get all constraints for timetable generation"""
        constraints = {
            "teacher_availability": defaultdict(dict),
            "room_availability": defaultdict(dict),
            "teacher_workload": defaultdict(int),
            "teacher_max_workload": defaultdict(lambda: 20),  # Default max workload of 20 hours per week
            "subject_lectures_count": defaultdict(int),
            "subject_practicals_count": defaultdict(int),
            "max_lectures_per_subject": 2,    # Default max 2 lectures per week per subject
            "max_practicals_per_subject": 1,  # Default max 1 practical per week per subject
            "room_suitability": defaultdict(list),  # Maps subject types to appropriate room types
            "department_subject_priority": defaultdict(int),  # Priority level for department-specific subjects
            "cross_department_teachers": [],  # Teachers who teach across departments
            "shared_rooms": [],  # Rooms shared between departments
            "batch_size_constraints": defaultdict(int),  # Maximum batch size for rooms
        }
        
        # Add teacher availability constraints (if defined in database)
        for teacher in teachers:
            teacher_id = str(teacher["_id"])
            
            # Set teacher's maximum workload if defined
            if "max_workload" in teacher:
                constraints["teacher_max_workload"][teacher_id] = teacher["max_workload"]
            
            # Set teacher's availability
            if "availability" in teacher:
                constraints["teacher_availability"][teacher_id] = teacher["availability"]
                
            # Identify cross-department teachers
            if "departments" in teacher and len(teacher["departments"]) > 1:
                constraints["cross_department_teachers"].append(teacher_id)
        
        # Add room suitability constraints
        constraints["room_suitability"]["lecture"] = ["classroom", "lecture_hall"]
        constraints["room_suitability"]["practical"] = ["lab", "computer_lab"]
        constraints["room_suitability"]["project"] = ["lab", "project_room", "seminar_room"]
        
        # Add shared rooms (if defined)
        for room in rooms:
            room_id = str(room["_id"])
            
            # Mark shared rooms
            if "shared" in room and room["shared"]:
                constraints["shared_rooms"].append(room_id)
                
            # Set batch size constraints based on room capacity
            if "capacity" in room:
                constraints["batch_size_constraints"][room_id] = room["capacity"]
        
        # Add subject-specific constraints
        for subject in subjects:
            subject_id = str(subject["_id"])
            
            # Set custom max lectures/practicals per week if defined
            if "lectures_per_week" in subject:
                constraints["max_lectures_per_subject"] = subject["lectures_per_week"]
                
            if "practicals_per_week" in subject:
                constraints["max_practicals_per_subject"] = subject["practicals_per_week"]
                
            # Set subject priority (core subjects get higher priority)
            if "is_core" in subject and subject["is_core"]:
                constraints["department_subject_priority"][subject_id] = 10
            elif "priority" in subject:
                constraints["department_subject_priority"][subject_id] = subject["priority"]
            else:
                constraints["department_subject_priority"][subject_id] = 5  # Default priority
        
        # Add department-specific constraints
        if department:
            dept_id = str(department["_id"])
            
            # Get department time constraints if defined
            if "working_days" in department:
                constraints["working_days"] = department["working_days"]
            else:
                constraints["working_days"] = self.days  # Default to all days
                
            # Get department-specific break times if defined  
            if "break_slots" in department:
                constraints["break_slots"] = department["break_slots"]
            else:
                constraints["break_slots"] = self.break_slots  # Default breaks
                
            # Get preferred time slots for specific subject types
            if "preferred_slots" in department:
                constraints["preferred_slots"] = department["preferred_slots"]
        
        # Add program-specific constraints
        if program:
            prog_id = str(program["_id"])
            
            # Get program-specific lecture/practical patterns
            if "lecture_pattern" in program:
                constraints["lecture_pattern"] = program["lecture_pattern"]
                
            if "practical_pattern" in program:
                constraints["practical_pattern"] = program["practical_pattern"]
        
        # Add academic year specific constraints
        if acad_year:
            # Any special scheduling rules for this academic year
            if "special_constraints" in acad_year:
                constraints["special_constraints"] = acad_year["special_constraints"]
        
        return constraints
    
    def _schedule_lectures(self, timetables, subjects, teachers, rooms, constraints):
        """
        Schedule lectures for all branches together in the Main timetable
        """
        # Get working days (default or department-specific)
        working_days = constraints.get("working_days", self.days)
        
        # Get lecture subjects and sort by priority
        lecture_subjects = [s for s in subjects if s.get("type", "lecture") == "lecture"]
        lecture_subjects.sort(key=lambda s: constraints["department_subject_priority"].get(str(s["_id"]), 5), reverse=True)
        
        for day in working_days:
            for time_slot in self.time_slots:
                # Skip break slots
                if time_slot in self.break_slots or time_slot in constraints.get("break_slots", []):
                    continue
                    
                # Skip if this slot is already filled
                if timetables["Main"][day][time_slot]["subject"] is not None:
                    continue
                    
                # Try each lecture subject
                for subject in lecture_subjects:
                    subject_id = str(subject["_id"])
                    subject_code = subject.get("code", "")
                    
                    # Skip if this subject has reached its maximum lectures per week
                    max_lectures = constraints.get("max_lectures_per_subject", 2)
                    if "lectures_per_week" in subject:
                        max_lectures = subject["lectures_per_week"]
                        
                    if constraints["subject_lectures_count"][subject_id] >= max_lectures:
                        continue
                    
                    # Check if we should follow a specific lecture pattern
                    if "lecture_pattern" in constraints:
                        pattern = constraints["lecture_pattern"]
                        # Skip if this slot doesn't match the pattern for this subject
                        if not self._matches_pattern(subject_id, day, time_slot, pattern):
                            continue
                    
                    # Try teachers who can teach this subject, prioritizing those with expertise
                    suitable_teachers = []
                    for teacher in teachers:
                        teacher_id = str(teacher["_id"])
                        
                        # Check if teacher can teach this subject
                        can_teach = False
                        if "subjects" in teacher and subject_id in teacher["subjects"]:
                            can_teach = True
                            # Higher priority if it's a subject they specialize in
                            expertise_level = 2 if "expertise" in teacher and subject_id in teacher["expertise"] else 1
                        elif "departments" in teacher and subject.get("department_id") in teacher["departments"]:
                            can_teach = True
                            expertise_level = 0  # Can teach but not specialized
                            
                        if can_teach:
                            # Check if teacher has reached max workload
                            if constraints["teacher_workload"][teacher_id] >= constraints["teacher_max_workload"][teacher_id]:
                                continue
                                
                            # Check teacher availability
                            if day in constraints["teacher_availability"][teacher_id] and \
                               time_slot in constraints["teacher_availability"][teacher_id][day]:
                                continue
                                
                            suitable_teachers.append((teacher, expertise_level))
                    
                    # Sort teachers by expertise level (highest first)
                    suitable_teachers.sort(key=lambda x: x[1], reverse=True)
                    
                    assignment_made = False
                    # Try each suitable teacher
                    for teacher, _ in suitable_teachers:
                        teacher_id = str(teacher["_id"])
                        teacher_code = teacher.get("code", "")
                        
                        # Try each appropriate room
                        suitable_room_types = constraints["room_suitability"].get("lecture", ["classroom", "lecture_hall"])
                        for room in rooms:
                            room_id = str(room["_id"])
                            room_number = room.get("number", "")
                            room_type = room.get("type", "classroom")
                            
                            # Skip if room type doesn't match
                            if room_type not in suitable_room_types:
                                continue
                            
                            # Check room availability
                            if day in constraints["room_availability"][room_id] and \
                               time_slot in constraints["room_availability"][room_id][day]:
                                continue
                                
                            # All conditions met, assign lecture in the Main timetable
                            timetables["Main"][day][time_slot] = {
                                "subject": subject_id,
                                "subject_code": subject_code,
                                "teacher": teacher_id,
                                "teacher_code": teacher_code,
                                "room": room_id,
                                "room_number": room_number,
                                "type": "lecture"
                            }
                            
                            # Update constraints
                            constraints["subject_lectures_count"][subject_id] += 1
                            constraints["teacher_workload"][teacher_id] += 1
                            
                            # Mark teacher as unavailable for this slot
                            if day not in constraints["teacher_availability"][teacher_id]:
                                constraints["teacher_availability"][teacher_id][day] = []
                            constraints["teacher_availability"][teacher_id][day].append(time_slot)
                            
                            # Mark room as unavailable for this slot
                            if day not in constraints["room_availability"][room_id]:
                                constraints["room_availability"][room_id][day] = []
                            constraints["room_availability"][room_id][day].append(time_slot)
                            
                            assignment_made = True
                            break
                        
                        if assignment_made:
                            break
                    
                    if assignment_made:
                        break
        
        return True  # We only return False if it's impossible to schedule

    def _matches_pattern(self, subject_id, day, time_slot, pattern):
        """Helper method to check if a subject matches a specific lecture/practical pattern"""
        # Example pattern: {"ML": {"days": ["MONDAY", "WEDNESDAY"], "preferred_slots": ["9:00 am - 10:00 am"]}}
        if subject_id not in pattern:
            return True  # No specific pattern for this subject, so it matches
            
        subject_pattern = pattern[subject_id]
        
        # Check day constraint
        if "days" in subject_pattern and day not in subject_pattern["days"]:
            return False
            
        # Check time slot constraint
        if "preferred_slots" in subject_pattern and time_slot not in subject_pattern["preferred_slots"]:
            return False
            
        return True

    def _schedule_practicals(self, timetables, subjects, teachers, rooms, constraints):
        """
        Schedule practical sessions for each batch separately (B1, B2, B3)
        """
        # Get working days (default or department-specific)
        working_days = constraints.get("working_days", self.days)
        
        # Get all practical subjects and sort by priority
        practical_subjects = [s for s in subjects if s.get("type", "practical") == "practical"]
        practical_subjects.sort(key=lambda s: constraints["department_subject_priority"].get(str(s["_id"]), 5), reverse=True)
        
        # Get batch configuration - default is 3 batches (B1, B2, B3)
        batch_config = constraints.get("batch_config", {"count": 3, "prefix": "B"})
        batch_count = batch_config.get("count", 3)
        batch_prefix = batch_config.get("prefix", "B")
        batch_names = [f"{batch_prefix}{i}" for i in range(1, batch_count + 1)]
        
        for subject in practical_subjects:
            subject_id = str(subject["_id"])
            subject_code = subject.get("code", "")
            
            # Get maximum practicals per week for this subject
            max_practicals = constraints.get("max_practicals_per_subject", 1)
            if "practicals_per_week" in subject:
                max_practicals = subject["practicals_per_week"]
            
            # Get subject requirements
            req_consecutive_slots = subject.get("consecutive_slots", 1)  # Number of consecutive slots needed
            req_lab_type = subject.get("lab_type", "lab")  # Type of lab needed
            
            # Try each batch
            for batch_name in batch_names:
                # Try scheduling required number of practicals
                practicals_scheduled = 0
                while practicals_scheduled < max_practicals:
                    # Try each day and time_slot combination
                    assigned = False
                    
                    for day in working_days:
                        if assigned:
                            break
                        
                        # Check if we should follow a specific practical pattern
                        if "practical_pattern" in constraints:
                            pattern = constraints["practical_pattern"]
                            # If this subject has specific day constraints, check them
                            if subject_id in pattern and "days" in pattern[subject_id]:
                                if day not in pattern[subject_id]["days"]:
                                    continue  # Skip this day if it doesn't match the pattern
                            
                        for time_slot_idx in range(len(self.time_slots) - req_consecutive_slots + 1):
                            if assigned:
                                break
                                
                            # Check if we can schedule consecutive slots
                            can_schedule = True
                            slots_to_schedule = []
                            
                            # Check each consecutive slot
                            for i in range(req_consecutive_slots):
                                curr_slot_idx = time_slot_idx + i
                                if curr_slot_idx >= len(self.time_slots):
                                    can_schedule = False
                                    break
                                    
                                curr_slot = self.time_slots[curr_slot_idx]
                                
                                # Skip if this is a break slot
                                if curr_slot in self.break_slots or curr_slot in constraints.get("break_slots", []):
                                    can_schedule = False
                                    break
                                    
                                # Skip if this slot is used for a lecture in the Main timetable
                                if timetables["Main"][day][curr_slot]["subject"] is not None:
                                    can_schedule = False
                                    break
                                    
                                # Skip if slot is already occupied in this batch's timetable
                                if timetables[batch_name][day][curr_slot]["subject"] is not None:
                                    can_schedule = False
                                    break
                                
                                slots_to_schedule.append(curr_slot)
                            
                            if not can_schedule or not slots_to_schedule:
                                continue
                            
                            # Find suitable teachers who can teach all consecutive slots
                            suitable_teachers = []
                            for teacher in teachers:
                                teacher_id = str(teacher["_id"])
                                teacher_code = teacher.get("code", "")
                                
                                # Check if teacher can teach this subject
                                can_teach = False
                                if "subjects" in teacher and subject_id in teacher["subjects"]:
                                    can_teach = True
                                    # Higher priority if it's a subject they specialize in
                                    expertise_level = 2 if "expertise" in teacher and subject_id in teacher["expertise"] else 1
                                elif "departments" in teacher and subject.get("department_id") in teacher["departments"]:
                                    can_teach = True
                                    expertise_level = 0  # Can teach but not specialized
                                
                                if not can_teach:
                                    continue
                                    
                                # Check if teacher has reached max workload
                                remaining_workload = constraints["teacher_max_workload"][teacher_id] - constraints["teacher_workload"][teacher_id]
                                if remaining_workload < req_consecutive_slots:
                                    continue
                                
                                # Check if teacher is available for all consecutive slots
                                teacher_available = True
                                for slot in slots_to_schedule:
                                    # Check teacher availability
                                    if (day in constraints["teacher_availability"][teacher_id] and 
                                        slot in constraints["teacher_availability"][teacher_id][day]):
                                        teacher_available = False
                                        break
                                    
                                    # Check if teacher is busy with another practical in a different batch
                                    for other_batch in batch_names:
                                        if other_batch != batch_name:
                                            other_slot = timetables[other_batch][day][slot]
                                            if other_slot.get("teacher") == teacher_id and other_slot.get("type") == "practical":
                                                teacher_available = False
                                                break
                                
                                if teacher_available:
                                    suitable_teachers.append((teacher, expertise_level))
                            
                            # Sort teachers by expertise level (highest first)
                            suitable_teachers.sort(key=lambda x: x[1], reverse=True)
                            
                            if not suitable_teachers:
                                continue
                                
                            # Find suitable lab rooms that can be used for all consecutive slots
                            suitable_rooms = []
                            
                            # Get appropriate room types for this subject
                            room_types = constraints["room_suitability"].get("practical", ["lab"])
                            if req_lab_type:
                                if isinstance(req_lab_type, list):
                                    room_types = req_lab_type
                                else:
                                    room_types = [req_lab_type]
                                    
                            for room in rooms:
                                room_id = str(room["_id"])
                                room_number = room.get("number", "")
                                room_type = room.get("type", "lab")
                                room_capacity = room.get("capacity", 30)
                                
                                # Skip if room type doesn't match required types
                                if room_type not in room_types:
                                    continue
                                
                                # Check if room capacity is sufficient
                                batch_size = constraints.get("batch_size", 30)
                                if room_capacity < batch_size:
                                    continue
                                
                                # Check if room is available for all consecutive slots
                                room_available = True
                                
                                for slot in slots_to_schedule:
                                    # Check room availability from constraints
                                    if (day in constraints["room_availability"][room_id] and 
                                        slot in constraints["room_availability"][room_id][day]):
                                        room_available = False
                                        break
                                    
                                    # Check if room is busy with another practical
                                    for other_batch in batch_names:
                                        if other_batch != batch_name:
                                            other_slot = timetables[other_batch][day][slot]
                                            if (other_slot.get("room") == room_id and 
                                                other_slot.get("type") == "practical"):
                                                room_available = False
                                                break
                                
                                if room_available:
                                    # Check if shared room has specific department restrictions
                                    if room_id in constraints["shared_rooms"]:
                                        if "department_restriction" in room:
                                            dept_id = subject.get("department_id")
                                            if dept_id not in room["department_restriction"]:
                                                continue
                                    
                                    suitable_rooms.append(room)
                            
                            if not suitable_rooms:
                                continue
                            
                            # We have suitable teachers and rooms for all slots, assign the practical
                            teacher, _ = suitable_teachers[0]
                            teacher_id = str(teacher["_id"])
                            teacher_code = teacher.get("code", "")
                            
                            room = suitable_rooms[0]
                            room_id = str(room["_id"])
                            room_number = room.get("number", "")
                            
                            # Assign practical for all consecutive slots
                            for slot in slots_to_schedule:
                                timetables[batch_name][day][slot] = {
                                    "subject": subject_id,
                                    "subject_code": subject_code,
                                    "teacher": teacher_id,
                                    "teacher_code": teacher_code,
                                    "room": room_id,
                                    "room_number": room_number,
                                    "type": "practical",
                                    "practical_group": f"{subject_code}-{batch_name}"
                                }
                                
                                # Mark teacher as unavailable for this slot
                                if day not in constraints["teacher_availability"][teacher_id]:
                                    constraints["teacher_availability"][teacher_id][day] = []
                                constraints["teacher_availability"][teacher_id][day].append(slot)
                                
                                # Mark room as unavailable for this slot
                                if day not in constraints["room_availability"][room_id]:
                                    constraints["room_availability"][room_id][day] = []
                                constraints["room_availability"][room_id][day].append(slot)
                                
                                # Update teacher workload
                                constraints["teacher_workload"][teacher_id] += 1
                            
                            # Update constraints
                            constraints["subject_practicals_count"][subject_id] += 1
                            
                            assigned = True
                            practicals_scheduled += 1
                            break
                    
                    # If we couldn't assign a practical in any slot, give up on this batch
                    if not assigned:
                        break
                
                # If we couldn't schedule all required practicals for this subject and batch, return failure
                if practicals_scheduled < max_practicals:
                    return False
        
        return True
        
    def generate_formatted_timetable(self, department_id, academic_year):
        """
        Generate timetable and format it according to department-specific requirements
        """
        timetables = self.generate_timetable(department_id, academic_year)
        if not timetables:
            return None
            
        formatted_timetables = {}
        
        # Get department and program info
        department = self.db.departments.find_one({"_id": department_id})
        if not department:
            return None
            
        # Get batch configuration based on department settings
        batch_config = department.get('batch_config', {"count": 3, "prefix": "B"})
        batch_count = batch_config.get("count", 3)
        batch_prefix = batch_config.get("prefix", "B")
        batch_names = [f"{batch_prefix}{i}" for i in range(1, batch_count + 1)]
        
        # Format the Main timetable (lectures)
        main_timetable = {}
        for day, slots in timetables["Main"].items():
            main_timetable[day] = {}
            for time_slot, details in slots.items():
                if time_slot in self.break_slots or details["type"] == "break":
                    main_timetable[day][time_slot] = "BREAK"
                elif details["subject"] is None:
                    main_timetable[day][time_slot] = "-"
                else:
                    # Format: SUBJECT_CODE - TEACHER_CODE
                    subject_code = details.get("subject_code", "")
                    teacher_code = details.get("teacher_code", "")
                    room_number = details.get("room_number", "")
                    
                    # Get format from department settings or use default
                    format_template = department.get("format_template", "{subject_code} - {teacher_code}\n{room_number}")
                    formatted_cell = format_template.format(
                        subject_code=subject_code,
                        teacher_code=teacher_code,
                        room_number=room_number,
                        type=details.get("type", "")
                    )
                    main_timetable[day][time_slot] = formatted_cell
        
        formatted_timetables["Main"] = main_timetable
        
        # Format the batch timetables (practicals)
        for batch_name in timetables:
            if batch_name == "Main":
                continue
                
            batch_timetable = {}
            for day, slots in timetables[batch_name].items():
                batch_timetable[day] = {}
                for time_slot, details in slots.items():
                    if time_slot in self.break_slots or details["type"] == "break":
                        batch_timetable[day][time_slot] = "BREAK"
                    elif details["subject"] is None:
                        # If no batch-specific activity, check the Main timetable
                        main_details = timetables["Main"][day][time_slot]
                        if main_details["subject"] is None:
                            batch_timetable[day][time_slot] = "-"
                        else:
                            # Include the Main timetable lecture
                            subject_code = main_details.get("subject_code", "")
                            teacher_code = main_details.get("teacher_code", "")
                            room_number = main_details.get("room_number", "")
                            
                            # Get format from department settings or use default
                            format_template = department.get("format_template", "{subject_code} - {teacher_code}\n{room_number}")
                            formatted_cell = format_template.format(
                                subject_code=subject_code,
                                teacher_code=teacher_code,
                                room_number=room_number,
                                type=main_details.get("type", "")
                            )
                            batch_timetable[day][time_slot] = formatted_cell
                    else:
                        # Format: SUBJECT_CODE - TEACHER_CODE (BATCH)
                        subject_code = details.get("subject_code", "")
                        teacher_code = details.get("teacher_code", "")
                        room_number = details.get("room_number", "")
                        
                        # Get practical format from department settings or use default
                        practical_format_template = department.get("practical_format_template", 
                            "{subject_code} - {teacher_code}\n{batch_name}\n{room_number}")
                        formatted_cell = practical_format_template.format(
                            subject_code=subject_code,
                            teacher_code=teacher_code,
                            room_number=room_number,
                            batch_name=batch_name,
                            type=details.get("type", "")
                        )
                        batch_timetable[day][time_slot] = formatted_cell
            
            formatted_timetables[batch_name] = batch_timetable
        
        # Create combined view for all batches with different display formats based on department preference
        view_type = department.get("timetable_view_type", "combined")
        
        if view_type == "combined":
            # Create the final formatted timetable with all batches combined
            class_timetable = {}
            for day, slots in main_timetable.items():
                class_timetable[day] = {}
                for time_slot, details in slots.items():
                    if "BREAK" in details:
                        class_timetable[day][time_slot] = "BREAK"
                    else:
                        if details == "-":
                            # Check if any batch has a practical here
                            batch_entries = []
                            for batch_name in batch_names:
                                if batch_name not in formatted_timetables:
                                    continue
                                    
                                batch_details = formatted_timetables[batch_name][day][time_slot]
                                if batch_details != "-" and "BREAK" not in batch_details:
                                    batch_entries.append(f"{batch_name} - {batch_details}")
                            
                            if batch_entries:
                                class_timetable[day][time_slot] = "\n".join(batch_entries)
                            else:
                                class_timetable[day][time_slot] = "-"
                        else:
                            # This is a lecture for all
                            class_timetable[day][time_slot] = details
            
            formatted_timetables["Class"] = class_timetable
        elif view_type == "division":
            # Create separate views for each division if department has divisions
            divisions = department.get("divisions", ["A", "B", "C"])
            for division in divisions:
                div_timetable = {}
                for day, slots in main_timetable.items():
                    div_timetable[day] = {}
                    for time_slot, details in slots.items():
                        # Copy main timetable for divisions
                        div_timetable[day][time_slot] = details
                
                division_batches = [f"{batch_prefix}{division}{i}" for i in range(1, batch_count + 1)]
                for batch_name in division_batches:
                    if batch_name in formatted_timetables:
                        # Incorporate division-specific batch schedules
                        for day in div_timetable:
                            for time_slot in div_timetable[day]:
                                batch_details = formatted_timetables[batch_name][day][time_slot]
                                if batch_details != "-" and "BREAK" not in batch_details and div_timetable[day][time_slot] == "-":
                                    div_timetable[day][time_slot] = batch_details
                
                formatted_timetables[f"Division_{division}"] = div_timetable
        
        # Add metadata for reference
        formatted_timetables["metadata"] = {
            "department": department.get("name", ""),
            "academic_year": academic_year,
            "generated_at": self._get_current_timestamp(),
            "batch_structure": batch_names,
            "view_type": view_type
        }
        
        return formatted_timetables
        
    def _get_current_timestamp(self):
        """Returns current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
