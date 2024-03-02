import csv
import json
import logging
import os
import random
import re
import string
from cgi import print_arguments
from io import StringIO

import flask

# from flask_session import Session
import requests
from engineio.payload import Payload
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from PIL import Image

import GlobalData as GD
import plotlyExamples as PE

# import GlobalData as GD
import uploader
from io_blueprint import IOBlueprint
from search import *
from uploader import *
from websocket_functions import *
from websocket_functions import bcolors

url_prefix = "/doku"
blueprint = IOBlueprint(
    "doku",
    __name__,
    url_prefix=url_prefix,
    template_folder=os.path.abspath("./extensions/documentation/templates"),
    static_folder=os.path.abspath("./extensions/documentation/static"),
)


@blueprint.route("/")
def help():
    return render_template("help.html")


@blueprint.route("/helloflask")
def helloflask():
    return render_template("helloflask.html")


@blueprint.route("/websockets")
def websockets():
    return render_template("websockets.html")


@blueprint.route("/websockets_tutorial")
def websocketsT():
    data = json.dumps(
        {
            "fruits": ["apples", "bananas", "oranges"],
            "pets": ["lizard", "bug", "cat", "mouse", "pokemon"],
        }
    )
    return render_template("websockets_tutorial.html", data=data)


@blueprint.route("/CustomElements1")
def CustomElements1R():
    return render_template("CustomElements1.html")


@blueprint.route("/ServerSideVar")
def ServerSideVarR():
    return render_template("serverVar.html")


@blueprint.route("/manipulateTextures")
def manipulateTextures():
    return render_template("manipulateTextures.html")


@blueprint.route("/plotly")
def plotly():
    return render_template("Plotly.html")


@blueprint.route("/extensions")
def Extentions():
    return render_template("extensions.html")


@blueprint.route("/webui")
def webUI():
    return render_template("webui.html")


@blueprint.route("/dataFormat")
def dataFormat():
    return render_template("dataFormat.html")


@blueprint.route("/Graphs")
def graphs():
    return render_template("Graphs.html")


@blueprint.route("/uploadFormat")
def uploadFormat():
    return render_template("uploadFormat.html")


@blueprint.route("/Initialization")
def Initialization():
    return render_template("Initialization.html")


@blueprint.route("/annotations")
def doku_annotations():
    return render_template("annotations.html")


@blueprint.route("/uimodules")
def doku_modules():
    return render_template("newmodules.html")


@blueprint.route("/cytoscape")
def doku_cytoscape():
    return render_template("cytoscapeBridge.html")


@blueprint.on("join", namespace="/doku")
def join(message):
    room = flask.session.get("room")
    join_room(room)
    print("join doku " + message["usr"])


@blueprint.on("ex", namespace="/doku")
def ex(message):

    room = flask.session.get("room")
    # print(webfunc.bcolors.WARNING+ flask.session.get("username")+ "ex: "+ json.dumps(message)+ webfunc.bcolors.ENDC)
    # message["usr"] = flask.session.get("username")
    print("incoming doku " + str(message))

    if message["fn"] == "Plotly2js":
        response = {}
        response["fn"] = "plotly2js"
        response["parent"] = message["parent"]  # target <div>

        if message["msg"] == "VecField":
            response["val"] = PE.vectorfieldGraph()
            emit("ex", response, room=room)
        elif message["msg"] == "HistRug":
            response["val"] = PE.histRugGraph()
            emit("ex", response, room=room)
        elif message["msg"] == "BoxPlot":
            response["val"] = PE.boxPlotGraph()
            emit("ex", response, room=room)
        elif message["msg"] == "Barchart":
            data = [
                {"name": "aaron", "val": 200, "id": 0},
                {"name": "erica", "val": 500, "id": 1},
                {"name": "anton", "val": 250, "id": 2},
                {"name": "emma", "val": 180, "id": 3},
            ]
            response["val"] = PE.barGraph(data)
            emit("ex", response, room=room)
        elif message["msg"] == "timeGraph":
            response["val"] = PE.timeGraph()
            emit("ex", response, room=room)
        elif message["msg"] == "scatterGraph":
            response["val"] = PE.scatterGraph()
            emit("ex", response, room=room)
        elif message["msg"] == "sankey":
            response["val"] = PE.sankeyGraph()
            emit("ex", response, room=room)
        elif message["msg"] == "Heatmap":
            response["val"] = PE.heatmapGraph()
            emit("ex", response, room=room)
        # if message["id"] == "plotly2js":

    emit("ex", message, room=room)
