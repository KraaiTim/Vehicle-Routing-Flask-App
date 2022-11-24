
import math

import pandas as pd
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim


def read_depots(form_result):
    # List of a list of depots

    address_keys = ['street', 'number',
                    'postcode', 'city', 'state', 'country', 'latitude', 'longitude']

    num_depots = len(form_result.getlist("depot_autcomplete"))

    depots = []
    for i in range(num_depots):
        # For each start and return depot combination:
        # 1. Get the values of the start depot from the form
        # 2. If the return checkbox is checked, get the values of the return depot
        # 3. Append the return depot to the list with the start depot
        depot_number = math.floor((i / 2)+1)
        if (i + 1) % 2 != 0:
            depot_type = "start"
            depot = {}
            for key in address_keys:
                field_key = depot_type + "_" + \
                    str(key) + "_" + str(depot_number)
                depot[key] = form_result.get(field_key)
            depots.append([depot])
        else:
            depot_type = "return"
            return_key = "return_checkbox" + "_" + str(depot_number)
            # If returncheckbox is checked, then append the return depot to the list with the start depot
            if form_result.get(return_key) != "":
                depot = {}
                for key in address_keys:
                    field_key = depot_type + "_" + \
                        str(key) + "_" + str(depot_number)
                    depot[key] = form_result.get(field_key)
                depots[math.floor((i-1)/2)].append(depot)
    return depots


def read_addresses(file) -> pd.DataFrame:
    file_extension = file.filename.split(".")[-1]
    if file_extension == "csv":
        df = pd.read_csv(file, header=0)
    elif file_extension == "xls" or file_extension == "xlsx":
        df = pd.read_excel(file, header=0)
    else:
        # TODO change to flash message
        print("Incorrect file type")

    # Change column names
    df['ADDRESS'] = df[['Street', 'Number', 'Postcode', 'City',
                        'State', 'Country']].stack().astype(str).groupby(level=0).agg(', '.join)

    geolocator = Nominatim(user_agent="application")

    # 1 second delay between geocoding calls
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    # Apply geocoding
    df['location'] = df['ADDRESS'].apply(geocode)
    # Extract Lat and Long from locations
    df['latitude'] = df['location'].apply(lambda x: x.latitude if x else None)
    df['longitude'] = df['location'].apply(
        lambda y: y.longitude if y else None)

    return df


def df_routes(inputs, routes, objective):
    column_names = ["vehicle", "location_id",
                    "street", "number", "postcode", "city", "distance", "cumulative"]
    routes_df = pd.DataFrame(columns=column_names)
    # TODO check for multiple routes
    for index, location in enumerate(routes[0]["route"]):
        # If the location is the depot
        if location == 0:
            if index == 0:
                distance = 0
                cumulative = 0
            else:
                if objective == "distances":
                    distance = routes[0]["route_cost"][index - 1] / 1000
                    cumulative = (
                        routes_df.iloc[index - 1]["cumulative"] + routes[0]["route_cost"][index - 1] / 1000)
                else:
                    # Objective durations
                    distance = routes[0]["route_cost"][index - 1]
                    cumulative = (
                        routes_df.iloc[index - 1]["cumulative"] + routes[0]["route_cost"][index - 1])
            location_info = {"vehicle": routes[0]["id"],
                             "location_id": location,
                             "street": inputs["depot"]["street"],
                             "number": inputs["depot"]["number"],
                             "postcode": inputs["depot"]["postcode"],
                             "city": inputs["depot"]["city"],
                             "country": inputs["depot"]["country"],
                             "distance": distance,
                             "cumulative": cumulative}
            location_info = pd.DataFrame([
                location_info], columns=routes_df.columns)
            routes_df = pd.concat(
                [routes_df, location_info])
        else:
            # TODO change for random locations
            if objective == "distances":
                distance = routes[0]["route_cost"][index - 1] / 1000
                cumulative = (
                    routes_df.iloc[index - 1]["cumulative"] + routes[0]["route_cost"][index - 1] / 1000)
            else:
                # Objective durations
                distance = routes[0]["route_cost"][index - 1]
                cumulative = (
                    routes_df.iloc[index - 1]["cumulative"] + routes[0]["route_cost"][index - 1])

            location_info = {"vehicle": routes[0]["id"],
                             "location_id": location,
                             "street": inputs["location_addresses"].iloc[location - 1]["Street"],
                             "number": inputs["location_addresses"].iloc[location - 1]["Number"],
                             "postcode": inputs["location_addresses"].iloc[location - 1]["Postcode"],
                             "city": inputs["location_addresses"].iloc[location - 1]["City"],
                             "country": inputs["location_addresses"].iloc[location - 1]["Country"],
                             "distance": distance,
                             "cumulative": cumulative}
            location_info = pd.DataFrame(
                [location_info], columns=routes_df.columns)
            routes_df = pd.concat(
                [routes_df, location_info])
    return routes_df
