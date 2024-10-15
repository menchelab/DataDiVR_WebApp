import json

import PIL
from flask_socketio import emit

import cartographs_func as CG
import GlobalData as GD
import plotlyExamples as PE
import search


def protein_load_event(message, room):
    response = {}
    response["usr"] = message["usr"]
    response["id"] = message["id"]
    response["fn"] = "loadProtein"
    response["val"] = GD.pdata["protnamedown"], GD.pdata["protstyle"]
    emit("ex", response, room=room)  # send to all clients


def search_event(message, room):
    if len(message["val"]) > 1:
        x = '{"id": "search", "val":[], "fn": "makeNodeButton", "parent":"scrollbox2"}'
        results = json.loads(x)
        results["val"] = search.search(message["val"])
        emit("ex", results, room=room)




def chat_message_event(message, room):
    response = {}
    response = message
    # print("C_DEBUG: in app if chatmessage", response)
    emit("ex", response, room=room)


def node_list_event(message, room):
    message["names"] = []
    message["fn"] = "cnl"
    message["prot"] = []
    message["protsize"] = []
    for id in message["data"]:
        message["names"].append(GD.nodes["nodes"][id]["n"])

    emit("ex", message, room=room)
    # print(message)


def plot_to_js_event(message, room):
    response = {}
    response["fn"] = "plotly2js"
    response["parent"] = message["parent"]  # target <div>

    if message["msg"] == "Graph":
        response["val"] = PE.networkGraph()
        emit("ex", response, room=room)
    elif message["msg"] == "Barchart":
        response["val"] = PE.connectionBarGraph()
        emit("ex", response, room=room)
    elif message["msg"] == "timeGraph":
        response["val"] = PE.timeGraph()
        emit("ex", response, room=room)
    elif message["msg"] == "scatterGraph":
        response["val"] = PE.scatterGraph()
        emit("ex", response, room=room)

    # Draw Cartographs
    elif message["msg"] == "draw graph":
        response["val"] = CG.cartoGraphs()
        emit("ex", response, room=room)


def module_event(message, room):
    module_id = message["id"]
    response = {}
    response["usr"] = message["usr"]
    response["id"] = message["id"]
    response["fn"] = "moduleState"

    # False = minimized, True = maximized

    if message["val"] == "init":
        if module_id not in GD.pdata.keys():
            GD.pdata[module_id] = False
            GD.savePD()
        response["val"] = GD.pdata[module_id]
        emit("ex", response, room=room)

    if message["val"] == "maximize":
        GD.pdata[module_id] = True
        GD.savePD()
        response["val"] = True
        emit("ex", response, room=room)

    if message["val"] == "minimize":
        GD.pdata[module_id] = False
        GD.savePD()
        response["val"] = False
        emit("ex", response, room=room)
