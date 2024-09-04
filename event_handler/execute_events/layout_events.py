from flask_socketio import emit

import GlobalData as GD
import layout_module
import util


def init_event(message, room):
    if message["val"] != "init":
        return
    # session data initialisation
    check_log = layout_module.init_client_display_log()
    # check if selected layout type already exists in session_data to handle button display
    # use sel from global data on drop down and use it as key to store and check for layout results
    check_existing_layout = layout_module.init_client_layout_exists()

    response = {}
    response["usr"] = message["usr"]
    response["id"] = message["id"]
    response["fn"] = "layout"
    response["val"] = {
        "showLog": check_log,
        "selectedLayoutGenerated": check_existing_layout,
    }
    emit("ex", response, room=room)


def log_show_hide_event(message, room, show=True):
    layout_module.show_log()
    response = {}
    response["usr"] = message["usr"]
    response["id"] = "showLog"
    response["fn"] = "layout"
    response["val"] = show
    emit("ex", response, room=room)


# LAYOUT POS 0
def random_apply_event(message, room):
    layout_id = layout_module.LAYOUT_IDS[0]  # 0 -> random layout

    # write log starting
    response_log = {}
    response_log["usr"] = message["usr"]
    response_log["id"] = "addLog"
    response_log["fn"] = "layout"
    response_log["log"] = {
        "type": "log",
        "msg": "Random layout generation running ...",
    }
    emit("ex", response_log, room=room)

    # retreive data and get layout positions
    if layout_id not in GD.session_data["layout"]["results"].keys():
        if "graph" not in GD.session_data.keys():
            GD.session_data["graph"] = util.project_to_graph(GD.data["actPro"])
        graph = GD.session_data["graph"]
        result_obj = layout_module.layout_random(ordered_graph=graph)
        if result_obj["success"] is False:
            print("ERROR: ", result_obj["error"])
            response_log["log"] = result_obj["log"]
            emit("ex", response_log, room=room)
            return

        GD.session_data["layout"]["results"][layout_id] = result_obj["content"]

    # generate layout textures
    positions = GD.session_data["layout"]["results"][layout_id]
    result_obj = layout_module.pos_to_textures(positions)
    if result_obj["success"] is False:
        print("ERROR: ", result_obj["error"])

        response_log["log"] = result_obj["log"]
        emit("ex", response_log, room=room)
        return

    # write log finish
    response_log["log"] = {
        "type": "log",
        "msg": "Generated random layout successfully.",
    }
    emit("ex", response_log, room=room)

    # display rerun and save buttons
    response_layout_exists = {}
    response_layout_exists["usr"] = message["usr"]
    response_layout_exists["fn"] = "layout"
    response_layout_exists["id"] = "layoutExists"
    response_layout_exists["val"] = layout_module.check_layout_exists()
    emit("ex", response_layout_exists, room=room)

    # update temp layout
    response = {}
    response["usr"] = message["usr"]
    response["fn"] = "updateTempTex"
    response["textures"] = result_obj["textures"]
    emit("ex", response, room=room)
    return


# LAYOUT POS 1
def forcedirected_apply_event(message, room):
    layout_id = layout_module.LAYOUT_IDS[1]  # 1 -> spring layout

    # write log starting
    response_log = {}
    response_log["usr"] = message["usr"]
    response_log["id"] = "addLog"
    response_log["fn"] = "layout"
    response_log["log"] = {
        "type": "log",
        "msg": "Spring layout generation running ...",
    }
    emit("ex", response_log, room=room)

    # retreive data and get layout positions
    if layout_id not in GD.session_data["layout"]["results"].keys():
        if "graph" not in GD.session_data.keys():
            GD.session_data["graph"] = util.project_to_graph(GD.data["actPro"])
        graph = GD.session_data["graph"]
        result_obj = layout_module.layout_forcedirected(ordered_graph=graph)
        if result_obj["success"] is False:
            print("ERROR: ", result_obj["error"])
            response_log["log"] = result_obj["log"]
            emit("ex", response_log, room=room)
            return

        GD.session_data["layout"]["results"][layout_id] = result_obj["content"]

    # generate layout textures
    positions = GD.session_data["layout"]["results"][layout_id]
    result_obj = layout_module.pos_to_textures(positions)
    if result_obj["success"] is False:
        print("ERROR: ", result_obj["error"])

        response_log["log"] = result_obj["log"]
        emit("ex", response_log, room=room)
        return

    # write log finish
    response_log["log"] = {
        "type": "log",
        "msg": "Generated Spring layout successfully.",
    }
    emit("ex", response_log, room=room)

    # display rerun and save buttons
    response_layout_exists = {}
    response_layout_exists["usr"] = message["usr"]
    response_layout_exists["fn"] = "layout"
    response_layout_exists["id"] = "layoutExists"
    response_layout_exists["val"] = layout_module.check_layout_exists()
    emit("ex", response_layout_exists, room=room)

    # update temp layout
    response = {}
    response["usr"] = message["usr"]
    response["fn"] = "updateTempTex"
    response["textures"] = result_obj["textures"]
    emit("ex", response, room=room)
    return


