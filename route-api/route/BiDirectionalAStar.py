import heapq
from math import sqrt
from functools import lru_cache

class BiDirectionalAStar:
    def __init__(self, graph, node_details):
        self.graph = graph
        self.node_details = node_details  # Cached node details in memory

    def heuristic(self, node, goal):
        """Optimized Euclidean distance heuristic with a weight factor."""
        weight_factor = 1.1  # Adjust this factor for tuning
        node_data, goal_data = self.node_details[node], self.node_details[goal]
        
        dx = node_data['longitude'] - goal_data['longitude']
        dy = node_data['latitude'] - goal_data['latitude']
        euclidean_distance = sqrt(dx ** 2 + dy ** 2)
        
        return weight_factor * euclidean_distance  # Return weighted Euclidean distance

    def find_path_within_distance(self, start, goal, target_distance):
        """Find a path from start to goal as close as possible to the target distance."""
        
        min_distance = target_distance * 0.85
        max_distance = target_distance * 1.15

        forward_open_set = []
        backward_open_set = []

        heapq.heappush(forward_open_set, (0, start, 0, [start]))
        heapq.heappush(backward_open_set, (0, goal, 0, [goal]))

        forward_visited = {start: (0, [start])}
        backward_visited = {goal: (0, [goal])}

        best_path = None
        closest_distance = float('inf')

        def expand_search(queue, visited, other_visited, direction):
            nonlocal best_path, closest_distance
            if not queue:
                return None

            _, current_node, current_distance, path = heapq.heappop(queue)

            if current_node in other_visited:
                other_distance, other_path = other_visited[current_node]
                total_distance = current_distance + other_distance
                if min_distance <= total_distance <= max_distance:
                    full_path = path + other_path if direction == 'forward' else other_path + path
                    if abs(total_distance - target_distance) < abs(closest_distance - target_distance):
                        best_path = full_path
                        closest_distance = total_distance
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

        return best_path if best_path is not None else None
