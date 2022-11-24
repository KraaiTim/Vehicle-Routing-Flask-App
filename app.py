import os

from dotenv import load_dotenv
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)

from data_processing_functions import df_routes, read_addresses, read_depots
from flask_session import Session
from jinja_functions import seconds_to_time
from map import empty_map, locations_map, numbermap
from random_locations import random_coords

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["seconds_to_time"] = seconds_to_time

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# TODO GOAL of the application minimize the length of the longest single route among all vehicles

ORS_api_key = ""


def configure() -> str:
    load_dotenv()
    return os.getenv('OPENROUTESERVICE_API_KEY')


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        print(request.form)
        # TODO remove num vehicles and set max 15
        num_vehicles = 1

        # TODO think of the flow of the application and error messages
        inputs = session["inputs"]
        # Locations
        if "locations" in inputs:
            map = locations_map(inputs["location_coords"])
        if "depot" in request.form:
            depots = read_depots(request.form)
            # TODO change for multiple depots
            depot = depots[0][0]
            inputs["depot"] = depot
            inputs["depot_coords"] = [depot["longitude"], depot["latitude"]]
            session["inputs"] = inputs
            # plot map
            map = locations_map(
                inputs["location_coords"], inputs["depot_coords"])

        # If calculate route button is pressed.
        if "calculate_route" in request.form:
            # TODO think about price/km zero but with a cost for dropped locations
            # Km price from form
            if request.form.get("kmprice"):
                km_price = float(request.form.get("kmprice"))
            else:
                km_price = None
            # Penalty from form
            if request.form.get("missedlocation"):
                penalty = float(request.form.get("missedlocation"))
            else:
                penalty = None
            # MOT from form
            if request.form.get("MOT") == "car":
                mot = "driving-car"
                inputs["mot"] = mot
            else:
                # Bike
                mot = "cycling-regular"
                inputs["mot"] = mot
            # Objective from form
            if request.form.get("objective") == "distance":
                objective = "distances"
                inputs["objective"] = objective
            else:
                objective = "durations"
                inputs["objective"] = objective

            # Determine the route and create the map with route
            map, routes = numbermap(points=inputs["location_coords"],
                                    depot=inputs["depot_coords"], api_key=ORS_api_key, objective=objective,
                                    num_vehicles=num_vehicles, mot=mot, price_km=km_price, penalty=penalty)
            # DF with columns: Vehicle, Location id, Street, Number, Postcode, City, Distance
            routes_df = df_routes(inputs, routes, objective)
            inputs["routes"] = routes_df
            inputs["routes_total"] = routes
            session["inputs"] = inputs
    else:
        # If api keys are not set, redirect to keys
        if ORS_api_key is None:
            return redirect("/keys")
        else:
            if "inputs" in session:
                inputs = session["inputs"]
                if "location_coords" in inputs:
                    map = locations_map(inputs["location_coords"])
                else:
                    map = empty_map()
            else:
                inputs = {}
                map = empty_map()
    return render_template('index.html', map=map._repr_html_(), inputs=inputs)


@app.route('/locations', methods=["GET", "POST"])
def locations():
    if "inputs" in session:
        inputs = session["inputs"]
    else:
        inputs = {}
    if request.method == "POST":
        if request.form.get("locationsRadio") == "random":
            num_locations = int(request.form.get("randomRange"))
            coordinates = random_coords(num_locations)
            # Update inputs
            inputs["method"] = "random"
            inputs["locations"] = num_locations
            inputs["location_coords"] = coordinates
        elif request.form.get("locationsRadio") == "file":
            # TODO Async coordinates determination. Directly load addresses and later the coordinates
            file = request.files["formFile"]
            df = read_addresses(file)
            coordinates = [[df.loc[i, "latitude"], df.loc[i, "longitude"]]
                           for i in range(len(df))]
            # Update inputs
            inputs["method"] = "file"
            inputs["locations"] = len(df.index)
            inputs["location_coords"] = coordinates
            inputs["location_addresses"] = df
        # Store updated inputs in session
        session["inputs"] = inputs
    return render_template('locations.html', inputs=inputs)


@app.route('/depots', methods=["GET"])
def depots():
    inputs = session["inputs"]
    # ORS_api_key = session["openrouteservice_api_key"]
    return render_template('depots.html', ORS_api_key=ORS_api_key, inputs=inputs)


@app.route('/google', methods=["GET"])
def google():
    inputs = session["inputs"]
    return render_template('google.html', inputs=inputs)


@app.route('/keys', methods=["GET", "POST"])
# Route to set the API keys
def set_api_keys():
    if request.method == "POST":
        session["openrouteservice_api_key"] = request.form.get(
            "openrouteservice_api_key")
        return redirect('/')
    else:
        return render_template('keys.html')


@app.route('/clear')
def clear_session():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    ORS_api_key = configure()
    app.run(debug=True)
