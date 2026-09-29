import json
import os
import uuid

import PIL
from flask_socketio import emit

import GlobalData as GD


def _atomic_save(image, path):
    """
    Save `image` to the shared/well-known `path` without ever exposing a
    partially-written file to a concurrent reader.

    These temp textures (temp1.png, temp_nodes.png, temp_links.png) are fixed,
    well-known filenames shared by every connected client (main/preview/unreal
    all read the same path). With multiple clients in the same room, two node
    selections / paint actions arriving close together can be handled on
    overlapping threads, and PIL's Image.save() writes the destination file
    in place - a client's texture fetch landing mid-write would see a
    truncated/corrupt PNG (intermittent "something's off" glitches that
    disappear if you happen to retry). Write to a unique staging file first,
    then atomically rename it onto the canonical path (os.replace is atomic
    on the same filesystem) so readers only ever see a fully-written file.
    """
    # PIL infers the save format from the filename's extension when `format`
    # isn't passed explicitly - keep the real extension on the staging file
    # (and pass format explicitly too) rather than appending ".tmp", which
    # made PIL raise "unknown file extension: .tmp".
    root, ext = os.path.splitext(path)
    staging_path = f"{root}.{uuid.uuid4().hex}{ext}"
    image.save(staging_path, format=image.format or "PNG")
    os.replace(staging_path, path)


def selection_event(message):
    if not message["id"] in GD.pdata.keys():  # check if selection exists in pdata.json
        GD.pdata[message["id"]] = ""
    GD.pdata[message["id"]] = message["opt"]
    GD.savePD()



def colorbox_event(message, room):
    # copy active color texture
    im1 = PIL.Image.open(
        "static/projects/"
        + GD.data["actPro"]
        + "/layoutsRGB/"
        + GD.pfile["layoutsRGB"][GD.safe_pdata_index("layoutsRGBDD", GD.pfile["layoutsRGB"])]
        + ".png",
        "r",
    )
    im2 = im1.copy()
    # convert rgb to hex string
    color = (
        int(message["r"]),
        int(message["g"]),
        int(message["b"]),
        int(message["a"] * 255),
    )
    pix_val = list(im1.getdata())

    # colorize clipboard selection
    for n in GD.pdata["cbnode"]:
        id = int(n["id"])
        pix_val[id] = color
    im2.putdata(pix_val)

    # save temp texture

    path = "static/projects/" + GD.data["actPro"] + "/layoutsRGB/temp1.png"
    _atomic_save(im2, path)
    im1.close()
    im2.close()
    # send update signal to clients
    textures = [
        {
            "channel": "nodeRGB",
            "path": "static/projects/" + GD.data["actPro"] + "/layoutsRGB/temp1.png",
        }
    ]
    response = {"usr": message["usr"], "fn": "updateTempTex", "textures": textures}

    emit("ex", response, room=room)
    emit("ex", message, room=room)



# --- NODE PAINTER ---
# VR paint brush (and the web UI's nodePaint module) -> GD.paintedNodes -> temp1.png
# node color texture broadcast to all clients via updateTempTex.
#
# Messages handled here:
#   {"fn":"paintnodes", "id":"paintnodes", "op":"ADD"|"SUB"|"CLEAR", "data":[ids]}
#   {"fn":"colorbox",   "id":"nodePaintColorInput", "r","g","b","a"(0..1)}
#   {"fn":"saveNodeSelection", "id":"paintSelSave", "val": "<selection name>"}

color_default = (255,0,0,255)


def _parse_paint_ids(data):
    # UE hands paint strokes over through ue.interface.paintnodesADD/SUB, which can
    # arrive as a list, a JSON string ('[1,2,3]'), a comma separated string or a
    # single id - normalize to a list of ints and drop anything that isn't an id
    if isinstance(data, str):
        text = data.strip()
        try:
            data = json.loads(text)
        except ValueError:
            data = [t for t in text.replace(";", ",").split(",") if t.strip()]
    if isinstance(data, dict):
        data = data.get("data", data.get("ids", []))
    if not isinstance(data, (list, tuple, set)):
        data = [data]

    ids = []
    for item in data:
        try:
            ids.append(int(item))
        except (TypeError, ValueError):
            print("C_DEBUG: nodepaint - ignoring invalid node id:", item)
    return ids


