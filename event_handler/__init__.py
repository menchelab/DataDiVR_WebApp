from flask_socketio import emit

import plotlyExamples as PE

from . import execute_events, join_events, left_events
from .execute_events import (
    analytics_events,
    annotation_events,
    clipboard_events,
    drop_down_events,
    enrichment_events,
    label_events,
    layout_events,
    ui_events,
    universal_events,

    search_events,
    nodeinfo_events,
    project_events
)


def handle_socket_execute(message, room, project):

    #print("C_DEBUG: handle_socket_execute", message)

    # catch if no message fn
    if "fn" not in message: # or message["fn"] is None:
        #print("C_DEBUG: No function specified in message:", message)
        return None
    
    # catch if no message id
    if "id" not in message: # or message["id"] is None:
        #print("C_DEBUG: No id specified in message:", message)
        return None




    if message["fn"] == "sel":
        ui_events.selection_event(message)

    if message["id"] == "protLoad":
        universal_events.protein_load_event(message, room)


    # --- SEARCH NODE EVENTS --- 
    elif message["id"] == "search": 
        search_events.search_event(message, room) 

        # + automatically trigger the graph plotly update after node event
        message_mod = message.copy()
        message_mod["parent"] = "plotly2js"
        message_mod["msg"] = "Graph"
        message_mod["fn"] = "Plotly2js"
        message_mod["id"] = "plotly2jsB"
        universal_events.plot_to_js_event(message_mod, room)

    elif message["fn"] == "node":
        nodeinfo_events.node_event(message, room) #ui_events.node_event(message, room)
        
        ui_events.highlight_node_and_links_ue4(message, room)


        # + automatically trigger the graph plotly update after node event
        message_mod = message.copy()
        message_mod["parent"] = "plotly2js"
        message_mod["msg"] = "Graph"
        message_mod["fn"] = "Plotly2js"
        message_mod["id"] = "plotly2jsB"
        universal_events.plot_to_js_event(message_mod, room)

    # Chat text message
    elif message["fn"] == "chatmessage":
        universal_events.chat_message_event(message, room)



    # --- NODEPAINT SAVE SELECTION EVENTS --- 
    elif message["fn"] == "saveNodeSelection":
        #print("C_DEBUG: saveNodeSelection event triggered")
        sel_name = message["val"]  
        ui_events.save_node_selection_event(message, room)
   










    # --- UNIVERSAL EVENTS ---
    elif message["id"] == "nl":
        universal_events.node_list_event(message, room)


    # CLIPBOARD
    # TODO: dont save the colors to file but retrieve them from selected color texture
    elif message["id"] == "cbaddNode":
        clipboard_events.add_node_event(message, room)

    elif message["fn"] == "colorbox":
        if message["id"] == "cbColorInput":
            ui_events.colorbox_event(message, room)
        elif message["id"] == "nodePaintColorInput":
            ui_events.colorbox_nodePaint_event(message, room)
        emit("ex", message, room=room)

    elif message["fn"] == "paintnodes":
        if message["id"] == "paintnodes":
            ui_events.paintNodes_event(message, room)

        emit("ex", message, room=room)

    elif message["fn"] == "labelSuggest":
        label_events.suggest_label_event(message, room)

    elif message["fn"] == "selections":
        if message["id"] == "selectionsCb":
            clipboard_events.node_selections_event(message, room)

    elif message["fn"] == "clipboard":
        if message["id"] == "cbClear":
            clipboard_events.clear_event(message, room)
        if message["val"] == "clear":
            clipboard_events.clear_event(message, room)


    # --- ANALYTICS EVENTS --- 
    elif message["fn"] == "analytics":
        analytics_events.main(message, room, project)


    # --- Annotations EVENTS --- 
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
        # ALSO CONTAINS THE PROJECT INITIALIZATION
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


    elif message["fn"] == "children":
        ui_events.children_event(message, room)

    elif message["fn"] == "manLabel":
        ui_events.manLabel_event(message, room)
        
        
    # elif message["fn"] == "but":
    #     if message["id"] == "resetlayout":
    #         ui_events.reset_layout_event(message, room)

    elif message["fn"] == "add_community_to_clipboard":
        analytics_events.add_community_to_clipborad(message, room, project)        
                

    else:
        #print("C_DEBUG: Unknown function in handle_socket_execute:", message)
        emit("ex", message, room=room, namespace = "/main") # quick fix - adding namespace = "/main" to emit