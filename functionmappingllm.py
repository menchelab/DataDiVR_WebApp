# pip install --upgrade --quiet huggingface_hub

# hugging face "dev-datascope" token: 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
# get a token: https://huggingface.co/docs/api-inference/quicktour#get-your-api-token
from pathlib import Path



from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint

import re

# dummy functions 
import dummyfuncs as duf

# Define app actions and their corresponding keywords
actions = {
    "open project": ["open a project", "open project", "show project", "load project"],
    "show node info": ["get node information", "show node attributes", "get node details"],
    "make subnetwork": ["visualize subnetwork", "create subnetwork view"]
}

# Template for the prompt
template = """Question: {question}
Context: ... (rest of your context)
Actions:
  - Open project (e.g., "open project A")
    Tooltip: Opens a previously saved project file in the project collection.
  - Show node info (e.g., "get details for node 123")
    Tooltip: Displays information about a specific node, including its attributes and connections.
  - Make subnetwork (e.g., "visualize subnetwork centered on node 456")
    Tooltip: Creates a visualization of a subset of nodes and their connections, focusing on a particular node.
Tooltip: If you're unsure about the available actions, try using more specific terms.
Identify the intended action based on the user's request and the available actions.
Summarize: Provide a concise response indicating the identified action. If no action is found, provide a helpful tooltip."""

# Create a prompt object
prompt = PromptTemplate.from_template(template)

# Load the LLM
keyfile = str(Path(__file__).resolve().parents[0])+'/HF_token_doNOTcommit.txt'
print(keyfile)
with open(keyfile) as f:
    lines = f.readlines()
    HUGGINGFACEHUB_API_TOKEN = lines[0] 
    
repo_id = "mistralai/Mistral-7B-Instruct-v0.2"
llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    max_length=128,
    temperature=0.5,
    huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
)

# Create an LLM chain to process the prompt and execute the mapped action
llm_chain = LLMChain(prompt=prompt, llm=llm)

def process_input(user_input):
    
    # Invoke the LLM chain to map the user input to an action
    response = llm_chain.invoke({"question": user_input, "actions": actions})
    generated_text = response["text"].strip()

    # Log the generated response for debugging or analysis
    print(f"C_DEBUG: Generated Text: {generated_text}")


    # Identify the mapped action and extract the project name
    mapped_action = None
    project_name = None
    for action, keywords in actions.items():
        for keyword in keywords:
            if keyword.lower() in user_input.lower():
                mapped_action = action
                match = re.search(r"project\s+(\w+)", user_input, re.IGNORECASE)
                if match:
                    project_name = match.group(1)
                break

    if mapped_action:
        if mapped_action == "open project":
            result = duf.action_open_project(project_name)
            return {
                "message": f"Executed action: {mapped_action} for project {project_name}",
                "generated_text": generated_text
            }
        elif mapped_action == "show node info":
            duf.action_show_node_info()
        elif mapped_action == "make subnetwork":
            duf.action_make_subnetwork()
        else:
            return {
                "message": "Action not implemented yet", 
                "generated_text": generated_text
            }

        # Return both the action and generated text
        return {
            "message": f"Executed action: {mapped_action}",
            "generated_text": generated_text
        }
    else:
        return {
            "message": "No action found. Please specify more details.",
            "generated_text": generated_text  
        }
    
