import openai
import os
from openai import OpenAI
from dotenv import load_dotenv
import json 
import importlib

from flask import session 

from extensions.languageUI.src.lui_helpers import load_project_info
import GlobalData as GD

from langchain.memory import ConversationBufferMemory




FUNCTION_FN_MAPPING = {

    # register DataDiVR modules here
    # pattern: "python module name" : "fn value in message"
    # the "fn" value is handled in "handle_execute_socket" in event_handler/__init__.py

    "analytics_events": "analytics",
    "search_events": "node",
    "nodeinfo_events": "node",
    "project_events": "dropdown",

    # add others ... 
}




# ----------------------------------------
# MODELS + APIs
# ----------------------------------------

# define model
llm_from_openrouterai = "openai/gpt-oss-20b:free" # "gpt-3.5-turbo" # "meta-llama/llama-3.3-70b-instruct:free"   #"z-ai/glm-4.5-air:free", "openai/gpt-oss-20b:free" #"meta-llama/llama-3.3-70b-instruct:free" 

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
# CREATE FUNCTION REGISTRY
# ----------------------------------------

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



registry_VR = get_action_registry_from_DataDiVR()
ACTION_REGISTRY = {**registry_VR} 

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
print("C_DEBUG: Initialized conversation memory.", memory)
print("C_DEBUG: Initial memory state:", memory.load_memory_variables({})["chat_history"])


# ----------------------------------------
# Use LLM to match input to a function
# ----------------------------------------
# Build a system prompt for the LLM based on the action registry
# This prompt will be used to instruct the LLM to map user input to a specific function
# and its arguments.
def build_system_prompt(registry):
    """
    Builds a system prompt for the LLM based on the action registry and project-specific information.

    This prompt instructs the LLM to map user input to one of the available Python functions
    and their arguments. It dynamically includes all registered functions and their docstrings,
    as well as project-specific information retrieved from the current project's metadata.

    The project information is dynamically retrieved from GD.data["actPro"].

    Args:
        registry (dict): The action registry containing function metadata.

    Returns:
        str: A system prompt for the LLM.
    """

    print("C_DEBUG - LANGUAGE_INTERFACE.PY - build_system_prompt...")


    lines = []
    for fname, meta in registry.items():
        # Extract the module name from the file path
        module_name = os.path.splitext(os.path.basename(meta["file_path"]))[0]
        fn_value = FUNCTION_FN_MAPPING.get(module_name, "general")  # Map module to `fn` value
        lines.append(f"- `{fname}(...)` (fn: `{fn_value}`): {meta['doc']}")

    # get project information 
    project_data = load_project_info()
    project_name = project_data.get("name", "Unknown Project")
    project_info = project_data.get("info", "No description available.")

    # Build the project-specific section of the prompt
    project_section = (
        f"Project Name: {project_name}\n"
        f"Project Description: {project_info}\n\n"
        f"You have access to this project information. Use it to answer user queries.\n"
        f"If the user asks about the project or information about the project, provide details based on the above information.\n"
    )

    return (
        "You are a smart router for user requests. Based on the user input, you must decide whether to:\n"
        "1. Map the input to one of the following Python functions (type: 'action').\n"
        "2. If no function matches, treat the input as a general query (type: 'general_query').\n\n"
        + project_section +
        "Available functions:\n"
        + "\n".join(lines) +
        "\n\n"
        "Return ONLY a JSON object in one of the following formats:\n"
        "For an action:\n"
        '{"type": "action", "function": "function_name", "args": {"arg1": "value1", "arg2": "value2"}}\n'
        "For a general query:\n"
        '{"type": "general_query", "response": {"feedback": "Your natural language response here."}}\n'
        "Do not include any additional text or explanations outside the JSON object."
    )





