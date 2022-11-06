import os

from dotenv import load_dotenv
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)

from flask_session import Session
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
        print(request.form)
        if "locations" in request.form:
            if request.form.get("locationsRadio") == "random":
                num_locations = int(request.form.get("randomRange"))
                coordinates = random_coords(num_locations)
                # Update inputs
                inputs = session["inputs"]
                inputs["method"] = "random"
                inputs["locations"] = num_locations
                inputs["location_coords"] = coordinates
            elif request.form.get("locationsRadio") == "file":
                file = request.files["formFile"]
                df = read_addresses(file)
                coordinates = [[df.loc[i, "Lat"], df.loc[i, "Lon"]]
                               for i in range(len(df))]
                # Update inputs
                inputs = session["inputs"]
                inputs["method"] = "file"
                inputs["locations"] = len(df.index)
                inputs["location_coords"] = coordinates
            # If depot not defined, set standard value
            if "depot" not in inputs:
                inputs["depot"] = [51.688193, 5.547352]
            # Store updated inputs in session
            session["inputs"] = inputs
            # plot maps
            map = locations_map(inputs["depot"], inputs["location_coords"])
            return render_template('index.html', map=map._repr_html_(), inputs=inputs)
        elif "depot" in request.form:
            # TODO change for multiple depots
            inputs = session["inputs"]
            inputs["depot"] = [float(request.form.get("depot_lat")), float(
                request.form.get("depot_long"))]
            session["inputs"] = inputs
            # plot maps
            map = locations_map(inputs["depot"], inputs["location_coords"])
            return render_template('index.html', map=map._repr_html_(),  inputs=inputs)
    else:
        # If api keys are not set, redirect to keys
        if ORS_api_key is None:
            return redirect("/keys")
        else:
            inputs = {}
            session["inputs"] = inputs
            map = empty_map()
            return render_template('index.html', map=map._repr_html_(), inputs=inputs)


@app.route('/locations', methods=["GET"])
def locations():
    inputs = session["inputs"]
    return render_template('locations.html', inputs=inputs)


@app.route('/depots', methods=["GET"])
def depots():
    inputs = session["inputs"]
    #ORS_api_key = session["openrouteservice_api_key"]
    return render_template('depots.html', ORS_api_key=ORS_api_key, inputs=inputs)


@app.route('/google', methods=["GET"])
def google():
    inputs = session["inputs"]
    return render_template('google.html', inputs=inputs)


@app.route('/calculateroute', methods=["GET"])
def calculateroute():
    inputs = session["inputs"]
    # 1. Use all inputs to calculate the route
    # 2. While calculating, show progress bar with
    # 3. When route determined, redirect to index
    # 4. On index show map
    # 5. Below map show the totals and the locations per vehicle


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
