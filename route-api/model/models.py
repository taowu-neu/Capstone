from database.db import db
from geoalchemy2 import Geometry

class Node(db.Model):
    __tablename__ = 'nodes'
    id = db.Column(db.BigInteger, primary_key=True)
    geom = db.Column(Geometry(geometry_type='POINT', srid=4326))  # PostGIS Geometry column

class Edge(db.Model):
    __tablename__ = 'edges'

    id = db.Column(db.String, primary_key=True)  # Use appropriate data types
    osm_id = db.Column(db.BigInteger)
    source = db.Column(db.BigInteger)
    target = db.Column(db.BigInteger)
    length = db.Column(db.Float)
    foot = db.Column(db.String)
    car_forward = db.Column(db.String)
    car_backward = db.Column(db.String)
    bike_forward = db.Column(db.String)
    bike_backward = db.Column(db.String)
    train = db.Column(db.String)
    wkt = db.Column(db.String)

    def to_dict(self):
        """Convert the model to a dictionary for JSON response."""
        return {
            'id': self.id,
            'osm_id': self.osm_id,
            'source': self.source,
            'target': self.target,
            'length': self.length,
            'foot': self.foot,
            'car_forward': self.car_forward,
            'car_backward': self.car_backward,
            'bike_forward': self.bike_forward,
            'bike_backward': self.bike_backward,
            'train': self.train,
            'wkt': self.wkt
        }