import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from database.db import db
from model.models import Edge
from dotenv import load_dotenv
from route.AStarAlgorithmn import AStarAlgorithm
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
    # verify_graph()

@app.route('/')
def home():
    return jsonify(message="Welcome to my Flask app!")

@app.route('/route', methods=['POST'])
def get_route():
    data = request.get_json()
    source = data.get('source')
    target = data.get('target')
    source_node = find_closest_node(source[1], source[0])
    target_node = find_closest_node(target[1], target[0])
    
    algo = AStarAlgorithm(graph)
    route = algo.calculate_path(source_node.id, target_node.id)
    path = get_node_coordinates(route)
    return jsonify({"path": path})

@app.route('/edges')
def get_edges():
    edges = query_edges()
    return edges

if __name__ == '__main__':
    app.run(debug=True)