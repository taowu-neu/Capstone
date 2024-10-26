# route-api/route/round_trip_algorithm.py

import math
from util.dist_table_wrapper import DistTableWrapper
from sqlalchemy import text
from database.db import db
from model.models import Node

class RoundTripAlgorithm:
    def __init__(self, graph):
        self.graph = graph

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate the Haversine distance between two latitude/longitude pairs."""
        R = 6371e3  # Radius of the Earth in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c  # Distance in meters

    def build_distance_table(self, nodes):
        """Build a distance matrix for the provided nodes."""
        n = len(nodes)
        distance_matrix = [[0] * n for _ in range(n)]

        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes):
                if i != j:
                    distance = self.calculate_distance(
                        node1.latitude, node1.longitude,
                        node2.latitude, node2.longitude
                    )
                    distance_matrix[i][j] = distance
                else:
                    distance_matrix[i][j] = float('inf')  # No self-loops

        return DistTableWrapper(distance_matrix, n)

    def generate_round_trip(self, start_node_id, distance_km):
        """Generate a round trip route starting from the given node."""
        print(f"Generating round trip for start node {start_node_id} with distance {distance_km} km")

        # 获取距离起点一定范围内的节点，例如用户输入距离的1.5倍
        start_node = db.session.query(Node).filter_by(id=start_node_id).first()
        radius_km = distance_km * 1.5  # 可以调整这个倍数
        nodes = self.get_all_nodes(start_node, radius_km)
        print(f"Found {len(nodes)} nodes for round trip calculation.")

        # 如果获取的节点数过少，给出提示
        if len(nodes) < 3:
            print("Not enough nodes to generate a round trip.")
            return None, 0

        node_id_map = {node.id: idx for idx, node in enumerate(nodes)}
        start_index = node_id_map[start_node_id]

        distance_matrix = self.build_distance_table(nodes)
        print(f"Built distance matrix for {len(nodes)} nodes.")

        # Use the farthest insertion heuristic to find the round trip
        path_indices = self.farthest_insertion_trip(distance_matrix, start_index)
        print(f"Path indices after farthest insertion: {path_indices}")

        # Map node indices back to IDs and create the path
        path = [nodes[idx] for idx in path_indices]
        path_coords = [(node.latitude, node.longitude) for node in path]

        distance_m = sum(
            distance_matrix(path_indices[i], path_indices[i + 1]) for i in range(len(path_indices) - 1)
        ) + distance_matrix(path_indices[-1], path_indices[0])  # Return to start

        print(f"Generated path coordinates: {path_coords}")
        print(f"Total calculated distance: {distance_m / 1000.0} km")

        return path_coords, distance_m / 1000.0  # Return distance in km

    def farthest_insertion_trip(self, dist_table, start_index):
        """Implement the farthest insertion algorithm."""
        n = dist_table.get_number_of_nodes()
        unvisited = set(range(n))
        unvisited.remove(start_index)
        path = [start_index]

        while unvisited:
            next_node = max(unvisited, key=lambda node: min(dist_table(path[-1], node) for path in path))
            path.append(next_node)
            unvisited.remove(next_node)

        path.append(start_index)  # Close the round trip
        return path

    def get_all_nodes(self, start_node, radius_km=10):
        """Retrieve all nodes within a bounding box, then filter by distance."""
        radius_m = radius_km * 1000  # Convert km to meters

        # Convert radius to degrees (approximation)
        delta_lat = radius_km / 111  # Approximate: 1 degree latitude ~ 111 km
        delta_lon = radius_km / (111 * math.cos(math.radians(start_node.latitude)))

        min_lat = start_node.latitude - delta_lat
        max_lat = start_node.latitude + delta_lat
        min_lon = start_node.longitude - delta_lon
        max_lon = start_node.longitude + delta_lon

        print(f"Bounding box: ({min_lat}, {min_lon}) to ({max_lat}, {max_lon})")

        query = text("""
            SELECT id, longitude, latitude
            FROM nodes
            WHERE latitude BETWEEN :min_lat AND :max_lat
            AND longitude BETWEEN :min_lon AND :max_lon;
        """)

        result = db.session.execute(query, {
            "min_lat": min_lat, "max_lat": max_lat,
            "min_lon": min_lon, "max_lon": max_lon
        }).fetchall()

        # Map query result to Node objects
        nodes = [Node(id=row[0], longitude=row[1], latitude=row[2]) for row in result]

        # Further filter nodes using Haversine formula to ensure they are within radius
        filtered_nodes = [
            node for node in nodes
            if self.calculate_distance(start_node.latitude, start_node.longitude, node.latitude, node.longitude) <= radius_m
        ]

        print(f"Query returned {len(filtered_nodes)} nodes within {radius_km} km after filtering.")
        return filtered_nodes
