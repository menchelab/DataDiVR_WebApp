
from flask_socketio import emit

import GlobalData as GD


def node_event(message, room):
    """
    Handles the node event to display detailed information about a specific node.

    This function updates the active node in the application state and emits a response
    containing the node's details. It is used to display node information in the UI panel.

    Args:
        message (dict): The message containing the node information.
            - "val" (str): The ID of the node to display.
            - "usr" (str): The user ID initiating the request.
        room (str): The room identifier for emitting the response.

    Emits:
        dict: A response containing the node's details, including:
            - "fn" (str): The function name ("node").
            - "id" (str): The ID of the node.
            - "nch" (int): The number of children of the node.
            - "val" (dict): The detailed information of the node.

    Example:
        Input:
            message = {"val": "5", "usr": "user123"}
        Output (Emitted):
            {
                "fn": "node",
                "id": "5",
                "nch": 3,
                "val": {
                    "id": 5,
                    "name": "Node 5",
                    "attributes": {...}
                }
            }

    Use Case:
        - Trigger this function when a user requests to display detailed information
          about a specific node in the application.
        - Example user input: "Show details for node 5."

    Notes:
        - Updates the `activeNode` in the `GD.pdata` state.
        - If the node contains protein information, additional fields like `protstyle`
          and `protnamedown` are updated in the application state.
        - Saves the updated state to persistent storage using `GD.savePD()`.
    """
    
    #  {'usr': 'DEFt2ZFbgw', 'msg': 'CDK4', 'id': None, 'val': '4240', 'fn': 'node'}

    response = {}

    response["val"] = {}
    response["fn"] = "node"

    response["id"] = message["val"]
    response["val"] = GD.nodes["nodes"][int(message["val"])]

    response["nch"] = len(GD.nchildren[int(message["val"])])
    
    GD.pdata["activeNode"] = message["val"]

    if "protein_info" in GD.nodes["nodes"][int(message["val"])]:
        if (
            not "protstyle" in GD.pdata.keys()
        ):  # check if selection exists in pdata.json
            GD.pdata["protstyle"] = ""
        GD.pdata["protstyle"] = list(
            GD.nodes["nodes"][int(message["val"])]["protein_info"][0].keys()
        )[1]

        if (
            not "protnamedown" in GD.pdata.keys()
        ):  # check if selection exists in pdata.json
            GD.pdata["protstyle"] = ""
        GD.pdata["protnamedown"] = GD.nodes["nodes"][int(message["val"])]["uniprot"][0]

        GD.savePD()

    emit("ex", response, room=room, namespace = "/main") # quick fix - adding namespace = "/main" to emit
