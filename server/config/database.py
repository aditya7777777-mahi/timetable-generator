import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    def __init__(self):
        self.client = None
        self.db = None

    def connect(self):
        try:
            # Use environment variables for connection settings
            mongo_uri = os.getenv('MONGO_URI', "mongodb+srv://adityabasude13:13777adi@cluster0.4weinpi.mongodb.net/")
            db_name = os.getenv('DB_NAME', 'timetable_db')
            
            print(f"Connecting to MongoDB at: {mongo_uri}")
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
            
            # Force a connection to verify it works
            self.client.server_info()
            print("Connected to MongoDB successfully!")
            
            self.db = self.client[db_name]
            return self.db
            
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise e

    def get_db(self):
        if not self.db:
            return self.connect()
        return self.db

# Create a global instance
db = Database()