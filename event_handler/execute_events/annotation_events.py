from flask_socketio import emit

import annotation
import GlobalData as GD


def annotation_operation_event(message, room):
    if message["val"] == "init":
        if "annotationOperationsActive" not in GD.pdata.keys():
            GD.pdata["annotationOperationsActive"] = False
    else:
        if "annotationOperationsActive" in GD.pdata.keys():
            if GD.pdata["annotationOperationsActive"] == True:
                GD.pdata["annotationOperationsActive"] = False
            elif GD.pdata["annotationOperationsActive"] == False:
                GD.pdata["annotationOperationsActive"] = True
            if "annotationOperationsActive" not in GD.pdata.keys():
                GD.pdata["annotationOperationsActive"] = True
    response = {}
    response["usr"] = message["usr"]
    response["id"] = message["id"]
    response["fn"] = "annotation"
    response["val"] = GD.pdata["annotationOperationsActive"]
    GD.savePD()
    emit("ex", response, room=room)


def annotation_run_event(message, room):
    if message["val"] == "init":
        return
    if (
        "annotation_1" not in GD.pdata.keys() or GD.pdata["annotation_1"] == "-"
    ):  # at least annotation 1 should be set
        print("ERROR: Select Annotation 1 to perform set operation on annotations.")
        return
    if "annotation-Operations" not in GD.pdata.keys():
        print("ERROR: Select operation to perform set operation on annotations.")
        return
    if "annotation_2" not in GD.pdata.keys():
        print("ERROR: Select Annotation 2 to perform set operation on annotations.")
        return
    if "annotation_type_1" not in GD.pdata.keys():
        print("ERROR: Select Annotation 1 to perform set operation on annotations.")
        return
    if "annotation_type_2" not in GD.pdata.keys():
        print("ERROR: Select Annotation 2 to perform set operation on annotations.")
        return

    annotation_1 = GD.pdata["annotation_1"]
    annotation_2 = GD.pdata["annotation_2"]
    type_1 = GD.pdata["annotation_type_1"]
    type_2 = GD.pdata["annotation_type_2"]
    operations = ["union", "intersection", "subtraction"]
    operation = operations[int(GD.pdata["annotation-Operations"])]

    if "annotationOperationsActive" in GD.pdata.keys():
        # color only one type of annotation
        if GD.pdata["annotationOperationsActive"] is False:
            operation = "single"

    annotation_texture = annotation.AnnotationTextures(
        project=GD.data["actPro"],
        nodes=GD.nodes["nodes"],
        links=GD.links["links"],
        annotations=GD.annotations,
    )
    generated_annotation_textures = annotation_texture.gen_textures(
        annotation_1=annotation_1,
        annotation_2=annotation_2,
        type_1=type_1,
        type_2=type_2,
        operation=operation,
    )

    if generated_annotation_textures["generated_texture"] is False:
        print("Failed to create textures for Annotation")
        return
    response = {}
    response["usr"] = message["usr"]
    response["fn"] = "updateTempTex"
    response["textures"] = []
    response["textures"].append(
        {
            "channel": "nodeRGB",
            "path": generated_annotation_textures["path_nodes"],
        }
    )
    response["textures"].append(
        {
            "channel": "linkRGB",
            "path": generated_annotation_textures["path_links"],
        }
    )
    emit("ex", response, room=room)


