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
from extensions.languageUI.src.language_interface import route_command, handle_routed_command

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



@blueprint.route("/languageUI_process", methods=["POST"])
def language_ui_process():

    user_input = request.json.get("text", "")
    username = request.json.get("usr", "")
    room = 'shared-room' # TO FIX! shared room everywhere for now -  #flask.session.get("room") # request.json.get("room", "shared-room")
    message = user_input
    project = GD.data["actPro"]

    # Initialize conversation history in session if not present
    if "conversation_history" not in session:
        session["conversation_history"] = []

    # Add the user's input to the conversation history
    session["conversation_history"].append({"role": "user", "content": user_input})

    command = route_command(message)

    try:
        command["args"]["room"] = room
        command["args"]["project"] = project
    except: 
        command["args"] = {"room": room, "project": project}

    print("C_DEBUG: in LUI app - Routed command:", command)

    mapped_message = handle_routed_command(command)
    print("C_DEBUG: in LUI app - Mapped message:", mapped_message)


    if command["type"] == "general_query":
        # Add the assistant's response to the conversation history
        session["conversation_history"].append({"role": "assistant", "content":  mapped_message["feedback"]}) # mapped_message["response"]["feedback"]})

        # Return the general query response
        return jsonify({
            "function_name": "general_query",
            "response": mapped_message,
            "user": username,
        })

    if command["type"] == "action":
        # Pass to event handler
        mapped_message["usr"] = username
        mapped_message["room"] = room
        mapped_message["project"] = project

        feedback = mapped_message.get("feedback", "No feedback provided.")
        mapped_message["feedback"] = feedback

        # Add the action feedback to the conversation history
        session["conversation_history"].append({"role": "assistant", "content": feedback})

        event_handler.handle_socket_execute(mapped_message, room, project)  # Same as how main-app handles execute events

        return jsonify({
            "function_name": command.get("function", "general_query"),
            "response": mapped_message,
            "user": username,
        })

