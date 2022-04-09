from flask_session import Session
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from dotenv import load_dotenv
import os

from random_locations import random_coords

from map import plotmap

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

ORS_api_key = ""


def configure() -> str:
    load_dotenv()
    return os.getenv('OPENROUTESERVICE_API_KEY')


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        print(request.form)
        depot = request.form.get("depot")
        random_yesno = request.form.get("random")
        file_name = request.form.get("formFile")
        home_address = request.form.get("home")
        num_vehicles = request.form.get("numVehicles")
        km_price = request.form.get("kmPrice")

        # Depot
        if depot != "":
            depot_coords = [float(request.form.get(
                "depot_lat")), float(request.form.get("depot_lng"))]
        else:
            depot_coords = [51.688193, 5.547352]

        if num_vehicles != "":
            num_vehicles = int(num_vehicles)
        else:
            num_vehicles = 1

        # Plot random map
        if request.form.get("locationsRadio") == "random":
            N_random = int(request.form.get("numRandom"))
            if N_random != "":
                # Get list of random coordinates from within NL
                random_coordinates = random_coords(N_random)
                map, routes = plotmap(depot_coords, random_coordinates,
                                      ORS_api_key, num_vehicles)

        return render_template('index.html', map=map._repr_html_(), routes=routes)
    else:
        # If api keys are not set, redirect to keys
        if session.get('googleplaces_api_key') is None:
            return redirect("/keys")
        else:
            return render_template('index.html')


@app.route('/keys', methods=["GET", "POST"])
# Route to set the API keys
def set_api_keys():
    if request.method == "POST":
        session["googleplaces_api_key"] = request.form.get(
            "googleplaces_api_key")
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
