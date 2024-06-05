import base64
import csv
import json
import logging
import os
import os.path

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
#import load_extensions
import plotlyExamples as PE

import search
import spam_protection as spam

# load audio and pad/trim it to fit 30 seconds
import TextToSpeech
import uploader
import uploaderGraph
import util
import websocket_functions as webfunc
from extensions import load_extensions


import pandas as pd
import plotly
import plotly.express as px
#### Settings

spam_protector = spam.SpamProtector()

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

Payload.max_decode_packets = 50

app = Flask(__name__)
app.debug = False
app.config["SECRET_KEY"] = "secret"
app.config["SESSION_TYPE"] = "filesystem"

socketio = SocketIO(app, manage_session=False)
app, extensions = load_extensions.load(app)

### HTML ROUTES ###


### Execute code before first request ###
@app.before_first_request
def execute_before_first_request():
    uploader.check_ProjectFolder()
    util.create_dynamic_links(app)
    GD.loadGD()
    GD.loadPFile()
    GD.loadPD()
    GD.loadColor()
    GD.loadLinks()
    GD.load_annotations()




@app.route("/")
def index():
    return flask.redirect("/home")


@app.route("/preview")
def preview():
    return render_template("preview.html", extensions=extensions)


#----------------------------------------------------------------------
# Natural Language UI 

from functionmapping import process_input


@app.route("/languageUI")
def languageUI():
    return render_template("languageUI.html", extensions=extensions)

@app.route('/languageUI_process', methods=['POST'])
def process():
    data = request.get_json()
    user_input = data.get('text')
    result = process_input(user_input)
    return jsonify({"result": result})

#----------------------------------------------------------------------





@app.route("/main", methods=["GET"])
def main():
    username = util.generate_username()
    project = GD.data["actPro"]  # flask.request.args.get("project")
    if project is None:
        project = GD.data["actPro"]
        return "no project selected in GD.json"

    if flask.request.method == "GET":
        room = 1
        # Store the data in session
        flask.session["username"] = username
        flask.session["room"] = room
        # prolist = uploader.listProjects()

        return render_template("main.html", user=username, extensions=extensions)
    else:
        return "error"



myusers = [{'uid': 4, 'links': [2, 2, 2, 2, 2, 133, 666, 666, 666, 666, 125, 125]}, {'uid': 666, 'links': [133]}, {'uid': 133, 'links': [666]}, {'uid': 555, 'links': [666, 133, 4, 123, 124, 125, 125, 125]}, {'uid': 125, 'links': [555, 128]}, {'uid': 128, 'links': [555]}, {'uid': 130, 'links': [555]}]


import plotlyExamples

@app.route('/evilAI')
def evilAI():

    nodes=[]
    links=[]
    annot=[]
    
    # Create graphJSON
    #graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    if  request.cookies.get('userID'): # has cookie, add to links
        if request.args.get('uid'):
            uid = request.args.get('uid')
            name = request.cookies.get('userID')
            for i in myusers:
                if i['uid'] == int(name):
                    i['links'].append(int(uid))
                    break
            for i in myusers:
                if i['uid'] == uid:
                    i['links'].append(int(name))
                    break

            for i in myusers:
                nodes.append(int(i['uid']))
                annot.append("agent"+ str(i['uid']))

            for i in myusers:
                start = -1
                try:
                    start = nodes.index(i['uid']) 
                except ValueError:
                    start = -1
                 
                for l in i['links']:
                    try:
                        end = nodes.index(l)
                        links.append((start,end))
                    except ValueError:
                        end = -1
                        
            
            print(links)
            print(nodes)
            print(annot)
            print(myusers)
        graphJSON = plotlyExamples.networkGraphRT(nodes, annot , links)
        #return '<h1>welcome ' + name + '</h1><br>You just met Agent ' + uid
        return render_template("evilAi.html", user=name, data=myusers, graphJSON=graphJSON)
    
    #login set cookie
    else:
        if request.args.get('uid'):
            uid = request.args.get('uid')

            exists = False

            for i in myusers:
                if i['uid'] == uid:
                    exists = True

            if not exists:
                thisUser = {}
                thisUser["uid"] = int(uid)
                thisUser["links"] = []
                myusers.append(thisUser)
                resp = make_response(render_template('evilAi.html',user=uid, data=myusers) + uid)
                resp.set_cookie('userID', uid)
                return resp
            else:
                return '<h1>QR code already claimed</h1>'
 
        
        #return render_template('login.html')



@app.route('/setcookie', methods = ['POST', 'GET'])
def setcookie():
   #if request.method == 'POST':
        user = request.form['nm']
        
        resp = make_response(render_template('readcookie.html'))
        #resp = make_response(render_template('readcookie.html'))
        resp.set_cookie('userID', user)
        
        return resp

@app.route('/getcookie')
def getcookie():
    if  request.cookies.get('userID'):
        name = request.cookies.get('userID')
        return '<h1>welcome ' + name + '</h1>'
    else:
        return '<h1>no cookie</h1>'



