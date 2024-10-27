# route-api/route/ConstrainedPathFinder.py

import heapq

class ConstrainedPathFinder:
    def __init__(self, graph):
        self.graph = graph

    def heuristic(self, node, goal):
        """Heuristic function for A* (can use straight-line distance as an example)."""
        # Placeholder heuristic function, returns 0
        return 0

    def find_path_within_distance(self, start, goal, target_distance):
        """Find a path from start to goal within target_distance ± 10% using A* with distance constraint."""

        min_distance = target_distance * 0.9
        max_distance = target_distance * 1.1

        # Priority queue for A* search
        open_set = []
        heapq.heappush(open_set, (0, start, 0, [start]))  # (priority, current_node, current_distance, path)

        # Track the closest path found within distance range
        best_path = None
        closest_distance = float('inf')

        while open_set:
            # Pop node with lowest priority
            _, current_node, current_distance, path = heapq.heappop(open_set)

            # Check if current path reaches the goal within distance range
            if current_node == goal:
                if min_distance <= current_distance <= max_distance:
                    if abs(current_distance - target_distance) < abs(closest_distance - target_distance):
                        best_path = path[:]
                        closest_distance = current_distance
                    # Continue to explore other possible paths to see if a closer one exists
                    continue

            # Expand neighbors
            for neighbor in self.graph.neighbors(current_node):
                edge_weight = self.graph[current_node][neighbor]['weight']
                new_distance = current_distance + edge_weight

                # Skip this path if the new distance exceeds max_distance
                if new_distance > max_distance:
                    continue

                # Calculate heuristic (estimate to goal) for A* priority
                priority = new_distance + self.heuristic(neighbor, goal)

                # Add neighbor to the open set with updated path and distance
                heapq.heappush(open_set, (priority, neighbor, new_distance, path + [neighbor]))

        return best_path if best_path is not None else None
