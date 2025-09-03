import openai
import os
from openai import OpenAI
from dotenv import load_dotenv
import json 
import importlib

from flask import session 


FUNCTION_FN_MAPPING = {

    # register DataDiVR modules here
    # pattern: "python module name" : "fn value in message"
    # the "fn" value is handled in "handle_execute_socket" in event_handler/__init__.py

    "analytics_events": "analytics",
    "search_events": "makeNodeButton",
    "nodeinfo_events": "node"
    # add others ... 
}


# ----------------------------------------
# MODELS + APIs
# ----------------------------------------

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






# ----------------------------------------
# Use LLM to match input to a function
# ----------------------------------------

# Build a system prompt for the LLM based on the action registry
# This prompt will be used to instruct the LLM to map user input to a specific function
# and its arguments.
def build_system_prompt(registry):
    """
    Builds a system prompt for the LLM based on the action registry.

    This prompt instructs the LLM to map user input to one of the available Python functions
    and their arguments. It dynamically includes all registered functions and their docstrings.

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

    # return (
    #     "You're a smart router. Based on a user request, map it to one of the following Python functions:\n"
    #     + "\n".join(lines) + 
    #     "\nReturn ONLY a JSON object like:\n"
    #     '{"function": "", "args": {"": ""}}\n'
    # )

    return (
        "You are a smart router for user requests. Based on the user input, you must decide whether to:\n"
        "1. Map the input to one of the following Python functions (type: 'action').\n"
        "2. If no function matches, treat the input as a general query (type: 'general_query').\n\n"
        "Available functions:\n"
        + "\n".join(lines) +
        "\n\n"
        "Return ONLY a JSON object in one of the following formats:\n"
        "For an action:\n"
        '{"type": "action", "function": "function_name", "args": {"arg1": "value1", "arg2": "value2"}}\n'
        "For a general query:\n"
        '{"type": "general_query", "query": "original user input"}\n'
        "Do not include any additional text or explanations."
    )



# Route the user input to the appropriate function using the LLM
# This function sends the user input to the LLM, which will return a JSON object
# containing the function name and its arguments.
# def route_command(user_input: str) -> dict:
#     """
#     Routes the user input to the appropriate function using the LLM.
#     If the LLM response does not match a known function, treat it as a general query.

#     Args:
#         user_input (str): The user input.

#     Returns:
#         dict: A dictionary containing the routed command or general query response.
#     """
#     print("C_DEBUG - LANGUAGE_INTERFACE.PY - route_command:", user_input)

#     # Build the system prompt
#     system_prompt = build_system_prompt(ACTION_REGISTRY)
#     messages = [
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": user_input}
#     ]

#     # Send the prompt to the LLM
#     response = client.chat.completions.create(
#         model="openai/gpt-oss-20b",  # or gpt-3.5-turbo
#         messages=messages,
#         temperature=0.3,  # Lower temperature for more deterministic responses
#         max_tokens=500
#     )

#     # Parse the LLM response
#     llm_response = response.choices[0].message.content.strip()
#     print("C_DEBUG - LANGUAGE_INTERFACE.PY - LLM Response:", llm_response)

#     # Attempt to parse the response as JSON
#     parsed = json.loads(llm_response)

#     validated_response = validate_llm_response(parsed, user_input)
#     return validated_response

