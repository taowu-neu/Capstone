import csv
import logging
import os
from pyhigh import get_elevation_batch

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])  # Logs to console

logger = logging.getLogger()
elevation_data = {}
currdir = os.getcwd()

def get_elevation():
    # Dictionary to store node_id as key and elevation as value

    # Read coordinates from the CSV file
    coordinates = []
    FILEPATH = os.path.join(currdir, 'csv_data/nodes.csv')

    with open(FILEPATH, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Extract node_id, latitude, and longitude from the row
            node_id = row['id']
            lat = float(row['lat'])
            lon = float(row['lon'])
            # Append a tuple with node_id and coordinates
            coordinates.append((node_id, (lat, lon)))

    # Process in batches of 100
    batch_size = 100
    for i in range(0, len(coordinates), batch_size):
        batch = coordinates[i:i + batch_size]
        # Prepare the batch of only coordinates for the API call
        coord_batch = [coord for _, coord in batch]
        
        try:
            # Get elevation data for the batch
            elevations = get_elevation_batch(coord_batch) 
            # Store results in the dictionary
            for (node_id, coord), elevation in zip(batch, elevations):
                elevation_data[node_id] = elevation
                logger.info(f"Node ID: {node_id}, Coordinates: {coord}, Elevation: {elevation} meters")
        
        except Exception as e:
            logger.error(f"Error retrieving elevation for batch starting at index {i}: {e}")
  
def save_dict_to_csv(filename):
    output_file_path = os.path.join(currdir, filename)
    with open(output_file_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['node_id', 'elevation'])  # Write the header
        for node_id, elevation in elevation_data.items():
            writer.writerow([node_id, elevation])  # Write each node_id and elevation

if __name__ == "__main__":
    get_elevation()
    save_dict_to_csv('csv_data/nodes_with_elevation.csv')
