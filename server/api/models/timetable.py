from .base_model import BaseModel
from bson import ObjectId
import datetime

class Timetable(BaseModel):
    collection_name = 'timetables'

    @classmethod
    def create_with_metadata(cls, timetable_data, raw_data=None):
        # Add metadata
        timetable_data['created_at'] = datetime.datetime.now()
        
        # Convert department_id to ObjectId if it's a string
        if isinstance(timetable_data.get('department_id'), str):
            timetable_data['department_id'] = ObjectId(timetable_data['department_id'])
            
        # If raw timetable data is provided, store both raw and formatted
        if raw_data:
            timetable_data['raw_data'] = raw_data
            timetable_data['type'] = 'raw'
        else:
            timetable_data['type'] = 'formatted'
            
        return cls.create(timetable_data)

    @classmethod
    def find_by_department(cls, department_id):
        """Find all timetables for a specific department"""
        return cls.find_all({
            "department_id": ObjectId(department_id)
        })

    @classmethod
    def get_formatted(cls, timetable_id):
        """Get a formatted version of a timetable"""
        timetable = cls.find_by_id(timetable_id)
        if not timetable:
            return None
            
        # If it's already formatted, return as is
        if timetable.get('formatted_timetables'):
            return {
                "_id": timetable['_id'],
                "department_id": timetable.get('department_id'),
                "academic_year": timetable.get('academic_year'),
                "timetable": timetable['formatted_timetables']
            }
            
        # If it's raw data, convert branch format to combined view
        if timetable.get('timetable'):
            branch_keys = [key for key in timetable['timetable'] if key.startswith('Branch-')]
            if branch_keys:
                combined = {}
                for day in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]:
                    combined[day] = {}
                    
                    # Get all time slots from the first branch
                    time_slots = list(timetable['timetable']['Branch-1'][day].keys()) if 'Branch-1' in timetable['timetable'] and day in timetable['timetable']['Branch-1'] else []
                    
                    for time_slot in time_slots:
                        if "break" in time_slot.lower():
                            continue
                            
                        combined[day][time_slot] = {}
                        
                        for branch_key in branch_keys:
                            branch_num = branch_key.split('-')[1]
                            branch_data = timetable['timetable'][branch_key].get(day, {}).get(time_slot, {})
                            
                            if branch_data and branch_data.get('subject'):
                                if combined[day][time_slot].get('subject'):
                                    combined[day][time_slot]['subject'] += f", B{branch_num}: {branch_data['subject']}"
                                    combined[day][time_slot]['teacher'] += f", {branch_data.get('teacher', 'N/A')}"
                                    combined[day][time_slot]['room'] += f", {branch_data.get('room', 'N/A')}"
                                else:
                                    combined[day][time_slot] = {
                                        'subject': f"B{branch_num}: {branch_data.get('subject', 'N/A')}",
                                        'teacher': branch_data.get('teacher', 'N/A'),
                                        'room': branch_data.get('room', 'N/A'),
                                        'type': branch_data.get('type', 'lecture')
                                    }
                
                return {
                    "_id": timetable['_id'],
                    "department_id": timetable.get('department_id'),
                    "academic_year": timetable.get('academic_year'),
                    "timetable": combined
                }
                
        return timetable