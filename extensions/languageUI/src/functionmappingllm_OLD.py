import os
import json
from huggingface_hub import InferenceClient
from extensions.languageUI.LUI_funcs.actioncollection import (
    action_open_project,
    action_show_node_info,
    action_make_subnetwork
)

def get_api_token_from_file(file_path="extensions/languageUI/LUI_funcs/HF_token_doNOTcommit.txt"):
    with open(file_path, "r") as file:
        api_token = file.read().strip()
        if not api_token:
            raise ValueError("Token file is empty.")
        return api_token


# Define tool schema in text format for prompting
TOOLS = [
    {
        "name": "action_open_project",
        "description": "Opens a project by its exact name. Use when the input mentions opening a project.",
        "parameters": {
            "project_name": "The name of the project to open."
        }
    },
    {
        "name": "action_show_node_info",
        "description": "Shows info about a node given its ID.",
        "parameters": {
            "node_id": "The ID of the node to look up."
        }
    },
    {
        "name": "action_make_subnetwork",
        "description": "Creates a subnetwork centered around a node ID.",
        "parameters": {
            "node_id": "The ID of the central node."
        }
    }
]


def get_completion_huggingface(messages, model="mistralai/Mistral-7B-Instruct-v0.2", tempr=0.0, max_tok=300):
    api_token = get_api_token_from_file()

    client = InferenceClient(
        model=model,
        token=api_token
    )

    # Build system prompt with tool info
    tool_text = "\n".join(
        f"- {tool['name']}: {tool['description']} (params: {', '.join(tool['parameters'].keys())})"
        for tool in TOOLS
    )

    system_prompt = f"""You are a smart assistant that helps route user requests to the correct tool function.

Respond strictly in this format:
Function choice: <function_name>
Parameters: <JSON object>
Output: <short description>
Action: <explanation>

If no match is found, return:
Function choice: tooltip
Parameters: {{}}
Output: Show help.
Action: No matching function.

Available tools:
{tool_text}
"""

    chat_messages = [
        {"role": "system", "content": system_prompt},
        *messages
    ]

    response = client.chat_completion(
        messages=chat_messages,
        temperature=tempr,
        max_tokens=max_tok
    )

    return {"text": response.choices[0].message["content"]}

