import mongo_ops
from flask import Flask, render_template, jsonify

app = Flask(__name__)
mops = mongo_ops.MongoOps()

@app.route("/", strict_slashes=False)
def main_route():
    return app.send_static_file("index.html")

@app.route("/chart", strict_slashes=False)
def chart_route():
    return app.send_static_file("chart.html")

########################
# API endpoints routes #
########################

@app.route("/api/db/<db>", strict_slashes=False)
@app.route("/api/db/<db>/<coll>", strict_slashes=False)
########################
# API endpoints routes #
########################

@app.route("/api/db/<db>", strict_slashes=False)
@app.route("/api/db/<db>/<coll>", strict_slashes=False)
def db_route(db, coll=None):
    if coll is None:
        return jsonify(mops.get_db_colls(db))
    else:
        return jsonify(mops.get_raw_coll(db, coll))
