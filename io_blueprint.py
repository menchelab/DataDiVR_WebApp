"""
A Flask Blueprint class to be used with Flask-SocketIO.
This class inherits from the Flask Blueprint class so that
 we can use the standard Blueprint interface.
Derived from https://github.com/m-housh/io-blueprint
Original work by Michael Housh, mhoush@houshhomeenergy.com
Modified by Brian Wojtczak
@author Brian Wojtczak
"""

# noinspection PyPackageRequirements
import socketio

from flask import Blueprint


class IOBlueprint(Blueprint):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace = self.url_prefix or '/'
        self._socketio_handlers = []
        self.socketio = None
        self.record_once(self.init_socketio)

    def init_socketio(self, state):
        self.socketio: socketio.Client = state.app.extensions['socketio']
        for f in self._socketio_handlers:
            f(self.socketio)

        return self.socketio

    def on(self, key,**socketio_kwargs):
        """ A decorator to add a handler to a blueprint. """
        if "namespace" not in socketio_kwargs:
            socketio_kwargs["namespace"] = self.namespace
        def wrapper(f):
            def wrap(sio):
                @sio.on(key, **socketio_kwargs)
                def wrapped(*args, **kwargs):
                    return f(*args, **kwargs)
                return sio

            self._socketio_handlers.append(wrap)

        return wrapper

    def emit(self, *args, **kwargs):
        if "namespace" not in kwargs:
            kwargs["namespace"] = self.namespace
        self.socketio.emit(*args, **kwargs)