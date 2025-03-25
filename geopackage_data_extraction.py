import geopandas as gpd
import psycopg2
from shapely.geometry import Point

# 🔹 Load GPKG file
gpkg_file = "tunis_network.gpkg"  # Replace with your actual file

nodes = gpd.read_file(gpkg_file, layer="nodes")
edges = gpd.read_file(gpkg_file, layer="edges")

print("Edges columns:", edges.columns)
print("Nodes columns:", nodes.columns)

# 🔹 Ensure 'id' column in nodes and 'from', 'to' in edges exist
assert 'osmid' in nodes.columns, "Nodes layer must have an 'id' column."
assert 'from' in edges.columns and 'to' in edges.columns, "Edges layer must have 'from' and 'to' columns."

# 🔹 Create a dictionary mapping node IDs to geometries
node_geometries = nodes.set_index('osmid')['geometry'].to_dict()

# 🔹 Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="12345678"
)
cur = conn.cursor()

# 🔹 Enable PostGIS
cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
conn.commit()

# 🔹 Drop existing table (if needed)
cur.execute("DROP TABLE IF EXISTS tunisia")
conn.commit()

# 🔹 Create `tunisia` table with geometry columns
cur.execute("""
    CREATE TABLE tunisia (
        id SERIAL PRIMARY KEY,
        start_node GEOMETRY(Point, 4326),
        end_node GEOMETRY(Point, 4326),
        edge_length REAL
    )
""")
conn.commit()

# 🔹 Insert Edges with Geometry
for _, row in edges.iterrows():
    start_node_geom = node_geometries.get(row['from'])  # Get geometry from dict
    end_node_geom = node_geometries.get(row['to'])  # Get geometry from dict

    if start_node_geom and end_node_geom:
        cur.execute("""
            INSERT INTO tunisia (start_node, end_node, edge_length) 
            VALUES (ST_GeomFromText(%s, 4326), ST_GeomFromText(%s, 4326), %s)
        """, (start_node_geom.wkt, end_node_geom.wkt, float(row['length'])))

conn.commit()
cur.close()
conn.close()

print("Data inserted successfully into `tunisia` table with geometry!")
