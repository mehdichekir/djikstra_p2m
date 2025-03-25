import psycopg2
from collections import defaultdict
from dijkstra import dijkstra
import os
from shapely.ops import nearest_points
from shapely.geometry import Point


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

#print("Available node keys:", list(node_mapping.keys()))

# Print the processed graph
#print("Graph (integer IDs):", dict(graph))
#print("Node Mapping:", node_mapping)

# cur.execute("""
#  SELECT ST_AsText(start_node) FROM tunisia ORDER BY RANDOM() LIMIT 1;

#             """)
# src_point=cur.fetchone()[0]
# cur.execute("""
#  SELECT ST_AsText(end_node) FROM tunisia ORDER BY RANDOM() LIMIT 1;

#             """)

#dst_point=cur.fetchone()[0]


# Example source and destination nodes
src_point = "POINT(32.1759143 9.7390648)"
dst_point = "POINT(32.5390522 10.4582293)"

# Get their integer IDs
src_id = node_mapping[src_point]
dst_id = node_mapping[dst_point]

# Run Dijkstra
result = dijkstra(graph, src_id, dst_id)

# Translate result back to POINT(x y) format
path = [reverse_mapping[node_id] for node_id in result["path"]]
print("Shortest Path:", path)
print("Total Cost:", result["cost"])

path_geom = [reverse_mapping[node_id] for node_id in result["path"]]


cur.execute("""
    DROP TABLE IF EXISTS shortest_path;
    CREATE TABLE shortest_path (
        id SERIAL PRIMARY KEY,
        geom geometry(LineString, 4326)
    );
""")

linestring = "LINESTRING(" + ", ".join(node.replace("POINT(", "").replace(")", "") for node in path_geom) + ")"

# Insert the LINESTRING into the table
cur.execute("""
    INSERT INTO shortest_path (geom)
    VALUES (ST_GeomFromText(%s, 4326));
""", (linestring,))

conn.commit()
cur.close()
conn.close()