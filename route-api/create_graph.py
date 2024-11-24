import networkx as nx
import joblib
import os
from model.models import Edge, Node
from database.db import db
from sqlalchemy.orm import aliased
from sqlalchemy import func
from sqlalchemy import text

cache_directory = 'cache'
cache_graph_path = os.path.join(cache_directory, 'graph_cache.pkl')

def build_graph():
    print('build graph start...')
    # Load cached graph
    if os.path.exists(cache_graph_path):
        cached_graph = joblib.load(cache_graph_path)
        print("load cached graph complete.")
        return cached_graph
  
    # Create a new graph
    graph = nx.Graph()
    
    # Query all edges from the database
    edges =  Edge.query.add_columns(Edge.source, Edge.target, Edge.length).all()
    
    # Add edges to the graph
    for edge in edges:
        graph.add_edge(edge.source, edge.target, weight=edge.length)
    # Cache the graph
    os.makedirs(cache_directory, exist_ok=True)
    joblib.dump(graph, cache_graph_path)
    print('build graph complete...', graph)
    return graph


def find_path_with_min_distance(graph, source_node_id, min_distance):
    def dfs(node, current_path, current_distance, visited):
        # Base case: If the path distance exceeds min_distance, return the path
        if current_distance > min_distance:
            return current_path
        
        visited.add(node)  # Mark the node as visited

        # Explore neighbors
        for neighbor in graph.neighbors(node):
            if neighbor in visited:  # Skip visited nodes
                continue
            
            # Get the weight (distance) of the edge
            distance = graph[node][neighbor]['weight']

            # Recurse with the updated path and distance
            result = dfs(
                neighbor,
                current_path + [neighbor],
                current_distance + distance,
                visited
            )
            
            if result:  # If a valid path is found, return it
                return result

        visited.remove(node)  # Backtrack
        return None  # No valid path found

    # Initialize DFS
    visited = set()
    start_path = [source_node_id]  # Path starts at the source node
    return dfs(source_node_id, start_path, 0, visited)