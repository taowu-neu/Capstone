import networkx as nx
from model.models import Edge

def build_graph():
    # Create a directed graph
    graph = nx.MultiGraph()
    
    # Query all edges from the database
    edges =  Edge.query.add_columns(Edge.source, Edge.target, Edge.length).all()
    
    # Add edges to the graph
    for edge in edges:
        graph.add_edge(edge.source, edge.target, length=edge.length)
    
    return graph


def draw_graph(self):
    """Draws and saves the graph as an image."""
    pos = nx.spring_layout(self.graph)  # Positions for the nodes

    # Draw nodes and edges
    nx.draw(self.graph, pos, with_labels=True, node_size=500, node_color='lightblue', font_size=10, font_color='black', arrows=True)
    edge_labels = nx.get_edge_attributes(self.graph, 'length')
    nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)

    # Save the graph to a file
    plt.title("Graph Visualization")
    plt.savefig("graph_visualization.png")  # Save as PNG file
    plt.show()  # Display the graph
