# a_star_algorithm.py

class AStarAlgorithm:
    def __init__(self, graph):
        self.graph = graph

    def heuristic(self, node, target):
        """Calculates the heuristic for A* (currently a placeholder)."""
        return 0  # Implement your heuristic logic based on coordinates if needed

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

            # If we reach the goal, reconstruct the path
            if current == goal:
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

                # Calculate tentative g_score
                tentative_g_score = g_score[current] + self.graph[current][neighbor]['weight']

                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)

                    if neighbor not in open_set:
                        open_set.add(neighbor)

        return None, None  # Return None if no path is found
