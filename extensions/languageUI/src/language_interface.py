import openai
import os
from openai import OpenAI
from dotenv import load_dotenv
import json 
import inspect
import importlib



# API / Model keys - Load .env and init OpenAI
load_dotenv()

# Read the API key from the text file
with open("extensions\\languageUI\\LUI_funcs\\token_doNOTcommit.txt", "r") as key_file:
    api_key = key_file.read().strip()

# Assign the API key to OpenAI
openai.api_key = api_key

# Initialize the OpenAI client (if needed)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)


# ----------------------------------------
# Register all action_* functions
# ----------------------------------------


# automaticall discover python files in a directory and register their action_* functions
def get_action_registry_from_directory(directory, package_prefix):
    """
    Dynamically load all action_* functions from Python files in a directory.
    """
    registry = {}
    for filename in os.listdir(directory):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"{package_prefix}.{filename[:-3]}"  # Remove .py extension
            module = importlib.import_module(module_name)
            
            # Inspect the module for functions starting with "action_"
            for name, func in inspect.getmembers(module, inspect.isfunction):
                if name.startswith("action_"):
                    doc = func.__doc__ or "No description."
                    registry[name] = {
                        "function": func,
                        "doc": doc.strip()
                    }
    return registry


def get_action_registry_from_files(module_names):
    """
    Dynamically load all action_* functions from a list of module names.
    """
    registry = {}
    for module_name in module_names:
        # Dynamically import the module
        module = importlib.import_module(module_name)
        
        # Inspect the module for functions starting with "action_"
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if name.startswith("action_"):
                doc = func.__doc__ or "No description."
                registry[name] = {
                    "function": func,
                    "doc": doc.strip()
                }
    return registry




def get_action_registry_from_DataDiVR():
    """
    Dynamically load all functions with docstrings from Python files in the DataDiVR_WebApp/event_handler/execute_events folder.
    This function inspects all .py files in the specified folder and registers only functions that have docstrings.
    
    Returns:
        dict: A dictionary mapping function names to their corresponding functions, documentation, and file paths.
    """
    import inspect
    import os
    import sys

    # Define the absolute path to the event_handler/execute_events folder
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current file
    project_root = os.path.abspath(os.path.join(base_dir, "..", "..", ".."))  # Adjust to point to the root of the project
    directory = os.path.join(project_root, "event_handler", "execute_events")
    
    registry = {}

    # Debugging: Print the constructed directory path
    print(f"Scanning directory: {directory}")

    # Add the project root to sys.path if not already present
    if project_root not in sys.path:
        sys.path.append(project_root)

    # Iterate through all Python files in the target directory
    try:
        for file in os.listdir(directory):
            if file.endswith(".py"):  # Include all .py files
                file_path = os.path.join(directory, file)
                module_name = file[:-3]  # Remove the .py extension

                try:
                    # Open the file and execute its content in a temporary namespace
                    namespace = {}
                    with open(file_path, "r") as f:
                        exec(f.read(), namespace)

                    # Inspect the namespace for all functions
                    for name, func in namespace.items():
                        if inspect.isfunction(func) and func.__doc__:  # Only register functions with docstrings
                            registry[name] = {
                                "function": func,
                                "doc": func.__doc__.strip(),
                                "file_path": file_path  # Add the file path to the registry
                            }
                except Exception as e:
                    print(f"Error processing file {file}: {e}")
    except FileNotFoundError as e:
        print(f"Error: Directory not found - {directory}")
        return {}

    # Print the resulting registry
    print("Registered functions:")
    for func_name, meta in registry.items():
        print(f"- {func_name}: {meta['file_path']}")
    
    return registry




# ==================================================================================================================

# TO DO - LINK EXISTING FUNCTIONS FROM PLATFORM 
# check output of functions and match current "action_..." functions 
# doc strings to all platform functions 

#registry1 = get_action_registry_from_directory("extensions/languageUI/LUI_funcs", "extensions.languageUI.LUI_funcs")
registry_VR = get_action_registry_from_DataDiVR()
ACTION_REGISTRY = {**registry_VR} #, **registry2}

# ==================================================================================================================






# ----------------------------------------
# Use LLM to match input to a function
# ----------------------------------------

# Build a system prompt for the LLM based on the action registry
# This prompt will be used to instruct the LLM to map user input to a specific function
# and its arguments.
def build_system_prompt(registry):


    print("C_DEBUG - LANGUAGE_INTERFACE.PY - build_system_prompt..")#, registry)


    lines = []
    for fname, meta in registry.items():
        lines.append(f"- `{fname}(...)`: {meta['doc']}")
    return (
        "You're a smart router. Based on a user request, map it to one of the following Python functions:\n"
        + "\n".join(lines) +
        "\nReturn ONLY a JSON object like:\n"
        '{"function": "action_show_node_info", "args": {"node_id": 5}}'
    )




