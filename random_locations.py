# Generate random points within the shapefile of the Netherlands and calculate route
import os
import random
import re

import shapefile
from shapely.geometry import Point, shape


def random_coords(N_random: int) -> list:
    # Import shapefile
    myshp = open(
        os.getcwd()+"/static/shapefiles/TM_WORLD_BORDERS-0.3.shp", "rb")
    mydbf = open(
        os.getcwd()+"/static/shapefiles/TM_WORLD_BORDERS-0.3.dbf", "rb")
    shapes = shapefile.Reader(shp=myshp, dbf=mydbf, encoding="latin1")

    # getting feature(s) that match the country name
    countries = [s for s in shapes.records() if s[2] in ['BEL', 'NLD']]
    countries_id = []
    for country in countries:
        # getting feature(s)'s id of that match
        country_id = int(re.findall(r'\d+', str(country))[0])
        countries_id.append(country_id)

    shapeRecs = shapes.shapeRecords()
    feature = shapeRecs[country_id].shape.__geo_interface__
    shp_geom = shape(feature)

    # function that takes a shapefile as inputs

    def random_point_in_country(shp_geom):
        minx, miny, maxx, maxy = shp_geom.bounds

        while True:
            p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
            if shp_geom.contains(p):
                return list(p.coords)

    points = []
    for i in range(N_random):
        # Reverse points from [Long, Lat] to [Lat, Long]
        points.append(list(reversed(random_point_in_country(shp_geom)[0])))

    return points
