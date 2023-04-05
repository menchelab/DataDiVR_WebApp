import requests
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def sendUE4(adress, data):
    # The POST request to our node server
    res = requests.post('http://127.0.0.1:3000/in', json=data)
    #return
    # Convert response data to json
    #returned_data = res.json() 
    #print(returned_data)


def wsreceiver(socketObj):
    if request.method == 'POST':
        data =request.get_json()
    else:
        data = request.args

    #global idata

    #idata = data
    #print(bcolors.WARNING + data['usr']  + "says: " + data['mes'] + bcolors.ENDC)

    #outstr = data['usr'] +' : ' + data['mes']
### Multicast to connected web clients (not UE4!)
    #socketObj.emit('message', {'msg': outstr}, namespace = '/main' , room='1')
### Send it back to node wich multicasts it to ue4 clients
    #sendUE4('http://127.0.0.1:3000/in', data)
    #return "created image"