def annotation_clipboard_event(message, room):
    if "annotationOperationsActive" not in GD.pdata.keys():
        GD.pdata["annotationOperationsActive"] = False

    # single annotation case
    if GD.pdata["annotationOperationsActive"] is False:
        if "annotation_1" not in GD.pdata.keys():
            print("ERROR: Select Annotation 1 to clipboard annotations.")
            return
        if "annotation_type_1" not in GD.pdata.keys():
            print("ERROR: Select Annotation 1 to clipboard annotations.")
            return
        selectionNodes = GD.annotations[GD.pdata["annotation_type_1"]][
            GD.pdata["annotation_1"]
        ]

    # result case
    else:
        if "annotation-Operations" not in GD.pdata.keys():
            print("ERROR: Select operation to clipboard annotations.")
            return
        if "annotation_1" not in GD.pdata.keys():
            print("ERROR: Select Annotation 1 to clipboard annotations.")
            return
        if "annotation_2" not in GD.pdata.keys():
            print("ERROR: Select Annotation 2 to clipboard annotations.")
            return
        if "annotation_type_1" not in GD.pdata.keys():
            print("ERROR: Select Annotation 1 to perform set operation on annotations.")
            return
        if "annotation_type_2" not in GD.pdata.keys():
            print("ERROR: Select Annotation 2 to perform set operation on annotations.")
            return
        operations = ["union", "intersection", "subtraction"]
        selectionNodes = annotation.get_annotation_operation_clipboard(
            annotation_1=GD.pdata["annotation_1"],
            annotation_2=GD.pdata["annotation_2"],
            type_1=GD.pdata["annotation_type_1"],
            type_2=GD.pdata["annotation_type_2"],
            operation=operations[int(GD.pdata["annotation-Operations"])],
        )

    if not "cbnode" in GD.pdata.keys():
        GD.pdata["cbnode"] = []

    for nodeID in selectionNodes:
        exists = False  # check if node already exists in clipboard
        if int(nodeID) == int(GD.pdata["activeNode"]):
            exists = True
            continue

        for cbnode in GD.pdata["cbnode"]:
            if int(nodeID) == int(cbnode["id"]):
                exists = True
                break

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

    response = {}
    response["usr"] = message["usr"]
    response["id"] = message["id"]
    response["fn"] = "cbaddNode"
    response["val"] = GD.pdata["cbnode"]
    emit("ex", response, room=room)


