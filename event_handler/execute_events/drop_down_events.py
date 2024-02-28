from flask_socketio import emit

import analytics
import enrichment_module
import GlobalData as GD
import layout_module


def main(message, room):
    response = {}
    response["usr"] = message["usr"]
    response["id"] = message["id"]
    response["fn"] = "dropdown"
    response["parent"] = message["id"]

    if "val" in message.keys():
        # init message called when socket connection is established
        if message["val"] == "init":
            # C A R T O G R A P H S
            # dropdown for layout type selection
            layout_selected = 0
            if message["id"] == "CGlayouts":
                response["opt"] = [
                    "Local layout",
                    "Global layout",
                    "Importance layout",
                ]
                response["sel"] = layout_selected

            # dropdown for fixed selections
            if message["id"] == "analytics":
                response["opt"] = analytics.ANALYTICS_TABS
                response["sel"] = "0"

            if message["id"] == "layoutModule":
                response["opt"] = layout_module.LAYOUT_TABS
                response["sel"] = "0"

            if message["id"] == "enrichment-cutoff":
                response["opt"] = enrichment_module.ALPHA_VALUES
                response["sel"] = 0

            if message["id"] == "enrichment-features":
                response["opt"] = GD.annotation_types
                response["sel"] = 0

            # dropdown for visualization type selection
            vis_selected = 0
            if message["id"] == "CGvis":
                response["opt"] = [
                    "2D Portrait",
                    "3D Portrait",
                    "Topographic",
                    "Geodesic",
                ]
                response["sel"] = vis_selected

            elif message["id"] == "projDD":
                response["opt"] = GD.plist
                response["sel"] = GD.plist.index(GD.data["actPro"])

                response2 = {}
                response2["usr"] = message["usr"]
                if not "nodecount" in GD.pfile:
                    GD.pfile["nodecount"] = len(GD.nodes["nodes"])
                    GD.pfile["labelcount"] = 0
                    GD.pfile["linkcount"] = len(GD.links["links"])
                    GD.savePFile()

                response2["val"] = GD.pfile
                response2["fn"] = "project"
                emit("ex", response2, room=room)
            else:
                if message["id"] not in GD.pdata:
                    GD.pdata[message["id"]] = 0
                response["sel"] = GD.pdata[message["id"]]
                # assign data for options
                if message["id"] == "layoutsDD":
                    response["opt"] = GD.pfile["layouts"]
                elif message["id"] == "layoutsRGBDD":
                    response["opt"] = GD.pfile["layoutsRGB"]
                elif message["id"] == "linksDD":
                    response["opt"] = GD.pfile["links"]
                elif message["id"] == "linksRGBDD":
                    response["opt"] = GD.pfile["linksRGB"]
                elif message["id"] == "selectionsDD":
                    options = []
                    for i in range(len(GD.pfile["selections"])):
                        options.append(GD.pfile["selections"][i]["name"])
                    response["opt"] = options
                    print(options)

                if "opt" in response.keys():
                    # dirty fix that sel of pdata layoutsDD is somwhow always = 2
                    response["sel"] = str(
                        min(len(response["opt"]) - 1, int(response["sel"]))
                    )

            # dropdown for annotations
            if message["id"] == "annotation-1":
                response["opt"] = (
                    list(GD.annotations.keys())
                    if len(list(GD.annotations.keys())) > 0
                    else ["-"]
                )
                response["sel"] = (
                    0
                    if "annotation-1" not in GD.pdata.keys()
                    else GD.pdata["annotation-1"]
                )
            if message["id"] == "annotation-2":
                response["opt"] = (
                    list(GD.annotations.keys())
                    if len(list(GD.annotations.keys())) > 0
                    else ["-"]
                )
                response["sel"] = (
                    0
                    if "annotation-2" not in GD.pdata.keys()
                    else GD.pdata["annotation-2"]
                )
            if message["id"] == "annotation-Operations":
                response["opt"] = ["UNION", "INTERSECTION", "SUBTRACTION"]
                response["sel"] = (
                    0
                    if "annotation-Operations" not in GD.pdata.keys()
                    else GD.pdata["annotation-Operations"]
                )

        else:  # user input message
            # clear analytics container
            if message["id"] == "analytics":
                # check if you actually switch
                if message["val"] != GD.pdata["analytics"]:
                    response_clear = {}
                    response_clear["fn"] = "analytics"
                    response_clear["id"] = "clearAnalyticsContainer"
                    response_clear["usr"] = message["usr"]
                    emit("ex", response_clear, room=room)

            if message["id"] == "projDD":  # PROJECT CHANGE
                GD.data["actPro"] = GD.plist[int(message["val"])]
                GD.saveGD()
                GD.loadGD()
                GD.loadPFile()
                GD.loadPD()
                GD.loadColor()
                GD.loadLinks()
                GD.load_annotations()

                response["sel"] = message["val"]
                response["name"] = message["msg"]
                print("changed Project to " + str(GD.plist[int(message["val"])]))

                response2 = {}
                response2["usr"] = message["usr"]
                response2["val"] = GD.pfile
                response2["fn"] = "project"
                emit("ex", response2, room=room)

                # display rerun and save buttons for layout module
                emit(
                    "ex",
                    {
                        "usr": message["usr"],
                        "fn": "layout",
                        "id": "layoutExists",
                        "val": False,
                    },
                    room=room,
                )
                # update not self updating elements

            else:
                response["sel"] = message["val"]
                response["name"] = message["msg"]
                if message["id"] not in GD.pdata:
                    GD.pdata[message["id"]] = ""
                    print("newGD Variable created")

                GD.pdata[message["id"]] = message["val"]
                GD.savePD()

            if message["id"] == "selectionsDD":
                # print(GD.pfile["selections"][int(message["val"])]["nodes"])
                response2 = {}
                response2["usr"] = message["usr"]
                response2["id"] = message["id"]
                response2["parent"] = "scrollbox1"
                response2["fn"] = "makeNodeButton"
                response2["val"] = []
                ids = GD.pfile["selections"][int(message["val"])]["nodes"]
                for d in ids:
                    node = {}
                    node["name"] = GD.nodes["nodes"][int(d)]["n"]
                    node["color"] = GD.pixel_valuesc[int(d)]
                    node["id"] = d
                    response2["val"].append(node)
                emit("ex", response2, room=room)

            if message["id"] == "layoutModule":
                # check for layout switch
                # display rerun and save buttons
                response_layout_exists = {}
                response_layout_exists["usr"] = message["usr"]
                response_layout_exists["fn"] = "layout"
                response_layout_exists["id"] = "layoutExists"
                response_layout_exists["val"] = layout_module.check_layout_exists()
                emit("ex", response_layout_exists, room=room)
    emit("ex", response, room=room)
    print(response)
