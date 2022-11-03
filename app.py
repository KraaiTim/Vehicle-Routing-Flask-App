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
        depot_coords = [51.688193, 5.547352]
        # TODO remove num vehicles
        num_vehicles = 1

        print(request.form)

        if request.form.get("locationsRadio") == "random":
            num_locations = int(request.form.get("randomRange"))
            coordinates = random_coords(num_locations)

            session["method"] = "random"
            session["qty"] = num_locations
            location_data = {
                "method": session["method"], "#locations": session["qty"]}

        elif request.form.get("locationsRadio") == "file":
            file = request.files["formFile"]
            df = read_addresses(file)
            coordinates = [[df.loc[i, "Lon"], df.loc[i, "Lat"]]
                           for i in range(len(df))]
            session["method"] = "file"
            session["qty"] = len(df.index)
            location_data = {
                "method": session["method"], "#locations": session["qty"]}

        # plot maps
        # TODO change the map to only locations
        map = locations_map(depot_coords, coordinates)
        return render_template('index.html', map=map._repr_html_(), locations=location_data)
    else:
        # If api keys are not set, redirect to keys
        if ORS_api_key is None:
            return redirect("/keys")
        else:
            map = empty_map()
            return render_template('index.html', map=map._repr_html_())


@app.route('/locations', methods=["GET"])
def locations():
    return render_template('locations.html')


@app.route('/keys', methods=["GET", "POST"])
# Route to set the API keys
def set_api_keys():
    if request.method == "POST":
        ORS_api_key = request.form.get(
            "openrouteservice_api_key")
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
