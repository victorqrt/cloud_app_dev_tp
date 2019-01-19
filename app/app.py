import mongo_ops
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
mops = mongo_ops.MongoOps()

#################
# Webapp routes #
#################

@app.route("/", strict_slashes=False)
def main_route():
    return app.send_static_file("index.html")

@app.route("/chart", strict_slashes=False)
def chart_route():
    return app.send_static_file("chart.html")

########################
# API endpoints routes #
########################

@app.route("/api/db", strict_slashes=False)
@app.route("/api/db/<coll>", strict_slashes=False)
def db_route(coll=None):
    if coll is None:
        return jsonify(mops.get_db_colls())
    else:
        return jsonify(mops.get_raw_coll(coll, pop_oid=True))

@app.route("/api/players", strict_slashes=False)
def player_info_route():
    return jsonify(mops.get_full_players_documents())

# The simple interrogations

# 1
@app.route("/api/playoff_palmares", strict_slashes=False)
def palmares_route():
    if "teamid" not in request.args:
        return jsonify([])
    return jsonify(mops.team_playoff_palmares(request.args["teamid"]))
