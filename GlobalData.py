import json
import os.path
import threading
from collections import OrderedDict
from os import path

from PIL import Image

import util


# idata = {'mes': 'dfhdfhfh', 'usr': 'NaS7QA89nxLg9nKQAAAn', 'tag': 'flask'}

# scb1Data = ["TMP","MMU", "PAM", "CHR", "OMG","WTF","HH2H","ASS1"]
# pairs = [("a", "1"), ("b", "2"), ("c", "3")]
# sliders = [("ddfd", "1"), ("bfsd", "2"), ("cdfsdf", "3")]

# prolist = json.dumps(listProjects())
# x = '{"proj": ["ere","rrr"], "actPro": "C_CUBE"}'
# sessionData = json.loads(x)
# global
# sessionData = {}
data = {}  # GD.json
# project
plist = []
pfile = {}
pdata = {}

# Guards the "which project is active" critical section (data["actPro"],
# pfile, pdata, links, annotations - all swapped out wholesale on a project
# switch) against a concurrent, unrelated GD.pdata write from another client's
# request (e.g. a layout/color/link dropdown selection). Without this lock, a
# write like "GD.pdata[key] = val; savePD()" that happens to interleave
# between a switch's data["actPro"] reassignment and loadPD() re-populating
# pdata for the new project ends up saving an old project's dropdown value
# into the new project's pdata.json - corrupting it permanently (every later
# load of that project reads the same wrong, persisted index back) rather
# than just being a one-off race.
project_switch_lock = threading.Lock()
nodes = {}
links = {}
names = {}
functions = {"ex": [], "join": [], "left": []}
paintedNodes = []
paintedNodesColor = (128,0,255,255)
annotations = {}  # categorical annotations map: type -> {term: [node_ids]}
annotation_types = (
    []
)  # stores types of annotations, per default if no types exist it holds only "default"
annotations_numeric = {}  # numeric annotations map: type -> {node_id: value}
annotation_types_numeric = []  # stores types of numeric annotations


# todo deal with multiple linklists
nchildren = []

pixel_valuesc = []

session_data = (
    {}
)  # caching data computed in expensive algorithms once during session -> key: str of algorithm id, value result of algoriuthm/function
# ideas to improve performance and avoid large data problems:
# - cache size limit -> might rewrite all functions which use and produce this data to not store it and retreive it afterwards but skip this process if data size is to big
# - LRU approach to kill things which are never used (maybe combine with first one) -> using ordered dict
# - expiration limits to keep it lightweight using timestamps (might be hard since id need to regularly check it but maybe still useful)
# - serialization like pickling big objects (maybe graph)


def socket_execute(func):
    functions["ex"].append(func)


def socket_join(func):
    functions["join"].append(func)


def socket_left(func):
    functions["left"].append(func)


def listProjects():
    # add catch if folder does not exist
    if not path.exists("static/projects"):
        os.mkdir("static/projects")
         
    folder = "static/projects"
    sub_folders = [
        name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))
    ]
    return sub_folders

def listExampleProjects():
    folder = "static/demo_project"
    sub_folders = [
        name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))
    ]
    return sub_folders


def checkProjectGDexists():

    global data
    example_projects = listExampleProjects()
    all_projects = listProjects()

    # this is not necessary due to catch in uploader.check_ProjectFolder() 
    # # in case of GD json not exists
    # if not path.exists("static/projects/GD.json"):
    #     data = {}
    #     data["actPro"] = example_projects[0]
    #     with open("static/projects/GD.json", "w") as json_file:
    #         json.dump(data, json_file, indent="\t")
    
    #if path.exists("static/projects/GD.json"):
    
    with open("static/projects/GD.json", "r") as json_file:
        data = json.load(json_file)

    # if project does not exist, set to example project 
    if not path.exists("static/projects/" + data["actPro"]):
        try:
            data["actPro"] = all_projects[0]
        except:
            data["actPro"] = example_projects[0]
        with open("static/projects/GD.json", "w") as json_file:
            json.dump(data, json_file, indent="\t")
            #print("C_DEBUG: Project set to example project since GD.json project not existing ", data["actPro"])

    json_file.close()
    


# how to save and load GD?
def loadGD():
    global plist
    plist = listProjects()
    # print(globals())
    
    with open("static/projects/GD.json", "r") as json_file:
        data = json.load(json_file)   

    json_file.close()
    # global sessionData
    # sessionData["actPro"] = data["actPro"]


def loadPFile():
    global pfile
    with open("static/projects/" + data["actPro"] + "/pfile.json", "r") as json_file:
        pfile = json.load(json_file)
    json_file.close()

    # sync legendfiles from the legends/ folder so dropping files there is sufficient
    _legend_exts = {'.jpg', '.jpeg', '.png', '.gif', '.html', '.htm'}
    _legends_dir = "static/projects/" + data["actPro"] + "/legends"
    if path.exists(_legends_dir):
        _files = sorted(
            f for f in os.listdir(_legends_dir)
            if os.path.splitext(f)[1].lower() in _legend_exts
        )
        if _files != pfile.get("legendfiles", []):
            pfile["legendfiles"] = _files
            savePFile()