# TEST VERSION - with conversation history
def route_command(user_input: str) -> dict:
    """
    Routes the user input to the appropriate function using the LLM.
    If the LLM response does not match a known function, treat it as a general query.

    Args:
        user_input (str): The user input.

    Returns:
        dict: A dictionary containing the routed command or general query response.
    """
    print("C_DEBUG - LANGUAGE_INTERFACE.PY - route_command:", user_input)

    # Initialize conversation history if not already present
    if "conversation_history" not in session:
        session["conversation_history"] = []

    # Add the user's input to the conversation history
    session["conversation_history"].append({"role": "user", "content": user_input})

    # Build the system prompt
    system_prompt = build_system_prompt(ACTION_REGISTRY)
    messages = [{"role": "system", "content": system_prompt}] + session["conversation_history"]

    # Send the prompt to the LLM
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # "openai/gpt-oss-20b",  # or z-ai/glm-4.5-air:free
        messages=messages,
        temperature=0.3,  # Lower temperature for more deterministic responses
        max_tokens=500
    )

    # Parse the LLM response
    llm_response = response.choices[0].message.content.strip()
    print("C_DEBUG - LANGUAGE_INTERFACE.PY - LLM Response:", llm_response)

    # Add the assistant's response to the conversation history
    session["conversation_history"].append({"role": "assistant", "content": llm_response})

    # Attempt to parse the response as JSON
    try:
        parsed = json.loads(llm_response)
        return validate_llm_response(parsed, user_input)
    except json.JSONDecodeError:
        # If the response is not JSON, treat it as a general query
        return {"type": "general_query", "response": {"feedback": llm_response}}



def validate_llm_response(parsed_response, user_input):
    """
    Validates the LLM response to ensure it matches the expected structure.

    Args:
        parsed_response (dict): The parsed response from the LLM.
        user_input (str): The original user input.

    Returns:
        dict: A validated response.
    """
    if "type" not in parsed_response:
        return {
            "type": "general_query",
            "query": user_input,
            "error": "Missing 'type' in LLM response."
        }

    if parsed_response["type"] == "action":
        if "function" not in parsed_response or "args" not in parsed_response:
            return {
                "type": "general_query",
                "query": user_input,
                "error": "Invalid 'action' response format."
            }
        return parsed_response

    if parsed_response["type"] == "general_query":
        if "query" not in parsed_response:
            return {
                "type": "general_query",
                "query": user_input,
                "error": "Invalid 'general_query' response format."
            }
        return parsed_response

    return {
        "type": "general_query",
        "query": user_input,
        "error": "Unknown response type."
    }


# ----------------------------------------
# Dispatcher
# ----------------------------------------
# This function takes the routed command and executes the corresponding action.
# def handle_routed_command(command: dict):
#     """
#     Handles the routed command by creating a structured message instead of directly calling the function.
#     The message structure is based on the matched function and its arguments.
    
#     Args:
#         command (dict): The routed command containing the function name and arguments.
    
#     Returns:
#         dict: A structured message based on the matched function.
#     """
#     print("C_DEBUG - LANGUAGE_INTERFACE.PY - handle_routed_command:", command)

#     if command["type"] == "action":
#         # Found a matching action / function
#         func_name = command.get("function")
#         args = command.get("args", {})

#         if func_name in ACTION_REGISTRY:
#             try:
#                 # Get the file path of the function
#                 file_path = ACTION_REGISTRY[func_name]["file_path"]

#                 # Create a structured message dynamically
#                 message = create_message(func_name, args, file_path)
#                 return message
#             except Exception as e:
#                 return {"error": f"Function error: {e}"}
#         else:
#             return {"error": f"Unknown action: {func_name}"}

#     elif command["type"] == "general_query":
#         # Fall-back to general query handling
#         return handle_general_prompt(command["query"])

#     return {"error": "Unknown command format."}

# TEST Version - with conversation history and feedback
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

                # Add the action feedback to the conversation history
                feedback = message.get("feedback", "No feedback provided.")
                session["conversation_history"].append({"role": "assistant", "content": feedback})

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
def extract_id_value_analytics(func_name: str) -> str:
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

    print("C_DEBUG - LANGUAGE_INTERFACE.PY - message fn :", message["fn"])
    print("C_DEBUG - LANGUAGE_INTERFACE.PY - complete message :", message)


    #-------------------------------------------------------------------
    # MODULE CATCH CASES HERE: 
    # Dynamically extract the `id` and 'msg' value from the file

    # catch if analytics module
    if module_name == "analytics_events":
        print("C_DEBUG: in analytics events module...")
        id_value = extract_id_value_analytics(func_name)
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

    #-------------------------------------------------------------------


    message["id"] = id_value

    print("C_DEBUG - LANGUAGE_INTERFACE.PY - Created message:", message)

    return message