# LAYOUT POS 2
def eigen_apply_event(message, room):
    layout_id = layout_module.LAYOUT_IDS[2]  # 2 -> eigen layout

    # write log starting
    response_log = {}
    response_log["usr"] = message["usr"]
    response_log["id"] = "addLog"
    response_log["fn"] = "layout"
    response_log["log"] = {
        "type": "log",
        "msg": "Eigenlayout generation running ...",
    }
    emit("ex", response_log, room=room)

    # retreive data and get layout positions
    if layout_id not in GD.session_data["layout"]["results"].keys():
        if "graph" not in GD.session_data.keys():
            GD.session_data["graph"] = util.project_to_graph(GD.data["actPro"])
        graph = GD.session_data["graph"]
        result_obj = layout_module.layout_eigen(ordered_graph=graph)
        if result_obj["success"] is False:
            print("ERROR: ", result_obj["error"])
            response_log["log"] = result_obj["log"]
            emit("ex", response_log, room=room)
            return

        GD.session_data["layout"]["results"][layout_id] = result_obj["content"]

    # generate layout textures
    positions = GD.session_data["layout"]["results"][layout_id]
    result_obj = layout_module.pos_to_textures(positions)
    if result_obj["success"] is False:
        print("ERROR: ", result_obj["error"])

        response_log["log"] = result_obj["log"]
        emit("ex", response_log, room=room)
        return

    # write log finish
    response_log["log"] = {
        "type": "log",
        "msg": "Generated Eigenlayout successfully.",
    }
    emit("ex", response_log, room=room)

    # display rerun and save buttons
    response_layout_exists = {}
    response_layout_exists["usr"] = message["usr"]
    response_layout_exists["fn"] = "layout"
    response_layout_exists["id"] = "layoutExists"
    response_layout_exists["val"] = layout_module.check_layout_exists()
    emit("ex", response_layout_exists, room=room)

    # update temp layout
    response = {}
    response["usr"] = message["usr"]
    response["fn"] = "updateTempTex"
    response["textures"] = result_obj["textures"]
    emit("ex", response, room=room)
    return


# LAYOUT POS 3
def carto_local_apply_event(message, room):
    layout_id = layout_module.LAYOUT_IDS[3]  # 3 -> local layout

    # write log starting
    response_log = {}
    response_log["usr"] = message["usr"]
    response_log["id"] = "addLog"
    response_log["fn"] = "layout"
    response_log["log"] = {
        "type": "log",
        "msg": "cartoGRAPHS Local layout generation running ...",
    }
    emit("ex", response_log, room=room)

    # retreive data and get layout positions
    if layout_id not in GD.session_data["layout"]["results"].keys():
        if "graph" not in GD.session_data.keys():
            GD.session_data["graph"] = util.project_to_graph(GD.data["actPro"])
        graph = GD.session_data["graph"]
        result_obj = layout_module.layout_carto_local(ordered_graph=graph)
        if result_obj["success"] is False:
            print("ERROR: ", result_obj["error"])
            response_log["log"] = result_obj["log"]
            emit("ex", response_log, room=room)
            return

        GD.session_data["layout"]["results"][layout_id] = result_obj["content"]

    # generate layout textures
    positions = GD.session_data["layout"]["results"][layout_id]
    result_obj = layout_module.pos_to_textures(positions)
    if result_obj["success"] is False:
        print("ERROR: ", result_obj["error"])

        response_log["log"] = result_obj["log"]
        emit("ex", response_log, room=room)
        return

    # write log finish
    response_log["log"] = {
        "type": "log",
        "msg": "Generated cartoGRAPHS Local layout successfully.",
    }
    emit("ex", response_log, room=room)

    # display rerun and save buttons
    response_layout_exists = {}
    response_layout_exists["usr"] = message["usr"]
    response_layout_exists["fn"] = "layout"
    response_layout_exists["id"] = "layoutExists"
    response_layout_exists["val"] = layout_module.check_layout_exists()
    emit("ex", response_layout_exists, room=room)

    # update temp layout
    response = {}
    response["usr"] = message["usr"]
    response["fn"] = "updateTempTex"
    response["textures"] = result_obj["textures"]
    emit("ex", response, room=room)
    return


