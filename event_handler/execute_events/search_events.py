

import json

from flask_socketio import emit
import search

from event_handler.execute_events.nodeinfo_events import node_event   


def search_event(message, room):
    """
    Searches for and displays information about a specific node in the network.

    This function takes a node ID or node name (e.g., "cdk2"), searches for the corresponding
    node information in the network, and emits the results to the frontend. If a node is found,
    additional details about the node are retrieved and displayed.

    Args:
        message (dict): The message containing the search query and metadata.
            - "usr" (str): The user ID initiating the search.
            - "val" (str): The search query string (e.g., "cdk2").
            - "id" (str): The event ID for the search operation.
        room (str): The room to which the search results should be emitted.

    Behavior:
        - Searches the network for nodes matching the query string in `message["val"]`.
        - Emits the search results to the frontend.
        - If a node is found, triggers the `node_event` function to retrieve and display
          additional details about the node.

    Emits:
        dict: A response containing the search results and metadata.
            - "id" (str): The event ID ("search").
            - "val" (list): The search results returned by the `search` module.
            - "fn" (str): The function name ("makeNodeButton").
            - "parent" (str): The parent element ID ("scrollbox2").

    Example:
        To search for a node named "cdk2" in the network:
        {
            "usr": "user123",
            "val": "cdk2",
            "id": "search"
        }

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