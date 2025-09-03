

import json

from flask_socketio import emit
import search

from event_handler.execute_events.nodeinfo_events import node_event   


def search_event(message, room):
    """
    Displays information about a specific node.
    This function takes a node ID or node name, searches for the corresponding node information,
    and prints the progress along with the retrieved information.

    Args:
        message (dict): The message containing the search query and metadata.
            - "usr" (str): The user ID initiating the search.
            - "val" (str): The search query string.
            - "id" (str): The event ID for the search operation.
        room (str): The room to which the search results should be emitted.

    Emits:
        dict: A response containing the search results and metadata.
            - "id" (str): The event ID ("search").
            - "val" (list): The search results returned by the `search` module.
            - "fn" (str): The function name ("makeNodeButton").
            - "parent" (str): The parent element ID ("scrollbox2").

    Returns:
        None
    """

    if len(message["val"]) > 1:
        x = '{"id": "search", "val":[], "fn": "makeNodeButton", "parent":"scrollbox2"}'
        results = json.loads(x)

        results["val"] = search.search_by_termtype(message["val"])

        emit("ex", results, room=room, namespace="/main") # quick fix - adding namespace = "/main" to emit


    # Trigger the node_event function if a node is found
    if results["val"]:  # Check if there are any search results
        first_node = results["val"][0]  # Get the first node from the results
        node_message = {
            "val": str(first_node["id"]),  # Use the node ID as input for node_event
            "usr": message["usr"]
        }
        print(f"C_DEBUG - Triggering node_event for node ID: {first_node['id']}")
        node_event(node_message, room)  # Trigger the node_event function