import osmnx as ox
from shapely.geometry import Point

def download_graph(point: Point, distance: int, network_type: str, filename: str):
    g = ox.graph_from_point(
        center_point=(point.y, point.x),
        dist=distance,
        network_type=network_type,
    )
    ox.save_graph_geopackage(g, filename)


monastir= Point(35.7780, 10.8262)  # Longitude, Latitude


download_graph(
    point=monastir,
    distance=400000,  
    network_type="drive",  
    filename="tunis_network.gpkg",
)

print("Road network for Tunis has been downloaded and saved as 'tunis_network.gpkg'.")