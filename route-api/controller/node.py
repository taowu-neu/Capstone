from database.db import db
from model.models import Node
from sqlalchemy.orm import aliased
from sqlalchemy import func
from sqlalchemy import text

def find_closest_node(lon: float, lat: float):
    """Find the closest node to the given longitude and latitude."""
    query = text("""
        SELECT 
            id,
            longitude,
            latitude,
            ST_Distance(
                geom, 
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
            ) AS distance
        FROM nodes
        ORDER BY distance
        LIMIT 1;
    """)
    # Execute the query and return the closest node
    result = db.session.execute(query, {"lon": lon, "lat": lat}).fetchone()
    print('find the clost node', result)
    return Node(id=result.id, longitude=result.longitude, latitude=result.latitude)

def get_node_coordinates(node_ids):
    """Retrieve the coordinates for a list of node IDs."""
    query = text("""
        SELECT 
            id, longitude, latitude
        FROM nodes
        WHERE id = ANY(:node_ids);
    """)

    # Execute the query with the list of node IDs
    result = db.session.execute(query, {"node_ids": node_ids}).fetchall()

    # Map the result to a list of coordinate tuples [(lat, lon), ...]
    coordinates = [(row.latitude, row.longitude) for row in result]
    
    return coordinates