import psycopg2
import binascii
from shapely.wkb import loads, dumps
import binascii
from shapely.geometry import Point
# Your WKB hex string (lat, long)
wkb_hex = "01010000009626A5A0DBD741408D9C853DED302440"

# Convert the hex WKB to raw bytes
# wkb_bytes = binascii.unhexlify(wkb_hex)
# point = loads(wkb_bytes)
# corrected_point = Point(point.y, point.x)
# corrected_wkb = dumps(corrected_point, hex=True, srid=4326)




# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="12345678"
)
cur = conn.cursor()

# Query to find the closest start_node to the given corrected WKB geometry
cur.execute("""
    SELECT id, ST_AsText(start_node), ST_DistanceSphere(
               start_node, 
               ST_GeomFromWKB(%s, 4326)
           ) AS distance
    FROM tunisia
    ORDER BY distance
    LIMIT 1;
""", (binascii.unhexlify(wkb_hex),))


# Fetch and print the closest node based on the corrected WKB geometry
closest_node = cur.fetchone()
print(closest_node)

# Close connection
cur.close()
conn.close()
