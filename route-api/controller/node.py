from database.db import db
from model.models import Node
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
    result = db.session.execute(query, {"lon": lon, "lat": lat}).fetchone()
    return Node(id=result.id, longitude=result.longitude, latitude=result.latitude)

def get_node_coordinates(node_ids):
    """Retrieve the coordinates for a list of node IDs."""
    query = text("""
        SELECT 
            id, longitude, latitude
        FROM nodes
        WHERE id = ANY(:node_ids);
    """)
    result = db.session.execute(query, {"node_ids": node_ids}).fetchall()

    coordinates_dict = {row.id: (row.latitude, row.longitude) for row in result}
    coordinates = [coordinates_dict[node_id] for node_id in node_ids if node_id in coordinates_dict]
    return coordinates

def get_node_details(node_ids):
    """Retrieve the elevation, is_poi status, and POI description for a list of node IDs."""
    query = text("""
        SELECT 
            id, elevation, is_poi, poi_desc
        FROM nodes
        WHERE id = ANY(:node_ids);
    """)

    result = db.session.execute(query, {"node_ids": node_ids}).fetchall()
    details_dict = {row.id: {'elevation': float(row.elevation), 'is_poi': row.is_poi, 'poi_desc': row.poi_desc} for row in result}
    return details_dict
