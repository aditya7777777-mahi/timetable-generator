from bson import ObjectId
from api.models.department import Department
from api.models.subject import Subject
from api.models.teacher import Teacher
from api.models.room import Room

class TimetableGeneratorService:
    def __init__(self):
        self.days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        self.time_slots = [
            "9:00 am", "10:00 am", "11:00 am", "11:15 am",
            "12:15 pm", "1:15 pm", "1:45 pm", "2:45 pm", "3:45 pm"
        ]
        self.breaks = [
            "11:00 am - 11:15 am",
            "1:15 pm - 1:45 pm"
        ]
        # Track teacher and room assignments for conflict prevention
        self.teacher_assignments = {}  # {day: {slot: teacher_id}}
        self.room_assignments = {}     # {day: {slot: room_id}}

    def generate_timetable(self, department_id, academic_year):
        try:
            # Reset assignments for new generation
            self.teacher_assignments = {day: {slot: {} for slot in self.time_slots} for day in self.days}
            self.room_assignments = {day: {slot: {} for slot in self.time_slots} for day in self.days}
            
            # Validate department exists
            department = Department.find_by_id(department_id)
            if not department:
                raise ValueError("Department not found")
                
            # Get subjects for this department
            subjects = Subject.find_by_department(department_id)
            if not subjects:
                raise ValueError("No subjects found for this department")
                
            # Get all teachers and rooms
            teachers = Teacher.find_all()
            rooms = Room.find_all()
            if not teachers:
                raise ValueError("No teachers available")
            if not rooms:
                raise ValueError("No rooms available")
                
            # Generate timetables for each year (SE, TE, BE)
            timetable_data = {}
            for year in ['SE', 'TE', 'BE']:
                year_subjects = [s for s in subjects if s['year'] == year]
                if year_subjects:
                    timetable_data[f"{year}_Main"] = self._generate_year_timetable(
                        year_subjects, teachers, rooms, department, f"{year}_Main"
                    )
                    
                    # Generate batch timetables if needed
                    for batch in range(1, 4):  # 3 batches
                        batch_key = f"{year}_B{batch}"
                        timetable_data[batch_key] = self._generate_batch_timetable(
                            year_subjects, teachers, rooms, department, batch, batch_key
                        )
            return timetable_data
        except Exception as e:
            print(f"Error in timetable generation: {e}")
            raise

    def _generate_year_timetable(self, subjects, teachers, rooms, department, timetable_id):
        timetable = {}
        for day in self.days:
            timetable[day] = {}
            for slot in self.time_slots:
                if self._is_break_time(slot):
                    timetable[day][slot] = {"type": "break"}
                else:
                    # Assign subjects based on constraints
                    timetable[day][slot] = self._assign_slot(
                        subjects, teachers, rooms, day, slot, timetable_id
                    )
        return timetable

    def _generate_batch_timetable(self, subjects, teachers, rooms, department, batch_num, timetable_id):
        # Similar to _generate_year_timetable but only for practical subjects
        timetable = {}
        practical_subjects = [s for s in subjects if s.get('type') == 'practical']
        
        for day in self.days:
            timetable[day] = {}
            for slot in self.time_slots:
                if self._is_break_time(slot):
                    timetable[day][slot] = {"type": "break"}
                else:
                    # For batch timetables, only assign practical sessions
                    timetable[day][slot] = self._assign_slot(
                        practical_subjects, teachers, rooms, day, slot, timetable_id, True
                    )
        return timetable

    def _is_break_time(self, time_slot):
        return any(break_time.startswith(time_slot) for break_time in self.breaks)

    def _assign_slot(self, subjects, teachers, rooms, day, time_slot, timetable_id, practical_only=False):
        # Enhanced assignment logic with conflict prevention
        for subject in subjects:
            if practical_only and subject.get('type') != 'practical':
                continue
                
            # Check if subject has a specific teacher assigned
            if 'teacher_id' in subject and subject['teacher_id']:
                # Find the assigned teacher
                teacher = next((t for t in teachers if str(t.get('_id')) == str(subject['teacher_id'])), None)
                
                # Check if the teacher is already scheduled for this time slot
                if teacher:
                    teacher_id = str(teacher.get('_id'))
                    
                    # Skip if teacher is already assigned in this time slot
                    if teacher_id in self.teacher_assignments[day][time_slot]:
                        continue
            else:
                # Find any available teacher with the right specialization
                teacher = next((t for t in teachers 
                               if t.get('specialization') == subject.get('specialization')
                               and str(t.get('_id')) not in self.teacher_assignments[day][time_slot]), None)
                
            # If no teacher found, skip this subject
            if not teacher:
                continue
                
            # Find an appropriate available room
            room_type = 'lab' if subject.get('type') == 'practical' else 'classroom'
            room = next((r for r in rooms 
                       if r.get('type') == room_type
                       and str(r.get('_id')) not in self.room_assignments[day][time_slot]), None)
            
            # If no room available, skip
            if not room:
                continue
                
            # Mark teacher and room as assigned for this slot
            teacher_id = str(teacher.get('_id'))
            room_id = str(room.get('_id'))
            
            self.teacher_assignments[day][time_slot][teacher_id] = timetable_id
            self.room_assignments[day][time_slot][room_id] = timetable_id
            
            return {
                "subject": subject.get('code', subject.get('name', '')),
                "subject_name": subject.get('name', ''),
                "teacher": teacher.get('code', ''),
                "teacher_name": teacher.get('name', ''),
                "room": room.get('number', ''),
                "type": subject.get('type', '')
            }
        
        return {"type": "free"}  # No assignment could be made, slot is free