import flask
from flask_socketio import emit

import analytics
import enrichment_module
import GlobalData as GD
import layout_module

import VRrooms




def init(message, response, room=None, namespace="/main"):
    if room is None:
        room = flask.session.get("room")
    
    # VRrooms
    if message["id"] == "VRrooms":
        if "VRrooms" in GD.pdata.keys():
            newval = int(GD.pdata["VRrooms"])
            newname = VRrooms.VRROOMS_TABS[newval]
        else:   
            newval = 0
            newname = "Dome"
        response["opt"] = VRrooms.VRROOMS_TABS      
        response["sel"] = newval
        response["name"] = newname
        response["usr"] = message["usr"]

        
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
        # emit only to the requesting socket — broadcasting to room causes VR to reload
        # its project every time any other client (e.g. a web browser) connects
        emit("ex", response2, room=flask.request.sid, namespace=namespace)
    else:
        # serialized against the project-switch critical section and the
        # pdata write in user_input() below - without this, a request landing
        # mid-switch could read GD.pfile already swapped to the new project
        # but GD.pdata still holding the old project's values (or vice versa),
        # feeding a mismatched index into whatever gets pushed to Unreal (see
        # project_switch_lock's docstring in GlobalData.py)
        with GD.project_switch_lock:
            if message["id"] not in GD.pdata:
                GD.pdata[message["id"]] = 0
            response["sel"] = GD.pdata[message["id"]]
            # assign options for layout/color/link dropdowns, keeping the persisted
            # selection (GD.pdata) instead of forcing back to 0. init() runs on every
            # "dropdown"/init message, which fires on *every* socket (re)connect - not
            # just first project load - including SocketIO's automatic reconnect after
            # a refresh/network blip/server hiccup. Hardcoding 0 here snapped the
            # dropdown (and, for whichever client is bridged into a live Unreal Engine
            # pixel-streaming session, the actual running UE4 instance via the ue4()
            # broadcast at the end of the "dropdown" case) back to the first layout
            # every time, discarding whatever layout was actually active.
            if message["id"] == "layoutsDD":
                response["opt"] = GD.pfile["layouts"]
                response["sel"] = GD.safe_pdata_index(message["id"], GD.pfile["layouts"])
            elif message["id"] == "layoutsRGBDD":
                response["opt"] = GD.pfile["layoutsRGB"]
                response["sel"] = GD.safe_pdata_index(message["id"], GD.pfile["layoutsRGB"])
            elif message["id"] == "linksDD":
                response["opt"] = GD.pfile["links"]
                response["sel"] = GD.safe_pdata_index(message["id"], GD.pfile["links"])
            elif message["id"] == "linksRGBDD":
                response["opt"] = GD.pfile["linksRGB"]
                response["sel"] = GD.safe_pdata_index(message["id"], GD.pfile["linksRGB"])
            elif message["id"] == "selectionsDD":
                options = []
                for i in range(len(GD.pfile["selections"])):
                    options.append(GD.pfile["selections"][i]["name"])
                response["opt"] = options
                print(options)

            if "opt" in response.keys() and message["id"] not in ("layoutsDD", "layoutsRGBDD", "linksDD", "linksRGBDD"):
                response["sel"] = str(min(len(response["opt"]) - 1, int(response["sel"])))

    # dropdown for annotations
    if message["id"] == "annotation-1":
        response["opt"] = (
            list(GD.annotations.keys())
            if len(list(GD.annotations.keys())) > 0
            else ["-"]
        )
        response["sel"] = (
            0 if "annotation-1" not in GD.pdata.keys() else GD.pdata["annotation-1"]
        )
    if message["id"] == "annotation-2":
        response["opt"] = (
            list(GD.annotations.keys())
            if len(list(GD.annotations.keys())) > 0
            else ["-"]
        )
        response["sel"] = (
            0 if "annotation-2" not in GD.pdata.keys() else GD.pdata["annotation-2"]
        )
    if message["id"] == "annotation-Operations":
        response["opt"] = ["UNION", "INTERSECTION", "SUBTRACTION"]
        response["sel"] = (
            0
            if "annotation-Operations" not in GD.pdata.keys()
            else GD.pdata["annotation-Operations"]
        )


