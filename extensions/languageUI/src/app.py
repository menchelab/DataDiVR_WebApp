import base64
import csv
import json
import logging
import os
import os.path
import re 

# import preview as pre
import random
import wave
from base64 import b64encode
from cgi import print_arguments
from io import StringIO
from mimetypes import guess_extension
from os import path

import flask
import numpy as np
import requests

# from flask_session import Session
from engineio.payload import Payload
from flask import (
    Flask,
    abort,
    current_app,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename

import chatGPTTest
import event_handler
import GlobalData as GD
import layout_module
import plotlyExamples as PE

import search
import spam_protection as spam

# load audio and pad/trim it to fit 30 seconds
import TextToSpeech
import uploader
import uploaderGraph
import util
import websocket_functions as webfunc


import pandas as pd
import plotly.express as px

from io_blueprint import IOBlueprint

#from extensions.languageUI.LUI_funcs.functionmappingllm import *
import extensions.languageUI.src.language_interface as lang_interface

#from langchain.schema import SystemMessage, HumanMessage







# access via : http://127.0.0.1:5000/LUI/languageUI
url_prefix = "/LUI"
blueprint = IOBlueprint(
    "LUI",
    __name__,
    url_prefix=url_prefix,
    template_folder=os.path.abspath("./extensions/languageUI/templates"),
    static_folder=os.path.abspath("./extensions/languageUI/static"),
)


@blueprint.route("/languageUI", methods=["GET"])
def language_ui():
    username = flask.session.get("username")

    room = session.get("room")
    return render_template("LanguageUI.html", room=room, user=username)



from extensions.languageUI.src.language_interface import memory

@blueprint.route("/languageUI_process", methods=["POST"])
@blueprint.route("/languageUI_process", methods=["POST"])
def language_ui_process():
    """
    Processes user input, routes the command using the LLM, and handles the response.
    Integrates LangChain's memory buffer for conversation history management.
    """
    user_input = request.json.get("text", "").strip()
    username = request.json.get("usr", "")
    room = "shared-room"  # Shared room for now
    project = GD.data.get("actPro", None)

    # Validate user input and project context
    if not user_input:
        return jsonify({
            "status": "error",
            "response": "User input is empty. Please provide a valid command.",
            "user": username
        }), 400

    if not project:
        return jsonify({
            "status": "error",
            "response": "No active project found. Please select a project first.",
            "user": username
        }), 400

    print(f"C_DEBUG: User input: {user_input}, User: {username}, Room: {room}, Project: {project}")

    try:
        # Route the command using the LLM
        command = lang_interface.route_command(user_input)
        print("C_DEBUG: Routed command:", command)

        # Add room and project context to the command arguments
        command.setdefault("args", {})
        command["args"]["room"] = room
        command["args"]["project"] = project

        # Process the routed command
        if command["type"] == "action":
            # Handle actions
            func_name = command.get("function")
            args = command.get("args", {})
            print(f"C_DEBUG: Handling action '{func_name}' with args: {args}")

            # Create a structured message for the action
            action_message = lang_interface.create_message(func_name, args, lang_interface.ACTION_REGISTRY[func_name]["file_path"])
            print("C_DEBUG: Action message:", action_message)

            # Add feedback to the memory buffer
            feedback = action_message.get("feedback", "No feedback provided.")
            lang_interface.memory.chat_memory.add_ai_message(feedback)

            # Pass the message to the event handler
            event_handler.handle_socket_execute(action_message, room, project)

            # Return the action response
            return jsonify({
                "function_name": func_name,
                "response": action_message,
                "user": username,
            })

        elif command["type"] == "general_query":
            print("C_DEBUG: Handling general query")

            #general_response = lang_interface.handle_general_prompt(command["general_query"])
            general_response = command.get("response", "")
            general_response_feedback = general_response.get("feedback", "No response generated.")


            # Add the assistant's response to the memory buffer
            lang_interface.memory.chat_memory.add_ai_message(general_response_feedback)

            # Return the general query response
            return jsonify({
                "function_name": "general_query",
                "response": general_response,
                "user": username,
            })

        else:
            # Unknown command type
            print("C_DEBUG: Unknown command type")
            return jsonify({
                "status": "error",
                "response": "Unknown command type.",
                "user": username
            }), 400

    except Exception as e:
        print(f"C_DEBUG: Error in language_ui_process: {str(e)}")
        return jsonify({
            "status": "error",
            "response": f"An error occurred while processing the command: {str(e)}",
            "user": username
        }), 500