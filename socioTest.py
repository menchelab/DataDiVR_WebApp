import socketio

sio = socketio.Client()
sio.connect('http://localhost:5000', namespaces=['/main'])

sio.emit('ex', {'id': 'client', "usr":"reee", "fn":"refresh"}, namespace='/main' )


@sio.on('ex', namespace='/main')
def response(data):
    print(data)  # {'from': 'server'}

    sio.disconnect()
    exit(0)