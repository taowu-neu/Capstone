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


def verify_graph():
    min_lon, min_lat, max_lon, max_lat = -123.3, 49.0, -123.0, 49.4
    node_alias = aliased(Node)
    node_subquery = (
        db.session.query(node_alias.id)
        .filter(
            func.ST_Within(
                node_alias.geom, 
                func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
            )
        ).subquery()
    )

    # Main query: Select source and target from edges
    edges_query = (
        db.session.query(Edge.source, Edge.target)
        .filter(Edge.source.in_(node_subquery))
    )
    # Execute the query and fetch all results
    results = edges_query.all()

    # Convert results to a list of dictionaries (optional)
    edges_list = [{'source': src, 'target': tgt} for src, tgt in results]
    print(edges_list[:10])
    G = nx.Graph()  # Use nx.DiGraph() if your edges are directed

    # Add edges to the graph
    for edge in edges_list:
        G.add_edge(edge['source'], edge['target'])

   # Get the largest connected component
    largest_cc = max(nx.connected_components(G), key=len)

    # Identify unconnected nodes (nodes not in the largest component)
    unconnected_nodes = set(G.nodes) - set(largest_cc)

    # Output the results
    print(f"Total nodes: {G.number_of_nodes()}")
    print(f"Connected nodes: {len(largest_cc)}")
    print(f"Unconnected nodes: {len(unconnected_nodes)}")
    return edges_list

    