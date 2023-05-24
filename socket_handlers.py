import GlobalData as GD
import search as label_search
from project import Project


def projects(message: dict) -> None:
    """Writes the state data of the current project to its pfile and changes the active project. Project file of the new active project is loaded into GD.pfile and node labels into GD.names. Selected nodes are stored in GD.sessionData["selected"] and selected links are stored in GD.sessionData["selectedLinks"].

    Args:
        message (dict): Socket.IO message
    Returns:
        None
    """
    curr_project = GD.sessionData["actPro"]
    curr_project = Project(curr_project)
    state_data = GD.pfile.get("stateData")
    if not state_data:
        state_data = {}
    curr_project.set_pfile_value("stateData", state_data)
    for key, layout_list in zip(
        ["layouts", "nodecolors", "links", "linkcolors"],
        ["layouts", "layoutsRGB", "links", "linksRGB"],
    ):
        if key not in state_data:
            curr_project.define_pfile_value(
                "stateData", key, curr_project.pfile[layout_list][0]
            )
        for sel in ["selected", "selectedLinks"]:
            if sel not in state_data:
                curr_project.define_pfile_value("stateData", sel, [])
    curr_project.write_pfile()

    GD.sessionData["actPro"] = message["opt"]
    project = Project(GD.sessionData["actPro"])
    project.read_names()
    GD.pfile = project.pfile
    if "stateData" not in GD.pfile:
        GD.pfile["stateData"] = {}
    GD.names = project.names

    print("changed project to " + GD.sessionData["actPro"])
    # print("names_files to " + str(GD.names))
    print("changed activ project " + message["opt"])
    print(message)


def node_labels(message):
    message["names"] = []
    message["fn"] = "cnl"
    message["prot"] = []
    message["protsize"] = []
    for id in message["data"]:
        message["names"].append(GD.names["names"][id][0])

        if len(GD.names["names"][id]) == 5:
            message["prot"].append(GD.names["names"][id][3])
            message["protsize"].append(GD.names["names"][id][4])
        else:
            message["prot"].append("x")
            message["protsize"].append(-1)


def add_node(selected_id):
    stateData = GD.pfile.get("stateData")
    if stateData is None:
        stateData = {}
    selected = stateData.get("selected")
    if selected is None:
        selected = []
    if selected_id not in selected:
        selected.append(selected_id)
    stateData["selected"] = selected
    GD.pfile["stateData"] = stateData
    print(GD.pfile["stateData"]["selected"])
    GD.save_pfile(GD.pfile)


def node_selection(message):
    selected_id = int(message["data"])
    add_node(selected_id)


def sres_button_clicked(message):
    selected_id = int(message["id"])
    add_node(selected_id)


def slider(message):
    main_slider = [
        "slider-node_size",
        "slider-link_size",
        "slider-link_transparency",
        "slider-label_scale",
    ]
    if message["id"] in main_slider:
        if "stateData" not in GD.pfile:
            GD.pfile["stateData"] = {}
        GD.pfile["stateData"][message["id"]] = message["val"]
        GD.save_pfile(GD.pfile)


def select_menu(message):
    id_map = {
        "layouts": "layouts",
        "nodecolors": "layoutsRGB",
        "links": "links",
        "linkcolors": "linksRGB",
    }
    main_menus = ["layouts", "nodecolors", "links", "linkcolors"]
    if message["id"] in main_menus:
        if "stateData" not in GD.pfile:
            GD.pfile["stateData"] = {}
        pfile_key = id_map.get(message["id"])
        if pfile_key and message["opt"] in GD.pfile[pfile_key]:
            GD.pfile["stateData"][message["id"]] = message["opt"]
            GD.save_pfile(GD.pfile)
            return
        exit()


def tab(message):
    tab_ids = ["tabs", "nodepanel_tabs"]
    if message["id"] in tab_ids:
        tab_id = message["id"]
        if "stateData" not in GD.pfile:
            GD.pfile["stateData"] = {}
        if tab_id == "tabs":
            tab_id = "main_tab"

        GD.pfile["stateData"][tab_id] = message["msg"]
        GD.save_pfile(GD.pfile)


def search(message):
    results = {"id": "sres", "val": [], "fn": "sres"}
    project = Project(GD.sessionData["actPro"])
    if project.origin:
        project = project.origin
    else:
        project = project.name
    results["val"] = label_search.search(message["val"], project)
    return results


def get_stateData(message):
    ids = message.get("ids")
    values = {}
    sateData = GD.pfile.get("stateData")
    for id in ids:
        if id == "projects":
            values[id] = GD.sessionData["actPro"]
            continue

        if sateData:
            values[id] = sateData.get(id)
    return values