def route_command(user_input: str) -> dict:
    """
    Routes the user input to the appropriate function using the LLM.
    If the LLM response does not match a known function, treat it as a general query.
    Includes project-specific information in the system prompt.

    Args:
        user_input (str): The user input.

    Returns:
        dict: A dictionary containing the routed command or general query response.
    """
    # Add the user's input to the memory buffer
    memory.chat_memory.add_user_message(user_input)
    print("C_DEBUG: Current memory buffer:", memory.load_memory_variables({})["chat_history"])

    # Build the system prompt
    system_prompt = build_system_prompt(ACTION_REGISTRY)
    messages = [{"role": "system", "content": system_prompt}] + memory.load_memory_variables({})["chat_history"]

    # Send the prompt to the LLM
    try:
        response = client.chat.completions.create(
            model=llm_from_openrouterai,
            messages=messages,
            temperature=0.3,  # Lower temperature for more deterministic responses
            max_tokens=500
        )

        # Parse the LLM response
        llm_response = response.choices[0].message.content.strip()

        # Add the assistant's response to the memory buffer
        memory.chat_memory.add_ai_message(llm_response)

        print("\nLLM response:", llm_response)

        parsed = json.loads(llm_response)

        return validate_llm_response(parsed, user_input)

    except Exception as e:
        print("C_DEBUG: Error in route_command:", str(e))
        return {
            "type": "error",
            "feedback": f"An error occurred while processing the command: {str(e)}"
        }
 


def validate_llm_response(parsed_response, user_input):
    """
    Validates the LLM response to ensure it matches the expected structure.

    Args:
        parsed_response (dict): The parsed response from the LLM.
        user_input (str): The original user input.

    Returns:
        dict: A validated response.
    """

    print("C_DEBUG: Validating LLM response: ", parsed_response)
    if "type" not in parsed_response:
        return {
            "type": "general_query",
            "query": user_input,
            "feedback": "Missing 'type' in LLM response."
        }

    if parsed_response["type"] == "action":
        if "function" not in parsed_response or "args" not in parsed_response:
            return {
                "type": "general_query",
                "query": user_input,
                "feedback": "Invalid 'action' response format."
            }
        return parsed_response

    if parsed_response["type"] == "general_query":
        if "response" in parsed_response:
            if "feedback" not in parsed_response.get("response", {}):
                return {
                    "type": "general_query",
                    "query": user_input,
                    "feedback": "No feedback provided."
                }
            return parsed_response 

    return {
        "type": "general_query",
        "query": user_input,
        "feedback": "Unknown response type."
    }



def handle_general_prompt(prompt: str) -> dict:
    """
    Handles general prompts by sending the user input to the LLM and retrieving a structured response.
    The response includes a "feedback" key containing the answer.

    Args:
        prompt (str): The user input.

    Returns:
        dict: A structured response with the answer under "feedback".
    """
    print("C_DEBUG - LANGUAGE_INTERFACE.PY - handle_general_prompt:", prompt)

    # Add the user's input to the memory buffer
    memory.chat_memory.add_user_message(prompt)

    # Send the conversation history to the LLM
    try:
        messages = memory.load_memory_variables({})["chat_history"]
        response = client.chat.completions.create(
            model=llm_from_openrouterai,
            messages=messages,
            temperature=0.3,
            max_tokens=500
        )

        # Extract the LLM response content
        llm_response = response.choices[0].message.content.strip()
        print("C_DEBUG - LANGUAGE_INTERFACE.PY - in handle_general_prompt - LLM response:", llm_response)

        # Add the assistant's response to the memory buffer
        memory.chat_memory.add_ai_message(llm_response)

        # Return the response in the required structure
        return {"feedback": llm_response}

    except Exception as e:
        print("C_DEBUG: Error in handle_general_prompt:", str(e))
        return {"feedback": f"An error occurred: {str(e)}"}







