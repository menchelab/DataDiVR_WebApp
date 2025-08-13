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

# Combine registries from multiple directories or files
registry1 = get_action_registry_from_directory("extensions/languageUI/LUI_funcs", "extensions.languageUI.LUI_funcs")
#registry2 = get_action_registry_from_files(["some.other.module", "another.module"])

ACTION_REGISTRY = {**registry1} #, **registry2}






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


    print("C_DEBUG - LANGUAGE_INTERFACE.PY - handle_routed_command:", command)


    if command["type"] == "action":
        # found a matching action / function
        func_name = command.get("function")
        args = command.get("args", {})

        if func_name in ACTION_REGISTRY:
            try:
                return ACTION_REGISTRY[func_name]["function"](**args)
            except Exception as e:
                return f"Function error: {e}"
        else:
            return f"Unknown action: {func_name}"

    elif command["type"] == "general_query":
        # fall-back to general query handling
        return handle_general_prompt(command["query"])

    return "Unknown command format."






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



