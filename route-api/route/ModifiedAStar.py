# ModifiedAStar.py

import random

class ModifiedAStarAlgorithm:
    def __init__(self, graph, D_min, D_max):
        self.graph = graph
        self.D_min = D_min  # Minimum acceptable distance
        self.D_max = D_max  # Maximum acceptable distance

    def heuristic(self, node, target):
        """Calculates a heuristic with a slight randomness to explore alternative paths."""
        # A small random factor helps to explore alternative paths
        return random.uniform(0.8, 1.2) * 0  # Adjust as needed for the randomness

    def calculate_path(self, start, goal):
        open_set = {start}  # Nodes to be evaluated
        closed_set = set()   # Nodes already evaluated
        came_from = {}  # Records the best path

        g_score = {node: float('inf') for node in self.graph.nodes()}
        g_score[start] = 0

        f_score = {node: float('inf') for node in self.graph.nodes()}
        f_score[start] = self.heuristic(start, goal)

        while open_set:
            # Pick the node in open_set with the lowest f_score
            current = min(open_set, key=lambda node: f_score[node])

            # If we reach the goal and the distance is within the desired range, return the path
            if current == goal and self.D_min <= g_score[goal] <= self.D_max:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                # Convert g_score of the goal from meters to kilometers
                distance_in_km = g_score[goal] / 1000
                return path, distance_in_km

            open_set.remove(current)
            closed_set.add(current)

            # Evaluate neighbors of the current node
            for neighbor in self.graph.neighbors(current):
                if neighbor in closed_set:
                    continue

                tentative_g_score = g_score[current] + self.graph[current][neighbor]['weight']

                # Pruning: Skip paths that exceed the maximum allowed distance
                if tentative_g_score > self.D_max:
                    continue

                if tentative_g_score < g_score[neighbor]:
                    # This path to neighbor is better
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)

                    if neighbor not in open_set:
                        open_set.add(neighbor)

        # If no suitable path is found, try to adjust or find an alternative path
        return self._attempt_backtrack(start, goal, came_from, g_score)

    def _attempt_backtrack(self, start, goal, came_from, g_score):
        """Attempt to find a longer path if the found path is shorter than D_min."""
        # Backtracking logic to try and explore longer alternative paths
        path = []
        current = goal
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()

        # Check if the path length is less than D_min, then explore alternatives
        if g_score[goal] < self.D_min:
            # Logic to attempt longer paths, e.g., explore other neighbors
            for node in path:
                for neighbor in self.graph.neighbors(node):
                    tentative_g_score = g_score[node] + self.graph[node][neighbor]['weight']
                    if self.D_min <= tentative_g_score <= self.D_max:
                        g_score[goal] = tentative_g_score
                        path.append(neighbor)
                        break

        distance_in_km = g_score[goal] / 1000
        return path, distance_in_km if self.D_min <= g_score[goal] <= self.D_max else (None, None)
