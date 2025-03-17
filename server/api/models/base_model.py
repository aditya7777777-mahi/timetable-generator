from bson import ObjectId
from pymongo.errors import PyMongoError

class BaseModel:
    collection_name = None
    _db = None

    @classmethod
    def initialize(cls, db):
        cls._db = db

    @classmethod
    def _get_collection(cls):
        if cls._db is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return cls._db[cls.collection_name]

    @classmethod
    def create(cls, data):
        try:
            result = cls._get_collection().insert_one(data)
            return str(result.inserted_id)
        except PyMongoError as e:
            print(f"Database error in create: {str(e)}")
            raise

    @classmethod
    def find_all(cls):
        try:
            return list(cls._get_collection().find())
        except PyMongoError as e:
            print(f"Database error in find_all: {str(e)}")
            raise

    @classmethod
    def find_by_id(cls, id):
        try:
            if isinstance(id, str):
                try:
                    id = ObjectId(id)
                except:
                    return None
            return cls._get_collection().find_one({"_id": id})
        except PyMongoError as e:
            print(f"Database error in find_by_id: {str(e)}")
            raise

    @classmethod
    def update_by_id(cls, id, data):
        try:
            if isinstance(id, str):
                try:
                    id = ObjectId(id)
                except:
                    return False
            result = cls._get_collection().update_one(
                {"_id": id},
                {"$set": data}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            print(f"Database error in update_by_id: {str(e)}")
            raise

    @classmethod
    def delete_by_id(cls, id):
        try:
            if isinstance(id, str):
                try:
                    id = ObjectId(id)
                except:
                    return False
            result = cls._get_collection().delete_one({"_id": id})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"Database error in delete_by_id: {str(e)}")
            raise

    @staticmethod
    def to_json_friendly(data):
        """
        Recursively convert MongoDB documents to JSON-serializable format.
        Handles ObjectId instances, nested dictionaries and lists.
        """
        if isinstance(data, list):
            return [BaseModel._convert_document(item) for item in data]
        elif isinstance(data, dict):
            return BaseModel._convert_document(data)
        return data

    @staticmethod
    def _convert_document(doc):
        """Helper method to convert a single document to JSON-friendly format"""
        if not isinstance(doc, dict):
            return doc

        result = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, list):
                result[key] = [BaseModel._convert_document(item) if isinstance(item, dict) 
                              else (str(item) if isinstance(item, ObjectId) else item) 
                              for item in value]
            elif isinstance(value, dict):
                result[key] = BaseModel._convert_document(value)
            else:
                result[key] = value

        return result