import pandas as pd


def df_routes(inputs, routes):
    column_names = ["vehicle", "location_id",
                    "street", "number", "postcode", "city", "distance"]
    routes_df = pd.DataFrame(columns=column_names)
    # TODO check for multiple routes
    for index, location in enumerate(routes[0]["route"]):
        # If the location is the depot
        if location == 0:
            if index == 0:
                distance = 0
            else:
                distance = routes[0]["route_cost"][index-1] / 1000
            distance = routes[0]["route_cost"][index - 1]
            location_info = {"vehicle": routes[0]["id"],
                             "location_id": location,
                             "street": inputs["depot_address"],
                             "number": "X",
                             "postcode": "X",
                             "city": "X",
                             "distance": distance}
            location_info = pd.DataFrame([
                location_info], columns=routes_df.columns)
            routes_df = pd.concat(
                [routes_df, location_info])
        else:
            location_info = {"vehicle": routes[0]["id"],
                             "location_id": location - 1,
                             "street": inputs["location_addresses"].iloc[location - 1]["Street"],
                             "number": inputs["location_addresses"].iloc[location - 1]["Number"],
                             "postcode": inputs["location_addresses"].iloc[location - 1]["Postcode"],
                             "city": inputs["location_addresses"].iloc[location - 1]["City"],
                             "distance": routes[0]["route_cost"][index-1] / 1000}
            location_info = pd.DataFrame(
                [location_info], columns=routes_df.columns)
            routes_df = pd.concat(
                [routes_df, location_info])
    return routes_df
