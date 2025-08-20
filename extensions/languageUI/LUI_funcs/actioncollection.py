
import re
import GlobalData as GD
import flask

from event_handler.execute_events.drop_down_events import main
from event_handler.execute_events.universal_events import * 
#from flask_socketio import emit


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

    # return all projects, each in a new line
    if all_projects_text:
        return f"Available projects: {all_projects_text}"
    
    # if no projects are available, return an error message
    if not all_projects_text:
        all_projects_text = "No projects available. Please create a project first."
        return f"Project not found. Please choose from list of projects: {all_projects_text}"



def action_open_project(projectname):
    """
    Opens a project by its name and loads it into the application.
    This function searches for a project with the specified name (case-insensitive)
    in the list of available projects. If the project is found, it loads the project
    and updates the application state accordingly. If the project is not found, it
    prints an error message and lists all available projects.
    Args:
        projectname (str): The name of the project to open.
    Returns:
        str: A success message indicating the project was loaded, or a list of all
             available projects if the specified project was not found.
    """

    projectname_lower = projectname.lower()
    matching_projects = [proj for proj in GD.listProjects() if proj.lower() == projectname_lower]

    if not matching_projects:
        print(f"ERROR: Project '{projectname}' not found.")
        return action_list_all_projects()

    projectname = matching_projects[0]

    sel_id = GD.listProjects().index(projectname)
    sel_name = GD.listProjects()[sel_id]

    # construct the message dictionary
    message = {
        'usr': flask.session.get("username") or "backend",
        'id': 'projDD',
        'fn': 'dropdown',
        'parent': 'projDD',
        'val': sel_id,
        'msg': sel_name
    }

    return message #f"Project '{projectname}' loaded successfully."



from search import search
from search import search_by_termtype
def action_show_node_info(node_id):
    """
    Displays information about a specific node.
    This function takes a node ID or node name, searches for the corresponding node information,
    and prints the progress along with the retrieved information.
    Args:
        node_id (int or str): The ID of the node to be searched.
    Returns:
        None
    """

    print("C_DEBUG: in action_show_node_info:", node_id)

    if not node_id:
        # If nodeid is empty, return an error message
        return "ERROR: Please provide a node ID to retrieve information."
    
    termtype = type(node_id)
    print("C_DEBUG: Node:", node_id)
    if termtype == int:
        print("C_DEBUG: Node ID is an integer.")
    elif termtype == str:
        print("C_DEBUG: Node ID is a string.")
    else:
        print("C_DEBUG: Node ID is of an unknown type.", type(node_id))

    response = search_by_termtype(termtype, node_id) #response = search(str(nodeid))

    # message = {
    #     'usr': flask.session.get("username") or "backend",
    #     'id': 'search', 
    #     'parent': 'scrollbox2', 
    #     'fn': 'search', 
    #     'val': node_id
    # }

    return response



def action_make_subnetwork(nodeid):
    """
    Visualize a subnetwork of nodes with the selected node as the center.
    Args:
        nodeid (int): The ID of the node to be used as the center of the subnetwork.
    Returns:
        None
    """

    print("C_DEBUG:in action_make_subnetwork:", nodeid)


    # Construct the message dictionary
    message = {
        'usr': flask.session.get("username") or "backend",
        'id': 'plotly2jsB',
        'fn': 'Plotly2js',
        'msg': 'Graph',
        'parent': 'plotly2js',
        'val': nodeid,
    }

    # Define the room (adjust as needed for your application)
    room = flask.session["room"]


    print("C_DEBUG: room:", room)
    print("C_DEBUG: message:", message)


    # Trigger the plot_to_js_event function
    plot_to_js_event(message, room)

    

    print("PROGRESS: Making subnetwork...")
    return f"Subnetwork created with node {nodeid} at the center."

