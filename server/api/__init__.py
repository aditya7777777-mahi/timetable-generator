import os
import sys

# Use direct imports for database and models
from config.database import db

def init_models():
    """Initialize all models with database connection"""
    # Import models here to avoid circular imports
    from server.api.models.department import Department
    from server.api.models.teacher import Teacher
    from server.api.models.subject import Subject
    from server.api.models.room import Room
    from server.api.models.timetable import Timetable
    
    database = db.get_db()
    Department.initialize(database)
    Teacher.initialize(database)
    Subject.initialize(database)
    Room.initialize(database)
    Timetable.initialize(database)