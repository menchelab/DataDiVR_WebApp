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


# moved to search_events.py
# def search_event(message, room): 
#     if len(message["val"]) > 1:
#         x = '{"id": "search", "val":[], "fn": "makeNodeButton", "parent":"scrollbox2"}'
#         results = json.loads(x)
#         results["val"] = search.search(message["val"])
#         results["node_id"] = search.search_nodeid_by_name(message["val"])
        
#         print("C_DEBUG: in search_event RESULTS", results)

#         emit("ex", results, room=room, namespace="/main") # quick fix - adding namespace = "/main" to emit
        

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
    """
    Generates and sends various types of visualizations to the frontend.

    This function processes a request to generate a specific type of graph or chart
    (e.g., network graph, bar chart, time graph, scatter plot, or cartograph) and sends
    the generated visualization data to the frontend for rendering.

    Args:
        message (dict): Event data containing the following keys:
            - "msg" (str): Specifies the type of graph or chart to generate.
                Supported values and their corresponding prompts:
                - "Graph": Generates a network graph. Triggered by prompts like:
                    "Show the network graph" or "Generate a subgraph for node X."
                - "Barchart": Generates a bar chart. Triggered by prompts like:
                    "Show a bar chart of connections" or "Generate a bar chart."
                - "timeGraph": Generates a time-series graph. Triggered by prompts like:
                    "Show a time graph" or "Generate a time-series visualization."
                - "scatterGraph": Generates a scatter plot. Triggered by prompts like:
                    "Show a scatter plot" or "Generate a scatter graph."
                - "draw graph": Generates a cartograph. Triggered by prompts like:
                    "Draw a cartograph" or "Generate a cartograph visualization."
            - "parent" (str): The target HTML `<div>` element where the graph will be rendered.
        room (str): Socket connection room identifier for sending the response.

    Behavior:
        - Based on the "msg" value in the `message` dictionary, the function calls the appropriate
          graph generation function from the `plotlyExamples` (PE) or `cartographs_func` (CG) modules.
        - The generated graph data is sent to the frontend using the `emit` function.

    Example:
        To generate a network graph for a specific node and render it in a specific `<div>`:
        {
            "msg": "Graph",
            "parent": "graph-container"
        }

    Emits:
        dict: A response dictionary with the following structure:
            - "fn" (str): The function name ("plotly2js").
            - "parent" (str): The target HTML `<div>` element for rendering the graph.
            - "val" (dict): The generated graph data.

    Prompts:
        This function can be triggered by prompts such as:
        - "Show the network graph."
        - "Generate a subgraph for node X."
        - "Show a bar chart of connections."
        - "Generate a time-series visualization."
        - "Draw a cartograph."
    """
        
    response = {}
    response["fn"] = "plotly2js"
    response["parent"] = message["parent"]  # target <div>

    if message["msg"] == "Graph":
        response["val"] = PE.networkGraph()
        emit("ex", response, room=room, namespace="/main")
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