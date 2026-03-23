import PIL
from flask_socketio import emit

import GlobalData as GD


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
        + GD.pfile["layoutsRGB"][int(GD.pdata["layoutsRGBDD"])]
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
    im2.save(path)
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



color_default = (255,0,0,255)
def paintNodes_renderTexture(message, room):            
    # copy active color texture
    im1 = PIL.Image.open(
        "static/projects/"
        + GD.data["actPro"]
        + "/layoutsRGB/"
        + GD.pfile["layoutsRGB"][int(GD.pdata["layoutsRGBDD"])]
        + ".png",
        "r",
    )
    im2 = im1.copy()
    # convert rgb to hex string
    '''
    color = (
        int(message["r"]),
        int(message["g"]),
        int(message["b"]),
        int(message["a"] * 255),
    )'''
    if not hasattr(GD, 'paintedNodesColor'):
        GD.paintedNodesColor = color_default

    # notetoself (C): put into pdata instead of GD
    color = GD.paintedNodesColor
    print("C_DEBUG: painting with color: ", color)

    pix_val = list(im1.getdata())
    print("C_DEBUG: pix_val: ", len(pix_val))

    # colorize clipboard selection
    if len(GD.paintedNodes) > 0:
        for id in GD.paintedNodes:
            pix_val[id] = color
            #print("C_DEBUG: painted nodes: ", id)
            
    im2.putdata(pix_val)

    # save temp texture
    path = "static/projects/" + GD.data["actPro"] + "/layoutsRGB/temp1.png"
    im2.save(path)
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



def paintNodes_event(message, room):
    if message["op"] == "ADD":
        for id in message["data"]:
            if id not in GD.paintedNodes:
                GD.paintedNodes.append(id)
    if message["op"] == "SUB":
        for id in message["data"]:
            try: 
                x = GD.paintedNodes.index(id)
                GD.paintedNodes.pop(x)
            except ValueError: found = False
    paintNodes_renderTexture(message, room)



def colorbox_nodePaint_event(message, room):
    GD.paintedNodesColor = (int(message["r"]),int(message["g"]),int(message["b"]),int(message["a"]*255))
    paintNodes_renderTexture(message, room)



def save_node_selection_event(message, room):
    
    response = {}
    response["usr"] = message["usr"]
    response["id"] = message["id"]
    response["fn"] = message["fn"]

    GD.pdata["nodeSelections2"] = {}
    GD.pdata["nodeSelections2"][message["val"]] = GD.paintedNodes
        
    print("C_DEBUG: saved node selection: ", message["val"], GD.pdata["nodeSelections2"][message["val"]])
                                                                      
    GD.savePD()
    emit("ex", response, room=room)




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
        


import os
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
        + GD.pfile["layoutsRGB"][int(GD.pdata["layoutsRGBDD"])]
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
    im2_nodes.save(path)
    im1_nodes.close()
    im2_nodes.close()

    # L I N K S
    im1_links = PIL.Image.open(
        "static/projects/"
        + GD.data["actPro"]
        + "/linksRGB/"
        + GD.pfile["linksRGB"][int(GD.pdata["linksRGBDD"])]
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
    im2_links.save(path)
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