def create_message(func_name: str, args: dict, file_path: str) -> dict:
    """
    Creates a structured message dynamically based on the matched function and its arguments.
    Dynamically sets the `fn` value based on the module (e.g., analytics_events, layout_events).

    Args:
        func_name (str): The name of the matched function.
        args (dict): The arguments for the matched function.
        file_path (str): The path to the Python file containing the function.

    Returns:
        dict: A dynamically generated message.
    """
    # Extract the module name from the file path
    module_name = os.path.splitext(os.path.basename(file_path))[0]  # e.g., "analytics_events"

    # Default message structure
    message = {
        "usr": args.get("usr", "default_user"),
        "msg": None,
        "id": None,
        "parent": args.get("parent", None),
        "val": args.get("val", None),
        "fn": None,  # To be determined dynamically
        "feedback": f"'{func_name}' has been triggered successfully."
    }

    # Set the `fn` value based on the module name
    message["fn"] = FUNCTION_FN_MAPPING.get(module_name, "general")  # Default to "general" if not found


    #-------------------------------------------------------------------
    # MODULE CATCH CASES HERE: 
    # Dynamically extract the `id` and 'msg' value from the file

    # catch if analytics module
    if module_name == "analytics_events":
        print("C_DEBUG: in analytics events module...")
        func_name_generated = func_name.split("_")[0]  # Extract the first term before "_"
        id_value = rf'"analytics{func_name_generated.capitalize()}Run"'
        if id_value and isinstance(id_value, str) and id_value.startswith('"') and id_value.endswith('"'):
            id_value = id_value.strip('"')  # Remove quotes if present
            msg_msg = "RUN"
            message["msg"] = msg_msg
            
    # catch if search module
    if module_name == "search_events":
        print("C_DEBUG: in search events module...")
        id_value = "search"
        msg_value = args.get("message", {}).get("val", "")
        node_id = args.get("message", {}).get("id", "")
        message["val"] = msg_value

    # catch if nodeinfo module
    if module_name == "nodeinfo_events":
        print("C_DEBUG: in nodeinfo events module...")
        id_value = None
        node_name = args.get("message", {}).get("val", "")
        node_id = args.get("message", {}).get("id", "")
        message["val"] = node_id
        message["msg"] = node_name
        message["fn"] = "node"

    # catch if project module
    if module_name == "project_events":
        print("C_DEBUG: in project events module...")
        id_value = "projDD"
        message["fn"] = "dropdown"
        message["parent"] = "projDD"

        # get project name and index
        projectname_raw = args.get("message", {}).get("msg", "")
        all_projects = GD.plist
        all_projects_capitalized = [proj.capitalize() for proj in all_projects]
        projectname = projectname_raw.capitalize()

        if projectname not in all_projects_capitalized:
            message["feedback"] = f"No project name provided. Selecting default project. Choose from available projects: {', '.join(all_projects)}"
            project_index = 0
            projectname = all_projects[project_index]

        else:
            project_index = all_projects_capitalized.index(projectname) # get index of matched project name     
            message["feedback"] = f"Project '{projectname}' selected successfully."
        
        message["msg"] = projectname
        message["val"] = project_index
        print("C_DEBUG: matched project name:", projectname)
        print("C_DEBUG: matched project index:", project_index)


    #-------------------------------------------------------------------


    message["id"] = id_value

    print("C_DEBUG - LANGUAGE_INTERFACE.PY - Created message:", message)

    return message





# ----------------------------------------
# Fallback LLM general chat - choose model here
# ----------------------------------------
# This function handles general prompts that do not match any specific action.
# It sends the prompt to the LLM and returns the response.
def handle_general_prompt(prompt: str) -> dict:
    """
    Handles general prompts by sending the user input to the LLM and retrieving a structured response.
    The response includes a "feedback" key containing the answer.

    Args:
        prompt (str): The user input.

    Returns:
        dict: A structured response with the answer under "feedback".
    """
    print("C_DEBUG - LANGUAGE_INTERFACE.PY - handle_general_prompt:", prompt)

    # Add the user's input to the conversation history
    session["conversation_history"].append({"role": "user", "content": prompt})

    # Send the conversation history to the LLM
    response = client.chat.completions.create(
        model=llm_from_openrouterai,
        messages=session["conversation_history"],
        temperature=0.3,
        max_tokens=500
    )

    # Extract the LLM response content
    llm_response = response.choices[0].message.content.strip()
    print("C_DEBUG - LANGUAGE_INTERFACE.PY - in handle_general_prompt - LLM response:", llm_response)

    # Add the assistant's response to the conversation history
    session["conversation_history"].append({"role": "assistant", "content": llm_response})
    #print(f"C_DEBUG: Conversation history before LLM call:\n{json.dumps(session['conversation_history'], indent=4)}")

    # Return the response in the required structure
    return {"feedback": llm_response}





def clear_memory():
    """
    Clears the conversation memory buffer.
    """
    memory.chat_memory.clear()
    print("C_DEBUG: Memory buffer cleared.")

