import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from database.db import db
from model.models import Edge
from dotenv import load_dotenv
from route.BiDirectionalAStar import BiDirectionalAStar
from create_graph import build_graph, verify_graph
from controller.edge import query_edges
from controller.node import find_closest_node, get_node_coordinates, get_node_details

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/')
def home():
    return jsonify(message="Welcome to my Flask app!")

@app.route('/route', methods=['POST'])
def get_route():
    data = request.get_json()
    source = data.get('source')
    target = data.get('target')
    input_distance = data.get('input_distance')

    source_node = find_closest_node(source[1], source[0])
    target_node = find_closest_node(target[1], target[0])

    finder = BiDirectionalAStar(graph)
    route = finder.find_path_within_distance(source_node.id, target_node.id, input_distance * 1000)

    if route:
        current_segment = []
        total_distance = 0.0
        total_elevation_change = 0.0  # Initialize elevation change
        poi_count = 0  # Initialize POI count

        path_coordinates = get_node_coordinates(route)
        node_details = get_node_details(route)

        for i in range(len(route) - 1):
            node_id = route[i]
            next_node_id = route[i + 1]

            if node_id in node_details and next_node_id in node_details:
                elevation_diff = abs(node_details[next_node_id]['elevation'] - node_details[node_id]['elevation'])
                total_elevation_change += elevation_diff

            if node_details[node_id]['is_poi']:
                poi_count += 1

            if graph.has_edge(route[i], route[i + 1]):
                edge = graph[route[i]][route[i + 1]]
                total_distance += edge['weight']

        total_distance_km = total_distance / 1000
        return jsonify({
            "path_segments": path_coordinates,
            "distance": round(total_distance_km, 2),
            "elevation_change": round(total_elevation_change, 2),
            "poi_count": poi_count
        })
    else:
        return jsonify({"message": "No path found within the specified distance range"}), 404

@app.route('/edges')
def get_edges():
    edges = query_edges()
    return edges

if __name__ == '__main__':
  with app.app_context():
      CORS(app)
      db.init_app(app)
      graph = build_graph()
  app.run(debug=True)
