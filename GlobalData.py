import json
from PIL import Image
import os.path
from os import path
import util
from collections import OrderedDict

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
annotations = {}
# todo deal with multiple linklists
nchildren = []

pixel_valuesc = []


def listProjects():
    folder = "static/projects"
    sub_folders = [
        name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))
    ]
    print(sub_folders)
    return sub_folders


# how to save and load GD?
def loadGD():
    global plist
    plist = listProjects()
    # print(globals())
    if path.exists("static/projects/GD.json"):
        with open("static/projects/GD.json", "r") as json_file:
            global data
            data = json.load(json_file)
            if not path.exists("static/projects/" + data["actPro"]):
                print("project does not exist")
    else:
        print("GD.json not found")

    json_file.close()
    # global sessionData
    # sessionData["actPro"] = data["actPro"]


def loadPFile():
    # print(globals())
    with open("static/projects/" + data["actPro"] + "/pfile.json", "r") as json_file:
        global pfile
        pfile = json.load(json_file)
        print(pfile)

    json_file.close()


def loadPD():
    # print(globals())
    global pdata
    global nodes
    global links
    if not path.exists("static/projects/" + data["actPro"] + "/pdata.json"):
        with open("static/projects/" + data["actPro"] + "/pdata.json", "w") as outfile:
            json.dump(pdata, outfile)
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
        json.dump(data, outfile)
        # print(data)
    outfile.close()


def savePD():
    with open("static/projects/" + data["actPro"] + "/pdata.json", "w") as outfile:
        json.dump(pdata, outfile)
        # print(data)
    outfile.close()


def savePFile():
    with open("static/projects/" + data["actPro"] + "/pfile.json", "w") as outfile:
        json.dump(pfile, outfile)
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



#----------------------------------
# GRAPH TITLE + DESCRIPTION 

# loaded at start / page refresh 
def loadGraphinfoFile(): 
    if path.exists("static/projects/" + data["actPro"] + "/graphinfofile.json"):
        with open("static/projects/" + data["actPro"] + "/graphinfofile.json", "r") as json_file:
            global graphinfofile
            graphinfofile = json.load(json_file)
            #print("C_DEBUG in Globaldata: loadGraphInfoFile - loaded.")
            json_file.close()
    else:
        graphinfofile = {"graphtitle":"Graph title not specified.", "graphdesc": "Graph description not specified."}
        #print("C_DEBUG in Globaldata: loadGraphInfoFile - created.")

#----------------------------------

def load_annotations():
    global annotations
    temp_annotations = {}
    for node in nodes["nodes"]:
        if "attrlist" not in node.keys():
            continue
        
        # efficient filtering of annotation which are not strings (i.e. json) or name of node 
        valid_annotations = [annotation for annotation in node["attrlist"] if isinstance(annotation, str) and annotation != node["n"]]

        for annotation in valid_annotations:
            if annotation not in temp_annotations:
                temp_annotations[annotation] = []
            temp_annotations[annotation].append(node["id"])
    annotations = OrderedDict(sorted(temp_annotations.items(), key=lambda x: x[0].lower()))  # annotations initilized increasing alphabetically

    