def annoation_dd_event(message, room):
    if message["id"] == "annotationInit":
        emit(
            "ex",
            {"fn": "annotationDD", "id": "initDD", "options": GD.annotation_types},
        )
        return

    # some useful variables
    id_GD_key_type = (
        "annotation_type_1"
        if message["id"] == "annotation-dd-1"
        else "annotation_type_2"
    )
    id_GD_key = "annotation_1" if message["id"] == "annotation-dd-1" else "annotation_2"

    response = {}
    response["usr"] = message["usr"]
    response["fn"] = message["fn"]
    response["id"] = message["id"]

    if message["val"] == "init":
        # on init

        #####
        # implement them as case where to ignore on annotation analytics
        #####
        anno = "Select Annotation"
        anno_type = "-"

        if id_GD_key in GD.pdata.keys():
            anno = GD.pdata[id_GD_key]
        else:
            GD.pdata[id_GD_key] = anno
        if id_GD_key_type in GD.pdata.keys():
            anno_type = GD.pdata[id_GD_key_type]
        else:
            GD.pdata[id_GD_key_type] = anno_type

        response["val"] = "initDD"
        response["valAnnotation"] = anno
        response["valType"] = anno_type
        emit("ex", response, room=room)
        GD.savePD()
        return

    if message["val"] == "clickBack":
        dd_state = message["state"]
        if dd_state == "selType":
            # from type selection to inactive
            response["val"] = "close"
            emit("ex", response, room=room)
            return

        elif dd_state == "selSub":
            # from sub selection to type selection
            # "annotationTypes" check to differentiate on which annotation format your'e working
            # close directly for list type annotations
            if GD.pfile["annotationTypes"] is True:
                response["val"] = "openType"
                response["valOptions"] = GD.annotation_types
                emit("ex", response, room=room)
            else:
                response["val"] = "close"
                emit("ex", response, room=room)
            return

        elif dd_state == "selMain":
            # from main annotation selection to sub selection
            # check here if too less annotations to show subs based on DD_AVOID_SUB_LIMIT from annotation.py
            if len(GD.annotations[GD.pdata[id_GD_key_type]].items()) <= len(
                annotation.DD_SUB_OPTIONS.items()
            ):
                response["val"] = "close"
                emit("ex", response, room=room)
            else:
                response["val"] = "openSub"
                response["valSelected"] = GD.pdata[id_GD_key_type]
                response["valOptions"] = annotation.get_sub_options_dd(
                    GD.pdata[id_GD_key_type]
                )
                emit("ex", response, room=room)
            return

        else:
            response["val"] = "close"
            emit("ex", response, room=room)
            print("ERROR: This should not happen: ", message)
            return

    if message["val"] == "clickHeader":
        dd_state = message["state"]
        if dd_state == "inactive":
            # clicked on it to activate the dropdown and open type selection
            # or annotation selection for GD.pfile["annotationTypes"] is false
            if GD.pfile["annotationTypes"] is True:
                # handle complex annotations
                response["val"] = "openType"
                response["valOptions"] = GD.annotation_types
                emit("ex", response, room=room)
                return
            else:
                # handle basic annotations by setting default as type directly and pulling sub for default
                GD.pdata[id_GD_key_type] = "default"
                GD.savePD()
                emit(
                    "ex",
                    {
                        "usr": message["usr"],
                        "fn": message["fn"],
                        "id": message["id"],
                        "val": "setTypeDisplay",
                        "valType": GD.pdata[id_GD_key_type],
                    },
                    room=room,
                )
                # check here if too less annotations to show subs based on DD_AVOID_SUB_LIMIT from annotation.py
                if len(GD.annotations[GD.pdata[id_GD_key_type]].items()) <= len(
                    annotation.DD_SUB_OPTIONS.items()
                ):
                    response["valOptions"] = annotation.get_main_options_dd(
                        GD.pdata[id_GD_key_type], None
                    )
                    response["valSelected"] = GD.pdata[id_GD_key_type]
                    response["val"] = "openMain"
                    emit("ex", response, room=room)
                    return
                response["valOptions"] = annotation.get_sub_options_dd(
                    GD.pdata[id_GD_key_type]
                )
                response["valSelected"] = GD.pdata[id_GD_key_type]
                response["val"] = "openSub"
                emit("ex", response, room=room)
                return

        else:
            # clicked on it to shut off dropdown and close it
            response["val"] = "close"
            emit("ex", response, room=room)
            return

    if message["val"] == "clickOptionType":
        # save type in pdata
        GD.pdata[id_GD_key_type] = message["option"]
        GD.savePD()
        emit(
            "ex",
            {
                "usr": message["usr"],
                "fn": message["fn"],
                "id": message["id"],
                "val": "setTypeDisplay",
                "valType": GD.pdata[id_GD_key_type],
            },
            room=room,
        )

        # check here if too less annotations to show subs based on DD_AVOID_SUB_LIMIT from annotation.py
        if len(GD.annotations[GD.pdata[id_GD_key_type]].items()) <= len(
            annotation.DD_SUB_OPTIONS.items()
        ):
            response["valOptions"] = annotation.get_main_options_dd(
                GD.pdata[id_GD_key_type], None
            )
            response["valSelected"] = GD.pdata[id_GD_key_type]
            response["val"] = "openMain"
            emit("ex", response, room=room)
            return
        # case amount of annotations is sufficient large that you want to have sub level options
        response["valOptions"] = annotation.get_sub_options_dd(GD.pdata[id_GD_key_type])
        response["valSelected"] = GD.pdata[id_GD_key_type]
        response["val"] = "openSub"
        emit("ex", response, room=room)
        return

    if message["val"] == "clickOptionSub":
        # no benefit from saving sub in backend
        response["valOptions"] = annotation.get_main_options_dd(
            GD.pdata[id_GD_key_type], message["option"]
        )
        response["valSelected"] = message["option"]
        response["val"] = "openMain"
        emit("ex", response, room=room)
        return

    if message["val"] == "clickOptionAnnotation":
        GD.pdata[id_GD_key] = message["option"]
        response["valSelected"] = GD.pdata[id_GD_key]
        response["val"] = "annotationSelected"
        emit("ex", response, room=room)
        GD.savePD()
        return