def user_input(message, response, room=None, namespace="/main"):
    if room is None:
        room = flask.session.get("room")
    
    # get which user changed
    #namespace = message["usr"]

    # clear analytics container
    if message["id"] == "analytics":
        # check if you actually switch
        if message["val"] != GD.pdata["analytics"]:
            response_clear = {}
            response_clear["fn"] = "analytics"
            response_clear["id"] = "clearAnalyticsContainer"
            response_clear["usr"] = message["usr"]
            emit("ex", response_clear, room=room, namespace=namespace)

    if message["id"] == "projDD":  # PROJECT CHANGE

        print("C_DEBUG - project change in dropdown_events.py: message : ", message)

        # serialized against the pdata write below - see project_switch_lock's
        # docstring in GlobalData.py for why this matters
        with GD.project_switch_lock:
            GD.data["actPro"] = GD.plist[int(message["val"])]
            GD.saveGD()
            GD.loadGD()
            GD.loadPFile()
            GD.loadPD()
            GD.loadColor()
            GD.loadLinks()
            GD.load_annotations()

        projectname = message["msg"]
        projectid = int(message["val"])

        response["sel"] = projectid #message["val"]
        response["name"] = projectname
        print("changed Project to " + str(GD.plist[int(message["val"])]))

        response2 = {}
        response2["usr"] = message["usr"]
        response2["val"] = GD.pfile
        response2["fn"] = "project"

        #emit("ex", response2, room=room, namespace=namespace)
        emit("ex", response2, room=room, namespace="/main")

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
            namespace=namespace,
        )
        # update not self updating elements

    else:
        response["sel"] = message["val"]
        response["name"] = message["msg"]

        # serialized against the project-switch critical section above - a
        # write landing between a switch's data["actPro"] reassignment and its
        # loadPD() would otherwise persist an old project's dropdown value
        # into the new project's pdata.json (see project_switch_lock's
        # docstring in GlobalData.py)
        with GD.project_switch_lock:
            if message["id"] not in GD.pdata:
                GD.pdata[message["id"]] = ""
                print("newGD Variable created")

            GD.pdata[message["id"]] = message["val"]

            # layout-family dropdowns are used later as list indices into the
            # matching pfile.json list (e.g. GD.pfile["layoutsRGB"][idx]) - clamp
            # here so a bad/stale value (out-of-sync forward/backward step, or a
            # value left over from before a project's layouts were reorganized)
            # can't get persisted and blow up an IndexError further down the line
            _pfile_key = {
                "layoutsDD": "layouts",
                "layoutsRGBDD": "layoutsRGB",
                "linksDD": "links",
                "linksRGBDD": "linksRGB",
            }.get(message["id"])
            if _pfile_key is not None:
                GD.safe_pdata_index(message["id"], GD.pfile.get(_pfile_key, []))

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
        emit("ex", response2, room=room, namespace=namespace)

    if message["id"] == "layoutModule":
        # check for layout switch
        # display rerun and save buttons
        response_layout_exists = {}
        response_layout_exists["usr"] = message["usr"]
        response_layout_exists["fn"] = "layout"
        response_layout_exists["id"] = "layoutExists"
        response_layout_exists["val"] = layout_module.check_layout_exists()
        emit("ex", response_layout_exists, room=room, namespace=namespace)


def main(message, room=None, namespace="/main"):

    if room is None:
        room = flask.session.get("room")
    response = {}
    response["usr"] = message["usr"]
    response["id"] = message["id"]
    response["fn"] = "dropdown"
    response["parent"] = message["id"]
    if "val" in message.keys():
        # init message called when socket connection is established
        if message["val"] == "init":
            init(message, response, room, namespace)
            # send init response only to the requesting socket, not the whole room
            # broadcasting init responses causes VR clients to receive other clients'
            # init sequences and reload their project unexpectedly
            emit("ex", response, room=flask.request.sid, namespace=namespace)
        else:  # user input message
            user_input(message, response, room, namespace)
            emit("ex", response, room=room, namespace=namespace)
    else:
        emit("ex", response, room=room, namespace=namespace)
   
    print(response)
