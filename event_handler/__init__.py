from flask_socketio import emit

import plotlyExamples as PE

from . import execute_events, join_events, left_events
from .execute_events import (
    analytics_events,
    annotation_events,
    clipboard_events,
    drop_down_events,
    enrichment_events,
    layout_events,
    ui_events,
    universal_events,
)


def handle_socket_execute(message, room, project):
    if message["fn"] == "sel":
        ui_events.selection_event(message)

    if message["id"] == "protLoad":
        universal_events.protein_load_event(message, room)

    if message["id"] == "search":
        universal_events.search_event(message, room)

    # Chat text message
    if message["fn"] == "chatmessage":
        universal_events.chat_message_event(message, room)

    elif message["id"] == "nl":
        universal_events.node_list_event(message, room)

    # CLIPBOARD
    # TODO: dont save the colors to file but retrieve them from selected color texture
    elif message["id"] == "cbaddNode":
        clipboard_events.add_node_event(message, room)

    elif message["fn"] == "colorbox":
        if message["id"] == "cbColorInput":
            ui_events.colorbox_event(message, room)

        emit("ex", message, room=room)

    elif message["fn"] == "selections":
        if message["id"] == "selectionsCb":
            clipboard_events.node_selections_event(message, room)

    elif message["fn"] == "legend_scene_display":
        ui_events.legend_scene_display_event(message, room)

    elif message["fn"] == "clipboard":
        if message["id"] == "cbClear":
            clipboard_events.clear_event(message, room)

    elif message["fn"] == "analytics":
        analytics_events.main(message, room, project)

    elif message["fn"] == "annotation":
        if message["id"] == "annotationOperation":
            annotation_events.annotation_operation_event(message, room)

        if message["id"] == "annotationRun":
            annotation_events.annotation_run_event(message, room)

        if message["id"] == "annotationCb":
            annotation_events.annotation_clipboard_event(message, room)

    elif message["fn"] == "annotationDD":
        annotation_events.annoation_dd_event(message, room)

    elif message["fn"] == "layout":
        layout_events.main(message, room)

    elif message["fn"] == "module":
        universal_events.module_event(message, room)

    elif message["fn"] == "enrichment":
        enrichment_events.main(message, room)

    elif message["fn"] == "dropdown":
        drop_down_events.main(message, room)

    # EXPERIMENTAL dynamic svg creation with matplotlib
    elif message["fn"] == "showSVG":
        emit("ex", PE.matplotsvg(message), room=room)

    # EXPERIMENTAL saving html file to disk
    elif message["fn"] == "showPlotly":
        emit("ex", PE.writeHtml(), room=room)

    elif message["fn"] == "Plotly2js":
        universal_events.plot_to_js_event(message, room)

    elif message["fn"] == "submit_butt":
        ui_events.submit_event(message, room)

    elif message["fn"] == "sli":
        ui_events.slider_event(message, room)

    elif message["fn"] == "node":
        ui_events.node_event(message, room)

    elif message["fn"] == "children":
        ui_events.children_event
    else:
        emit("ex", message, room=room)
