import json
import os.path
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
nodes = {}
links = {}
names = {}
functions = {"ex": [], "join": [], "left": []}

annotations = {}  # annotations map
annotation_types = (
    []
)  # stores types of annotations, per default if no types exist it holds only "default"


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
        print(pfile)
    json_file.close()


def loadPD():
    # print(globals())
    global pdata
    global nodes
    global links

    global session_data
    session_data = {}  # empty session data on changing project

    if not path.exists("static/projects/" + data["actPro"] + "/pdata.json"):
        with open("static/projects/" + data["actPro"] + "/pdata.json", "w") as outfile:
            json.dump(pdata, outfile, indent="\t")
            # print(data)
            outfile.close()
            print("pdata created")

    with open("static/projects/" + data["actPro"] + "/pdata.json", "r") as json_file:

        pdata = json.load(json_file)
        print(pdata)

    with open("static/projects/" + data["actPro"] + "/nodes.json", "r") as json_file:

        nodes = json.load(json_file)
        nodes = util.prepare_protein_structures(nodes)

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


def load_annotations_complex():
    global annotations
    global annotation_types
    annotation_types = []
    annotations = {}

    for node in nodes["nodes"]:
        if "attrlist" not in node.keys():
            continue
        
        # check if dict beforehand: 
        if not isinstance(node["attrlist"], dict):
            #print("C_DEBUG: loading annotations simple due to invalid format.")
            load_annotations_simple()
            
        else: 
            for anno_type, anno_list in node["attrlist"].items():

                if anno_type not in annotation_types:
                    annotation_types.append(anno_type)
                    annotations[anno_type] = {}

                # check if anno_list is a list
                if not isinstance(anno_list, list):
                    #print("C_DEBUG: loading annotations simple due to invalid format.")
                    load_annotations_simple()
                    return

                for anno in anno_list:
                    if anno not in annotations[anno_type].keys():
                        annotations[anno_type][anno] = []
                    annotations[anno_type][anno].append(node["id"])


def load_annotations_simple():
    global annotations
    global annotation_types
    annotation_types = ["default"]
    annotations = {"default": {}}

    for node in nodes["nodes"]:
        if "attrlist" not in node.keys():
            continue

        anno_list = node["attrlist"]

        for idx, anno in enumerate(anno_list):
            if idx == 0 and anno == node["n"]:
                continue
            if not isinstance(anno, str):
                continue
            if anno not in annotations["default"].keys():
                annotations["default"][anno] = []
            annotations["default"][anno].append(node["id"])


def load_annotations():
    if "annotationTypes" not in pfile.keys():
        pfile["annotationTypes"] = False  # assuming to be False for old projects
        savePFile()

    # current solution -> enhance by keeping only complex function and deprecate simple
    if pfile["annotationTypes"] is False:
        load_annotations_simple()
    else:
        load_annotations_complex()