@app.route("/GPT", methods=["POST"])
def GPT():
    result = {}
    if request.method == "POST":
        data = flask.request.get_json()
        answer = chatGPTTest.NewGPTrequest(data.get("text"))
        fname = TextToSpeech.makeogg(answer, 0)
        print(answer)
        return {"text": answer, "audiofile": fname + ".ogg"}


@app.route("/TTS", methods=["POST", "GET"])
def TTS():
    result = {}
    if request.method == "GET":
        text = flask.request.args.get("text")
        voice = int(flask.request.args.get("voice"))
        result["text"] = TextToSpeech.makeogg(text, voice)
    return result


@app.route("/nodepanel", methods=["GET"])
def nodepanel():
    data = []
    return render_template("nodepanel.html", data)


@app.route("/uploadOLD", methods=["GET"])
def upload():
    prolist = GD.listProjects()
    return render_template(
        "upload.html",
        namespaces=prolist,
        extensions=extensions,
        sessionData=json.dumps(GD.data),
    )


@app.route("/upload", methods=["GET"])
def uploadNew():
    prolist = GD.listProjects()
    return render_template(
        "uploadNew.html",
        namespaces=prolist,
        extensions=extensions,
        sessionData=json.dumps(GD.data),
    )


@app.route("/uploadJSON", methods=["GET"])
def uploadJSON():
    prolist = GD.listProjects()
    return render_template(
        "uploadGRAPH.html",
        namespaces=prolist,
        extensions=extensions,
        sessionData=json.dumps(GD.data),
    )


@app.route("/uploadfiles", methods=["GET", "POST"])
def upload_files():
    return uploader.upload_files(flask.request)


@app.route("/uploadfilesNew", methods=["GET", "POST"])
def upload_filesNew():
    return uploader.upload_filesNew(flask.request)


@app.route("/uploadfilesJSON", methods=["GET", "POST"])
def upload_filesJSON():
    return uploaderGraph.upload_filesJSON(flask.request)


@app.route("/delpro", methods=["GET", "POST"])
def delete_project():
    return util.delete_project(flask.request)


# gets information about a specific node (project must be provided as argument)
@app.route("/node", methods=["GET", "POST"])
def nodeinfo():
    id = flask.request.args.get("id")
    key = flask.request.args.get("key")
    name = "static/projects/" + str(flask.request.args.get("project")) + "/nodes"
    nodestxt = open(name + ".json", "r")
    nodes = json.load(nodestxt)
    nlength = len(nodes["nodes"]) - len(nodes["labels"])
    print(nlength)
    if key:
        return str(nodes["nodes"][int(id)].get(key))
    else:
        if int(id) > nlength:
            # is label
            print(nodes["labels"][int(id) - nlength])
        return nodes["nodes"][int(id)]


@app.route("/home")
def home():
    if not flask.session.get("username"):
        flask.session["username"] = util.generate_username()
        flask.session["room"] = 1
    return render_template("home.html", sessionData=json.dumps(GD.data))


### DATA ROUTES###


@app.route("/load_all_projects", methods=["GET", "POST"])
def loadAllProjectsR():
    return jsonify(projects=GD.listProjects())


@app.route("/load_project/<name>", methods=["GET", "POST"])
def loadProjectInfoR(name):
    return uploader.loadProjectInfo(name)


@app.route("/projectAnnotations/<name>", methods=["GET"])
def loadProjectAnnotations(name):
    return uploader.loadAnnotations(name)


###SocketIO ROUTES###


@socketio.on("join", namespace="/main")
def join(message):
    for func in GD.functions["join"]:
        func(message)
    room = flask.session.get("room")
    join_room(room)
    print(message["usr"])

    print(
        webfunc.bcolors.WARNING
        + message["usr"]
        + " has entered the room."
        + webfunc.bcolors.ENDC
    )   
    emit("status", {"usr": message["usr"], "msg": " has entered the room."}, room=room)


@socketio.on("ex", namespace="/main")
@spam_protector
def ex(message):
    for func in GD.functions["ex"]:
        func(message)

    room = flask.session.get("room")
    project = GD.data["actPro"]
    # print(webfunc.bcolors.WARNING+ flask.session.get("username")+ "ex: "+ json.dumps(message)+ webfunc.bcolors.ENDC)
    # message["usr"] = flask.session.get("username")

    print("incoming " + str(message))

    event_handler.handle_socket_execute(message, room, project)


@socketio.on("left", namespace="/main")
def left(message):
    for func in GD.functions["left"]:
        func(message)
    room = flask.session.get("room")
    username = flask.session.get("username")
    leave_room(room)
    flask.session.clear()
    emit("status", {"msg": username + " has left the room."}, room=room)
    print(
        webfunc.bcolors.WARNING
        + flask.session.get("username")
        + " has left the room."
        + webfunc.bcolors.ENDC
    )



if __name__ == "__main__":
    socketio.run(app, debug=True)