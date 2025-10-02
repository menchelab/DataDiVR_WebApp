

# contains helper functions for language interface

import json
import GlobalData as GD
import os 



def load_project_info():
    """
    Loads the current project's information from the pfile.json file and adds all available projects to memory.

    Returns:
        dict: A dictionary containing the current project's name and description.
    """

    print("C_DEBUG: Loading projects and project info...")

    try:
        # Load the current active project
        project_name = GD.data["actPro"]
        print(f"C_DEBUG: Current active project: {project_name}")

        project_file_path = os.path.abspath(f"static/projects/{project_name}/pfile.json")

        # Load all available projects into memory
        projects_dir = os.path.abspath("static/projects")
        if os.path.exists(projects_dir):
            all_projects = [
                project for project in os.listdir(projects_dir)
                if os.path.isdir(os.path.join(projects_dir, project))
            ]
            GD.plist = all_projects  # Store all projects in memory
            print(f"C_DEBUG: All available projects loaded into memory: {all_projects}")
        else:
            print(f"C_DEBUG: Projects directory not found: {projects_dir}")
            GD.plist = []

        # Load the current project's information
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



# NOT USED 
# def show_all_projects():
#     """
#     Retrieves and displays a list of all available projects.

#     This function fetches the list of available projects from the global `GD.plist` variable,
#     which is expected to contain the names of all projects. It formats the project names into
#     a user-friendly string and returns it as part of a structured response. If an error occurs
#     during retrieval, it logs the error and returns an empty list.

#     Returns:
#         dict: A structured response containing:
#             - "type" (str): The type of the response, set to "general_query".
#             - "query" (str): The query that triggered this function, set to "show all projects".
#             - "feedback" (str): A user-friendly string listing all available projects.
#         If an error occurs, an empty list is returned instead.

#     Notes:
#         - The `GD.plist` variable must be pre-populated with the list of project names.
#         - This function is designed to be used in contexts where a structured response is required,
#           such as routing user queries or generating feedback for a UI.

#     Example:
#         response = show_all_projects()
#         print(response["feedback"])
#         # Output: "Available projects: Project1, Project2, Project3"

#     Error Handling:
#         - If an exception occurs (e.g., `GD.plist` is not defined), the function logs the error
#           and returns an empty list.
#     """
#     try:
#         all_projects = GD.plist
#         print(f"C_DEBUG: Available projects: {all_projects}")
#         return {
#             "type": "general_query",
#             "query": "show all projects",
#             "feedback": "Available projects : " + ", ".join(all_projects),
#         }
#     except Exception as e:
#         print(f"C_DEBUG: Error retrieving projects: {e}")
#         return []   