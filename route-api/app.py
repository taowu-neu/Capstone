import os
from flask import Flask, jsonify
from database.db import db
from model.models import Edge
from dotenv import load_dotenv
from route.AStarAlgorithmn import AStarAlgorithm
from create_graph import build_graph

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

with app.app_context():
    db.init_app(app)
    graph = build_graph()
    print(graph)

@app.route('/')
def home():
    return jsonify(message="Welcome to my Flask app!")

@app.route('/route')
def get_route():
    algo = AStarAlgorithm(graph)
    route = algo.calculate_path(419439031, 139030956, 999999999)
    print(route)


if __name__ == '__main__':
    app.run(debug=True)