def _paint_status_response(message):
    # small status message so web UIs can show the painted count and UE can
    # keep its brush state in sync (the full id list would be too chatty)
    return {
        "usr": message.get("usr"),
        "fn": "paintnodes",
        "id": "paintnodesStatus",
        "count": len(GD.paintedNodes),
        "color": list(GD.paintedNodesColor),
    }


def paintNodes_renderTexture(message, room):
    # copy active color texture
    im1 = PIL.Image.open(
        "static/projects/"
        + GD.data["actPro"]
        + "/layoutsRGB/"
        + GD.pfile["layoutsRGB"][GD.safe_pdata_index("layoutsRGBDD", GD.pfile["layoutsRGB"])]
        + ".png",
        "r",
    )
    im2 = im1.copy()

    if not hasattr(GD, 'paintedNodesColor'):
        GD.paintedNodesColor = color_default
    color = GD.paintedNodesColor

    pix_val = list(im1.getdata())

    # a pixel is either RGB or RGBA depending on how the project's texture was generated
    if pix_val and not isinstance(pix_val[0], int) and len(pix_val[0]) == 3:
        color = color[:3]

    # colorize painted nodes
    for id in GD.paintedNodes:
        if 0 <= id < len(pix_val):
            pix_val[id] = color

    im2.putdata(pix_val)

    # save temp texture
    path = "static/projects/" + GD.data["actPro"] + "/layoutsRGB/temp1.png"
    _atomic_save(im2, path)
    im1.close()
    im2.close()
    # send update signal to clients
    textures = [
        {
            "channel": "nodeRGB",
            "path": "static/projects/" + GD.data["actPro"] + "/layoutsRGB/temp1.png",
        }
    ]
    response = {"usr": message.get("usr"), "fn": "updateTempTex", "textures": textures}

    emit("ex", response, room=room)
    emit("ex", _paint_status_response(message), room=room)


def paintNodes_event(message, room):
    op = str(message.get("op", "ADD")).upper()
    nodecount = len(GD.nodes.get("nodes", []))
    ids = [i for i in _parse_paint_ids(message.get("data", [])) if 0 <= i < nodecount]

    if op == "ADD":
        painted = set(GD.paintedNodes)
        for id in ids:
            if id not in painted:
                GD.paintedNodes.append(id)
                painted.add(id)
    elif op == "SUB":
        remove = set(ids)
        GD.paintedNodes[:] = [id for id in GD.paintedNodes if id not in remove]
    elif op == "CLEAR":
        GD.paintedNodes.clear()
    else:
        print("C_DEBUG: nodepaint - unknown op:", op)
        return

    paintNodes_renderTexture(message, room)


def clear_painted_nodes_event(message, room):
    """
    Clears the node painter: removes the paint from all nodes painted in VR and
    restores the original node colors. Use for requests like "clear the painted
    nodes", "reset the paint", "erase my node painting".
    """
    message = dict(message)
    message["op"] = "CLEAR"
    paintNodes_event(message, room)


def colorbox_nodePaint_event(message, room):
    GD.paintedNodesColor = (int(message["r"]),int(message["g"]),int(message["b"]),int(float(message["a"])*255))
    paintNodes_renderTexture(message, room)


def save_node_selection_event(message, room):
    """
    Saves the nodes currently painted in VR as a named node selection in the
    project, so it shows up in the Selections module and can be copied to the
    clipboard later. Use for requests like "save the painted nodes as <name>",
    "store this selection", "keep these painted nodes".
    """
    name = str(message.get("val") or "").strip()
    if not name:
        name = "painted selection " + str(len(GD.pfile.get("selections", [])) + 1)

    status = {"usr": message.get("usr"), "fn": "saveNodeSelection", "id": "paintSelStatus"}

    if not GD.paintedNodes:
        status["val"] = "Nothing painted - paint some nodes first."
        emit("ex", status, room=room)
        return

    selection = {"name": name, "nodes": [int(id) for id in GD.paintedNodes]}

    # serialized against project switches, which swap GD.pfile out wholesale
    with GD.project_switch_lock:
        selections = GD.pfile.setdefault("selections", [])
        # saving under an existing name overwrites that selection
        for i, sel in enumerate(selections):
            if sel.get("name") == name:
                selections[i] = selection
                sel_index = i
                break
        else:
            selections.append(selection)
            sel_index = len(selections) - 1
        GD.savePFile()

        GD.pdata["selectionsDD"] = sel_index
        GD.savePD()

    print("C_DEBUG: saved painted node selection: ", name, len(selection["nodes"]), "nodes")

    # refresh the selections dropdown on every client (opt rebuilds the list)
    emit(
        "ex",
        {
            "usr": message.get("usr"),
            "fn": "dropdown",
            "id": "selectionsDD",
            "parent": "selectionsDD",
            "opt": [sel["name"] for sel in selections],
            "sel": str(sel_index),
            "name": name,
        },
        room=room,
    )

    status["val"] = "Saved '" + name + "' (" + str(len(selection["nodes"])) + " nodes)"
    emit("ex", status, room=room)




