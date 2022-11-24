from folium import (FeatureGroup, Icon, LayerControl, Map, Marker,
                    PolyLine, Popup, TileLayer)
import folium.plugins as plugins

import matplotlib
# Import route function
from distance_matrix import route
# Import TSP model
from TSP_model import TSPmodel

# TODO max number of directions API calls is 40 per minute. Check how to make the route


def empty_map():
    midpoint = [51.688193, 5.547352]
    m = Map(location=midpoint, tiles=None, zoom_start=7,
            control_scale=True, zoom_control=False)
    TileLayer(tiles='OpenStreetMap', control=True).add_to(m)
    LayerControl(collapsed=False).add_to(m)
    return m


def locations_map(points, depot=None):
    # Initialize empty map
    midpoint = [51.688193, 5.547352]
    m = Map(location=midpoint, tiles=None, zoom_start=7,
            control_scale=True, zoom_control=False)
    TileLayer(tiles='OpenStreetMap', control=True).add_to(m)
    # If depot exists, add marker and FeatureGroup
    if depot:
        fg_depots = FeatureGroup(name="Depot")
        Marker(location=depot, popup=Popup("{}".format(
            ["{:.5}".format(float(coord)) for coord in depot])), icon=Icon(
            color="green", icon='home', prefix='fa')).add_to(fg_depots)
        fg_depots.add_to(m)

    fg_locations = FeatureGroup(name="Locations")

    # Place markers on the Folium map
    # TODO change popup to address if available
    for p in points:
        Marker(location=p, popup=Popup("{}".format(
            ["{:.5}".format(float(coord)) for coord in p])), color="blue").add_to(fg_locations)
    fg_locations.add_to(m)

    LayerControl(collapsed=False).add_to(m)
    return m

# Function to draw the map, TSP, get route coordinates and draw the route.


def numbermap(points, depot, api_key, objective, num_vehicles, mot, price_km=None, penalty=None):
    # TODO substitute below with above functions without LayerControl being in the above functions

    # Create map with locations and depot
    midpoint = [51.688193, 5.547352]
    m = Map(location=midpoint, tiles=None, zoom_start=7,
            control_scale=True, zoom_control=False)
    TileLayer(tiles='OpenStreetMap', control=True).add_to(m)
    # If depot exists, add marker and FeatureGroup
    if depot:
        fg_depots = FeatureGroup(name="Depot")
        Marker(location=depot, popup=Popup("{}".format(
            ["{:.5}".format(float(coord)) for coord in depot])), icon=Icon(
            color="green", icon='home', prefix='fa')).add_to(fg_depots)
        fg_depots.add_to(m)

    # Call TSP model
    tsp_locations = [list(reversed(depot))] + \
        [list(reversed(p)) for p in points]
    dropped_nodes, routes = TSPmodel(locations=tsp_locations, api_key=api_key,
                                     objective=objective, num_vehicles=num_vehicles, mot=mot, price_km=price_km, penalty=penalty)

    colors = [
        'green',
        'blue',
        'orange',
        'darkgreen',
        'purple',
        'pink',
        'red',
        'gray',
        'darkred',
        'lightred',
        'lightgreen',
        'darkblue',
        'lightblue',
        'darkpurple',
        'black'
    ]

    coordinates = [depot] + points

    # For each route
    for route_id, route_locs in enumerate(routes):

        fg_route = FeatureGroup(name="Route " + str(route_id + 1))

        # Create list of the coordinates of the locations on the route
        route_coords = []
        for i in route_locs["route"]:
            route_coords.append(coordinates[i])

        # Call ORS directions api for route details
        coords_route = route([list(reversed(p))
                             for p in route_coords], api_key, mot)
        coords_route = [list(reversed(p)) for p in coords_route]

        for i in range(len(route_coords)-1):
            PolyLine(locations=[coords_route],
                     color=colors[route_id]).add_to(fg_route)

        # If there is a route
        if len(route_locs["route"]) > 2:
            # Add locations of the route to the map with numbers
            for idx, p in enumerate(route_locs["route"]):
                # If not depot, add marker to the route
                if p != 0:
                    Marker(location=points[p-1],
                           popup=Popup("{}".format(
                               ["{:.5}".format(float(coord)) for coord in points[p-1]])),
                           icon=plugins.BeautifyIcon(
                        icon="arrow-down", icon_shape="marker",
                        number=idx,
                        border_width=1,
                        background_color=matplotlib.colors.cnames[colors[route_id]]
                    )).add_to(fg_route)
            fg_route.add_to(m)

    if len(dropped_nodes) > 1:
        dropped_locations = FeatureGroup(name="Missed locations")
        print(dropped_nodes)
        # Place markers on the Folium map
        for p in dropped_nodes:
            Marker(location=points[p-1], popup=Popup("{}".format(
                ["{:.5}".format(float(coord)) for coord in points[p-1]])), color="blue").add_to(dropped_locations)
        dropped_locations.add_to(m)

    LayerControl(collapsed=False).add_to(m)

    return m, routes
