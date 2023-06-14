import threading
import time

import flask
import GlobalData as GD

import socket_handlers as sh

from .. import settings
from . import anntoation_scraper
from . import extension_data as ED
from . import util


def highlight(bp, message):
    bp.emit("started", {"id": message["id"]})
    message = util.highlight_func(message)
    print(message)
    if message.get("set_project"):
        print("Setting project..")
        set_project(bp, "tmp")
        time.sleep(2)

    send_status(bp, message)


def reset(bp, message):
    print(message)
    if message["type"] == "project":
        project = GD.pfile.get("origin")
        if project:
            set_project(bp, project)
            message["message"] = f"Project reset to {project}."
            message["status"] = "success"
            print("Resetting..")
            time.sleep(0.5)
        else:
            message["message"] = "Current project is not highlighted."
            message["status"] = "error"
        send_status(bp, message)
        return

    if message["type"] == "node":
        GD.pdata["cbnode"] = []
        bp.emit("reset", message)
        response = {}
        response["usr"] = message["usr"]
        response["id"] = "cbscrollbox"
        response["fn"] = "cbaddNode"
        response["val"] = GD.pdata["cbnode"]
        bp.emit("ex", response, namespace="/main", room=flask.session.get("room"))

    if message["type"] == "link":
        GD.pdata["selectedLinks"] = []
        bp.emit("reset", message)


def set_project(bp, project_name):
    print("Setting project..", project_name)
    message = {"id": "projects", "opt": project_name, "fn": "sel"}
    sh.projects(message)
    GD.plist = GD.listProjects()
    print("PROJECT CHANGE")
    GD.data["actPro"] = project_name
    GD.saveGD()
    GD.loadGD()
    GD.loadPFile()
    GD.loadPD()
    GD.loadColor()
    GD.loadLinks()
    GD.load_annotations()
    print("changed Project to " + project_name)
    bp.emit("update", {}, namespace="/main", room=flask.session.get("room"))


def set_layout(bp, id, value):
    message = {"id": id, "opt": value, "fn": "sel"}
    sh.select_menu(message)
    bp.emit("ex", message, namespace="/chat")


def send_result(bp, message):
    bp.emit("result", message)


def send_status(bp, message):
    bp.emit("status", message)


def setup(bp):
    ED.annotationScraper = anntoation_scraper.AnnotationScraper(
        send_result=send_result, bp=bp
    )
    if settings.activate:
        threading.Thread(target=ED.annotationScraper.start, args=(2,)).start()
        ...


def select(bp, message):
    print(message)
    for key in ["type", "annotation", "dtype", "value", "operator"]:
        if key not in message:
            print("ERROR:", key, message)
            return
    message = util.get_selection(message)
    send_result(bp, message)
    if message["type"] == "node":
        update_cbnode(bp)


def update_cbnode(bp):
    response = {}
    response["usr"] = "Server"
    response["id"] = "cbscrollbox"
    response["fn"] = "cbaddNode"
    response["val"] = GD.pdata["cbnode"]
    bp.emit("ex", response, namespace="/main", room=flask.session.get("room"))


def waiter(bp, message):
    response = ED.annotationScraper.wait_for_annotation(message)
    pdata = GD.pdata

    if message["type"] == "node":
        message["selectedAnnot"] = pdata.get("nodeAnnot")
    elif message["type"] == "link":
        message["selectedAnnot"] = pdata.get("linkAnnot")

    if response is not None:
        message.update(response)
    send_result(bp, message)
    pass


def get_annotation(bp, message):
    threading.Thread(
        target=waiter,
        args=(
            bp,
            message,
        ),
    ).start()
    ...


def store_data(message):
    ED.colorbox_data[message["id"]] = message["data"]


def dropdown(bp, message):
    print("DROPDOWN")
    message["name"] = message["msg"]
    if message["id"] in ["util_nodeDD", "util_linkDD"]:
        handleAnnotationDD(bp, message)
    bp.emit("ex", message)


def handleAnnotationDD(bp, message):
    id = message["id"]
    val = message["val"]
    pdata = GD.pdata
    response = {}
    print("ANNOTATION", message)
    if id == "util_nodeDD":
        if pdata.get("nodeAnnot") != val:
            GD.pdata["nodeAnnot"] = val
        response = {"type": "node", "val": val, "fn": "sel"}
    elif id == "util_linkDD":
        if pdata.get("linkAnnot") == val:
            GD.pdata["linkAnnot"] = val
        response = {"type": "link", "val": val, "fn": "sel"}
    bp.emit("annotSel", response)
