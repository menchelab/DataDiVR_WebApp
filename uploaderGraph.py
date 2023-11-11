
# use functions from CSV-based uploader 
from matplotlib.colors import hex2color
import re 
import math 

from uploader import *



def hex_to_rgb(hx):
    hx = hx.lstrip('#')
    hlen = len(hx)
    return tuple(int(hx[i:i+hlen//3], 16) for i in range(0, hlen, hlen//3))

def hex_to_rgba(hex_color):
    hex_color = hex_color.lstrip('#')
    rgba_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4, 6))
    return rgba_color

def upload_filesJSON(request):
    form = request.form.to_dict()
    prolist = GD.plist

    namespace = form["namespaceJSON"]
    
    if not namespace:
        return "namespace fail"
    
    if namespace in prolist:
        print('project exists')
    else:
        # Make Folders
        makeProjectFolders(namespace)

    folder = 'static/projects/' + namespace + '/'
    pfile = {}
    with open(folder + 'pfile.json', 'r') as json_file:
        pfile = json.load(json_file)
    json_file.close()

    state = ''
    nodelist = {"nodes":[]}

    #------------------
    # get G_json and fill in parts as required for DataDiVR 
    #------------------
    jsonfiles = []
    nodepositions = []
    nodeinfo = []
    nodecolors = []
    links = []
    linkcolors = []
    labels = []
    

    loadGraphJSON(request.files.getlist("graphJSON"), jsonfiles)

    # decide which annotation type to go with
    # if complex_annotations is True it uses a dict to store annotations and their types
    # referenced by "annotationTypes" as true in uploaded JSON
    complex_annotations = False
    if "annotationTypes" in jsonfiles[0].keys():
        if jsonfiles[0]["annotationTypes"] is True:
            complex_annotations = True


    parseGraphJSON_nodepositions(jsonfiles, nodepositions)

    if complex_annotations is False:    
        parseGraphJSON_nodeinfo_simple(jsonfiles, nodeinfo)
    else:  # complex_annotations is True
        nodeinfo = parseGraphJSON_nodeinfo_complex(jsonfiles)
    
    parseGraphJSON_nodecolors(jsonfiles, nodecolors)
    parseGraphJSON_links(jsonfiles, links)
    parseGraphJSON_linkcolors(jsonfiles, linkcolors)
    parseGraphJSON_labels(jsonfiles, labels)
    names = parseGraphJSON_textureNames(jsonfiles)  # list, containing names for textures defined in uploaded json as "textureName"


    #----------------------------------
    # FOR GRAPH TITLE + DESCRIPTION 
    #----------------------------------
    graphtitle = []
    parseGraphJSON_graphtitle(jsonfiles,graphtitle)
    if len(graphtitle) > 0:
        title_of_graph = graphtitle[0]["graphtitle"]
    else:
        title_of_graph = namespace

    graphdesc = []
    parseGraphJSON_graphdesc(jsonfiles,graphdesc)
    if len(graphdesc) > 0:
        descr_of_graph = graphdesc[0]["graphdesc"]
    else:
        descr_of_graph = "Graph decription not specified."

    numnodes = len(nodepositions[0]["data"])

    # generate node.json
    if complex_annotations is False:
        for i in range(len(nodepositions[0]["data"])):
            thisnode = {}
            thisnode["id"] = i
            if "_geo" in nodepositions[0]["name"]:
                thisnode["lat"] = nodepositions[0]["data"][i][0]
                thisnode["lon"] = nodepositions[0]["data"][i][1]

            if len(nodeinfo[0]["data"]) == len(nodepositions[0]["data"]):
                thisnode["attrlist"] = nodeinfo[0]["data"][i]
                thisnode["n"] = str(nodeinfo[0]["data"][i][0]) # show first element in node annotation for node label

            else:
                thisnode["attrlist"] = ["node" + str(i)]
                thisnode["n"] = "node" + str(i)

            nodelist["nodes"].append(thisnode)
    
    else: # complex_annotations is True -> annotation types and name specified
        for i in range(len(nodeinfo)):
            this_node = {}
            this_node["id"] = i
            this_node["n"] = nodeinfo[i]["name"]
            this_node["attrlist"] = nodeinfo[i]["annotation"]
            nodelist["nodes"].append(this_node)

    
    for labellist in labels:   
        name = ""
        i = 0

        if "data" in labellist:

            for row in labellist["data"]:

                name = row[0]

                row.pop(0)
                # add to nodes.json
                thisnode = {}
                thisnode["id"] = i + numnodes
                thisnode["group"] = row
                thisnode["n"] = str(name)
                nodelist["nodes"].append(thisnode)

                #add to pfile
                pfile["selections"].append({"name":name, "nodes":row, "layoutname": labellist["name"]})               
                #print("C_DEBUG : pfile selections= ", pfile["selections"])


                # get average pos for Each layout            
                for layout in nodepositions:
                    accPos = [0,0,0]
                    pos = [0,0,0]

                    for x in row:

                        # catch for 2D positions for labels and for empty rows
                        if len(x) > 0 and len(layout["data"][int(x)]) == 3:
                            accPos[0] += float(layout["data"][int(x)][0])
                            accPos[1] += float(layout["data"][int(x)][1])
                            accPos[2] += float(layout["data"][int(x)][2])
                        
                        elif len(x) > 0 and len(layout["data"][int(x)]) == 2: 
                            accPos[0] += float(layout["data"][int(x)][0])
                            accPos[1] += float(layout["data"][int(x)][1])
                            accPos[2] += 0.0

                    pos[0] = str(accPos[0] / len(row))
                    pos[1] = str(accPos[1] / len(row))
                    pos[2] = str(accPos[2] / len(row))
                    layout["data"].append(pos)

                # label nodes to be black
                for color in nodecolors:
                    color["data"].append((0,0,0,0)) # 60,60,60,60

                i += 1
        else: 
            pass
        

    for file_index in range(len(nodepositions)):  # for layout in nodepositions:
        layout = nodepositions[file_index]
        if len(layout["data"]) > 0 and len(layout["data"][int(0)]) == 3:

            if names[file_index] is not None:
                # if texture name specified
                state =  state + makeXYZTexture(namespace, layout, names[file_index]) + '<br>'
                pfile["layouts"].append(names[file_index])    
                continue
            state =  state + makeXYZTexture(namespace, layout) + '<br>'
            pfile["layouts"].append(layout["name"] + "XYZ")

        # catch for 2D positions and for empty rows
        elif len(layout["data"]) > 0 and len(layout["data"][int(x)]) == 2:
            for i,xy in enumerate(layout["data"]):
                layout["data"][i] = (xy[0],xy[1],0.0)
            
            if names[file_index] is not None:
                # if texture name specified
                state =  state + makeXYZTexture(namespace, layout, names[file_index]) + '<br>'
                pfile["layouts"].append(names[file_index])    
                continue 
            state =  state + makeXYZTexture(namespace, layout) + '<br>'
            pfile["layouts"].append(layout["name"] + "XYZ")

        else: state = "upload must contain at least 1 node position list"
        
    # match labels to respective layout to get label colors for legend
    if len(pfile["selections"]) > 0:
        all_layouts = pfile["layouts"]
        #print("C_DEBUG: all_layouts: ", all_layouts)

        for e,subdict in enumerate(pfile["selections"]):
            layoutname_pfile = pfile["selections"][e]["layoutname"]+"XYZ"
            #print("C_DEBUG: layoutname_pfile: ", layoutname_pfile)

            for x,i in enumerate(all_layouts):        
                if i == layoutname_pfile:     

                    # get unique cluster values :
                    unique_clusters_firstnode = []
                    for lab in labels[x]["data"]:
                        if lab not in unique_clusters_firstnode:
                            unique_clusters_firstnode.append(lab[0]) # get id of first node in cluster to match with color 
                    
                    # get cluster colors based on first node id in cluster 
                    clustercolors = []
                    for nodeid in unique_clusters_firstnode:             
                        if nodeid == str(nodelist["nodes"][int(nodeid)]["id"]):
                            nodecol = nodecolors[x]["data"][int(nodeid)]
                            clustercolors.append(nodecol)
                        #print("C_DEBUG : CLUSTERCOLORS : ", clustercolors)

                        if nodeid in pfile["selections"][e]["nodes"]:
                            pfile["selections"][e]["labelcolor"] = nodecol # clustercolors
                            #print("C_DEBUG: pfile[selections][clustername and labelcolor] : ", (pfile["selections"][e]["name"], pfile["selections"][e]["labelcolor"]))

        pfile["labelcount"] = len(labels[x]["data"])

    else:
        print("C_DEBUG: project does not contain labels/clusters.")
        pfile["labelcount"] = 0


    for file_index in range(len(nodecolors)):  # for color in nodecolors:
        
        color = nodecolors[file_index]

        if len(color["data"]) == 0:
            color["data"] = [[255,0,255,100]] * numnodes
            color["name"] = "nan"
        if names[file_index] is not None:
            # if texture name specified
            state =  state + makeNodeRGBTexture(namespace, color, names[file_index]) + '<br>'
            pfile["layoutsRGB"].append(names[file_index])    
            continue
        state =  state + makeNodeRGBTexture(namespace, color) + '<br>'
        pfile["layoutsRGB"].append(color["name"]+ "RGB")

    
    for file_index in range(len(links)):  # for linklist in links:
        linklist = links[file_index]

        if len(linklist["data"]) == 0:
            linklist["name"] = "nan"

        if names[file_index] is not None:
            # if texture name specified
            state =  state + makeLinkTexNew(namespace, linklist, names[file_index]) + '<br>'
            pfile["links"].append(names[file_index])    
            continue
        state =  state + makeLinkTexNew(namespace, linklist) + '<br>'
        pfile["links"].append(linklist["name"]+ "XYZ")


    for file_index in range(len(linkcolors)):  # for lcolors in linkcolors:
        lcolors = linkcolors[file_index]

        if len(lcolors["data"]) == 0:
            lcolors["data"] = [[255,0,255,100]] * len(links[0]["data"])
            lcolors["name"] = "nan"

        if names[file_index] is not None:
            # if texture name specified
            state =  state + makeLinkRGBTex(namespace, lcolors, names[file_index]) + '<br>'
            pfile["linksRGB"].append(names[file_index])    
            continue
        state =  state + makeLinkRGBTex(namespace, lcolors) + '<br>'
        pfile["linksRGB"].append(lcolors["name"]+ "RGB")

    pfile["nodecount"] = numnodes
    #pfile["labelcount"] = len(labels[0]["data"])
    pfile["linkcount"] = len(links[0]["data"]) 

    # update new labels
    pfile["labels"] = [pfile["nodecount"], pfile["labelcount"]]

    #----------------------------------
    # adding graph info to pfile 
    #----------------------------------
    pfile["graphtitle"] = title_of_graph
    pfile["graphdesc"] = descr_of_graph
    pfile["annotationTypes"] = complex_annotations    # define in pfile if you use annotation types or default flat annotation list

    #----------------------------------
    # uploading and storing Legends files in folder
    # and adding filenames to pfile 
    #----------------------------------
    legendfiles = []
    loadLegendFiles(request.files.getlist("legendFiles"), folder+'legends/', legendfiles)
    pfile["legendfiles"] = legendfiles


    with open(folder + '/pfile.json', 'w') as outfile:
        json.dump(pfile, outfile)

    with open(folder + '/nodes.json', 'w') as outfile:
        json.dump(nodelist, outfile)
    
    GD.plist = GD.listProjects()
    return state


# -------------------------------------------
# PARSE GRAPH FUNCTIONS 
# -------------------------------------------

def loadGraphJSON(files, target):
    if len(files) > 0: 
        for file in files: 
            G_upload = file.read().decode('utf-8')
            G_json = json.loads(G_upload)
            target.append(G_json)


def parseGraphJSON_nodepositions(files, target):
    if len(files) > 0: 
        for file in files:

            name_of_file = file["graph"]["name"]
            num_of_nodes = len(file["nodes"])

            nodepositions = []
            for i in range(0, num_of_nodes):
                pos = file["nodes"][i]["pos"]
                # catch if positions contain "nan" values
                if math.isnan(pos[0]) or math.isnan(pos[1]) or math.isnan(pos[2]):
                    nodepositions.append([0,0,0])
                else: 
                    nodepositions.append(file["nodes"][i]["pos"])

            vecList = {}
            vecList["data"] = nodepositions
            vecList["name"] = name_of_file
            target.append(vecList)
            #print("C_DEBUG: NODEPOS:", vecList)


def parseGraphJSON_links(files, target):
    if len(files) > 0: 
        #for file in files:

        longest_list = []  
        all_lists = []  
        for idx,file in enumerate(files):

            name_of_file = file["graph"]["name"]+"_links"
            num_of_links = len(file["links"])

            links = []
            for i in range(0,num_of_links):
                links.append([str(file["links"][i]["source"]),str(file["links"][i]["target"])])
            vecList = {}
            vecList["data"] = links
            vecList["name"] = name_of_file
            #target.append(vecList)
            #print("C_DEBUG: LINKS:", vecList)

        # get all uploaded lists from all files i.e. layouts and keep only longest for "links.json" 
            all_lists.append(vecList)
        longest_list = max(all_lists, key=len)
        target.append(longest_list)
        #print("C_DEBUG: all_lists", target)


def parseGraphJSON_links_wip(files, target):
    if len(files) > 0: 

        for idx,file in enumerate(files):

            name_of_file = file["graph"]["name"]+"_links"
            num_of_links = len(file["links"])

            links = []
            for i in range(0,num_of_links):
                links.append([str(file["links"][i]["source"]),str(file["links"][i]["target"])])
            vecList = {}
            vecList["data"] = links
            vecList["name"] = name_of_file

            target.append(vecList)


def parseGraphJSON_linkcolors(files,target):
    if len(files) > 0: 
        #for file in files: 
        for idx,file in enumerate(files):

            name_of_file = file["graph"]["name"]+"_links"
            num_of_links = len(file["links"])

            linkcolor_rgba = []
            for i in range(0,num_of_links):
                color = file["links"][i]["linkcolor"]

                if isinstance(color, str):
                    #print("C_DEBUG: color is string")


                    # if HEX FORMAT
                    if re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color):
                        #print("C_DEBUG: link color is hex")
                        rgba_color = (*hex_to_rgb(color), 100)
                        linkcolor_rgba.append(rgba_color)

                    # if HEX FORMAT with alpha
                    elif re.match(r'^#([A-Fa-f0-9]{8})$', color):
                        #print("C_DEBUG: link color is hex with alpha")
                        rgba_color = (hex_to_rgba(color))
                        linkcolor_rgba.append(rgba_color)

                    # if RGBA FORMAT
                    elif re.match(r'^rgba\((\d+),(\d+),(\d+),(\d+)\)$', color) or re.match(r'^\((\d+),(\d+),(\d+),(\d+)\)$', color) or re.match(r'^RGBA\((\d+),(\d+),(\d+),(\d+)\)$', color):
                        #print("C_DEBUG: link color is rgba")
                        rgba = re.findall(r'\d+', color)
                        rgba_color = tuple(map(int, rgba))
                        linkcolor_rgba.append(rgba_color)

                elif isinstance(color, tuple) and len(color) == 4:
                    #print("C_DEBUG: link color is tuple")  
                    linkcolor_rgba.append(color)
                
                elif isinstance(color, list) and len(color) == 4:
                    #print("C_DEBUG: link color is list")  
                    linkcolor_rgba.append(tuple(color))

                else:
                    #print("C_DEBUG: NO LINKCOLOR FOUND")
                    linkcolor_rgba.append((255, 0, 255, 100))

            vecList = {}
            vecList["data"] = linkcolor_rgba
            vecList["name"] = name_of_file

            target.append(vecList)
            #print("C_DEBUG: LINKCOLORS:", vecList)


