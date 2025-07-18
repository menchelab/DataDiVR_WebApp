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

    command = route_command(user_input)
    result = handle_routed_command(command)

    return jsonify({
        "function_name": command.get("function", "general_query"),
        "response": result,
        "user": username
    })




# THIS DOES NOT WORK / SEEMS NOT TO BE USED ANYWHERE
@blueprint.on("ex", namespace="/LUI")
def ex(message):

    # room = flask.session.get("room")
    # print(webfunc.bcolors.WARNING+ flask.session.get("username")+ "ex: "+ json.dumps(message)+ webfunc.bcolors.ENDC)
    #message["usr"] = flask.session.get("username")
    
    # print("C_DEBUG : incoming LUI " + str(message))

    # emit("ex", message, room=room)

    
    print("Message received:", message)
    
    room = 'shared-room' #flask.session.get("room") or 1 # jupyter-room
    username = flask.session.get("username") or 'jupyter-user'
    print(f"Using room: {room}, user: {username}")

    for func in GD.functions["ex"]:
        #print("Executing function:", func)
        func(message)
    
    project = GD.data["actPro"]
    print("incoming :" + str(message))

    event_handler.handle_socket_execute(message, room, project)
    
    # added for jupyter client (or any client not sending http requests)
    emit('module-update', {
        'id': 'test-node',
        'val': 42
    }, room='shared-room', namespace='/LUI')  