# ----------------------------------------
# Fallback LLM general chat - choose model here
# ----------------------------------------
# This function handles general prompts that do not match any specific action.
# It sends the prompt to the LLM and returns the response.
# def handle_general_prompt(prompt: str) -> str:
#     """
#     Handles general prompts by sending the user input to the LLM and retrieving a structured response.
#     The response will always include a "response" key with a nested "feedback" key containing the answer.

#     Args:
#         prompt (str): The user input.

#     Returns:
#         dict: A structured response with the answer under "response" -> "feedback".
#     """
#     print("C_DEBUG - LANGUAGE_INTERFACE.PY - handle_general_prompt:", prompt)

#     try:
#         # Send the general query to the LLM
#         response = client.chat.completions.create(
#             model="z-ai/glm-4.5-air:free",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant. Respond to the following prompt as accurately as possible, be concise and answer short."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.3,
#             max_tokens=500
#         )

#         # Extract the LLM response content
#         llm_response = response.choices[0].message.content.strip()
#         print("C_DEBUG - LANGUAGE_INTERFACE.PY - LLM Response:", llm_response)

#         # Attempt to parse the response as JSON (if applicable)
#         try:
#             parsed_response = json.loads(llm_response)
#             if isinstance(parsed_response, dict):
#                 # If the response is valid JSON, wrap it in the required structure
#                 return {"response": {"feedback": parsed_response}}
#         except json.JSONDecodeError:
#             # If the response is not JSON, treat it as plain text
#             print("C_DEBUG - LANGUAGE_INTERFACE.PY - Response is not JSON, returning raw text.")

#         # Return the raw response in the required structure
#         return {"response": {"feedback": llm_response}}

#     except Exception as e:
#         print(f"C_DEBUG - LANGUAGE_INTERFACE.PY - Error in handle_general_prompt: {e}")
#         return {"response": {"feedback": f"Error: Unable to process the general query. Details: {str(e)}"}}
    
# TEST VERSION - with conversation history
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
        model="gpt-3.5-turbo", #"z-ai/glm-4.5-air:free",
        messages=session["conversation_history"],
        temperature=0.3,
        max_tokens=500
    )

    # Extract the LLM response content
    llm_response = response.choices[0].message.content.strip()
    print("C_DEBUG - LANGUAGE_INTERFACE.PY - LLM Response:", llm_response)

    # Add the assistant's response to the conversation history
    session["conversation_history"].append({"role": "assistant", "content": llm_response})

    # Return the response in the required structure
    return {"feedback": llm_response}








# ----------------------------------------
# Handle any python module and trigger function extracted from prompt 
# ----------------------------------------
def dynamic_import(module_name: str, function_name: str):
    """
    Dynamically imports a module and retrieves a function from it.

    Args:
        module_name (str): The name of the Python module to import.
        function_name (str): The name of the function to retrieve.

    Returns:
        function: The dynamically imported function.

    Raises:
        ImportError: If the module or function cannot be imported.
    """
    try:
        module = importlib.import_module(module_name)
        func = getattr(module, function_name)
        return func
    except ImportError as e:
        raise ImportError(f"Module '{module_name}' could not be imported: {e}")
    except AttributeError as e:
        raise ImportError(f"Function '{function_name}' not found in module '{module_name}': {e}")
    

def execute_function(module_name: str, function_name: str, *args, **kwargs):
    """
    Dynamically imports and executes a function with the given arguments.

    Args:
        module_name (str): The name of the Python module.
        function_name (str): The name of the function to execute.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.

    Returns:
        Any: The result of the function execution.
    """
    func = dynamic_import(module_name, function_name)
    return func(*args, **kwargs)