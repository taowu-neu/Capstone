#!/bin/bash

# Wait for PostgreSQL to start up
sleep 10


database=route-db
# Import locations CSV into the locations table
psql -h db -U user -d $database -c "\COPY nodes(id, longitude, latitude) FROM '/app/csv_data/nodes.csv' WITH (FORMAT csv, DELIMITER ',', HEADER, NULL '');"
# Update the geom column in the locations table with geographic data
psql -h db -U user -d $database -c "UPDATE nodes SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);"

# Import edges CSV into the edges table (except the geom column)
psql -h db -U user -d $database -c "\COPY edges(id, osm_id, source, target, length, foot, car_forward, car_backward, bike_forward, bike_backward, train, wkt)
FROM '/app/csv_data/edges.csv'
WITH (FORMAT csv, DELIMITER ',', HEADER);"
