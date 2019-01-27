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

# The simple interrogations

# 1
@app.route("/api/playoff_palmares", strict_slashes=False)
def palmares_route():
    if "teamid" not in request.args:
        return jsonify([])
    return jsonify(mops.team_playoff_palmares(request.args["teamid"]))


# 2
@app.route("/api/coach_history", strict_slashes=False)
def coach_history_route():
    if "coachid" not in request.args:
        return jsonify([])
    return jsonify(mops.coach_history(request.args["coachid"]))

# 3
@app.route("/api/player_coaches", strict_slashes=False)
def player_coaches_route():
    if "playerid" not in request.args:
        return jsonify([])
    return jsonify(mops.player_had_coaches(request.args["playerid"]))

# 4
@app.route("/api/player_playoffs", strict_slashes=False)
def player_playoffs_route():
    if "playerid" not in request.args:
        return jsonify([])
    return jsonify(mops.player_playoff_palmares(request.args["playerid"]))

# The heavy ones

# 1
@app.route("/api/coach_has_trained", strict_slashes=False)
def coach_players_trained_route():
    if "coachid" not in request.args:
        return jsonify([])
    return jsonify(mops.coach_all_trained(request.args["coachid"]))

# Those routes are related to the front-end

@app.route("/api/misc/coach_name_id_pairs", strict_slashes=False)
def coach_name_id_pairs():
    return jsonify(mops.coach_name_id_pairs())


@app.route("/api/misc/team_name_id_pairs", strict_slashes=False)
def team_name_id_pairs():
    return jsonify(mops.team_name_id_pairs())

@app.route("/api/misc/player_name_id_pairs", strict_slashes=False)
def player_name_id_pairs():
    return jsonify(mops.player_name_id_pairs())
