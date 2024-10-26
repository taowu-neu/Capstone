# route-api/app.py

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from database.db import db
from model.models import Edge
from dotenv import load_dotenv
from route.round_trip_algorithm import RoundTripAlgorithm
from create_graph import build_graph
from controller.node import find_closest_node

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

with app.app_context():
    db.init_app(app)
    graph = build_graph()
    round_trip_algorithm = RoundTripAlgorithm(graph)
    print('Graph built successfully.')

@app.route('/')
def home():
    return jsonify(message="Welcome to my Flask app!")

@app.route('/roundtrip', methods=['POST'])
def get_round_trip():
    data = request.get_json()
    user_location = data.get('user_location')
    distance_km = data.get('distance')

    print(f"Received request for round trip with user location: {user_location} and distance: {distance_km} km")

    if not user_location or not distance_km:
        print("Invalid input received.")
        return jsonify({"error": "Invalid input"}), 400

    closest_node = find_closest_node(user_location['lng'], user_location['lat'])
    if closest_node is None:
        print("No nearby nodes found.")
        return jsonify({"error": "No nearby nodes found"}), 404

    print(f"Closest node found: {closest_node.id}")

    path, actual_distance_km = round_trip_algorithm.generate_round_trip(closest_node.id, distance_km)
    
    if path is None:
        print("No round trip path found.")
        return jsonify({"error": "No round trip found"}), 404

    print(f"Generated round trip path: {path}")
    print(f"Actual round trip distance: {actual_distance_km} km")
    return jsonify({"path": path, "distance": actual_distance_km})

if __name__ == '__main__':
    app.run(debug=True)
