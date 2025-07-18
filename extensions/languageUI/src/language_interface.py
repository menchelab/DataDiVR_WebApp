import openai
import os
import re
from openai import OpenAI
from dotenv import load_dotenv

openai.api_key = os.getenv("OPENAI_API_KEY") #https://platform.openai.com/api-keys


from ..LUI_funcs.actioncollection import (
    action_open_project,
    action_show_node_info,
    action_make_subnetwork
)

    

# -----------------------------
# Command router
# -----------------------------
def route_command(user_input: str) -> dict:
    text = user_input.lower()

    # Robust project name detection
    match = re.search(r'open (?:the )?project\s+(.+)', text, re.IGNORECASE)
    if match:
        project_name = match.group(1).strip()
        return {
            "type": "action",
            "function": "action_open_project",
            "args": {"project_name": project_name}
        }

    # Node info
    match = re.search(r'show .*node\s+(\d+)', text)
    if match:
        return {
            "type": "action",
            "function": "action_show_node_info",
            "args": {"node_id": match.group(1)}
        }

    # Subnetwork
    match = re.search(r'(?:make|create).*network.*node\s+(\d+)', text)
    if match:
        return {
            "type": "action",
            "function": "action_make_subnetwork",
            "args": {"node_id": match.group(1)}
        }
    
    # list all projects
    match = re.search(r'(?:list|show).*all.*projects', text)
    if match:
        # This is a command to list all projects
        return {
            "type": "action",
            "function": "action_list_all_projects",
            "args": {}
        }

    # Fallback to LLM
    return {
        "type": "general_query",
        "query": user_input
    }


# -----------------------------
# Dispatcher
# -----------------------------
def handle_routed_command(command: dict):
    if command["type"] == "action":
        func_name = command["function"]
        args = command["args"]

        if func_name == "action_open_project":
            project_name = args["project_name"]
            return action_open_project(project_name)
            
        elif func_name == "action_show_node_info":
            return action_show_node_info(**args)
        
        elif func_name == "action_make_subnetwork":
            return action_make_subnetwork(**args)

    elif command["type"] == "general_query":
        return handle_general_prompt(command["query"])

    return "Unknown command or error."

# -----------------------------
# LLM Fallback (OpenAI)
# -----------------------------
# Load .env
load_dotenv()

# Initialize the new client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def handle_general_prompt(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4"
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
