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
    elevation_pref = data.get('elevation')
    poi_pref = data.get('poi')

    source_node = find_closest_node(source[1], source[0])
    target_node = find_closest_node(target[1], target[0])

    node_details = get_all_node_details()
    finder = BiDirectionalAStar(graph, node_details, elevation_pref=elevation_pref, poi_pref=poi_pref)

    # Generate paths within the specified distance range
    all_paths = finder.find_paths_within_distance(source_node.id, target_node.id, input_distance)
    
    paths = []
    for route, total_distance in all_paths:
        elevation_change, poi_count = 0.0, 0
        path_coordinates = [(node_details[node_id]['latitude'], node_details[node_id]['longitude']) for node_id in route]

        for j in range(len(route) - 1):
            node_id, next_node_id = route[j], route[j + 1]
            elevation_diff = abs(node_details[next_node_id]['elevation'] - node_details[node_id]['elevation'])
            elevation_change += elevation_diff
            if node_details[node_id]['is_poi']:
                poi_count += 1
        
        paths.append({
            "path_segments": path_coordinates,
            "distance": round(total_distance / 1000, 2),
            "elevation_change": round(elevation_change, 2),
            "poi_count": poi_count
        })
    
    # Normalize scores based on preferences
    elevation_changes = [path["elevation_change"] for path in paths]
    poi_counts = [path["poi_count"] for path in paths]
    min_elev, max_elev = min(elevation_changes), max(elevation_changes)
    min_poi, max_poi = min(poi_counts), max(poi_counts)

    def calculate_score(path):
        if elevation_pref == "max":
            elevation_score = (path["elevation_change"] - min_elev) / (max_elev - min_elev) if max_elev > min_elev else 0
        else:
            elevation_score = (max_elev - path["elevation_change"]) / (max_elev - min_elev) if max_elev > min_elev else 0

        if poi_pref == "max":
            poi_score = (path["poi_count"] - min_poi) / (max_poi - min_poi) if max_poi > min_poi else 0
        else:
            poi_score = (max_poi - path["poi_count"]) / (max_poi - min_poi) if max_poi > min_poi else 0

        # Weighted sum for multi-objective score
        return 0.5 * elevation_score + 0.5 * poi_score

    # Get the best path based on the calculated scores
    best_path = max(paths, key=calculate_score)
    
    return jsonify({"paths": paths, "best_path": best_path})

if __name__ == '__main__':
    with app.app_context():
        CORS(app)
        db.init_app(app)
        graph = build_graph()
    app.run(debug=True)
