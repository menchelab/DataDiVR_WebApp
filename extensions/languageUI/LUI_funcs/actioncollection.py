
import re
import GlobalData as GD

import flask
from flask_socketio import emit


from event_handler.execute_events.drop_down_events import main

def action_list_all_projects():
    """
    Lists all the projects available in the system.
    This function retrieves the list of all projects and returns them as a string.
    Args:
        None
    Returns:
        str: A string containing the names of all projects available in the system.
    """
    all_projects_text = ' , '.join(GD.listProjects())
    
    return f"Project not found. Please choose from list of projects: {all_projects_text}"



def action_open_project(projectname):

    projectname_lower = projectname.lower()
    matching_projects = [proj for proj in GD.listProjects() if proj.lower() == projectname_lower]

    if not matching_projects:
        print(f"ERROR: Project '{projectname}' not found.")
        return action_list_all_projects()

    projectname = matching_projects[0]

    sel_id = GD.listProjects().index(projectname)
    sel_name = GD.listProjects()[sel_id]

    main({
        'usr': flask.session.get("username") or "backend",
        'id': 'projDD',
        'fn': 'dropdown',
        'msg': sel_name,
        'val': sel_id
    })

    return f"Project '{projectname}' loaded successfully."





from search import search
def action_show_node_info(nodeid):
    """
    Displays information about a specific node.
    This function takes a node ID or node name, searches for the corresponding node information,
    and prints the progress along with the retrieved information.
    Args:
        node_id (int or str): The ID of the node to be searched.
    Returns:
        None
    """

    # test for nodeid
    if not nodeid:
        # If nodeid is empty, return an error message
        return "ERROR: Please provide a node ID to retrieve information."
    
    # search function in search.py
    response = search(str(nodeid))
    print("PROGRESS: Showing node information... : ", response)
    return f"Node {nodeid} information: {response}"  # Return the response for further use



def action_make_subnetwork(nodeid):
    """
    Visualize a subnetwork of nodes with the selected node as the center.

    Args:
        node_id (int): The ID of the node to be used as the center of the subnetwork.

    Returns:
        None
    """
    # Code to visualize a subnetwork of nodes with the selected node as the center
    print("PROGRESS: Making subnetwork...")
    return f"Subnetwork created with node {nodeid} at the center."
