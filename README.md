# Vehicle Routing Flask App

## Introduction

This project uses the Google ortools and OpenRouteServices API to determine the optimal route through random locations within the borders of The Netherlands.

## Locations (random_locations.py)

The app requires the number of random locations and the number of vehicles to be submitted in a form.
After the form is submitted, random locations within The Netherlands are determined by randomly generating latitude and logitude between the max and the min lat and long of The Netherlands. After that, each lat and long pair is evaluated on if it is within The Netherlands by cheking if it is within the bounds of a shapefile of the Netherlands. For this the Shapely package is used.

## Distance Matrix (distance_matrix.py)

With the list of locations, a distance matrix is created. The distances between the locations are obtained from the OperRouteService Matrix API. This API provides the distances between points over the road network with a car.

## Vehicle Routing (TSP_model.py)

The optimal route for the vehicles is determined with the Vehicle Routing calculator of Google ortools. The input for this calculator is the distance matrix, the number of vehicles and a depot (which is currently the first location). The result from the calculator is a total distance of all vehicles and the route and distance per vehicle.

## Route (map.py)

With the optimal route, the directions for check vehicle have be be determined. For this the OpenRouteServices Directions API is used.
The result from the API is a huge list with all the longitude and latitude pairs of the route.

## Map (map.py)

After all the calculations, a map with created with with Folium package. The locations and routes of the vehicles are added as layers to the map.
