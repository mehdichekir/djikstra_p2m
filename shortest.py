import psycopg2
from collections import defaultdict
from dijkstra import dijkstra
import os
from shapely.ops import nearest_points
from shapely.geometry import Point
import requests

def get_osrm_route(start, end):
    """Fetch the real road path between two points using OSRM."""
    base_url = "http://router.project-osrm.org/route/v1/driving/"
    url = f"{base_url}{start[0]},{start[1]};{end[0]},{end[1]}?geometries=geojson"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data['routes'][0]['geometry']['coordinates']
    else:
        print("OSRM request failed:", response.text)
        return []
    

db_password = os.getenv('DB_PASSWORD', 'default_password')
# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="12345678"
)

# Create a graph structure
graph = defaultdict(dict)
node_mapping = {}  # Maps POINT(x y) -> unique integer ID
reverse_mapping = {}  # Maps integer ID -> POINT(x y)

# Fetch edges
cur = conn.cursor()
cur.execute("""
    SELECT 
        ST_AsText(start_node) AS start_node,
        ST_AsText(end_node) AS end_node,
        edge_length
    FROM tunisia;
""")
edges = cur.fetchall()

# Generate unique integer IDs for nodes
next_id = 0

for start, end, length in edges:
    # Assign unique IDs to start and end nodes if not already mapped
    if start not in node_mapping:
        node_mapping[start] = next_id
        reverse_mapping[next_id] = start
        next_id += 1

    if end not in node_mapping:
        node_mapping[end] = next_id
        reverse_mapping[next_id] = end
        next_id += 1

    # Add edges to the graph using integer IDs
    start_id = node_mapping[start]
    end_id = node_mapping[end]
    graph[start_id][end_id] = length
    graph[end_id][start_id] = length  # Assuming bidirectional roads

# Example source and destination nodes
src_point = "POINT(35.7919282 9.9868349)"
dst_point = "POINT(34.5318488 9.3484355)"

# Get their integer IDs
src_id = node_mapping[src_point]
dst_id = node_mapping[dst_point]

# Run Dijkstra
result = dijkstra(graph, src_id, dst_id)

# Convert path to list of [latitude, longitude]
def point_to_latlng(point):
    point = point.replace("POINT(", "").replace(")", "")
    lon, lat = map(float, point.split())
    return [lat, lon]

path_geom = [point_to_latlng(reverse_mapping[node_id]) for node_id in result["path"]]

print(f'path_geom={path_geom}')


# real_path = []
# node_sequence = result["path"]
# for i in range(len(node_sequence) - 1):
#     start_node = reverse_mapping[node_sequence[i]].replace("POINT(", "").replace(")", "").split()
#     end_node = reverse_mapping[node_sequence[i+1]].replace("POINT(", "").replace(")", "").split()
    
#     start_coords = (float(start_node[0]), float(start_node[1]))
#     end_coords = (float(end_node[0]), float(end_node[1]))
    
#     segment = get_osrm_route(start_coords, end_coords)
    
#     # Ensure the format of each segment is "POINT(lon lat)"
#     real_path.extend([f"POINT({lon} {lat})" for lon, lat in segment])

# # Debug: Check what real_path contains
# print("Real Path Before Joining:", real_path)

cur.execute("""
    DROP TABLE IF EXISTS shortest_path;
    CREATE TABLE shortest_path (
        id SERIAL PRIMARY KEY,
        geom geometry(LineString, 4326)
    );
""")
linestring = "LINESTRING(" + ", ".join(node.replace("POINT(", "").replace(")", "") for node in path_geom) + ")"
cur.execute(""" 
    INSERT INTO shortest_path (geom) 
    VALUES (ST_GeomFromText(%s, 4326)); 
""", (linestring,))


conn.commit()
cur.close()
conn.close()