def loadPD():
    # print(globals())
    global pdata
    global nodes
    global links

    global session_data
    session_data = {}  # empty session data on changing project

    if not path.exists("static/projects/" + data["actPro"] + "/pdata.json"):
        with open("static/projects/" + data["actPro"] + "/pdata.json", "w") as outfile:
            json.dump({}, outfile, indent="\t")  # always use empty dict — global pdata may carry stale values from previous project
            outfile.close()
            print("pdata created")

    with open("static/projects/" + data["actPro"] + "/pdata.json", "r") as json_file:
        pdata = json.load(json_file)
        #print(pdata)
        json_file.close()

    with open("static/projects/" + data["actPro"] + "/nodes.json", "r") as json_file:
        nodes = json.load(json_file)
        nodes = util.prepare_protein_structures(nodes)
        json_file.close()

    if path.exists("static/projects/" + data["actPro"] + "/links.json"):
        with open(
            "static/projects/" + data["actPro"] + "/links.json", "r"
        ) as json_file:

            links = json.load(json_file)
            print("links.json loaded")

        json_file.close()
    else:
        links = {}


def saveGD():

    with open("static/projects/GD.json", "w") as outfile:
        json.dump(data, outfile, indent="\t")
        # print(data)
    outfile.close()


def savePD():
    with open("static/projects/" + data["actPro"] + "/pdata.json", "w") as outfile:
        json.dump(pdata, outfile, indent="\t")
        # print(data)
    outfile.close()


def savePFile():
    with open("static/projects/" + data["actPro"] + "/pfile.json", "w") as outfile:
        json.dump(pfile, outfile, indent="\t")
        # print(data)
    outfile.close()


def safe_pdata_index(pdata_key, options):
    """
    Returns a valid int index into `options` for GD.pdata[pdata_key].

    pdata.json is only loaded/saved per-project and is never re-validated
    against the current pfile.json lists (e.g. layoutsRGB), so a stored
    index can go stale and out of range - e.g. after a project's layouts
    were reorganized, or from a forward/backward step that briefly desynced
    the layout-family dropdowns. Rather than let callers do
    `pfile[key][int(pdata[pdata_key])]` and risk an IndexError, clamp here
    and persist the corrected value so it doesn't keep tripping.
    """
    if not options:
        return 0
    try:
        idx = int(pdata.get(pdata_key, 0))
    except (TypeError, ValueError):
        idx = 0
    if not (0 <= idx < len(options)):
        print(f"C_DEBUG: safe_pdata_index - pdata['{pdata_key}']={pdata.get(pdata_key)!r} "
              f"out of range for {len(options)} option(s), resetting to 0")
        idx = 0
        pdata[pdata_key] = 0
        savePD()
    return idx


def loadColor():
    try:
        imc = Image.open(
            "static/projects/"
            + data["actPro"]
            + "/layoutsRGB/"
            + pfile["layoutsRGB"][0]
            + ".png",
            "r",
        )
        global pixel_valuesc

        pixel_valuesc = list(imc.getdata())
        
        #print("C_DEBUG: pixel_valuesc = ", pixel_valuesc[:20])  
        
        print(
            "static/projects/"
            + data["actPro"]
            + "/layoutsRGB/"
            + pfile["layoutsRGB"][0]
            + ".png loaded"
        )
    except:
        print(
            "static/projects/"
            + data["actPro"]
            + "/layoutsRGB/"
            + pfile["layoutsRGB"][0]
            + ".png failed to load"
        )



def loadXYZTex():
    try:
        imc = Image.open(
            "static/projects/"
            + data["actPro"]
            + "/layouts/"
            + pfile["layouts"][0]
            + ".bmp",
            "r",
        )

        pixel_valuesc_test = list(imc.getdata())
        
        #print("C_DEBUG: pixel_valuesc_test = ", pixel_valuesc_test[:20])  
        
        print(
            "static/projects/"
            + data["actPro"]
            + "/layouts/"
            + pfile["layouts"][0]
            + ".bmp loaded"
        )
    except:
        print(
            "static/projects/"
            + data["actPro"]
            + "/layouts/"
            + pfile["layouts"][0]
            + ".bmp failed to load"
        )
        
    return pixel_valuesc_test



def loadLinks():
    # make a lookup table for each nodes children
    global nchildren
    global nodes
    nchildren = [[] for i in range(len(nodes["nodes"]))]

    if path.exists("static/projects/" + data["actPro"] + "/links.json"):
        with open(
            "static/projects/" + data["actPro"] + "/links.json", "r"
        ) as json_file:

            links = json.load(json_file)
            for l in links["links"]:
                if int(l["e"]) not in nchildren[int(l["s"])]:
                    nchildren[int(l["s"])].append(int(l["e"]))
                if int(l["s"]) not in nchildren[int(l["e"])]:
                    nchildren[int(l["e"])].append(int(l["s"]))

            print("links.json loaded")
        json_file.close()
    # print(nchildren)


