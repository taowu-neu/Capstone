import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from database.db import db
from model.models import Edge
from dotenv import load_dotenv
from route.BiDirectionalAStar import BiDirectionalAStar  # 导入新的双向A*算法
from create_graph import build_graph, verify_graph
from controller.edge import query_edges
from controller.node import find_closest_node, get_node_coordinates

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

with app.app_context():
    CORS(app)
    db.init_app(app)
    graph = build_graph()
    print('build graph complete...', graph)

@app.route('/')
def home():
    return jsonify(message="Welcome to my Flask app!")

@app.route('/route', methods=['POST'])
def get_route():
    data = request.get_json()
    source = data.get('source')
    target = data.get('target')
    input_distance = data.get('input_distance')

    # Find the closest nodes to the provided source and target points
    source_node = find_closest_node(source[1], source[0])
    target_node = find_closest_node(target[1], target[0])

    # 使用 BiDirectionalAStar 作为默认路径生成算法
    finder = BiDirectionalAStar(graph)
    route = finder.find_path_within_distance(source_node.id, target_node.id, input_distance * 1000)  # Convert km to meters

    # If route is found, return the path and distance
    if route:
        path = get_node_coordinates(route)
        total_distance = 0.0

        # Calculate total distance, with edge existence check
        for i in range(len(route) - 1):
            if graph.has_edge(route[i], route[i + 1]):
                edge = graph[route[i]][route[i + 1]]
                total_distance += edge['weight']
            else:
                print(f"Warning: Missing edge between {route[i]} and {route[i + 1]}")
                # Skip this segment if the edge does not exist
                continue

        total_distance_km = total_distance / 1000  # Convert meters to kilometers
        return jsonify({"path": path, "distance": round(total_distance_km, 2)})
    else:
        return jsonify({"message": "No path found within the specified distance range"}), 404

@app.route('/edges')
def get_edges():
    edges = query_edges()
    return edges

if __name__ == '__main__':
    app.run(debug=True)
