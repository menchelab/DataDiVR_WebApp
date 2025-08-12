import openai
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
import json 
import inspect

# Load .env and init OpenAI
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

# Import all available actions
from ..LUI_funcs import actioncollection

# ----------------------------------------
# Register all action_* functions
# ----------------------------------------
def get_action_registry():
    registry = {}
    for name, func in inspect.getmembers(actioncollection, inspect.isfunction):
        if name.startswith("action_"):
            doc = func.__doc__ or "No description."
            registry[name] = {
                "function": func,
                "doc": doc.strip()
            }
    return registry

ACTION_REGISTRY = get_action_registry()

# ----------------------------------------
# Use LLM to match input to a function
# ----------------------------------------
def build_system_prompt(registry):
    lines = []
    for fname, meta in registry.items():
        lines.append(f"- `{fname}(...)`: {meta['doc']}")
    return (
        "You're a smart router. Based on a user request, map it to one of the following Python functions:\n"
        + "\n".join(lines) +
        "\nReturn ONLY a JSON object like:\n"
        '{"function": "action_show_node_info", "args": {"node_id": 5}}'
    )

def route_command(user_input: str) -> dict:
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
        return parsed
    except Exception as e:
        return {
            "type": "general_query",
            "query": user_input,
            "error": str(e)
        }

# ----------------------------------------
# Dispatcher
# ----------------------------------------
def handle_routed_command(command: dict):
    if command["type"] == "action":
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
        return handle_general_prompt(command["query"])

    return "Unknown command format."

# ----------------------------------------
# Fallback LLM general chat
# ----------------------------------------
def handle_general_prompt(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4",
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

































# # -------------------- OLD --------------------

# # from ..LUI_funcs.actioncollection import (
# #     action_open_project,
# #     action_show_node_info,
# #     action_make_subnetwork
# # )

# # -----------------------------
# # Command router
# # -----------------------------
# def route_command(user_input: str) -> dict:
#     text = user_input.lower()

#     # Robust project name detection
#     match = re.search(r'open (?:the )?project\s+(.+)', text, re.IGNORECASE)
#     if match:
#         project_name = match.group(1).strip()
#         return {
#             "type": "action",
#             "function": "action_open_project",
#             "args": {"project_name": project_name}
#         }

#     # Node info
#     match = re.search(r'show .*node\s+(\d+)', text)
#     if match:
#         return {
#             "type": "action",
#             "function": "action_show_node_info",
#             "args": {"node_id": match.group(1)}
#         }

#     # Subnetwork
#     match = re.search(r'(?:make|create).*network.*node\s+(\d+)', text)
#     if match:
#         return {
#             "type": "action",
#             "function": "action_make_subnetwork",
#             "args": {"node_id": match.group(1)}
#         }
    
#     # list all projects
#     match = re.search(r'(?:list|show).*all.*projects', text)
#     if match:
#         # This is a command to list all projects
#         return {
#             "type": "action",
#             "function": "action_list_all_projects",
#             "args": {}
#         }

#     # Fallback to LLM
#     return {
#         "type": "general_query",
#         "query": user_input
#     }


# # -----------------------------
# # Dispatcher
# # -----------------------------
# def handle_routed_command(command: dict):
#     if command["type"] == "action":
#         func_name = command["function"]
#         args = command["args"]

#         if func_name == "action_open_project":
#             project_name = args["project_name"]
#             return action_open_project(project_name)
            
#         elif func_name == "action_show_node_info":
#             nodeid = args["node_id"]
#             return action_show_node_info(nodeid)
        
#         elif func_name == "action_make_subnetwork":
#             return action_make_subnetwork(**args)

#     elif command["type"] == "general_query":
#         return handle_general_prompt(command["query"])

#     return "Unknown command or error."

# # -----------------------------
# # LLM Fallback (OpenAI)
# # -----------------------------
# # Load .env
# load_dotenv()

# # Initialize the new client
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def handle_general_prompt(prompt: str) -> str:
#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",  # or "gpt-4"
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.7,
#             max_tokens=500
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"LLM error: {str(e)}"