def slider_event(message, room):
    if message["id"] not in GD.pdata:
        GD.pdata[message["id"]] = ""
        print("newGD Variable created")
    if message["val"] != "init":
        GD.pdata[message["id"]] = message["val"]
        GD.savePD()
    response = {}
    response["usr"] = message["usr"]
    response["fn"] = "sli"
    response["id"] = message["id"]
    response["val"] = GD.pdata[message["id"]]
    print(response)
    emit("ex", response, room=room)


def submit_event(message, room):
    if message["parent"] not in GD.pdata:
        GD.pdata[message["parent"]] = []
    if message["val"] != "init":
        GD.pdata[message["parent"]].append(message["val"])
        GD.savePD()
    response = {}
    response["fn"] = "serVarExample"
    response["parent"] = message["parent"]

    response["buttons"] = GD.pdata[message["parent"]]
    # print(response)
    emit("ex", response, room=room)




# moved to nodeinfo_events.py
# def node_event(message, room):
#     response = {}

#     response["val"] = {}
#     response["fn"] = "node"
#     response["id"] = message["val"]
#     response["nch"] = len(GD.nchildren[int(message["val"])])
#     response["val"] = GD.nodes["nodes"][int(message["val"])]
#     GD.pdata["activeNode"] = message["val"]

#     if "protein_info" in GD.nodes["nodes"][int(message["val"])]:
#         if (
#             not "protstyle" in GD.pdata.keys()
#         ):  # check if selection exists in pdata.json
#             GD.pdata["protstyle"] = ""
#         GD.pdata["protstyle"] = list(
#             GD.nodes["nodes"][int(message["val"])]["protein_info"][0].keys()
#         )[1]

#         if (
#             not "protnamedown" in GD.pdata.keys()
#         ):  # check if selection exists in pdata.json
#             GD.pdata["protstyle"] = ""
#         GD.pdata["protnamedown"] = GD.nodes["nodes"][int(message["val"])]["uniprot"][0]

#         GD.savePD()

#     emit("ex", response, room=room, namespace = "/main") # quick fix - adding namespace = "/main" to emit




def manLabel_event(message,room):
    #ToDo: save them in pfile and load on layout change
    emit("ex", message, room=room)

def children_event(message, room):
    response2 = {}
    response2["usr"] = message["usr"]
    response2["id"] = "children"
    response2["parent"] = "scrollbox3"
    response2["fn"] = "makeNodeButton"
    response2["nid"] = GD.nodes["nodes"][int(GD.pdata["activeNode"])]["n"]
    response2["val"] = []

    ids = GD.nchildren[int(GD.pdata["activeNode"])]
    for d in ids:
        node = {}
        node["name"] = GD.nodes["nodes"][int(d)]["n"]
        node["color"] = GD.pixel_valuesc[int(d)]
        node["id"] = d
        response2["val"].append(node)
    print(response2)
    emit("ex", response2, room=room)
    


def reset_layout_event(message, room):
    if message["id"] == "resetlayout":
        GD.pdata["layoutsRGBDD"] = 0
        GD.pdata["layoutsDD"] = 0
        GD.pdata["layoutsRGBDD"] = 0
        GD.pdata["layoutsRGBDD"] = 0
        GD.savePD()

        response = {}
        response["usr"] = message["usr"]
        response["fn"] = "ue4"
        response["id"] = "resetlayout"
        response["val"] = '0'
        emit("ex", response, room=room)
    else:
        emit("ex", message, room=room)
        


