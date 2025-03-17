from .base_model import BaseModel

class Room(BaseModel):
    collection_name = 'rooms'

    @classmethod
    def create_with_normalization(cls, room_data):
        # Normalize room number field
        if 'number' not in room_data and 'room_number' in room_data:
            room_data['number'] = room_data['room_number']
            del room_data['room_number']
        
        # Validate required fields
        if not room_data.get('number'):
            raise ValueError("Room number is required")
            
        # Updated to accept all room types used in timetable_generator.py
        valid_room_types = ['classroom', 'lab', 'lecture_hall', 'computer_lab']
        if not room_data.get('type') in valid_room_types:
            raise ValueError(f"Room type must be one of: {', '.join(valid_room_types)}")
            
        return cls.create(room_data)