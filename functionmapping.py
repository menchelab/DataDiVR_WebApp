import nltk
import re

# ------------------------------------------------
# import functions here
# ------------------------------------------------
from GlobalData import listProjects
from event_handler.execute_events.drop_down_events import trigger_change_project_to

# ------------------------------------------------
# Example functions for commands
# ------------------------------------------------
def function_XY():
    return "Function XY executed"

def function_AB(project_name=None):
    if project_name:
        return f"Function AB executed for project '{project_name}'"
    else:
        return "Function AB executed with no project specified"

def search_project(project_name):
    matching_projects = [project for project in listProjects() if project_name.lower() in project.lower()]
    if matching_projects:
        # open the project 
        trigger_change_project_to(project_name)

        return f"Matching project: {(project_name)}"
    else:
        return "No matching projects found."
    

# Mapping of command patterns to functions with a pattern and a function reference
command_to_function = {
    
    # dummy functions
    (r"calculate shortest path", r"find shortest path"): function_XY,
    (r"do XY", r"do AB(?: (.*))?"): function_AB,

    # project-related functions 
    (r"open project (.+)", r"search project (.+)"): search_project,
    (r"list all projects"): listProjects
    
}

def process_input(user_input):
    for patterns, func in command_to_function.items():
        for pattern in patterns:
            match = re.match(pattern, user_input, re.IGNORECASE)
            if match:
                if match.groups():
                    # Pass the matched groups as parameters to the function
                    result = func(*match.groups())
                else:
                    result = func()
                return result
    return "Command not recognized"


# Ensure you have the NLTK data required
nltk.download('punkt')

# Example usage
if __name__ == "__main__":
    user_input = "do XY"
    print(process_input(user_input))  # This will print "Function XY executed"
