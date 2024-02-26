from flask_socketio import emit

import GlobalData as GD


def node_selections_event(message, room):
    if "selections" not in GD.pfile.keys():
        GD.pfile["selections"] = []
        GD.savePFile()
    if not GD.pfile["selections"]:
        print("CLIPBOARD: No selections available.")
        return
    activeSelIndex = int(GD.pdata["selectionsDD"])
    selectionNodes = GD.pfile["selections"][activeSelIndex]["nodes"]

    if not "cbnode" in GD.pdata.keys():
        GD.pdata["cbnode"] = []

    exists = False  # check if node already exists in clipboard
    for nodeID in selectionNodes:
        if int(nodeID) == int(GD.pdata["activeNode"]):
            exists = True
        if not exists:
            cbnode = {}
            try:  ### improve this, runs sometimes into issues when activeNode is not valid
                cbnode["id"] = int(nodeID)
                cbnode["color"] = GD.pixel_valuesc[int(nodeID)]
                cbnode["name"] = GD.nodes["nodes"][int(nodeID)]["n"]
                GD.pdata["cbnode"].append(cbnode)
                GD.savePD()
            except:
                print("Select node to copy to clipboard.")

    response = {
        "usr": message["usr"],
        "id": message["id"],
        "fn": "cbaddNode",
        "val": GD.pdata["cbnode"],
    }
    emit("ex", response, room=room)


def clear_event(message, room):
    # clear in backend
    GD.pdata["cbnode"] = []
    GD.savePD()
    # tell frontend to remove all buttons
    response = {
        "usr": message["usr"],
        "id": message["id"],
        "fn": "cbaddNode",
        "val": GD.pdata["cbnode"],
    }
    emit("ex", response, room=room)


def add_node_event(message, room):
    if not "cbnode" in GD.pdata.keys():  # check if selection exists in pdata.json
        GD.pdata["cbnode"] = []
    if message["val"] != "init":  # used for initialization for newly joined client
        # if not, create it
        exists = False  # check if node already exists in selection
        for n in GD.pdata["cbnode"]:
            if int(n["id"]) == int(GD.pdata["activeNode"]):
                exists = True
        if not exists:  # if not, add it
            cbnode = {}
            try:  ### improve this, runs sometimes into issues when activeNode is not valid
                cbnode["id"] = int(GD.pdata["activeNode"])
                cbnode["color"] = GD.pixel_valuesc[int(GD.pdata["activeNode"])]
                cbnode["name"] = GD.nodes["nodes"][int(GD.pdata["activeNode"])]["n"]
                GD.pdata["cbnode"].append(cbnode)
                GD.savePD()
            except:
                print("Select node to copy to clipboard.")
        else:
            print("already in selection")

    response = {
        "usr": message["usr"],
        "id": message["id"],
        "fn": "cbaddNode",
        "val": GD.pdata["cbnode"],
    }

    emit("ex", response, room=room)  # send to all clients
