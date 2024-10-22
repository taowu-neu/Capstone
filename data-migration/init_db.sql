CREATE EXTENSION IF NOT EXISTS postgis;

DROP EXTENSION postgis_tiger_geocoder;
DROP TABLE IF EXISTS edges;
DROP TABLE IF EXISTS nodes;

CREATE TABLE nodes (
    id BIGINT PRIMARY KEY,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    geom GEOMETRY(Point, 4326)
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