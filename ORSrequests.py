# Function for Directions and Matrix OpenRouteServices API calls
import json

import requests

# TODO add counter to check for max 40 calls per minute


def directions(api_key: str, coordinates: list, mot: str):
    """
    Posts a request to the Directions endpoint of the OpenRouteService API. 
    Returns a list of coordinates of the recommended route for a car betweeen the locations.

    Args:
        api_key (str): API key obtained from OpenRouteServices.org
        locations (list): List of [lon, lat] per location
    """
    body = {"coordinates": coordinates, "instructions": "false",
            "preference": "recommended", "radiuses": [-1]}

    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': api_key,
        'Content-Type': 'application/json; charset=utf-8'
    }
    call = requests.post(
        f'https://api.openrouteservice.org/v2/directions/{mot}/geojson', json=body, headers=headers)

    # If there is a point for which no routable point can be found within 350 meters, error 2010, return empty list
    # TODO handle errors
    if "error" in json.loads(call.text):
        if json.loads(call.text)['error']['code'] == 200:
            return []
    else:
        return json.loads(call.text)['features'][0]['geometry']['coordinates']


def matrix(api_key: str, locations: list, sources: list, destinations: list, mot: str):
    """
    Posts a request to the Matrix endpoint of the OpenRouteService API. 
    Returns a dict with a distance matrix (in meters) and a duration matrix (in seconds) a car route between the sources and destinations.

    Args:
        api_key (str): API key obtained from OpenRouteServices.org
        locations (list): List of [lon, lat] per location
        sources (list): List of indexes of the locations that are sources in the locations list
        destinations (list): List of indexes of the locations that are destinations in the locations list
    """
    body = {"locations": locations, "destinations": destinations, "metrics": [
        "distance", "duration"], "sources": sources, "units": "m"}

    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': api_key,
        'Content-Type': 'application/json; charset=utf-8'
    }
    call = requests.post(
        f'https://api.openrouteservice.org/v2/matrix/{mot}', json=body, headers=headers)
    return json.loads(call.text)
