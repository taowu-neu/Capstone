import heapq
from math import sqrt

class BiDirectionalAStar:
    def __init__(self, graph, node_details, elevation_pref="max", poi_pref="max"):
        self.graph = graph
        self.node_details = node_details
        self.elevation_pref = elevation_pref
        self.poi_pref = poi_pref

    def heuristic(self, node, goal):
        """Heuristic that considers only elevation and POI difference based on user preference."""
        # Adjust weights based on user preferences for elevation and POI
        weight_factor_elevation = 0.6 if self.elevation_pref == "max" else 0.4
        weight_factor_poi = 0.4 if self.poi_pref == "max" else 0.2

        node_data, goal_data = self.node_details[node], self.node_details[goal]

        # Calculate elevation difference
        elevation_diff = abs(node_data['elevation'] - goal_data['elevation'])

        # Handle None for is_poi: if None, treat as 0 (no POI)
        node_is_poi = node_data['is_poi'] if node_data['is_poi'] is not None else 0
        goal_is_poi = goal_data['is_poi'] if goal_data['is_poi'] is not None else 0
        poi_diff = abs(node_is_poi - goal_is_poi)

        # Weighted heuristic sum, considering only elevation and POI
        return (
            weight_factor_elevation * elevation_diff +
            weight_factor_poi * poi_diff
        )

    def find_paths_within_distance(self, start, goal, target_distance):
        """Find paths from start to goal within the target distance range."""
        
        min_distance = target_distance * 0.85
        max_distance = target_distance * 1.15

        forward_open_set = []
        backward_open_set = []

        heapq.heappush(forward_open_set, (0, start, 0, [start]))
        heapq.heappush(backward_open_set, (0, goal, 0, [goal]))

        forward_visited = {start: (0, [start])}
        backward_visited = {goal: (0, [goal])}

        valid_paths = []

        def expand_search(queue, visited, other_visited, direction):
            if not queue:
                return None

            _, current_node, current_distance, path = heapq.heappop(queue)

            if current_node in other_visited:
                other_distance, other_path = other_visited[current_node]
                total_distance = current_distance + other_distance
                if min_distance <= total_distance <= max_distance:
                    full_path = path + other_path if direction == 'forward' else other_path + path
                    valid_paths.append((full_path, total_distance))
                return

            for neighbor in self.graph.neighbors(current_node):
                edge_weight = self.graph[current_node][neighbor]['weight']
                new_distance = current_distance + edge_weight

                if new_distance > max_distance:
                    continue

                priority = new_distance + self.heuristic(neighbor, goal if direction == 'forward' else start)

                if neighbor not in visited or new_distance < visited[neighbor][0]:
                    visited[neighbor] = (new_distance, path + [neighbor] if direction == 'forward' else [neighbor] + path)
                    heapq.heappush(queue, (priority, neighbor, new_distance, path + [neighbor] if direction == 'forward' else [neighbor] + path))

        while forward_open_set or backward_open_set:
            expand_search(forward_open_set, forward_visited, backward_visited, 'forward')
            expand_search(backward_open_set, backward_visited, forward_visited, 'backward')

        return valid_paths
