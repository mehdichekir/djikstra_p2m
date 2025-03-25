import fiona

gpkg_file = "tunis_network.gpkg"  # Replace with your file path

# List all available layers in the GPKG file
layers = fiona.listlayers(gpkg_file)
print("Available layers:", layers)