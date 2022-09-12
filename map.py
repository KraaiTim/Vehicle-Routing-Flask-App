from folium import FeatureGroup, LayerControl, Map, Marker, Polygon, Popup, Icon, PolyLine, TileLayer
from folium import plugins
import random

# Import TSP model
from TSP_model import TSPmodel
# Import route function
from distance_matrix import route

# TODO max number of directions API calls is 40 per minute. Check how to make the route

# Function to draw the map, TSP, get route coordinates and draw the route.


def plotmap(depot, points, api_key, num_vehicles=1, polybounds=[]):

    # Set midpoint as depot
    points = [list(reversed(depot))] + points

    # Create map
    # for titles also optional use "OpenStreetMap", "cartodbpositron"
    midpoint = [51.688193, 5.547352]
    m = Map(location=midpoint, tiles=None, zoom_start=7, control_scale=True)

    tile_layer = TileLayer(tiles='OpenStreetMap', control=False).add_to(m)

    # If polybounds given, draw polygons
    if polybounds:
        #        for idx, coords in enumerate(polybounds):
        #            Marker(location=list(coords),popup=Popup("ID: {}".format(idx))).add_to(m)

        Polygon(polybounds, color="blue", weight=2,
                fill_color="blue", fill_opacity=0.3).add_to(m)

    fg_markers = FeatureGroup(name="Locations")

    # Place markers on the Folium map with different icon for first point = depot
    for idx, p in enumerate(points):
        if idx == 0:
            Marker(location=list(reversed(p)), popup=Popup("ID: {}".format(idx)), icon=Icon(
                color="green", icon='home', prefix='fa')).add_to(fg_markers)
        else:
            Marker(location=list(reversed(p)), popup=Popup(
                "ID: {}".format(idx)), color="blue").add_to(fg_markers)

    fg_markers.add_to(m)

    # Call TSP model
    routes = TSPmodel(locations=points, api_key=api_key,
                      num_vehicles=num_vehicles)

    colors = [
        'red',
        'blue',
        'orange',
        'darkgreen',
        'purple',
        'pink',
        'green',
        'gray',
        'darkred',
        'lightred',
        'lightgreen',
        'darkblue',
        'lightblue',
        'darkpurple',
        'black'
    ]

    # For each route
    for route_id, route_locs in enumerate(routes):

        fg_route = FeatureGroup(name="Route " + str(route_id + 1))

        # Create list of the coordinates of the locations on the route
        route_coords = []
        for i in route_locs["route"]:
            route_coords.append(points[i])

        coords_route = route(route_coords, api_key)

        for i in range(len(route_coords)-1):
            PolyLine(locations=[list(reversed(
                coord)) for coord in coords_route], color=colors[route_id]).add_to(fg_route)

        fg_route.add_to(m)

    LayerControl(collapsed=False).add_to(m)

    return m, routes
