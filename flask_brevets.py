"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""
import os
import flask
from flask import Flask, redirect, url_for, request, render_template, jsonify, make_response
from flask_restful import Resource, Api
from pymongo import MongoClient
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config
import csv
from io import StringIO
import logging

###
# Globals
###
app = flask.Flask(__name__)
api = Api(app)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY

client = MongoClient("mongodb://db:27017/")
db = client.tododb
###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = url_for("index")
    return render_template('404.html'), 404


"""

Needed to comment this out to create the APIs

@app.route("/_calc_times")
def _calc_times():
    #Calculates open/close times from miles, using rules
    #described at https://rusa.org/octime_alg.html.
    #Expects one URL-encoded argument, the number of miles.
    app.logger.debug("Got a JSON request")
    try:
        km = request.args.get('km', 999, type=float)
        brevet_start_time = request.args.get('brevet_start_time')
        brevet_dist_km = request.args.get('brevet_dist_km', type=int)
    except ValueError:
        return jsonify(error="Input must be a number"), 400
    app.logger.debug(f"brevet_dist_km= {brevet_dist_km}")
    start_time = arrow.get(brevet_start_time)
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))
    
    open_time = acp_times.open_time(km, brevet_dist_km, start_time.isoformat())
    app.logger.debug(f"open_time === {open_time}")
    close_time = acp_times.close_time(km, brevet_dist_km, start_time.isoformat())
    result = {"open": open_time, "close": close_time}
    return jsonify(result=result)

@app.route('/add', methods=['POST'])
def add():
    data = request.get_json()
    item_doc = {
        "open_time": data["open_time"],
        "close_time": data["close_time"]
    }
    result = db.times.insert_one(item_doc)
    return redirect(url_for("index"))
"""


class CalcTimes(Resource):
    def get(self):
        app.logger.debug("Got a JSON request")
        try:
            km = request.args.get('km', 999, type=float)
            brevet_start_time = request.args.get('brevet_start_time')
            brevet_dist_km = request.args.get('brevet_dist_km', type=int)
        except ValueError:
            return jsonify(error="Input must be a number"), 400

        start_time = arrow.get(brevet_start_time)
        open_time = acp_times.open_time(km, brevet_dist_km, start_time.isoformat())
        close_time = acp_times.close_time(km, brevet_dist_km, start_time.isoformat())
        result = {"open": open_time, "close": close_time}
        return jsonify(result=result)

class AddTimes(Resource):
    def post(self):
        data = request.get_json()
        _items = {
            "open_time": data["open_time"],
            "close_time": data["close_time"]
        }
        result = db.times.insert_one(_items)
        return jsonify({"result": "success"}), 201

class listAll(Resource):
    def get(self, format=None):
        top = request.args.get('top', default=0, type=int)
        items = list(db.times.find({}, {"_id": 0, "open_time": 1, "close_time": 1}))
        all_times = []
        for item in items:
            open_times = [time for time in item["open_time"] if time]
            close_times = [time for time in item["close_time"] if time]
            paired_times = list(zip(open_times, close_times))
            all_times.extend([{"open_time": open, "close_time": close} for open, close in paired_times])
        if top > 0:
            all_times = all_times[:top]

        app.logger.debug(f"retrieved: {all_times}")
        if format == 'csv':
            return convert_to_csv(all_times, ["open_time", "close_time"])
        return jsonify(all_times)

class listOpenOnly(Resource):
    def get(self, format=None):
        top = request.args.get('top', default=0, type=int)
        items = list(db.times.find({}, {"_id": 0, "open_time": 1}))
        open_times = []
        for item in items:
            open_times.extend([time for time in item["open_time"] if time])

        if top > 0:
            open_times = open_times[:top]
        app.logger.debug(f"retrieved open times: {open_times}")

        if format == 'csv':
            return convert_to_csv([{"open_time": time} for time in open_times], ["open_time"])
        return jsonify(open_times)

class listCloseOnly(Resource):
    def get(self, format=None):
        top = request.args.get('top', default=0, type=int)
        items = list(db.times.find({}, {"_id": 0, "close_time": 1}))
        close_times = []
        for item in items:
            close_times.extend([time for time in item["close_time"] if time])

        if top > 0:
            close_times = close_times[:top]
        app.logger.debug(f"retrieved close times: {close_times}")

        if format == 'csv':
            return convert_to_csv([{"close_time": time} for time in close_times], ["close_time"])
        return jsonify(close_times)

class ClearTimes(Resource):
    def post(self):
        db.times.delete_many({})
        return redirect(url_for('index'))

def convert_to_csv(data, fields):
    si = StringIO()
    cw = csv.DictWriter(si, fieldnames=fields)
    cw.writeheader()
    cw.writerows(data)
    output = make_response(si.getvalue())
    output.headers["Content-type"] = "text/plain"
    return output

api.add_resource(CalcTimes, '/_calc_times')
api.add_resource(AddTimes, '/add')
api.add_resource(listAll, '/listAll', '/listAll/<string:format>') #cool trick to use either csv or json
api.add_resource(listOpenOnly, '/listOpenOnly', '/listOpenOnly/<string:format>')
api.add_resource(listCloseOnly, '/listCloseOnly', '/listCloseOnly/<string:format>')
api.add_resource(ClearTimes, '/clear')
            

@app.route('/todo', methods=['GET'])
def todo():
    items = list(db.times.find({}, {"_id": 0}))
    app.logger.debug(f"retrieved: {items}")

    unique_times = []
    seen_times = set()
    for item in items:
        for i in range(len(item["open_time"])):
            if item["open_time"][i] and item["close_time"][i]:
                time_pair = (item["open_time"][i], item["close_time"][i])
                if time_pair not in seen_times:
                    unique_times.append(time_pair)
                    seen_times.add(time_pair)

    return render_template("todo.html", items=unique_times)
"""
@app.route("/clear", methods=["POST"])
def clear():
    db.times.delete_many({})
    return redirect(url_for("index"))
#############
"""
app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
