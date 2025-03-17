from .base_model import BaseModel

class Department(BaseModel):
    collection_name = 'departments'

    @classmethod
    def create_with_defaults(cls, department_data):
        # Add default values if not present
        if 'years' not in department_data:
            department_data['years'] = {
                'SE': {'num_batches': 3},
                'TE': {'num_batches': 3},
                'BE': {'num_batches': 3}
            }
        
        department_data['batch_prefix'] = department_data.get('batch_prefix', 'B')
        department_data['breaks'] = department_data.get('breaks', [
            "11:00 am - 11:15 am",
            "1:15 pm - 1:45 pm"
        ])
        
        return cls.create(department_data)