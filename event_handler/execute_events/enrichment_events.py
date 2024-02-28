from flask_socketio import emit

import enrichment_module
import GlobalData as GD


def init(message, room):
    message["fn"] = "enrichment"
    if "enrichment_query" not in GD.pdata.keys():
        GD.pdata["enrichment_query"] = []
        GD.savePD()
    message["valQuery"] = GD.pdata["enrichment_query"]
    if "annotationTypes" not in GD.pfile.keys():
        # assumption: if flag is not set it will most likely be false
        GD.pfile["annotationTypes"] = False
        GD.savePFile()
    message["valHideNote"] = GD.pfile["annotationTypes"]
    emit("ex", message, room=room)


def import_event(message, room):
    enrichment_module.query_from_clipboard()
    message["fn"] = "enrichment"
    message["val"] = GD.pdata["enrichment_query"]
    emit("ex", message, room=room)


def clear_event(message, room):
    enrichment_module.query_clear()
    message["fn"] = "enrichment"
    message["val"] = []
    emit("ex", message, room=room)


def run_event(message, room):
    if not enrichment_module.validate():
        return

    result_plot, highlight_payload, highlight_texture_obj, display_note = (
        enrichment_module.main(highlight=message.get("val", None))
    )
    if result_plot is not None:
        message["fn"] = "enrichment"
        message["valPlot"] = result_plot
        message["valPayload"] = highlight_payload
        emit("ex", message, room=room)

    if display_note is not None:
        response_note = {}
        response_note["usr"] = message["usr"]
        response_note["fn"] = "enrichment"
        response_note["id"] = "enrichment-note-result"
        response_note["val"] = display_note
        emit("ex", response_note, room=room)

    if highlight_texture_obj is None:
        return

    if highlight_texture_obj["textures_created"] is False:
        print("Failed to create textures for Enrichment.")
        return

    response_colors = {}
    response_colors["usr"] = message["usr"]
    response_colors["fn"] = "enrichment"
    response_colors["id"] = "enrichment-colors"
    response_colors["val"] = True
    emit("ex", response_colors, room=room)

    response_textures = {}
    response_textures["usr"] = message["usr"]
    response_textures["fn"] = "updateTempTex"
    response_textures["textures"] = []
    response_textures["textures"].append(
        {
            "channel": "nodeRGB",
            "path": highlight_texture_obj["path_nodes"],
        }
    )
    response_textures["textures"].append(
        {
            "channel": "linkRGB",
            "path": highlight_texture_obj["path_links"],
        }
    )
    emit("ex", response_textures, room=room)


def plot_click_event(message, room):
    # TODO: implement
    print("TODO: plot responsive")


def main(message, room):
    response = {"usr": message["usr"], "id": message["id"]}
    if message["id"] == "init":
        init(response, room)

    elif message["id"] == "enrichment-import":
        import_event(response, room)

    elif message["id"] == "enrichment-clear":
        clear_event(response, room)
        return

    elif message["id"] == "enrichment-run":
        run_event(response, room)
        return

    if message["id"] == "enrichment-plotClick":
        plot_click_event(response, room)
