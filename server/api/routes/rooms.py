from flask import Blueprint, jsonify, request
from pymongo.errors import PyMongoError
from api.models.room import Room

rooms = Blueprint('rooms', __name__)

@rooms.route('/api/rooms', methods=['GET', 'POST'])
def handle_rooms():
    try:
        if request.method == 'POST':
            room_data = request.json
            room_id = Room.create(room_data)
            return jsonify({
                "id": room_id,
                "message": "Room added successfully"
            }), 201
        else:
            rooms = Room.find_all()
            return jsonify(Room.to_json_friendly(rooms))
    except PyMongoError as e:
        print(f"Database error in rooms route: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error in rooms route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@rooms.route('/api/rooms/<room_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_room(room_id):
    try:
        if request.method == 'GET':
            room = Room.find_by_id(room_id)
            if not room:
                return jsonify({"error": "Room not found"}), 404
            return jsonify(Room.to_json_friendly(room))
            
        elif request.method == 'PUT':
            if Room.update_by_id(room_id, request.json):
                return jsonify({"message": "Room updated successfully"})
            return jsonify({"error": "Room not found"}), 404
            
        elif request.method == 'DELETE':
            if Room.delete_by_id(room_id):
                return jsonify({"message": "Room deleted successfully"})
            return jsonify({"error": "Room not found"}), 404
    except PyMongoError as e:
        print(f"Database error in rooms route: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error in rooms route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@rooms.route('/api/rooms/types', methods=['GET'])
def get_room_types():
    try:
        types = ["classroom", "lecture_hall", "lab", "computer_lab"]
        return jsonify(types)
    except Exception as e:
        print(f"Unexpected error getting room types: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500