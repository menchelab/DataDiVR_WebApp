import flask
from flask_socketio import emit

import GlobalData as GD


# this file is necessary to recognize project change events and trigger appropriate actions when LUI is used
# project changes from dropdown are in dropdown_events.py still


def project_user_input(message, response, room=None, namespace="/main"):
    if room is None:
        room = flask.session.get("room")
    
    if message["id"] == "projDD":  # PROJECT CHANGE

        print("C_DEBUG - project change in dropdown_events.py")

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
        if message["id"] not in GD.pdata:
            GD.pdata[message["id"]] = ""
            print("newGD Variable created")

        GD.pdata[message["id"]] = message["val"]
        GD.savePD()


def project_main(message, room=None, namespace="/main"):
    """
    Main function to handle project-related commands and trigger appropriate actions.

    This function serves as the entry point for processing project-related user inputs, such as
    "change project to [project_name]" or "select project [project_name]" or "load project [project name]". 
    It determines whether the input is an initialization request or a user-triggered project change and delegates the
    task to the appropriate sub-function.

    Args:
        message (dict): A dictionary containing the user input details. Expected keys:
            - "usr" (str): The user ID.
            - "id" (str): The ID of the dropdown or project selector (e.g., "projDD").
            - "val" (str): The value associated with the input. For example:
                - "init": Indicates an initialization request.
                - Any other value: Indicates a user-triggered project change.
            - "msg" (str, optional): The name of the project to be loaded (for user-triggered inputs).
        room (str, optional): The room ID for socket communication. Defaults to the current session room.
        namespace (str, optional): The namespace for socket communication. Defaults to "/main".

    Returns:
        None: This function modifies the global state and emits responses via socket communication.

    Workflow:
        1. If "val" is "init", the `project_init` function is called to handle initialization.
        2. If "val" is any other value, the `project_user_input` function is called to handle user-triggered inputs.
        3. Emits the constructed response message to the appropriate room and namespace.

    Example:
        User Input Message:
        {
            "usr": "RxAoXw8rpx",
            "id": "projDD",
            "val": 10,
            "msg": "JSON_Zachary"
        }

        Emitted Response:
        {
            "usr": "RxAoXw8rpx",
            "id": "projDD",
            "fn": "dropdown",
            "parent": "projDD"
        }
    """
    if room is None:
        room = flask.session.get("room")
    response = {}
    response["usr"] = message["usr"]
    response["id"] = message["id"]
    response["fn"] = "dropdown"
    response["parent"] = message["id"]

    if "val" in message.keys():
        project_user_input(message, response, room, namespace)
    emit("ex", response, room=room, namespace=namespace)
   
    print(response)