def load_annotations_simple_old():
    global annotations
    global annotation_types
    annotation_types = ["default"]
    temp_annotations = {}
    for node in nodes["nodes"]:
        if "attrlist" not in node.keys():
            continue

        # efficient filtering of annotation which are not strings (i.e. json) or name of node
        valid_annotations = [
            annotation
            for annotation in node["attrlist"]
            if isinstance(annotation, str) and annotation != node["n"]
        ]

        for annotation in valid_annotations:
            if annotation not in temp_annotations:
                temp_annotations[annotation] = []
            temp_annotations[annotation].append(node["id"])
    annotations = OrderedDict(
        sorted(temp_annotations.items(), key=lambda x: x[0].lower())
    )  # annotations initilized increasing alphabetically


def _is_number(value):
    # bool is technically an int subclass in Python - exclude it, it's categorical
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _add_categorical_annotation(anno_type, term, node_id):
    if anno_type not in annotation_types:
        annotation_types.append(anno_type)
        annotations[anno_type] = {}
    if term not in annotations[anno_type]:
        annotations[anno_type][term] = []
    annotations[anno_type][term].append(node_id)


def _add_numeric_annotation(anno_type, value, node_id):
    if anno_type not in annotation_types_numeric:
        annotation_types_numeric.append(anno_type)
        annotations_numeric[anno_type] = {}
    annotations_numeric[anno_type][node_id] = value


def _classify_attr_value(anno_type, value, node_id):
    """
    Routes a single attribute value to the categorical or numeric annotation
    store based on its actual runtime type, so a mix of shapes within one
    project's attrlist (e.g. CDK5: scalar entrezID next to a GO:BP term list;
    Silhouettes_attributes: a nested similarity_scores dict next to single-value
    numeric attributes) is handled per-attribute instead of forcing one shape
    for the whole project.

    Handles: scalar string (-> single-value category), scalar number (-> numeric),
    list of strings (-> one category per item), list of numbers (-> numeric, mean
    of the list), and one level of nested dict (flattened into "type.subkey",
    recursively classified - covers e.g. {"similarity_scores": {"circle": 0.42}}).
    Anything else (None, bool, empty list, unsupported type) is skipped.
    """
    if value is None:
        return
    if isinstance(value, dict):
        for subkey, subvalue in value.items():
            _classify_attr_value(f"{anno_type}.{subkey}", subvalue, node_id)
        return
    if isinstance(value, list):
        if len(value) == 0:
            return
        if all(_is_number(v) for v in value):
            _add_numeric_annotation(anno_type, sum(value) / len(value), node_id)
        else:
            for v in value:
                if isinstance(v, str):
                    _add_categorical_annotation(anno_type, v, node_id)
        return
    if _is_number(value):
        _add_numeric_annotation(anno_type, value, node_id)
        return
    if isinstance(value, str):
        _add_categorical_annotation(anno_type, value, node_id)
        return
    # unsupported scalar type (e.g. bool) - skip


def load_annotations_complex():
    global annotations, annotation_types, annotations_numeric, annotation_types_numeric
    annotation_types = []
    annotations = {}
    annotation_types_numeric = []
    annotations_numeric = {}

    for node in nodes["nodes"]:
        if "attrlist" not in node.keys():
            continue

        attrlist = node["attrlist"]
        if not isinstance(attrlist, dict):
            # anomaly: this project is flagged as typed (annotationTypes=True) but
            # this one node doesn't follow that shape - skip just this node rather
            # than discarding every other node's already-classified attributes.
            print(f"C_DEBUG: node {node.get('id')} attrlist is not a dict, skipping for annotations.")
            continue

        for anno_type, anno_value in attrlist.items():
            _classify_attr_value(anno_type, anno_value, node["id"])


def load_annotations_simple():
    global annotations, annotation_types, annotations_numeric, annotation_types_numeric
    annotation_types = ["default"]
    annotations = {"default": {}}
    annotation_types_numeric = []
    annotations_numeric = {}

    for node in nodes["nodes"]:
        if "attrlist" not in node.keys():
            continue

        anno_list = node["attrlist"]
        if not isinstance(anno_list, list):
            continue

        for idx, anno in enumerate(anno_list):
            if idx == 0 and anno == node["n"]:
                continue
            _classify_attr_value("default", anno, node["id"])


def load_annotations():
    if "annotationTypes" not in pfile.keys():
        pfile["annotationTypes"] = False  # assuming to be False for old projects
        savePFile()

    # current solution -> enhance by keeping only complex function and deprecate simple
    if pfile["annotationTypes"] is False:
        load_annotations_simple()
    else:
        load_annotations_complex()




