
import re
import GlobalData as GD

import flask
from flask_socketio import emit

all_projects_text = '\n'.join(GD.listProjects())

def action_open_project(project_name):
    
    # Check if project_name is provided
    if project_name is None or not project_name:
        # Project name not provided, return list of available projects
        return "Please specify the project name. Available projects: " + all_projects_text
    
    # Check if project exists in the list
    if project_name not in GD.listProjects():
        # Project not found, return list of available projects
        return "Project not found. Available projects: " + all_projects_text
    
    else:
        for proj in GD.listProjects():
            if project_name.lower() == proj.lower():
                #print("C_DEBUG: Project found: ", proj)
                
                GD.data["actPro"] = proj
              

                namespace = proj
                room = flask.session.get("room") 
                usr = flask.session.get("usr")

                print("C_DEBUG: namespace: ", namespace)
                print("C_DEBUG: room: ", room)

                response = {}
                response["val"] = proj
                response["fn"] = "project"

                emit("ex", response, usr = usr, room=room, namespace=namespace) 

                return f"Project {(proj)} opened successfully."
            else:
                return "No matching projects found. Please try again. \n Here is a list of all projects : "+ all_projects_text


def action_show_node_info():
    # Code to get all attributes of a node and its connections
    print("PROGRESS: Showing node information...")

def action_make_subnetwork():
    # Code to visualize a subnetwork of nodes with the selected node as the center
    print("PROGRESS: Making subnetwork...")
    
def action_create_vis():
    # Code to visualize the network based on certain criteria
    print("PROGRESS: Making visualization...")