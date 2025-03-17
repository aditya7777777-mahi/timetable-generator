from .base_model import BaseModel

class Teacher(BaseModel):
    collection_name = 'teachers'

    @classmethod
    def create_with_code(cls, teacher_data):
        # Generate teacher code if not present
        if 'code' not in teacher_data and 'name' in teacher_data:
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
            
        return cls.create(teacher_data)