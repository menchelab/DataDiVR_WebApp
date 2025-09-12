

# contains helper functions for language interface

import json
import GlobalData as GD
import os 



def load_project_info():
    """
    Loads the current project's information from the pfile.json file.

    Returns:
        dict: A dictionary containing the project's name and description.
    """

    print("C_DEBUG: Loading project info...")

    try:
        project_name = GD.data["actPro"]
        print(f"C_DEBUG: Current active project: {project_name}")

        project_file_path = os.path.abspath(f"static/projects/{project_name}/pfile.json")

        if os.path.exists(project_file_path):
            with open(project_file_path, "r") as file:
                project_data = json.load(file)
                project_info = project_data.get("info", "No description available.")
                print(f"C_DEBUG: Loaded project info: {project_info}")
                return {"name": project_name, "info": project_info}
        else:
            print(f"C_DEBUG: Project file not found: {project_file_path}")
            return {"name": project_name, "info": "No description available."}
    except Exception as e:
        print(f"C_DEBUG: Error loading project info: {e}")
        return {"name": "Unknown Project", "info": "Error retrieving project information."}
    



def show_all_projects():
    """
    Retrieves a list of all available projects from the static/projects directory.

    Returns:
        list: A list of project names.
    """
    try:
        all_projects = GD.plist
        print(f"C_DEBUG: Available projects: {all_projects}")
        return {
            "type": "general_query",
            "query": "show all projects",
            "feedback": "Available projects : " + ", ".join(all_projects),
        }
    except Exception as e:
        print(f"C_DEBUG: Error retrieving projects: {e}")
        return []   