def parseGraphJSON_nodeinfo_simple(files,target):
    if len(files) > 0: 
        #for file in files: 
        for idx,file in enumerate(files):

            name_of_file = "nodeinfo" # name_of_file = file["graph"]["name"]    
            num_of_nodes = len(file["nodes"])

            nodeinfo = []
            for i in range(0,num_of_nodes):
                nodeinfo.append(file["nodes"][i]["annotation"])
            vecList = {}
            vecList["data"] = nodeinfo
            vecList["name"] = name_of_file
            target.append(vecList)
            #print("C_DEBUG: NODEINFO:", vecList)


def parseGraphJSON_nodeinfo_complex(files):
    if len(files) <= 0:
        return 
    
    out = []
    file = files[0]  # no need to iter over all files since you have to set it for all files the same way 
    num_of_nodes = len(file["nodes"])

    for i in range(num_of_nodes):
        node_info = {}
        node_info["annotation"] = file["nodes"][i]["annotation"]
        node_info["name"] = file["nodes"][i]["name"]
        out.append(node_info)

    return out


def parseGraphJSON_nodecolors(files,target):
    if len(files) > 0: 
        for file in files:

            name_of_file = file["graph"]["name"]
            num_of_nodes = len(file["nodes"])

            nodecolor_rgba = []

            for i in range(0, num_of_nodes):
                # to do: add catch for nodecolor key 
                color = file["nodes"][i]["nodecolor"]
                
                # if color is string 
                if isinstance(color, str):
                    # if HEX FORMAT
                    if re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color):                        
                        rgba_color = (hex_to_rgb(color), 100)
                        nodecolor_rgba.append(rgba_color)

                    # if HEX FORMAT with alpha
                    elif re.match(r'^#([A-Fa-f0-9]{8})$', color):
                        rgba_color = (hex_to_rgba(color))
                        nodecolor_rgba.append(rgba_color)

                    # if RGBA FORMAT
                    elif re.match(r'^rgba\((\d+),(\d+),(\d+),(\d+)\)$', color) or re.match(r'^RGBA\((\d+),(\d+),(\d+),(\d+)\)$', color):
                        rgba = re.findall(r'\d+', color)
                        rgba_color = tuple(map(int, rgba))
                        nodecolor_rgba.append(rgba_color)

                # if list of rgba int values (like for CSV upload)
                elif isinstance(color,list) and len(color) == 4:
                    nodecolor_rgba.append(color)
                   
                else:
                    nodecolor_rgba.append((255, 0, 255, 100))           

            #print("C_DEBUG in parseGraphJSON - nodecolor_rgba: ", nodecolor_rgba)

            vecList = {}
            vecList["data"] = nodecolor_rgba
            vecList["name"] = name_of_file
            target.append(vecList)
            #print("C_DEBUG: NODECOLORS:", vecList)