import json

def highlight_node_and_links_ue4(message, room):
    """ 
    Creates temporary textures to highlight a selected node and its connected links
    using the currently active layoutsRGB.
    """
    highlight_color = (0, 174, 255, 255) # yellow: (255, 255, 0, 255) 

    # N O D E S 
    # get current layout node colors
    im1_nodes = PIL.Image.open(
        "static/projects/"
        + GD.data["actPro"]
        + "/layoutsRGB/"
        + GD.pfile["layoutsRGB"][GD.safe_pdata_index("layoutsRGBDD", GD.pfile["layoutsRGB"])]
        + ".png",
        "r",
    )
    im2_nodes = im1_nodes.copy()

    # Highlight selected node
    node_id = int(message["val"]) #["data"][0]
    #print("C_DEBUG : highlighting node id: ", node_id)
    #print("C_DEBUG : type of node_id: ", type(node_id))

    pix_val = list(im1_nodes.getdata())
    pix_val[node_id] = highlight_color

    im2_nodes.putdata(pix_val)

    # save temp texture
    path = "static/projects/" + GD.data["actPro"] + "/layoutsRGB/temp_nodes.png"
    _atomic_save(im2_nodes, path)
    im1_nodes.close()
    im2_nodes.close()

    # L I N K S
    im1_links = PIL.Image.open(
        "static/projects/"
        + GD.data["actPro"]
        + "/linksRGB/"
        + GD.pfile["linksRGB"][GD.safe_pdata_index("linksRGBDD", GD.pfile["linksRGB"])]
        + ".png",
        "r",
    )

    im2_links = im1_links.copy()

    # Highlight connected links
    # Retrieve the links this node is part of from links.json in the active project

    links_path = (
        "static/projects/"
        + GD.data["actPro"]
        + "/links.json"
    )
    with open(links_path, "r") as f:
        links_data = json.load(f)
    #print("C_DEBUG : loaded links data: ", links_data)

    link_ids = []
    for link in links_data.get("links", []):  # iterate through all links
        id = link.get('id')
        sourcenode = link.get('s')
        targetnode = link.get('e')
        #print("C_DEBUG : checking link id ", id, " with source node ", sourcenode, " and target node ", targetnode)

        if str(node_id) == sourcenode or str(node_id) == targetnode:  # check if node_id matches "s" or "e"
            link_ids.append(int(id))  # append the link id to the list
    print("C_DEBUG : found link ids for node ", node_id, " : ", len(link_ids))

    # node_name = message["val"]["names"][0]
    # print("C_DEBUG : node name to highlight links for: ", node_name)
    # link_names = links_data.get("links", [])[0].get(str(node_name), {})  # get link names for the retrieved link ids
    # print("C_DEBUG : found link names for node ", node_id, " : ", len(link_names))

    # # check if link_ids and link_names are not empty and of same length
    # if not link_ids or not link_names or len(link_ids) != len(link_names):
    #     print("C_DEBUG : No valid links found for node ", node_id, " - link_ids: ", link_ids, " link_names: ", link_names)
    #     link_ids = []  # set to empty list to avoid errors in the following code
    #     link_names = []  # set to empty list to avoid errors in the following code
        
    pix_val_links = list(im1_links.getdata())
    for link_id in link_ids:
        pix_val_links[link_id] = highlight_color
    
    im2_links.putdata(pix_val_links)
    
    # save temp texture
    path = "static/projects/" + GD.data["actPro"] + "/linksRGB/temp_links.png"
    _atomic_save(im2_links, path)
    im1_links.close()
    im2_links.close()

    # send update signal to clients
    textures = [
        {
            "channel": "nodeRGB",
            "path": "static/projects/" + GD.data["actPro"] + "/layoutsRGB/temp_nodes.png",
        },
        {
            "channel": "linkRGB",
            "path": "static/projects/" + GD.data["actPro"] + "/linksRGB/temp_links.png",
        }
    ]

    response = {}
    # check for "usr" key in message
    if "usr" in message:
        response["usr"] = message["usr"]
    else:
        response["usr"] = "tempUser"

    response = {"id": None, "fn": "updateTempTex", "textures": textures}
    emit("ex", response, room=room)

