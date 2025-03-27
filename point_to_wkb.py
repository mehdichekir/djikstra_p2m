from shapely.geometry import Point

# Replace with your actual longitude and latitude
longitude = 10.09556  
latitude = 35.68639

# Create a Point geometry
point = Point(latitude, longitude)

# Get the WKB hex representation
wkb_hex = point.wkb_hex
print(wkb_hex)
