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

psql -h db -U user -d $database -c "\COPY osm_poi_points(id, name, tourism, historic, leisure, way) FROM '/app/csv_data/osm_point.csv' WITH (FORMAT csv, DELIMITER ',', HEADER, NULL '');"

psql -h db -U user -d $database -c "UPDATE osm_poi_points SET geom = ST_Transform(way, 4326);"

psql -h db -U user -d $database -c "\COPY temp_node_elevation(node_id, elevation) FROM '/app/csv_data/nodes_with_elevation.csv' WITH (FORMAT csv, DELIMITER ',', HEADER, NULL '');"

psql -h db -U user -d $database -c "UPDATE nodes SET elevation = tmp.elevation FROM temp_node_elevation tmp WHERE nodes.id = tmp.node_id;"

psql -h db -U user -d $database -c "\COPY temp_node_pois(node_id, poi_ids_text) FROM '/app/csv_data/nodes_with_poi.csv' DELIMITER ',' CSV HEADER;"

psql -h db -U user -d $database -c "UPDATE temp_node_pois SET poi_ids = string_to_array(poi_ids_text, ' ')::BIGINT[];"

psql -h db -U user -d $database -c "
        with tmp as (
        SELECT temp.node_id, ARRAY_TO_STRING(ARRAY_AGG(poi.name),', ') AS names
        FROM temp_node_pois temp
        JOIN osm_poi_points poi ON poi.id = ANY(temp.poi_ids)
        GROUP BY temp.node_id
        )
      update nodes set poi_desc = tmp.names, is_poi = true FROM tmp where tmp.node_id = nodes.id;
      "