# LAYOUT POS 4
def carto_global_apply_event(message, room):
    layout_id = layout_module.LAYOUT_IDS[4]  # 4 -> global layout

    # write log starting
    response_log = {}
    response_log["usr"] = message["usr"]
    response_log["id"] = "addLog"
    response_log["fn"] = "layout"
    response_log["log"] = {
        "type": "log",
        "msg": "cartoGRAPHS Global layout generation running ...",
    }
    emit("ex", response_log, room=room)

    # retreive data and get layout positions
    if layout_id not in GD.session_data["layout"]["results"].keys():
        if "graph" not in GD.session_data.keys():
            GD.session_data["graph"] = util.project_to_graph(GD.data["actPro"])
        graph = GD.session_data["graph"]
        result_obj = layout_module.layout_carto_global(ordered_graph=graph)
        if result_obj["success"] is False:
            print("ERROR: ", result_obj["error"])
            response_log["log"] = result_obj["log"]
            emit("ex", response_log, room=room)
            return

        GD.session_data["layout"]["results"][layout_id] = result_obj["content"]

    # generate layout textures
    positions = GD.session_data["layout"]["results"][layout_id]
    result_obj = layout_module.pos_to_textures(positions)
    if result_obj["success"] is False:
        print("ERROR: ", result_obj["error"])

        response_log["log"] = result_obj["log"]
        emit("ex", response_log, room=room)
        return

    # write log finish
    response_log["log"] = {
        "type": "log",
        "msg": "Generated cartoGRAPHS Global layout successfully.",
    }
    emit("ex", response_log, room=room)

    # display rerun and save buttons
    response_layout_exists = {}
    response_layout_exists["usr"] = message["usr"]
    response_layout_exists["fn"] = "layout"
    response_layout_exists["id"] = "layoutExists"
    response_layout_exists["val"] = layout_module.check_layout_exists()
    emit("ex", response_layout_exists, room=room)

    # update temp layout
    response = {}
    response["usr"] = message["usr"]
    response["fn"] = "updateTempTex"
    response["textures"] = result_obj["textures"]
    emit("ex", response, room=room)
    return


