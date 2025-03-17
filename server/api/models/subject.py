from .base_model import BaseModel
from bson import ObjectId

class Subject(BaseModel):
    collection_name = 'subjects'

    @classmethod
    def create_with_validation(cls, subject_data, department_collection, teacher_collection):
        # Validate department_id
        if 'department_id' not in subject_data or not subject_data['department_id']:
            raise ValueError("Department ID is required")
            
        # Get department to validate
        department = department_collection.find_one({"_id": ObjectId(subject_data['department_id'])})
        if not department:
            raise ValueError("Department not found")
        
        # Validate year field
        if 'year' not in subject_data or subject_data['year'] not in ['SE', 'TE', 'BE']:
            raise ValueError("Valid year (SE/TE/BE) is required")
            
        # Validate subject type
        if 'type' not in subject_data or subject_data['type'] not in ['lecture', 'practical']:
            raise ValueError("Valid type (lecture/practical) is required")
        
        # Validate teacher_id if provided
        if 'teacher_id' in subject_data and subject_data['teacher_id']:
            teacher = teacher_collection.find_one({"_id": ObjectId(subject_data['teacher_id'])})
            if not teacher:
                raise ValueError("Teacher not found")
            
            # Store teacher details
            subject_data['teacher_id'] = ObjectId(subject_data['teacher_id'])
            subject_data['teacher_id_str'] = str(subject_data['teacher_id'])
            subject_data['teacher_name'] = teacher.get('name', '')
            subject_data['teacher_code'] = teacher.get('code', '')
            
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
            subject_data['consecutive_slots'] = 2    # 2-hour practicals
        
        return cls.create(subject_data)

    @classmethod
    def find_by_department(cls, department_id, year=None):
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
            
        return cls.find_all(query)
        
    @classmethod
    def find_by_teacher(cls, teacher_id):
        # Query subjects by teacher
        query = {
            "$or": [
                {"teacher_id": ObjectId(teacher_id)},
                {"teacher_id_str": str(teacher_id)}
            ]
        }
        
        return cls.find_all(query)