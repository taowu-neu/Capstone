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
import networkx as nx
import requests

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

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

@app.route('/proxy/google_places', methods=['GET'])
def proxy_google_places():
    """Proxy route for Google Places API Autocomplete."""
    google_api_key = "AIzaSyDBpCjhtC6Ne9GqU84l4qLcMs4O_gzDwyM"
    input_text = request.args.get("input")
    url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json?input={input_text}&key={google_api_key}"

    response = requests.get(url)
    return jsonify(response.json())

@app.route('/proxy/google_geocode', methods=['GET'])
def proxy_google_geocode():
    """Proxy route for Google Geocode API."""
    google_api_key = "AIzaSyDBpCjhtC6Ne9GqU84l4qLcMs4O_gzDwyM"
    place_id = request.args.get("place_id")
    url = f"https://maps.googleapis.com/maps/api/geocode/json?place_id={place_id}&key={google_api_key}"

    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch geocode data"}), 500
    return jsonify(response.json())

@app.route('/route', methods=['POST'])
def get_route():
    try:
        data = request.get_json()
        source = data.get('source')
        target = data.get('target')
        input_distance = data.get('input_distance') * 1000 
        elevation_range = data.get('elevation_range')
        poi_min = data.get('poi_min')
        priority_factor = data.get('priority_factor')

        source_node = find_closest_node(source[1], source[0])
        target_node = find_closest_node(target[1], target[0])

        if not nx.has_path(graph, source_node.id, target_node.id):
            return jsonify({'message': 'Node is not reachable.'})
        
        shortest_distance = nx.dijkstra_path_length(graph, source_node.id, target_node.id, weight='weight')
        if input_distance < shortest_distance:
            return jsonify({
                'message': f'Input distance is too small. Please increase the distance to at least {shortest_distance / 1000:.2f} km.'
            })
        
        node_details = get_all_node_details()
        finder = BiDirectionalAStar(graph, node_details, elevation_pref="max", poi_pref="max")

        all_paths = finder.find_paths_within_distance(source_node.id, target_node.id, input_distance)

        def filter_paths(paths):
            filtered_paths = []
            elevation_changes = [] 
            poi_counts = [] 

            min_elev, max_elev = map(int, elevation_range.split('-') if '-' in elevation_range else (1000, float('inf')))

            for path, total_distance in paths:
                elevation_change, poi_count = 0.0, 0
                for i in range(len(path) - 1):
                    node_id, next_node_id = path[i], path[i + 1]
                    elevation_diff = abs(node_details[next_node_id]['elevation'] - node_details[node_id]['elevation'])
                    elevation_change += elevation_diff
                    if node_details[node_id]['is_poi']:
                        poi_count += 1
                
                elevation_changes.append(elevation_change)
                poi_counts.append(poi_count)

                if priority_factor == 'elevation':
                    if min_elev <= elevation_change <= max_elev:
                        filtered_paths.append((path, total_distance, elevation_change, poi_count))
                elif priority_factor == 'poi' and poi_count >= poi_min:
                    filtered_paths.append((path, total_distance, elevation_change, poi_count))
            
            if priority_factor == 'poi':
                filtered_paths.sort(key=lambda p: abs(p[2] - (min_elev + max_elev) / 2)) 
            elif priority_factor == 'elevation':
                filtered_paths.sort(key=lambda p: abs(p[3] - poi_min))
            
            return filtered_paths, elevation_changes, poi_counts

        valid_paths, elevation_changes, poi_counts = filter_paths(all_paths)

        if priority_factor == 'elevation' and not valid_paths:
            min_elevation_change = min(elevation_changes) if elevation_changes else 0
            max_elevation_change = max(elevation_changes) if elevation_changes else 0
            return jsonify({
                'message': f"No path exists within the current elevation range. "
                           f"The minimum elevation change is: {min_elevation_change:.2f} m, "
                           f"and the maximum elevation change is: {max_elevation_change:.2f} m."
            })

        if priority_factor == 'poi' and not valid_paths:
            min_poi_count = min(poi_counts) if poi_counts else 0
            max_poi_count = max(poi_counts) if poi_counts else 0
            return jsonify({
                'message': f"No path exists within the current POI limit. "
                           f"The minimum POIs count is: {min_poi_count}, "
                           f"and the maximum POIs count is: {max_poi_count}."
            })

        if not valid_paths:
            raise Exception("No route found.")

        paths = []
        for route, total_distance, elevation_change, poi_count in valid_paths:
            path_coordinates = [(node_details[node_id]['latitude'], node_details[node_id]['longitude']) for node_id in route]
            poi_nodes = [(node_details[node_id]['latitude'], node_details[node_id]['longitude'])
                         for node_id in route if node_details[node_id]['is_poi']]

            paths.append({
                "path_segments": path_coordinates,
                "poi_nodes": poi_nodes,
                "distance": round(total_distance / 1000, 2),
                "elevation_change": round(elevation_change, 2),
                "poi_count": poi_count
            })

        best_path = paths[0]
    
        return jsonify({"paths": paths, "best_path": best_path})
    except Exception as e:
        response = {
            'message': 'Route not found.',
            'error': str(e)
        }
        return jsonify(response), 404


if __name__ == '__main__':
    with app.app_context():
        db.init_app(app)
        graph = build_graph()
    app.run(debug=True)
