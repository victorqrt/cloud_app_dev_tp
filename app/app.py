#!/usr/bin/env python

from pymongo import MongoClient
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def main_route():
    return "WIPi"
