from shapely.wkb import loads


wkb_from_db = '0101000020E61000000AB31A5C84164040E33F93B3667A2340'
# Retrieve from database
retrieved_wkb = wkb_from_db  # Example from your database query
retrieved_point = loads(retrieved_wkb)  # Convert WKB to Shapely Point

# Print debug information
print("Retrieved Point:", retrieved_point)
# print("All Keys in node_mapping:", list(node_mapping.keys())[:5])

# # Check if the retrieved point is in node_mapping
# if retrieved_point not in node_mapping:
#     print("Point not found! Trying with rounding...")
