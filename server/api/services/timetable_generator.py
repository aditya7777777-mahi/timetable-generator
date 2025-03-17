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

    def generate_timetable(self, department_id, academic_year):
        try:
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
                        year_subjects, teachers, rooms, department
                    )
                    
                    # Generate batch timetables if needed
                    for batch in range(1, 4):  # 3 batches
                        batch_key = f"{year}_B{batch}"
                        timetable_data[batch_key] = self._generate_batch_timetable(
                            year_subjects, teachers, rooms, department, batch
                        )

            return timetable_data

        except Exception as e:
            print(f"Error in timetable generation: {e}")
            raise

    def _generate_year_timetable(self, subjects, teachers, rooms, department):
        timetable = {}
        for day in self.days:
            timetable[day] = {}
            for slot in self.time_slots:
                if self._is_break_time(slot):
                    timetable[day][slot] = {"type": "break"}
                else:
                    # Assign subjects based on constraints
                    timetable[day][slot] = self._assign_slot(subjects, teachers, rooms)
        return timetable

    def _generate_batch_timetable(self, subjects, teachers, rooms, department, batch_num):
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
                        practical_subjects, teachers, rooms, True
                    )
        return timetable

    def _is_break_time(self, time_slot):
        return any(break_time.startswith(time_slot) for break_time in self.breaks)

    def _assign_slot(self, subjects, teachers, rooms, practical_only=False):
        # Simple assignment logic - can be enhanced with more sophisticated algorithms
        for subject in subjects:
            if practical_only and subject.get('type') != 'practical':
                continue
                
            # Find available teacher and room
            teacher = next((t for t in teachers if t.get('specialization') == subject.get('specialization')), None)
            room = next((r for r in rooms if r.get('type') == ('lab' if subject.get('type') == 'practical' else 'classroom')), None)
            
            if teacher and room:
                return {
                    "subject": subject.get('code'),
                    "teacher": teacher.get('code'),
                    "room": room.get('number'),
                    "type": subject.get('type')
                }
        
        return {"type": None}