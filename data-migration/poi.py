import csv
import psycopg2
import logging
# Database connection settings
conn_settings = {
    "dbname": "route-db",
    "user": "user",
    "password": "example",
    "host": "localhost",
    "port": "5432"
}
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])  # Logs to console

logger = logging.getLogger()
nodes_dict = {}
def find_nearby_nodes():
    """Finds and prints nodes within 50 meters of each POI in the osm_poi_points table."""
    # Connect to the PostgreSQL database
    connection = psycopg2.connect(**conn_settings)
    cursor = connection.cursor()

    # Query to get all points in osm_poi_points
    poi_query = "SELECT id, geom FROM osm_poi_points;"

    # Prepare a query to find nearby nodes within 50 meters
    nearby_nodes_query = """
      SELECT n.id, ST_AsText(n.geom), ST_Distance(n.geom::geography, %s::geography) as distance
      FROM nodes AS n
      WHERE ST_DWithin(n.geom::geography, %s::geography, 100);
      """

    try:
        # Fetch all points of interest
        cursor.execute(poi_query)
        pois = cursor.fetchall()
        # Iterate over each poi and find nodes within 50 meters
        for index, poi in enumerate(pois):
            poi_id = poi[0]
            poi_geom = poi[1]
            # Execute the nearby nodes query with the current poi's geometry
            cursor.execute(nearby_nodes_query, (poi_geom, poi_geom))
            nearby_nodes = cursor.fetchall()
            if len(nearby_nodes) == 0:
                logger.info(f"{index} poi not found.")
                continue
            # Print or process each nearby node
            node_id, node_geom, distance = nearby_nodes[0]
            nodes_dict.setdefault(node_id, []).append(poi_id)
            logger.info(f" - Node ID: {node_id}, Distance: {distance:.2f} meters, Geometry: {node_geom}")

    finally:
        # Close the database connection
        cursor.close()
        connection.close()

def save_dict_to_csv(filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['node_id', 'pois_id'])
        
        # Write each node and its corresponding values
        for key, values in nodes_dict.items():
            # Join the list of values into a single string
            values_as_strings = [str(value) for value in values]
            writer.writerow([key, ' '.join(values_as_strings)])
          
def main():
    """Main function to initiate the nearby node search."""
    find_nearby_nodes()
    save_dict_to_csv('nodes_with_poi.csv')

if __name__ == "__main__":
    main()