def parseGraphJSON_labels(files,target):
    if len(files) > 0: 
        # keep loop in case cluster labels per layout in update
        for idx, file in enumerate(files):
            
            # get cluster labels from one file only (file i.e. layout)
            one_file = file #s[0]
            name_of_file = file["graph"]["name"]
            num_of_nodes = len(one_file["nodes"])

            nodeclus = []
            nodeids = []
             
            for node in one_file["nodes"]: 
                labels = []
                if "cluster" in node and node["cluster"] is not None:
                    nodeclus.append(node["cluster"])
                    nodeids.append(node["id"])
                    
            set_nodeclus = list(set(nodeclus))

            for cluster in set_nodeclus:
                sublist = [] 
                for k,v in zip(nodeids,nodeclus):
                    if cluster == v:
                        sublist.append(str(k))
                sublist.insert(0,cluster)
                labels.append(sublist)
            
            vecList = {}
            vecList["data"] = labels
            vecList["name"] = name_of_file
            
            target.append(vecList)
        

def parseGraphJSON_graphtitle(files,target):
    if len(files) > 0: 
        for file in files:
            name_of_graph = file["graph"]["name"]
            vecList = {}
            vecList["graphtitle"] = name_of_graph 
            target.append(vecList)


def parseGraphJSON_graphdesc(files,target):
    if len(files) > 0: 
        for file in files:
            if "desc" in file["graph"].keys():
                descr_of_graph = file["graph"]["desc"]            
            elif "graphdesc" in file["graph"].keys():
                descr_of_graph = file["graph"]["graphdesc"]
            else: 
                descr_of_graph = ""
            vecList = {}
            vecList["graphdesc"] = descr_of_graph 
            target.append(vecList)


def parseGraphJSON_textureNames(files):
    out = []

    for file in files:
        if "textureName" not in file.keys():
            # no texture name specified
            out.append(None)
            continue
        if file["textureName"] in out:
            # no duplicates allowed
            out.append(None)
            continue    
        out.append(file["textureName"])
    return out