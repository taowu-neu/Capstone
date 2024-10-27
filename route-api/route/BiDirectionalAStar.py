# route-api/route/BiDirectionalAStar.py

import heapq

class BiDirectionalAStar:
    def __init__(self, graph):
        self.graph = graph

    def heuristic(self, node, goal):
        """Heuristic function for A* (e.g., Euclidean or Manhattan distance)."""
        # Placeholder heuristic function, returns 0
        return 0

    def find_path_within_distance(self, start, goal, target_distance):
        """Find a path from start to goal within target_distance ± 10% using Bidirectional A*."""
        
        min_distance = target_distance * 0.9
        max_distance = target_distance * 1.1

        # Priority queues for forward and backward searches
        forward_open_set = []
        backward_open_set = []

        # Initialize the forward and backward search
        heapq.heappush(forward_open_set, (0, start, 0, [start]))  # (priority, node, distance, path)
        heapq.heappush(backward_open_set, (0, goal, 0, [goal]))

        # Dictionaries to store visited nodes and distances/paths for both searches
        forward_visited = {start: (0, [start])}
        backward_visited = {goal: (0, [goal])}

        best_path = None
        closest_distance = float('inf')

        def expand_search(queue, visited, other_visited, direction):
            """Expand one step in the search direction."""
            nonlocal best_path, closest_distance

            if not queue:
                return None

            # Pop the node with the lowest priority
            _, current_node, current_distance, path = heapq.heappop(queue)

            # Check if this node is also reached by the other search direction
            if current_node in other_visited:
                other_distance, other_path = other_visited[current_node]
                total_distance = current_distance + other_distance
                if min_distance <= total_distance <= max_distance:
                    full_path = path + other_path[::-1] if direction == 'forward' else other_path[::-1] + path
                    if abs(total_distance - target_distance) < abs(closest_distance - target_distance):
                        best_path = full_path
                        closest_distance = total_distance
                return

            # Expand neighbors
            for neighbor in self.graph.neighbors(current_node):
                edge_weight = self.graph[current_node][neighbor]['weight']
                new_distance = current_distance + edge_weight

                # Skip paths exceeding max_distance
                if new_distance > max_distance:
                    continue

                # Calculate priority with heuristic
                priority = new_distance + self.heuristic(neighbor, goal if direction == 'forward' else start)

                # Add to the priority queue if it's a shorter path to this neighbor
                if neighbor not in visited or new_distance < visited[neighbor][0]:
                    visited[neighbor] = (new_distance, path + [neighbor] if direction == 'forward' else [neighbor] + path)
                    heapq.heappush(queue, (priority, neighbor, new_distance, path + [neighbor] if direction == 'forward' else [neighbor] + path))

        # Start the bidirectional search
        while forward_open_set or backward_open_set:
            # Expand forward search
            expand_search(forward_open_set, forward_visited, backward_visited, 'forward')
            # Expand backward search
            expand_search(backward_open_set, backward_visited, forward_visited, 'backward')

        return best_path if best_path is not None else None