# Route the user input to the appropriate function using the LLM
# This function sends the user input to the LLM, which will return a JSON object
# containing the function name and its arguments.
def route_command(user_input: str) -> dict:


    print("C_DEBUG - LANGUAGE_INTERFACE.PY - route_command:", user_input)


    system_prompt = build_system_prompt(ACTION_REGISTRY)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",  # or gpt-3.5-turbo
            messages=messages,
            temperature=0.5,
            max_tokens=500
        )
        parsed = json.loads(response.choices[0].message.content.strip())
        parsed["type"] = "action"
        print("C_DEBUG - LANGUAGE_INTERFACE.PY - Parsed command TYPE ACTION:", parsed)
        return parsed
    
    except Exception as e:
        print("C_DEBUG - LANGUAGE_INTERFACE.PY - Error in route_command GENERAL QUERY :", str(e))
        return {
            "type": "general_query",
            "query": user_input,
            "error": str(e)
        }



# ----------------------------------------
# Dispatcher
# ----------------------------------------
# This function takes the routed command and executes the corresponding action.
def handle_routed_command(command: dict):
    """
    Handles the routed command by creating a structured message instead of directly calling the function.
    The message structure is based on the matched function and its arguments.
    
    Args:
        command (dict): The routed command containing the function name and arguments.
    
    Returns:
        dict: A structured message based on the matched function.
    """
    print("C_DEBUG - LANGUAGE_INTERFACE.PY - handle_routed_command:", command)

    if command["type"] == "action":
        # Found a matching action / function
        func_name = command.get("function")
        args = command.get("args", {})

        if func_name in ACTION_REGISTRY:
            try:
                # Get the file path of the function
                file_path = ACTION_REGISTRY[func_name]["file_path"]

                # Create a structured message dynamically
                message = create_message(func_name, args, file_path)
                return message
            except Exception as e:
                return {"error": f"Function error: {e}"}
        else:
            return {"error": f"Unknown action: {func_name}"}

    elif command["type"] == "general_query":
        # Fall-back to general query handling
        return handle_general_prompt(command["query"])

    return {"error": "Unknown command format."}





import re
def extract_id_value(file_path: str, func_name: str) -> str:
    """
    Extracts the unique `id` value for the given function from the Python file.
    
    Args:
        file_path (str): The path to the Python file to inspect.
        func_name (str): The name of the function to find the `id` for.
    
    Returns:
        str: The unique `id` value, or None if not found.
    """

    # pattern for ANALYTICS MODULE messages
    # Example: "id": "analyticsDegreeRun"
    # use first term in function name before "_" 
    # to generate the id, e.g., "degree" for "degree_distribution_run"
    # and the id follows the pattern "analytics{FuncName}Run"
    func_name_generated = func_name.split("_")[0]  # Extract the first term before "_"
    print("C_DEBUG - LANGUAGE_INTERFACE.PY - Extracted func_name_generated:", func_name_generated)

    id_pattern = rf'"analytics{func_name_generated.capitalize()}Run"'
    print("C_DEBUG - LANGUAGE_INTERFACE.PY - id_pattern:", id_pattern)

    return id_pattern



def create_message(func_name: str, args: dict, file_path: str) -> dict:
    """
    Creates a structured message dynamically based on the matched function and its arguments.
    Dynamically extracts the `id` for analytics module messages and sets `msg` and `fn` accordingly.
    
    Args:
        func_name (str): The name of the matched function.
        args (dict): The arguments for the matched function.
        file_path (str): The path to the Python file containing the function.
    
    Returns:
        dict: A dynamically generated message.
    """


    # Default message structure
    message = {
        "usr": args.get("usr", "default_user"),  # Replace with actual user ID if available
        "msg": "RUN",  # Always "RUN" for analytics module
        "id": None,  # To be populated dynamically
        "parent": args.get("parent", None),  # Default parent value
        "val": args.get("val", None),  # Default value
        "fn": "analytics",  # Always "analytics" for analytics module
    }

    # Dynamically extract the `id` value from the file
    id_value = extract_id_value(file_path, func_name)
    # check if "" are in id_value
    if id_value and isinstance(id_value, str) and id_value.startswith('"') and id_value.endswith('"'):
        id_value = id_value.strip('"')  # Remove quotes if present
    print("C_DEBUG - LANGUAGE_INTERFACE.PY - Extracted id_value:", id_value)


    if id_value:
        message["id"] = id_value  # Set the extracted `id` value
    else:
        message["id"] = f"unknown_{func_name}"  # Fallback for unknown IDs

    return message




import re
def extract_msg_value(file_path: str) -> str:
    """
    Extracts the value assigned to `message["msg"]` in the given Python file.
    
    Args:
        file_path (str): The path to the Python file to inspect.
    
    Returns:
        str: The value assigned to `message["msg"]`, or None if not found.
    """
    msg_pattern = r'message\["msg"\]\s*=\s*["\'](.*?)["\']'  # Regex to match message["msg"] = "value"
    
    try:
        with open(file_path, "r") as f:
            content = f.read()
            match = re.search(msg_pattern, content)
            if match:
                return match.group(1)  # Return the captured value
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    
    return None  # Return None if no match is found





# ----------------------------------------
# Fallback LLM general chat - one can use a different model here
# ----------------------------------------
# This function handles general prompts that do not match any specific action.
# It sends the prompt to the LLM and returns the response.
def handle_general_prompt(prompt: str) -> str:


    print("C_DEBUG - LANGUAGE_INTERFACE.PY - handle_general_prompt:", prompt)


    try:
        response = client.chat.completions.create(
            model="z-ai/glm-4.5-air:free",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"LLM error: {str(e)}"



