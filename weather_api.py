import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

RSA_KEY = ""

API_TOKEN = "hw1_1token*@"

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


def get_weather(location, date):
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{date}?" \
          f"unitGroup=metric" \
          f"&key={RSA_KEY}&include=days&elements=tempmax,tempmin,temp,windspeed,visibility,cloudcover"

    response = requests.get(url)

    if response.status_code == requests.codes.ok:
        return json.loads(response.text)
    else:
        raise InvalidUsage(response.text, status_code=response.status_code)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>Home Work №1, Zasiadko Matviy.</h2></p>"


@app.route("/content/api/v1/integration/get", methods=["POST"])
def joke_endpoint():
    start_dt = dt.datetime.now()
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")
    requester_name = json_data.get("requester_name")
    location = json_data.get("location")
    date = json_data.get("date")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    weather = get_weather(location, date)

    resolved_address = weather.get("resolvedAddress")
    forecast = weather.get("days")

    end_dt = dt.datetime.now()

    result = {
        "requester_name": requester_name,
        "event_start_datetime": start_dt.isoformat(),
        "event_finished_datetime": end_dt.isoformat(),
        "event_duration": str(end_dt - start_dt),
        "resolved_address": weather.get("resolvedAddress"),
        "forecast": weather.get("days")
    }

    return result
