"""
Timetable Generator Algorithm using Backtracking
"""
from collections import defaultdict
from bson.objectid import ObjectId
import random

class TimetableGenerator:
    def __init__(self, db):
        self.db = db
        self.days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        self.years = ["SE", "TE", "BE"]
        
        # Update time slots to include breaks
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
            "11:00 am - 11:15 am",  # Morning break
            "1:15 pm - 1:45 pm"     # Lunch break
        ]
        
        # Define consecutive slots for practicals (2 hours)
        self.practical_slot_pairs = [
            ("9:00 am - 10:00 am", "10:00 am - 11:00 am"),
            ("11:15 am - 12:15 pm", "12:15 pm - 1:15 pm"),
            ("1:45 pm - 2:45 pm", "2:45 pm - 3:45 pm")
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
        """Main function to generate timetable using backtracking algorithm"""
        # Convert string ID to ObjectId if needed
        if isinstance(department_id, str):
            try:
                department_id = ObjectId(department_id)
            except:
                # Keep as string if not a valid ObjectId
                pass

        department = self.db.departments.find_one({"_id": department_id})
        if not department:
            raise ValueError("Department not found")
        
        # Get subjects for all years using proper query
        year_subjects = {}
        for year in self.years:
            # Use both ObjectId and string versions of department_id in query
            subjects = list(self.db.subjects.find({
                "$or": [
                    {"department_id": department_id},
                    {"department_id_str": str(department_id)}
                ],
                "year": year
            }))
            
            if not subjects:
                print(f"No subjects found for {year} year. Creating demo subjects...")
                # Create demo subjects
                if year == "SE":
                    subjects = self._create_demo_se_subjects(department_id)
                elif year == "TE":
                    subjects = self._create_demo_te_subjects(department_id)
                else:  # BE
                    subjects = self._create_demo_be_subjects(department_id)
                
            year_subjects[year] = subjects
        
        # Get all teachers that can teach the subjects
        subject_ids = [str(s["_id"]) for year_subs in year_subjects.values() for s in year_subs]
        teachers = list(self.db.teachers.find({
            "$or": [
                {"subjects": {"$in": subject_ids}},
                {"departments": department_id}
            ]
        }))
        if not teachers:
            print("No teachers found. Creating demo teachers...")
            teachers = self._create_demo_teachers(department_id)
        
        # Get appropriate rooms for lectures and practicals
        rooms = list(self.db.rooms.find({
            "type": {"$in": ["classroom", "lecture_hall", "lab", "computer_lab"]}
        }))
        if not rooms:
            print("No rooms found. Creating demo rooms...")
            rooms = self._create_demo_rooms()
        
        # Initialize timetables for all years and batches
        timetables = {}
        for year in self.years:
            timetables[f"{year}_Main"] = self._create_empty_timetable()  # For lectures
            # Create batch timetables based on department configuration
            num_batches = department.get("years", {}).get(year, {}).get("num_batches", 3)
            for batch_num in range(1, num_batches + 1):
                timetables[f"{year}_B{batch_num}"] = self._create_empty_timetable()
        
        # Get constraints
        constraints = self._get_constraints(department, year_subjects, teachers, rooms)
        
        # Schedule for each year
        for year in self.years:
            year_success = self._schedule_year(
                year,
                timetables,
                year_subjects[year],
                teachers,
                rooms,
                constraints,
                existing_timetables={}  # We'll check conflicts directly in the timetables object
            )
            if not year_success:
                return None
        
        return timetables
    
    def _schedule_year(self, year, timetables, subjects, teachers, rooms, constraints, existing_timetables):
        """Schedule timetable for a specific year"""
        # First schedule lectures
        lecture_success = self._schedule_lectures(
            timetables[f"{year}_Main"],
            [s for s in subjects if s.get("type") == "lecture"],
            teachers,
            rooms,
            constraints,
            existing_timetables
        )
        
        if not lecture_success:
            return False
        
        # Then schedule practicals for each batch
        practical_success = self._schedule_practicals(
            timetables,
            [s for s in subjects if s.get("type") == "practical"],
            teachers,
            rooms,
            constraints,
            existing_timetables
        )
        
        return practical_success
    
    def _create_empty_timetable(self):
        """Create an empty timetable structure"""
        timetable = {}
        for day in self.days:
            timetable[day] = {}
            for time_slot in self.time_slots:
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
                        "type": None
                    }
        return timetable
    
    def _get_constraints(self, department, year_subjects, teachers, rooms):
        """Get all constraints for timetable generation"""
        constraints = {
            "teacher_availability": defaultdict(dict),
            "room_availability": defaultdict(dict),
            "teacher_workload": defaultdict(int),
            "teacher_max_workload": defaultdict(lambda: 20),
            "subject_lectures_count": defaultdict(int),
            "subject_practicals_count": defaultdict(int),
            "max_lectures_per_subject": 3,    # Theory subjects 3 times per week
            "max_practicals_per_subject": 1,  # Practicals once per week
            "practical_duration": 2,          # Practicals are 2 hours
            "lecture_duration": 1,            # Lectures are 1 hour
            "break_slots": self.break_slots,
            "practical_slot_pairs": self.practical_slot_pairs,
            "working_days": self.days         # Default to all weekdays
        }
        
        # Set up department subject priority
        constraints["department_subject_priority"] = {}
        
        # Add year-specific constraints
        for year, subjects in year_subjects.items():
            year_key = f"{year}_subjects"
            constraints[year_key] = {
                "lectures": [s for s in subjects if s.get("type") == "lecture"],
                "practicals": [s for s in subjects if s.get("type") == "practical"]
            }
            
            # Also add batch count for each year
            batch_key = f"{year}_batch_count"
            constraints[batch_key] = department.get("years", {}).get(year, {}).get("num_batches", 3)
        
        # Set up room types
        constraints["room_types"] = {
            "lecture": ["classroom", "lecture_hall"],
            "practical": ["lab", "computer_lab"]
        }
        
        # Initialize shared rooms list
        constraints["shared_rooms"] = []
        
        # Set up teacher-subject mapping for easier lookup
        teacher_subjects = defaultdict(list)
        for teacher in teachers:
            teacher_id = teacher.get("code", "")
            if "subjects" in teacher:
                for subject_id in teacher["subjects"]:
                    teacher_subjects[subject_id].append(teacher_id)
        
        constraints["teacher_subjects"] = dict(teacher_subjects)
        
        # Add department-specific constraints if available
        if department:
            # Department might specify specific working days
            if "working_days" in department:
                constraints["working_days"] = department["working_days"]
                
            # Department might specify specific break times
            if "breaks" in department:
                constraints["break_slots"] = department["breaks"]
                
            # Department might have specific room requirements
            if "room_requirements" in department:
                constraints["room_requirements"] = department["room_requirements"]
                
            # Subject priority might be specified by the department
            if "subject_priority" in department:
                for subject_id, priority in department["subject_priority"].items():
                    constraints["department_subject_priority"][subject_id] = priority
                    
        return constraints
    
    def _check_teacher_conflict(self, teacher_id, day, time_slot, existing_timetables):
        """Check if a teacher is already scheduled in other years/batches"""
        for year_timetable in existing_timetables:
            for timetable in year_timetable.values():
                if timetable[day][time_slot].get("teacher") == teacher_id:
                    return True
        return False
    
    def _check_room_conflict(self, room_id, day, time_slot, existing_timetables):
        """Check if a room is already scheduled in other years/batches"""
        for year_timetable in existing_timetables:
            for timetable in year_timetable.values():
                if timetable[day][time_slot].get("room") == room_id:
                    return True
        return False
    
    def _schedule_lectures(self, timetable, subjects, teachers, rooms, constraints, existing_timetables):
        """
        Schedule lectures for all branches together in the Main timetable
        """
        # Get working days (default or department-specific)
        working_days = constraints.get("working_days", self.days)
        
        # Get lecture subjects and sort by priority
        lecture_subjects = subjects
        if not lecture_subjects:
            return True  # No lectures to schedule
            
        # Sort by priority if available
        if "department_subject_priority" in constraints:
            lecture_subjects.sort(key=lambda s: constraints["department_subject_priority"].get(str(s["_id"]), 5), reverse=True)
        
        # Track subjects that have been scheduled
        scheduled_subjects = defaultdict(int)
        
        # Try to schedule each subject
        for subject in lecture_subjects:
            subject_id = subject.get("code", "SUBJ")  # Use code as ID for display
            max_lectures = subject.get("lectures_per_week", constraints.get("max_lectures_per_subject", 3))
            
            while scheduled_subjects[subject_id] < max_lectures:
                # Try to find a valid slot for this lecture
                scheduled = False
                
                # Randomize day and time slot order for variety
                days = list(working_days)
                random.shuffle(days)
                
                for day in days:
                    # Skip if we've already scheduled this subject on this day
                    day_scheduled = False
                    for time in self.time_slots:
                        if time in self.break_slots:
                            continue
                        if timetable[day][time]["subject"] == subject_id:
                            day_scheduled = True
                            break
                            
                    if day_scheduled:
                        continue
                        
                    # Get available time slots (excluding breaks)
                    available_slots = [time for time in self.time_slots 
                                      if time not in self.break_slots 
                                      and timetable[day][time]["subject"] is None]
                    random.shuffle(available_slots)
                    
                    for time_slot in available_slots:
                        # Check if valid slot (not a break)
                        if time_slot in self.break_slots:
                            continue
                            
                        # Select an available teacher for this subject
                        available_teachers = [t for t in teachers 
                                            if subject.get("teacher_id") is None  # If no specific teacher
                                            or t["_id"] == subject.get("teacher_id")]
                                            
                        random.shuffle(available_teachers)
                        teacher_assigned = False
                        
                        for teacher in available_teachers:
                            teacher_id = teacher.get("code", "TCH")  # Use code for display
                            
                            # Check if teacher is available at this time
                            if self._check_teacher_conflict(teacher_id, day, time_slot, existing_timetables):
                                continue
                                
                            # Check if teacher workload constraint is satisfied
                            if constraints["teacher_workload"][teacher_id] >= constraints["teacher_max_workload"][teacher_id]:
                                continue
                                
                            # Select an appropriate room
                            room_types = constraints["room_types"]["lecture"]
                            available_rooms = [r for r in rooms if r.get("type", "") in room_types]
                            random.shuffle(available_rooms)
                            
                            room_assigned = False
                            for room in available_rooms:
                                room_id = room.get("number", "RM")  # Use room number for display
                                
                                # Check if room is available
                                if self._check_room_conflict(room_id, day, time_slot, existing_timetables):
                                    continue
                                    
                                # We can schedule the lecture here!
                                timetable[day][time_slot] = {
                                    "subject": subject_id,
                                    "teacher": teacher_id,
                                    "room": room_id,
                                    "type": "lecture"
                                }
                                
                                # Update constraints
                                constraints["teacher_workload"][teacher_id] += 1
                                scheduled_subjects[subject_id] += 1
                                scheduled = True
                                teacher_assigned = True
                                room_assigned = True
                                break
                                
                            if room_assigned:
                                break
                                
                        if teacher_assigned:
                            break
                            
                    if scheduled:
                        break
                        
                if not scheduled:
                    # Could not schedule this lecture, might be impossible with current constraints
                    print(f"Warning: Could not schedule all lectures for {subject.get('name', subject_id)}")
                    break
        
        # Check if all required lectures were scheduled
        for subject in lecture_subjects:
            subject_id = subject.get("code", "SUBJ")
            required_lectures = subject.get("lectures_per_week", constraints.get("max_lectures_per_subject", 3))
            if scheduled_subjects[subject_id] < required_lectures:
                print(f"Warning: Scheduled only {scheduled_subjects[subject_id]} of {required_lectures} lectures for {subject.get('name', subject_id)}")
                
        return True  # Return success even with warnings
        
    def _schedule_practicals(self, timetables, subjects, teachers, rooms, constraints, existing_timetables):
        """
        Schedule practical sessions for each batch separately (B1, B2, B3)
        """
        # Get working days
        working_days = constraints.get("working_days", self.days)
        
        # Get practical subjects
        practical_subjects = subjects
        if not practical_subjects:
            return True  # No practicals to schedule
            
        # Get batch structure from constraints
        batch_counts = {}
        for year in self.years:
            year_key = f"{year}_batch_count"
            batch_counts[year] = constraints.get(year_key, 3)  # Default to 3 batches if not specified
            
        # Track practicals that have been scheduled
        scheduled_practicals = defaultdict(lambda: defaultdict(int))  # {subject_id: {batch: count}}
        
        # Try to schedule each practical for each batch
        for subject in practical_subjects:
            subject_id = subject.get("code", "SUBJ")
            year = subject.get("year", "TE")  # Default to TE if not specified
            max_practicals = subject.get("practicals_per_week", constraints.get("max_practicals_per_subject", 1))
            
            # Get all batch names for this year
            batch_names = [f"B{i}" for i in range(1, batch_counts.get(year, 3) + 1)]
            
            # For each batch, schedule the practical
            for batch_num, batch_name in enumerate(batch_names, 1):
                while scheduled_practicals[subject_id][batch_name] < max_practicals:
                    # Try to find a valid slot for this practical
                    scheduled = False
                    
                    # Get consecutive slots needed for practical
                    consecutive_slots = subject.get("consecutive_slots", constraints.get("practical_duration", 2))
                    
                    # Get list of slot pairs
                    slot_pairs = constraints.get("practical_slot_pairs", self.practical_slot_pairs)
                    if consecutive_slots > 2:
                        # If we need more than 2 consecutive slots, we need to build custom pairs
                        # This is a simplified version that assumes 2-hour practicals
                        slot_pairs = self.practical_slot_pairs
                        
                    # Randomize day order for variety
                    days = list(working_days)
                    random.shuffle(days)
                    
                    for day in days:
                        # Randomize slot pair order
                        slot_pair_indices = list(range(len(slot_pairs)))
                        random.shuffle(slot_pair_indices)
                        
                        for idx in slot_pair_indices:
                            slot_group = slot_pairs[idx]
                            
                            # Check if these slots are available for this batch
                            batch_timetable_key = f"{year}_{batch_name}"
                            
                            # Check if all slots are available
                            can_schedule = True
                            for slot in slot_group:
                                # Skip if slot is a break
                                if slot in self.break_slots:
                                    can_schedule = False
                                    break
                                    
                                # Check if slot is already scheduled in main or batch timetable
                                if timetables[f"{year}_Main"][day][slot]["subject"] is not None:
                                    can_schedule = False
                                    break
                                    
                                if timetables[batch_timetable_key][day][slot]["subject"] is not None:
                                    can_schedule = False
                                    break
                                    
                            if not can_schedule:
                                continue
                                
                            # Find an available teacher
                            available_teachers = [t for t in teachers 
                                                if subject.get("teacher_id") is None  # If no specific teacher
                                                or t["_id"] == subject.get("teacher_id")]
                            random.shuffle(available_teachers)
                            
                            teacher_assigned = False
                            for teacher in available_teachers:
                                teacher_id = teacher.get("code", "TCH")
                                
                                # Check if teacher is available for all slots
                                teacher_available = True
                                for slot in slot_group:
                                    # Check conflicts with existing timetables
                                    if self._check_teacher_conflict(teacher_id, day, slot, existing_timetables):
                                        teacher_available = False
                                        break
                                        
                                    # Check if teacher is busy with another practical in a different batch
                                    for other_batch in batch_names:
                                        if other_batch != batch_name:
                                            other_batch_key = f"{year}_{other_batch}"
                                            if other_batch_key in timetables:
                                                other_slot = timetables[other_batch_key][day][slot]
                                                if other_slot.get("teacher") == teacher_id and other_slot.get("type") == "practical":
                                                    teacher_available = False
                                                    break
                                                    
                                if not teacher_available:
                                    continue
                                    
                                # Find an available lab room
                                room_types = constraints["room_types"]["practical"]
                                available_rooms = [r for r in rooms if r.get("type", "") in room_types]
                                random.shuffle(available_rooms)
                                
                                room_assigned = False
                                for room in available_rooms:
                                    room_id = room.get("number", "LAB")
                                    
                                    # Check if room is available for all slots
                                    room_available = True
                                    for slot in slot_group:
                                        # Check conflicts with existing timetables
                                        if self._check_room_conflict(room_id, day, slot, existing_timetables):
                                            room_available = False
                                            break
                                            
                                        # Check if room is busy with another practical
                                        for other_batch in batch_names:
                                            if other_batch != batch_name:
                                                other_batch_key = f"{year}_{other_batch}"
                                                if other_batch_key in timetables:
                                                    other_slot = timetables[other_batch_key][day][slot]
                                                    if (other_slot.get("room") == room_id and 
                                                        other_slot.get("type") == "practical"):
                                                        room_available = False
                                                        break
                                                        
                                    if not room_available:
                                        continue
                                        
                                    # We can schedule the practical here!
                                    for slot in slot_group:
                                        timetables[batch_timetable_key][day][slot] = {
                                            "subject": subject_id,
                                            "teacher": teacher_id,
                                            "room": room_id,
                                            "type": "practical",
                                            "batch": batch_name
                                        }
                                        
                                    # Update counters
                                    constraints["teacher_workload"][teacher_id] += consecutive_slots
                                    scheduled_practicals[subject_id][batch_name] += 1
                                    scheduled = True
                                    room_assigned = True
                                    break
                                    
                                if room_assigned:
                                    teacher_assigned = True
                                    break
                                    
                            if teacher_assigned:
                                break
                                
                        if scheduled:
                            break
                            
                    if not scheduled:
                        # Could not schedule this practical
                        print(f"Warning: Could not schedule practical for {subject.get('name', subject_id)} - Batch {batch_name}")
                        break
                        
        # Check if all required practicals were scheduled
        all_scheduled = True
        for subject in practical_subjects:
            subject_id = subject.get("code", "SUBJ")
            year = subject.get("year", "TE")
            required_practicals = subject.get("practicals_per_week", constraints.get("max_practicals_per_subject", 1))
            
            batch_names = [f"B{i}" for i in range(1, batch_counts.get(year, 3) + 1)]
            for batch_name in batch_names:
                if scheduled_practicals[subject_id][batch_name] < required_practicals:
                    print(f"Warning: Could not schedule all practicals for {subject.get('name', subject_id)} - Batch {batch_name}")
                    all_scheduled = False
                    
        return True  # Return success even with warnings
        
    def generate_formatted_timetable(self, department_id, academic_year):
        """
        Generate timetable and format it according to department-specific requirements
        """
        # Generate raw timetable first
        timetables = self.generate_timetable(department_id, academic_year)
        if not timetables:
            return None
            
        # Get department and program details for formatting
        department = self.db.departments.find_one({"_id": department_id})
        if not department:
            return None
            
        # Format timetables for each academic year
        formatted_timetables = {}
        
        # Process each academic year
        for year in ["SE", "TE", "BE"]:
            # Create a combined timetable for this year
            formatted_timetables[year] = self._format_combined_timetable(timetables, year, department)
                
        return formatted_timetables
        
    def _format_combined_timetable(self, timetables, year, department):
        """
        Format a combined timetable that shows lectures and practicals for all batches in one view
        Organized by time slots (rows) and days (columns)
        """
        main_key = f"{year}_Main"
        if main_key not in timetables:
            return {}
            
        # Get batch information
        batch_count = department.get("years", {}).get(year, {}).get("num_batches", 3)
        batch_names = [f"B{i}" for i in range(1, batch_count + 1)]
        
        # Create a timetable structure with time slots as primary keys
        combined_timetable = {}
        
        # Initialize the structure first - time slots as primary keys
        time_slots_without_breaks = [ts for ts in self.time_slots if ts not in self.break_slots]
        for time_slot in time_slots_without_breaks:
            combined_timetable[time_slot] = {}
            for day in self.days:
                combined_timetable[time_slot][day] = "-"  # Empty slot by default
        
        # Fill in the lectures from main timetable
        for day in self.days:
            for time_slot in time_slots_without_breaks:
                # Skip breaks
                if time_slot in self.break_slots:
                    continue
                
                # Get main timetable entry (lectures)
                main_slot = timetables[main_key][day][time_slot]
                
                # If there's a lecture in the main timetable, add it
                if main_slot["subject"] is not None:
                    subject_code = main_slot["subject"]
                    teacher_code = main_slot["teacher"]
                    room_number = main_slot["room"]
                    
                    combined_timetable[time_slot][day] = f"{year} (Main): {subject_code} - {teacher_code} ({room_number})"
        
        # Add the practicals from batch timetables
        for batch_num in range(1, batch_count + 1):
            batch_name = f"B{batch_num}"
            batch_key = f"{year}_{batch_name}"
            
            if batch_key in timetables:
                for day in self.days:
                    for time_slot in time_slots_without_breaks:
                        # Skip breaks
                        if time_slot in self.break_slots:
                            continue
                        
                        batch_slot = timetables[batch_key][day][time_slot]
                        
                        if batch_slot["subject"] is not None:
                            subject_code = batch_slot["subject"]
                            teacher_code = batch_slot["teacher"]
                            room_number = batch_slot["room"]
                            
                            # If the slot already has a lecture, append the practical
                            # Otherwise create a new entry
                            current_value = combined_timetable[time_slot][day]
                            if current_value == "-":
                                combined_timetable[time_slot][day] = f"{year} ({batch_name}): {subject_code} - {teacher_code} ({room_number})"
                            else:
                                combined_timetable[time_slot][day] += f"\n{year} ({batch_name}): {subject_code} - {teacher_code} ({room_number})"
        
        return combined_timetable

    def _create_demo_se_subjects(self, department_id):
        """Create demo subjects for SE year"""
        se_subjects = [
            {
                "_id": ObjectId(),
                "name": "Data Structures",
                "code": "DS",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "SE",
                "type": "lecture",
                "lectures_per_week": 3
            },
            {
                "_id": ObjectId(),
                "name": "Object-Oriented Programming",
                "code": "OOP",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "SE",
                "type": "lecture",
                "lectures_per_week": 3
            },
            {
                "_id": ObjectId(),
                "name": "Database Management Systems",
                "code": "DBMS",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "SE",
                "type": "lecture",
                "lectures_per_week": 3
            },
            {
                "_id": ObjectId(),
                "name": "Computer Networks",
                "code": "CN",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "SE",
                "type": "lecture",
                "lectures_per_week": 3
            },
            {
                "_id": ObjectId(),
                "name": "Data Structures Lab",
                "code": "DS Lab",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "SE",
                "type": "practical",
                "practicals_per_week": 1,
                "consecutive_slots": 2
            },
            {
                "_id": ObjectId(),
                "name": "OOP Lab",
                "code": "OOP Lab",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "SE",
                "type": "practical",
                "practicals_per_week": 1,
                "consecutive_slots": 2
            },
            {
                "_id": ObjectId(),
                "name": "DBMS Lab",
                "code": "DBMS Lab",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "SE",
                "type": "practical",
                "practicals_per_week": 1,
                "consecutive_slots": 2
            }
        ]
        
        # Insert into database
        for subject in se_subjects:
            self.db.subjects.insert_one(subject)
            
        return se_subjects
        
    def _create_demo_te_subjects(self, department_id):
        """Create demo subjects for TE year"""
        te_subjects = [
            {
                "_id": ObjectId(),
                "name": "Machine Learning",
                "code": "ML",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "TE",
                "type": "lecture",
                "lectures_per_week": 3
            },
            {
                "_id": ObjectId(),
                "name": "Data Analytics and Visualization",
                "code": "DAV",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "TE",
                "type": "lecture",
                "lectures_per_week": 3
            },
            {
                "_id": ObjectId(),
                "name": "Software Engineering and Project Management",
                "code": "SEPM",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "TE",
                "type": "lecture",
                "lectures_per_week": 3
            },
            {
                "_id": ObjectId(),
                "name": "Machine Learning Lab",
                "code": "ML Lab",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "TE",
                "type": "practical",
                "practicals_per_week": 1,
                "consecutive_slots": 2
            },
            {
                "_id": ObjectId(),
                "name": "DAV Lab",
                "code": "DAV Lab",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "TE",
                "type": "practical",
                "practicals_per_week": 1,
                "consecutive_slots": 2
            },
            {
                "_id": ObjectId(),
                "name": "SEPM Lab",
                "code": "SEPM Lab",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "TE",
                "type": "practical",
                "practicals_per_week": 1,
                "consecutive_slots": 2
            }
        ]
        
        # Insert into database
        for subject in te_subjects:
            self.db.subjects.insert_one(subject)
            
        return te_subjects

    def _create_demo_be_subjects(self, department_id):
        """Create demo subjects for BE year"""
        be_subjects = [
            {
                "_id": ObjectId(),
                "name": "Distributed Computing",
                "code": "DC",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "BE",
                "type": "lecture",
                "lectures_per_week": 3
            },
            {
                "_id": ObjectId(),
                "name": "Cryptography and System Security",
                "code": "CSS",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "BE",
                "type": "lecture",
                "lectures_per_week": 3
            },
            {
                "_id": ObjectId(),
                "name": "Cloud Computing",
                "code": "CC",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "BE",
                "type": "lecture",
                "lectures_per_week": 3
            },
            {
                "_id": ObjectId(),
                "name": "DC Lab",
                "code": "DC Lab",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "BE",
                "type": "practical",
                "practicals_per_week": 1,
                "consecutive_slots": 2
            },
            {
                "_id": ObjectId(),
                "name": "CSS Lab",
                "code": "CSS Lab",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "BE",
                "type": "practical",
                "practicals_per_week": 1,
                "consecutive_slots": 2
            },
            {
                "_id": ObjectId(),
                "name": "Mini Project",
                "code": "MP",
                "department_id": department_id,
                "department_id_str": str(department_id),
                "year": "BE",
                "type": "practical",
                "practicals_per_week": 1,
                "consecutive_slots": 2
            }
        ]
        
        # Insert into database
        for subject in be_subjects:
            self.db.subjects.insert_one(subject)
            
        return be_subjects

    def _create_demo_teachers(self, department_id):
        """Create demo teachers"""
        teachers = [
            {
                "_id": ObjectId(),
                "name": "Dr. Sandeep B. Raskar",
                "code": "SBR",
                "departments": [department_id],
                "subjects": []
            },
            {
                "_id": ObjectId(),
                "name": "Prof. Sayalee Narkhede",
                "code": "SJN",
                "departments": [department_id],
                "subjects": []
            },
            {
                "_id": ObjectId(),
                "name": "Prof. Smita Pawar",
                "code": "SP",
                "departments": [department_id],
                "subjects": []
            },
            {
                "_id": ObjectId(),
                "name": "Mr. Shrikant Bamane",
                "code": "SB",
                "departments": [department_id],
                "subjects": []
            },
            {
                "_id": ObjectId(),
                "name": "Mr. Deepak Thorat",
                "code": "DT",
                "departments": [department_id],
                "subjects": []
            },
            {
                "_id": ObjectId(),
                "name": "Mr. Kishor Biradar",
                "code": "KB",
                "departments": [department_id],
                "subjects": []
            },
            {
                "_id": ObjectId(),
                "name": "Mr. Samsul Ekram",
                "code": "SE",
                "departments": [department_id],
                "subjects": []
            }
        ]
        
        # Insert into database
        for teacher in teachers:
            self.db.teachers.insert_one(teacher)
            
        return teachers

    def _create_demo_rooms(self):
        """Create demo rooms"""
        rooms = [
            {
                "_id": ObjectId(),
                "number": "101",
                "type": "classroom",
                "capacity": 60
            },
            {
                "_id": ObjectId(),
                "number": "102",
                "type": "classroom",
                "capacity": 60
            },
            {
                "_id": ObjectId(),
                "number": "103",
                "type": "lecture_hall",
                "capacity": 120
            },
            {
                "_id": ObjectId(),
                "number": "201",
                "type": "lab",
                "capacity": 30
            },
            {
                "_id": ObjectId(),
                "number": "202",
                "type": "lab",
                "capacity": 30
            },
            {
                "_id": ObjectId(),
                "number": "203",
                "type": "computer_lab",
                "capacity": 30
            }
        ]
        
        # Insert into database
        for room in rooms:
            self.db.rooms.insert_one(room)
            
        return rooms

    def _get_current_timestamp(self):
        """Returns current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
