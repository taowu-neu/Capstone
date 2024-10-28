from database.db import db
from sqlalchemy import text
def query_edges():
    query = text("""
      SELECT 
        e.source AS s, 
        ST_X(n1.geom) AS source_longitude,
        ST_Y(n1.geom) AS source_latitude,  
        e.target AS t, 
        ST_X(n2.geom) AS target_longitude,
        ST_Y(n2.geom) AS target_latitude
    FROM 
        edges e
    JOIN 
        nodes n1 ON e.source = n1.id  -- Join for source node coordinates
    JOIN 
        nodes n2 ON e.target = n2.id  -- Join for target node coordinates
    WHERE 
        ST_Within(
            n1.geom,
            ST_MakeEnvelope(-123.3, 49.0, -123.0, 49.4, 4326)
        );

        """)
    result = db.session.execute(query).fetchall()
    edges_list = [{'source': [slon, slat], 'target': [tarlon, tarlat]} for src, slon, slat, tar, tarlon, tarlat in result]
    return edges_list