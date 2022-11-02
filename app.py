import os

from dotenv import load_dotenv
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)

from flask_session import Session
from geocoding import read_addresses
from map import empty_map, plotmap
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

        if num_vehicles != "":
            num_vehicles = int(num_vehicles)
        else:
            num_vehicles = 1

        coordinates = random_coords(20)

        # plot maps
        map, routes = plotmap(depot_coords, coordinates,
                              ORS_api_key, num_vehicles)

        return render_template('index.html', map=map._repr_html_(), routes=routes)
    else:
        # If api keys are not set, redirect to keys
        if ORS_api_key is None:
            return redirect("/keys")
        else:
            map = empty_map()
            return render_template('index.html', map=map._repr_html_())


@app.route('/locations', methods=["GET", "POST"])
def locations():
    if request.method == "POST":
        file = request.files["formFile"]
        # Call function to extract addresses and return list of coordinates in [Lon, Lat]
        df = read_addresses(file)
        session["locations"] = [[df.loc[i, "Lon"], df.loc[i, "Lat"]]
                                for i in range(len(df))]
        return render_template('locations.html', locations=df)
    else:
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
