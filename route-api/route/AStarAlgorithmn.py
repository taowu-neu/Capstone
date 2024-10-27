# route-api/route/AStarAlgorithmn.py

class AStarAlgorithm:
    def __init__(self, graph):
        self.graph = graph

    def heuristic(self, node, target):
        """Calculates the heuristic for A* (currently a placeholder)."""
        return 0  # Implement your heuristic logic based on coordinates if needed

    def calculate_constrained_path(self, start, goal, target_distance):
        """Calculate a path from start to goal with a constrained distance range."""
        min_distance = target_distance * 0.9
        max_distance = target_distance * 1.1

        # Initialize structures
        open_set = {start}
        closed_set = set()
        came_from = {}

        g_score = {node: float('inf') for node in self.graph.nodes()}
        g_score[start] = 0

        f_score = {node: float('inf') for node in self.graph.nodes()}
        f_score[start] = self.heuristic(start, goal)

        closest_path = None
        closest_distance = float('inf')

        while open_set:
            # Pick the node with the lowest f_score
            current = min(open_set, key=lambda node: f_score[node])
            current_distance = g_score[current]

            # Check if current path to goal meets distance constraints
            if current == goal:
                if min_distance <= current_distance <= max_distance:
                    path = []
                    while current in came_from:
                        path.append(current)
                        current = came_from[current]
                    path.append(start)
                    return path[::-1]  # Return the path from start to goal

                # Record the closest path if within the min_distance
                if abs(current_distance - target_distance) < abs(closest_distance - target_distance):
                    closest_path = []
                    while current in came_from:
                        closest_path.append(current)
                        current = came_from[current]
                    closest_path.append(start)
                    closest_distance = current_distance

            # Remove current from open_set if it exists to prevent KeyError
            if current in open_set:
                open_set.remove(current)
            closed_set.add(current)

            # Evaluate neighbors
            for neighbor in self.graph.neighbors(current):
                if neighbor in closed_set:
                    continue

                tentative_g_score = g_score[current] + self.graph[current][neighbor]['weight']

                # Skip if over max_distance
                if tentative_g_score > max_distance:
                    continue

                # Update path if better than existing
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)

                    if neighbor not in open_set:
                        open_set.add(neighbor)

        # Return the closest path if no exact match within range
        return closest_path if closest_path is not None else None
