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

    if route:
        current_segment = []
        total_distance = 0.0

        # 遍历路径中的节点并检查边是否存在
        for i in range(len(route) - 1):
            if route[i] == route[i + 1]:
                continue
            if graph.has_edge(route[i], route[i + 1]):
                # 如果边存在，将该节点加入当前段
                if not current_segment:
                    current_segment.append(route[i])  # 添加段的起始节点
                current_segment.append(route[i + 1])

                # 计算距离
                edge = graph[route[i]][route[i + 1]]
                total_distance += edge['weight']
            else:
                print(f"Warning: Missing edge between {route[i]} and {route[i + 1]}")

        # 将每段的坐标转化为经纬度形式
        path_coordinates = get_node_coordinates(route)

        # 将路径总距离转换为公里
        total_distance_km = total_distance / 1000
        return jsonify({"path_segments": path_coordinates, "distance": round(total_distance_km, 2)})
    else:
        return jsonify({"message": "No path found within the specified distance range"}), 404

@app.route('/edges')
def get_edges():
    edges = query_edges()
    return edges

if __name__ == '__main__':
    app.run(debug=True)
