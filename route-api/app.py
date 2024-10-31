import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from database.db import db
from model.models import Edge, Node
from dotenv import load_dotenv
from route.BiDirectionalAStar import BiDirectionalAStar
from create_graph import build_graph
from controller.node import find_closest_node
from sqlalchemy import text

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Cache all node details in memory for faster access
def get_all_node_details():
    query = text("SELECT id, longitude, latitude, elevation, is_poi FROM nodes;")
    result = db.session.execute(query).fetchall()
    return {
        row.id: {
            "longitude": row.longitude,
            "latitude": row.latitude,
            "elevation": float(row.elevation),
            "is_poi": row.is_poi
        }
        for row in result
    }

@app.route('/route', methods=['POST'])
def get_route():
    data = request.get_json()
    source = data.get('source')
    target = data.get('target')
    input_distance = data.get('input_distance') * 1000  # Convert km to meters

    source_node = find_closest_node(source[1], source[0])
    target_node = find_closest_node(target[1], target[0])

    node_details = get_all_node_details()
    finder = BiDirectionalAStar(graph, node_details)
    
    paths = []
    distance_step = (input_distance * 1.15 - input_distance * 0.85) / 29  # Divide range into 30 steps

    for i in range(30):
        target_dist = input_distance * 0.85 + i * distance_step
        route = finder.find_path_within_distance(source_node.id, target_node.id, target_dist)
        
        if route:
            total_distance, elevation_change, poi_count = 0.0, 0.0, 0
            path_coordinates = [(node_details[node_id]['latitude'], node_details[node_id]['longitude']) for node_id in route]

            for j in range(len(route) - 1):
                node_id, next_node_id = route[j], route[j + 1]
                elevation_diff = abs(node_details[next_node_id]['elevation'] - node_details[node_id]['elevation'])
                elevation_change += elevation_diff
                if node_details[node_id]['is_poi']:
                    poi_count += 1
                if graph.has_edge(node_id, next_node_id):
                    total_distance += graph[node_id][next_node_id]['weight']
            
            paths.append({
                "path_segments": path_coordinates,
                "distance": round(total_distance / 1000, 2),  # Convert meters to km
                "elevation_change": round(elevation_change, 2),
                "poi_count": poi_count
            })
            print(f"Path {i+1}: Distance {total_distance / 1000} km, Elevation Change {elevation_change} m, POI Count {poi_count}")
    
    return jsonify(paths)

if __name__ == '__main__':
    with app.app_context():
        CORS(app)
        db.init_app(app)
        graph = build_graph()
    app.run(debug=True)