# LAYOUT POS 5 
def carto_importance_apply_event(message, room):
    layout_id = layout_module.LAYOUT_IDS[5]  # 5 -> importance layout

    # write log starting
    response_log = {}
    response_log["usr"] = message["usr"]
    response_log["id"] = "addLog"
    response_log["fn"] = "layout"
    response_log["log"] = {
        "type": "log",
        "msg": "cartoGRAPHS Importance layout generation running ...",
    }
    emit("ex", response_log, room=room)

    # retreive data and get layout positions
    if layout_id not in GD.session_data["layout"]["results"].keys():
        if "graph" not in GD.session_data.keys():
            GD.session_data["graph"] = util.project_to_graph(GD.data["actPro"])
        graph = GD.session_data["graph"]
        result_obj = layout_module.layout_carto_importance(ordered_graph=graph)
        if result_obj["success"] is False:
            print("ERROR: ", result_obj["error"])
            response_log["log"] = result_obj["log"]
            emit("ex", response_log, room=room)
            return

        GD.session_data["layout"]["results"][layout_id] = result_obj["content"]

    # generate layout textures
    positions = GD.session_data["layout"]["results"][layout_id]
    result_obj = layout_module.pos_to_textures(positions)
    if result_obj["success"] is False:
        print("ERROR: ", result_obj["error"])

        response_log["log"] = result_obj["log"]
        emit("ex", response_log, room=room)
        return

    # write log finish
    response_log["log"] = {
        "type": "log",
        "msg": "Generated cartoGRAPHS Importance layout successfully.",
    }
    emit("ex", response_log, room=room)

    # display rerun and save buttons
    response_layout_exists = {}
    response_layout_exists["usr"] = message["usr"]
    response_layout_exists["fn"] = "layout"
    response_layout_exists["id"] = "layoutExists"
    response_layout_exists["val"] = layout_module.check_layout_exists()
    emit("ex", response_layout_exists, room=room)

    # update temp layout
    response = {}
    response["usr"] = message["usr"]
    response["fn"] = "updateTempTex"
    response["textures"] = result_obj["textures"]
    emit("ex", response, room=room)
    return


# LAYOUT POS 6
def spectral_apply_event(message, room):
    layout_id = layout_module.LAYOUT_IDS[6]  # 6 -> spectral layout

    # write log starting
    response_log = {}
    response_log["usr"] = message["usr"]
    response_log["id"] = "addLog"
    response_log["fn"] = "layout"
    response_log["log"] = {
        "type": "log",
        "msg": "Spectral layout generation running ...",
    }
    emit("ex", response_log, room=room)

    # retreive data and get layout positions
    if layout_id not in GD.session_data["layout"]["results"].keys():
        if "graph" not in GD.session_data.keys():
            GD.session_data["graph"] = util.project_to_graph(GD.data["actPro"])
        graph = GD.session_data["graph"]
        result_obj = layout_module.layout_spectral(ordered_graph=graph)
        if result_obj["success"] is False:
            print("ERROR: ", result_obj["error"])
            response_log["log"] = result_obj["log"]
            emit("ex", response_log, room=room)
            return

        GD.session_data["layout"]["results"][layout_id] = result_obj["content"]

    # generate layout textures
    positions = GD.session_data["layout"]["results"][layout_id]
    result_obj = layout_module.pos_to_textures(positions)
    if result_obj["success"] is False:
        print("ERROR: ", result_obj["error"])

        response_log["log"] = result_obj["log"]
        emit("ex", response_log, room=room)
        return

    # write log finish
    response_log["log"] = {
        "type": "log",
        "msg": "Generated spectral layout successfully.",
    }
    emit("ex", response_log, room=room)

    # display rerun and save buttons
    response_layout_exists = {}
    response_layout_exists["usr"] = message["usr"]
    response_layout_exists["fn"] = "layout"
    response_layout_exists["id"] = "layoutExists"
    response_layout_exists["val"] = layout_module.check_layout_exists()
    emit("ex", response_layout_exists, room=room)

    # update temp layout
    response = {}
    response["usr"] = message["usr"]
    response["fn"] = "updateTempTex"
    response["textures"] = result_obj["textures"]
    emit("ex", response, room=room)
    return









def main(message, room):
    if message["id"] == "layoutInit":
        init_event(message, room)

    # handle log display
    if message["id"] == "layoutLogShow":
        log_show_hide_event(message, room)

    if message["id"] == "layoutLogHide":
        log_show_hide_event(message, room, False)

    # layout algorithms
    if message["id"] == "layoutRandomApply":
        random_apply_event(message, room)

    if message["id"] == "layoutFDApply":
        forcedirected_apply_event(message, room)

    if message["id"] == "layoutEigenApply":
        eigen_apply_event(message, room)

    if message["id"] == "layoutCartoLocalApply":
        carto_local_apply_event(message, room)

    if message["id"] == "layoutCartoGlobalApply":
        carto_global_apply_event(message, room)

    if message["id"] == "layoutCartoImportanceApply":
        carto_importance_apply_event(message, room)

    if message["id"] == "layoutSpectralApply":
        spectral_apply_event(message, room)
