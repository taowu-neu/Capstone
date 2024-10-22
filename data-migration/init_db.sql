DROP EXTENSION postgis_tiger_geocoder;
DROP TABLE IF EXISTS edges;
DROP TABLE IF EXISTS nodes;
DROP TABLE IF EXISTS osm_poi_points;

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE TABLE nodes (
    id BIGINT PRIMARY KEY,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    geom GEOMETRY(Point, 4326),
    elevation NUMERIC,
    is_poi BOOLEAN,
    poi_desc VARCHAR
);

CREATE TABLE edges (
    id VARCHAR,
    osm_id BIGINT,
    source BIGINT REFERENCES nodes(id),
    target BIGINT REFERENCES nodes(id),
    length REAL,
    foot VARCHAR,
    car_forward VARCHAR,
    car_backward VARCHAR,
    bike_forward VARCHAR,
    bike_backward VARCHAR,
    train VARCHAR,
    wkt TEXT
);

-- osm_data
CREATE TABLE osm_poi_points (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    leisure VARCHAR(255),
    historic VARCHAR(255),
    tourism VARCHAR(255),
    way TEXT,
    geom GEOMETRY(Point, 4326)
);

-- relation table
CREATE TABLE temp_node_pois (
    node_id BIGINT PRIMARY KEY,
    poi_ids_text TEXT,
    poi_ids BIGINT[]
);

-- elevation table
CREATE TABLE temp_node_elevation (
    node_id BIGINT PRIMARY KEY,
    elevation FLOAT
);


CREATE INDEX idx_nodes_geom ON nodes USING GIST (geom);
CREATE INDEX idx_osm_poi_points_geom ON osm_poi_points USING GIST (geom);
