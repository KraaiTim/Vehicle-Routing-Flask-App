import os

from dotenv import load_dotenv
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)

from flask_session import Session
from routes import df_routes
from geocoding import read_addresses
from map import empty_map, locations_map, plotmap
from random_locations import random_coords

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# GOAL of the application minimize the length of the longest single route among all vehicles

ORS_api_key = ""


def configure() -> str:
    load_dotenv()
    return os.getenv('OPENROUTESERVICE_API_KEY')


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # TODO remove num vehicles and set max 15
        num_vehicles = 1

        inputs = session["inputs"]
        if "depot" in request.form:
            print(request.form)
            inputs = session["inputs"]
            if not "returnCheck" in request.form:
                # Depot start location <> return location
                pass
            # Map expects coords in [Longtitude, Latitude]
            # TODO change for multiple depots
            inputs["depot"] = [float(
                request.form.get("start_long_1")), float(request.form.get("start_lat_1"))]
            inputs["depot_address"] = request.form.get("depot")
            session["inputs"] = inputs
            # plot map
            map = locations_map(inputs["location_coords"], inputs["depot"])
            return render_template('index.html', map=map._repr_html_(),  inputs=inputs)
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
            coordinates = [[df.loc[i, "Lat"], df.loc[i, "Lon"]]
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


@app.route('/calculateroute', methods=["POST"])
def calculateroute():
    inputs = session["inputs"]
    if request.method == "POST":
        if request.form.get("kmprice"):
            km_price = float(request.form.get("kmprice")) * 100
            km_price = int(km_price)
        else:
            km_price = None
        if request.form.get("missedlocation"):
            penalty = float(request.form.get("missedlocation")) * 100
            penalty = int(penalty)
        else:
            penalty = None

        if request.form.get("MOT") == "car":
            mot = "driving-car"
            map, routes = plotmap(points=inputs["location_coords"],
                                  depot=inputs["depot"], api_key=ORS_api_key, num_vehicles=1, mot=mot, price_km=km_price, penalty=penalty)
            # DF with columns: Vehicle, Location id, Street, Number, Postcode, City, Distance
            routes_df = df_routes(inputs, routes)
            inputs["routes"] = routes_df
            inputs["routes_total"] = routes
            session["inputs"] = inputs
        else:
            # Bike
            mot = "cycling-regular"
            map, routes = plotmap(points=inputs["location_coords"],
                                  depot=inputs["depot"], api_key=ORS_api_key, num_vehicles=1, mot=mot)
            # DF with columns: Vehicle, Location id, Street, Number, Postcode, City, Distance
            routes_df = df_routes(inputs, routes)
            inputs["routes"] = routes_df
            inputs["routes_total"] = routes
            session["inputs"] = inputs
        # TODO change to redirect
        return render_template('index.html', map=map._repr_html_(), inputs=inputs)
        # 1. Use all inputs to calculate the route
        # 2. While calculating, show progress bar with
        # 3. When route determined, redirect to index
        # 4. On index show map
        # 5. Below map show the totals and the locations per vehicle
    else:
        map = locations_map(inputs["location_coords"], inputs["depot"])
        return render_template('index.html', map=map._repr_html_(), inputs=inputs)


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
