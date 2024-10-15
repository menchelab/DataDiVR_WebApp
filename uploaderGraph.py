
# use functions from CSV-based uploader 
from matplotlib.colors import hex2color
import re 
import math 
import random 
import GlobalData as GD

from uploader import *



#########################################################################################
#
# U P L O A D I N G 
#
#########################################################################################
import json
import os
import shutil

def upload_filesJSON(request, overwrite=False):
    """
    Uploads JSON files and processes the data for visualization.

    Args:
        request (dict or Flask request object): The request object containing the JSON files or form data.
        overwrite (bool, optional): Flag indicating whether to overwrite an existing project. Defaults to False.

    Returns:
        str: A message indicating the status of the project creation or any errors encountered.
    """

    global create_project_bool
    create_project_bool = True

    
    if isinstance(request, dict):  
        form = request
        if "graph" in form.keys():
            namespace = form["graph"].get("projectname", form["graph"].get("graphtitle", "Auto_ProjectName"))
        else:
            namespace = form.get("projectname", form.get("graphtitle", "Auto_ProjectName"))
    else:  
        form = request.form.to_dict()
        namespace = form["namespaceJSON"]

    if not namespace:
        create_project_bool = False
        return "Namespace fail. Please specify a project name."

    prolist = GD.listProjects()

    # Check if the project already exists
    if namespace in prolist:  # <--- **Check if project exists**
        if not overwrite:  # <--- **Check if overwrite flag is False**
            if isinstance(request, dict):  # Jupyter Notebook
                response = input(f"Project '{namespace}' exists. Overwrite? (yes/no): ").strip().lower()  # <--- **Jupyter prompt**
                if response == 'yes':
                    folder = f'static/projects/{namespace}/'
                    if os.path.exists(folder):
                        shutil.rmtree(folder)  # <--- **Remove existing project directory**
                    print("PROGRESS: Overwriting Project...")
                    create_project_bool = True
                    
                else: 
                    create_project_bool = False
                    return print(f"Project '{namespace}' exists and was not overwritten.")
                
            else:  # Web browser
                return f"Project '{namespace}' exists. Set overwrite=True to overwrite it."  # <--- **Web browser message**
        if overwrite:
            folder = f'static/projects/{namespace}/'
            create_project_bool = True
            if os.path.exists(folder):
                shutil.rmtree(folder)  # <--- **Remove existing project directory**

    if create_project_bool == True:
        makeProjectFolders(namespace) 
    else:   
        return "Project creation failed."
    
    #-----------------------------------
    # CREATING PFILE.json
    #-----------------------------------
    folder = 'static/projects/' + namespace + '/'
    pfile = {}
    with open(folder + 'pfile.json', 'r') as json_file:
        pfile = json.load(json_file)
    json_file.close()

    #-----------------------------------
    # CREATING necessary variables to store data
    #-----------------------------------
    state = ''
    nodelist = {"nodes":[]}
    jsonfiles = []
    nodepositions = []
    nodeinfo = []
    nodecolors = []
    linksdicts = [] # this is where links per layout are stored to match visualization accordingly
    links = [] # this is the original linklist including all uploaded links 
    linkcolors = []
    labels = []
    graphlayouts = []
    
    if isinstance(request, dict): # using "_GeneratedProject.ipynb" 
        loadGraphDict([form], jsonfiles)
        print("PROGRESS: loaded graph JSON...")
    else:
        loadGraphJSON(request.files.getlist("graphJSON"), jsonfiles)

    #----------------------------------
    # GRAPH DATA
    #----------------------------------
    graphdesc = []
    parseGraphJSON_graphinfo(jsonfiles,graphdesc)
    if len(graphdesc) > 0 or graphdesc[0]["info"] is not None: #former "graphdesc"
        descr_of_graph = graphdesc[0]["info"] #former "graphdesc"
    pfile["info"] = descr_of_graph
    print("PROGRESS: stored graph data...")
    
    #----------------------------------------------
    # ALL LINKS - for analytics
    #---------------------------------------------- 
    parseGraphJSON_links(jsonfiles, links)  
    pfile["linkcount"] = len(links[0]["data"])
    #print("C_DEBUG: links: ", links[0]["data"])

    #----------------------------------------------
    # VISUALIZATION INFORMATION ("Layouts" key on most upper level)
    #----------------------------------------------
    # in case of new json format
    if "layouts" in jsonfiles[0].keys():
        layout = jsonfiles[0]["layouts"] 
        parseGraphJSON_nodepositions(layout, nodepositions)
        parseGraphJSON_nodecolors(layout, nodecolors)
        
        parseGraphJSON_labels(layout, labels) 
        
        parseGraphJSON_links_many(layout, linksdicts)
        parseGraphJSON_linkcolors(layout, linkcolors)
        
        parseGraphJSON_layoutnames(layout, graphlayouts)
        graphlayouts = [item for sublist in graphlayouts for item in sublist] # unpack list in lists
        names = graphlayouts
        
    # in case of no layouts key (i e "old" json format)
    else: 
        parseGraphJSON_nodepositions(jsonfiles, nodepositions)
        parseGraphJSON_nodecolors(jsonfiles, nodecolors)
    
        parseGraphJSON_labels(jsonfiles, labels)
        
        parseGraphJSON_links_many(jsonfiles, linksdicts)
        parseGraphJSON_linkcolors(jsonfiles, linkcolors)
        
        parseGraphJSON_layoutnames(jsonfiles, graphlayouts) 
        graphlayouts = [item for sublist in graphlayouts for item in sublist] # unpack list in lists
        names = graphlayouts
        
    pfile["scenes"] = names # rrdundant - to be removed
    print("PROGRESS: stored layouts...")

    #----------------------------------------------
    # ANNOTATIONS
    #----------------------------------------------
    # decide which annotation type to go with / if complex_annotations is True it uses a dict to store annotations and their types
    
    # # referenced by "annotationTypes" as true in uploaded JSON
    # complex_annotations = False
    # if "annotationTypes" in jsonfiles[0].keys():
    #     if jsonfiles[0]["annotationTypes"] is True:
    #         complex_annotations = True
    # if complex_annotations is False:
    #     parseGraphJSON_nodeinfo_simple(jsonfiles, nodeinfo)
    # else:  # complex_annotations is True
    #     nodeinfo = parseGraphJSON_nodeinfo_complex(jsonfiles)        

    #print("C_DEBUG: jsonfiles[0].keys(): ", jsonfiles[0].keys())
    nodeinfo = parseGraphJSON_nodeinfo(jsonfiles)
    print("PROGRESS: stored node info...")
    
    numnodes = len(nodepositions[0]["data"])
    #OLD: if complex_annotations is False:
    #NEW: without complex_annotations flag (json file) instead check for "name" key per node in "nodes" key - EXPLANATION: no complex_annotations flag is needed in json file, but the variabel still exists for analytics if required
    if "name" in nodeinfo[0]:
        for i in range(len(nodeinfo)):
            thisnode = {}
            thisnode["id"] = i
            thisnode["n"] = nodeinfo[i]["name"]
            thisnode["attrlist"] = nodeinfo[i]["annotation"]
            nodelist["nodes"].append(thisnode)
            complex_annotations = True # set if required for analytics
            
    else:   
        for i in range(len(nodepositions[0]["data"])):
            thisnode = {}
            thisnode["id"] = i
            
            # check for "geo" in layout name - needs reimplementation
            #if "_geo" in nodepositions[0]["name"]:
            #    thisnode["lat"] = nodepositions[0]["data"][i][0]
            #    thisnode["lon"] = nodepositions[0]["data"][i][1]
            
            if len(nodeinfo[0]["data"]) == len(nodepositions[0]["data"]):
                thisnode["attrlist"] = nodeinfo[0]["data"][i]          
                thisnode["n"] = "node" + str(i)

            nodelist["nodes"].append(thisnode)
            complex_annotations = False # set if required for analytics

    #----------------------------------
    # CLUSTER LABELS
    #----------------------------------
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
                if "name" in nodeinfo[0]:
                    thisnode["n"] = nodeinfo[i]["name"] # str(name)
                else:   
                    thisnode["n"] = str(name)
                nodelist["nodes"].append(thisnode)

                #add to pfile
                pfile["selections"].append({"name":name, "nodes": row, # use int id instead? e.g. [int(i) for i in row]
                                            "layoutname": labellist["name"]})     

                #if labellist["name"] not in pfile["scenes"]:
                #    pfile["scenes"].append(labellist["name"])
                
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

    #----------------------------------
    # MAKE TEXTURES - node positions
    #----------------------------------
    for file_index,layout in enumerate(nodepositions): # for file_index in range(len(nodepositions)):  #

        #print("C_DEBUG: fileindex = ", file_index)

        # catch for 2D positions and for empty rows
        if len(layout["data"]) > 0 and len(layout["data"][int(0)]) == 2:
            for i,xy in enumerate(layout["data"]):
                layout["data"][i] = (xy[0],xy[1],0.0)

        # handle layout name 
        if names[file_index] is not None and names[file_index] != "":
            state =  state + makeXYZTexture(namespace, layout, names[file_index]) + '<br>'
            pfile["layouts"].append(names[file_index])    
        else: # if no specified layout name
            temp_name = "Layoutname"+str(file_index)
            state =  state + makeXYZTexture(namespace, layout, temp_name) + '<br>'
            pfile["layouts"].append(temp_name) # + "XYZ")

    # match labels to respective layout to get label colors for legend
    clustercounter = 0
    if len(pfile["selections"]) > 0:
        all_layouts = graphlayouts

        for e,subdict in enumerate(pfile["selections"]):
            layoutname_pfile = pfile["selections"][e]["layoutname"] #+"XYZ"
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
                        
                    clustercounter += 1
                    #print("C_DEBUG: clustercounter: ", clustercounter)

        pfile["labelcount"] = clustercounter # ISSUE: this might only work for one label set per project and not per layout! 

    else:
        #print("C_DEBUG: project does not contain labels/clusters.")
        pfile["labelcount"] = 0
    print("PROGRESS: made node position textures...")


    #----------------------------------
    # MAKE TEXTURES - node colors 
    #----------------------------------
    for file_index,color in enumerate(nodecolors): #for file_index in range(len(nodecolors)):
        
        #color = nodecolors[file_index]
        if len(color["data"]) == 0:
            color["data"] = [[255,0,255,100]] * numnodes
            
        # handle layout name 
        if names[file_index] is not None and names[file_index] != "":
            state =  state + makeNodeRGBTexture(namespace, color, names[file_index]) + '<br>'
            pfile["layoutsRGB"].append(names[file_index])    
        else: # if no specified layout name
            temp_name = "Layoutname"+str(file_index)
            state =  state + makeNodeRGBTexture(namespace, color, temp_name) + '<br>'
            pfile["layoutsRGB"].append(temp_name) # + "RGB")
    print("PROGRESS: made textures for node colors...")


    #----------------------------------
    # MAKE TEXTURES - links for VISUALIZATION
    #----------------------------------
    # make a look up dict where key is id of all links  and value is the link
    links_ids_project = {i: links[0]["data"][i] for i in range(len(links[0]["data"]))}
    # sort links_ids_project by key
    links_ids_project = dict(sorted(links_ids_project.items()))
    #print("C_DEBUG: num of links_ids_project:", len(links_ids_project))
    #print("C_DEBUG: links_ids_project: ", links_ids_project)

    for sublist in linksdicts:  
        for file_index in range(len(sublist)): 
            linklist = sublist[file_index]
            
            #print("C_DEBUG: file_index: ", file_index)
            #print("C_DEBUG: layout has x links: ", len(linklist["data"]))
            
            # remap link-node ids based on nodelist "id" (in case of link-nodes are specified as nodenames (str)
            #for link in linklist["data"]:
                # try:
                #     link[0] = int(link[0])
                #     link[1] = int(link[1])
                # except: 
                #     link[0] = next(node["id"] for node in nodelist["nodes"] if node["n"] == link[0])
                #     link[1] = next(node["id"] for node in nodelist["nodes"] if node["n"] == link[1])

            # handle layout name 
            if names[file_index] is not None and names[file_index] != "":
                state =  state + makeLinkTexNew_withoutJSON_2(namespace, links_ids_project, linklist, names[file_index]) + '<br>'
                pfile["links"].append(names[file_index])    
            else: # if no specified layout name
                temp_name = "Layoutname"+str(file_index)
                state =  state + makeLinkTexNew_withoutJSON_2(namespace, links_ids_project, linklist, temp_name) + '<br>'
                pfile["links"].append(temp_name) # + "_linksXYZ")
    print("PROGRESS: stored link textures...")

    # NOT USED YET : links per layout json
    #makeLinksjson_multipleLinklists_2(namespace, links_ids_project, linksdicts)
    #print("PROGRESS: stored linklists per layout...")

    #----------------------------------
    # processing Links for ANALYTICS
    #----------------------------------
    # remap links to node ids matching them with node "n" names, in case link-nodes are specified as nodenames (str)
    #print("C_DEBUG: links before remapping:", links) 
    # for link in links[0]["data"]:
    #     try:
    #         link[0] = int(link[0])
    #         link[1] = int(link[1])
    #     except: 
    #         link[0] = next(node["id"] for node in nodelist["nodes"] if node["n"] == link[0])
    #         link[1] = next(node["id"] for node in nodelist["nodes"] if node["n"] == link[1])
    #print("C_DEBUG: links remapped:", links)   
    
    # all links json
    #print("C_DEBUG: counting all links for json: ", len(links[0]["data"]))
    makeLinksjson(namespace, links)
    print("PROGRESS: stored all links in json...")

    #----------------------------------
    # processing link colors 
    #----------------------------------
    # What happens here: matching of ID of links given all links in the graph and their respective color
    # to set pixel index according to link ID and color in bitmap
    # Match linkdicts with linkcolors to get link colors for visualization
    link_colors_matched = [
        {
            tuple(each): each2
            for each, each2 in zip(i["data"], j["data"])
        } | {"name": i["name"]}
        for i in linksdicts[0]
        for j in linkcolors
        if i["name"] == j["name"]
    ]
    #print("C_DEBUG: linkcolors matched: ", link_colors_matched)

    # Create a reverse lookup for links_ids_project
    reverse_links_ids_project = {tuple(map(str, v)): k for k, v in links_ids_project.items()}

    # Match color from link_colors_matched to id of link from links_ids_project
    link_ids_colors_matched = []  # contains each layout with key = edgeID (from all links in all layouts), val = color
    for elem in link_colors_matched:
        d_link_ids_colors_matched = {"name": elem.pop("name")}
        idcolmatch = [
            (reverse_links_ids_project[tuple(map(str, edge))], links_ids_project[reverse_links_ids_project[tuple(map(str, edge))]], color)
            for edge, color in elem.items()
            if tuple(map(str, edge)) in reverse_links_ids_project
        ]
        d_link_ids_colors_matched["data"] = idcolmatch
        link_ids_colors_matched.append(d_link_ids_colors_matched)
    #print("C_DEBUG: link_ids_colors_matched: ", link_ids_colors_matched)


    for file_index in range(len(link_ids_colors_matched)):  # for lcolors in linkcolors:
        lcolors = link_ids_colors_matched[file_index] # lcolors, per layout ie fileindex = data : (linkID, link [n1,n2], color), "name" : layoutname
        
        if len(lcolors["data"]) == 0:
            lcolors["data"] = [[255,0,255,100]] * len(links[0]["data"])
            lcolors["name"] = "nan"

        # handle layout name 
        if names[file_index] is not None and names[file_index] != "":
            state =  state + makeLinkRGBTex_2(namespace, links_ids_project, lcolors, names[file_index]) + '<br>'
            pfile["linksRGB"].append(names[file_index])    
        else: # if no specified layout name
            temp_name = "Layoutname"+str(file_index)
            state =  state + makeLinkRGBTex_2(namespace, links_ids_project, lcolors, temp_name) + '<br>'
            pfile["linksRGB"].append(temp_name) # + "_linksRGB")
    print("PROGRESS: stored links textures...")


    pfile["nodecount"] = numnodes
    #pfile["labelcount"] = len(labels[0]["data"])

    #----------------------------------
    # processing labels
    #----------------------------------
    # update new labels
    pfile["labels"] = [pfile["nodecount"], pfile["labelcount"]]
    
    pfile["annotationTypes"] = complex_annotations    # define in pfile if you use annotation types or default flat annotation list

    # consider reimplementation
    # #----------------------------------
    # # processing legends pictures (if any)
    # #----------------------------------
    # legendfiles = []
    # if isinstance(request, dict):
    #     #os.mkdir(folder+'legends/') # just generate legends folder
    #     pfile["legendfiles"] = None
    # else: 
    #     loadLegendFiles(request.files.getlist("legendFiles"), folder+'legends/', legendfiles)
    #     pfile["legendfiles"] = legendfiles


    #----------------------------------
    # make essential json files for DataDiVR
    #----------------------------------
    print("PROGRESS: writing json files for project and nodes...")
    with open(folder + '/pfile.json', 'w') as outfile:
        json.dump(pfile, outfile, indent=4)
    
    with open(folder + '/nodes.json', 'w') as outfile:
        json.dump(nodelist, outfile, indent=4)
        
    #GD.plist = GD.listProjects()
    
    print("Project created successfully.")

    return state  


    #except Exception as e:
    #    return f"An error occurred: {str(e)}"




#########################################################################################
# 
# PARSE GRAPH FUNCTIONS 
#
#########################################################################################


def hex_to_rgb(hx):
    hx = hx.lstrip('#')
    hlen = len(hx)
    return [int(hx[i:i+hlen//3], 16) for i in range(0, hlen, hlen//3)]

def hex_to_rgba(hex_color):
    hex_color = hex_color.lstrip('#')
    rgba_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4, 6))
    return rgba_color


def loadGraphJSON(files, target):
    if len(files) > 0: 
        for file in files: 
            G_upload = file.read().decode('utf-8')
            G_json = json.loads(G_upload)
            target.append(G_json)

def loadGraphDict(files, target):
    if len(files) > 0: 
        for file in files: 
            G_json = file
            target.append(G_json)


def parseGraphJSON_nodepositions(files, target):
    if len(files) > 0: 
        for ix,file in enumerate(files):


            # old JSON format (no "layout" key)
            if "graph" in file:
                name_of_file = file["graph"]["name"]  
            # with new "layout" key -> get layout name           
            elif "layoutname" in file:
                name_of_file = file["layoutname"] 
            else:
                name_of_file = "Automatic-LayoutID"+str(ix) 

            num_of_nodes = len(file["nodes"])
            nodepositions = []
            for i in range(0, num_of_nodes):
                pos = file["nodes"][i]["pos"]

                # catch if positions are empty
                if len(pos) == 0:
                    # create random uniform positions   
                    x, y, z = random.uniform(0, 0.1), random.uniform(0, 0.1), random.uniform(0, 0.1)
                    nodepositions.append([x, y, z])                 
                    #print("C_DEBUG: Position values are empty. Set positions to random.")
                
                # catch if positions are string 
                elif isinstance(pos, str) or isinstance(pos[0], str) or isinstance(pos[1], str) or isinstance(pos[2], str):
                    nodepositions.append([0, 0, 0])
                    #print("Position values are strings. Set positions to 0,0,0. Please upload a valid JSON file.")
                
                # catch if positions contain "nan" values
                elif math.isnan(pos[0]) or math.isnan(pos[1]) or math.isnan(pos[2]):
                    nodepositions.append([0, 0, 0])
                    #print("Position values are NaN. Set positions to 0,0,0. Please upload a valid JSON file.")
                
                else:
                    nodepositions.append(file["nodes"][i]["pos"])

            vecList = {}
            vecList["data"] = nodepositions
            vecList["name"] = name_of_file

            target.append(vecList)
            #print("C_DEBUG: NODEPOS:", vecList["name"])


def parseGraphJSON_links(files, target):
    if len(files) > 0: 
        for ix,file in enumerate(files):
            
            # get layout name
            if "layoutname" in file:
                name_of_file = file["layoutname"]
            else:
                name_of_file = "Automatic-LayoutID"+str(ix)
            
            # catch if there are links
            if "links" in file.keys():
                    
                num_of_links = len(file["links"])

                links = []
                for i in range(0,num_of_links):
                    links.append([str(file["links"][i]["source"]),str(file["links"][i]["target"])])

                vecList = {}
                vecList["data"] = links
                vecList["name"] = name_of_file
            else: 
                links = []
                vecList = {}
                vecList["data"] = links
                vecList["name"] = name_of_file

        target.append(vecList)


def parseGraphJSON_links_many(files, target):
    if len(files) > 0: 
            
        all = []  
        for ix,file in enumerate(files):
        
            # old JSON format (no "layout" key)
            if "graph" in file:
                name_of_file = file["graph"]["name"] #+"_linksXYZ"
            # with new "layout" key -> get layout name
            elif "layoutname" in file:
                name_of_file = file["layoutname"] #+"_linksXYZ"
            else:
                name_of_file = "Automatic-LayoutID"+str(ix) #+"_linksXYZ"

            # catch if there are links 
            if "links" in file.keys():
                num_of_links = len(file["links"])

                links = []
                for i in range(0,num_of_links):
                    links.append([str(file["links"][i]["source"]),str(file["links"][i]["target"])])
                vecList = {}
                vecList["data"] = links
                vecList["name"] = name_of_file
                all.append(vecList)
            else:
                links = []
                vecList = {}
                vecList["data"] = links
                vecList["name"] = name_of_file
                all.append(vecList)
        target.append(all)
    

def parseGraphJSON_append_links(all_dicts, target):
    
    if len(*all_dicts) > 1:
        merged_dict = {}
        sublist_data = []
        sublist_name = []

        for sublist in all_dicts:
            
            #print("C_DEBUG: sublist: ", sublist)

            for d in sublist:
                sublist_data.append(d["data"])
                sublist_name.append(d["name"])

        merged_dict["data"] = [item for slist in sublist_data for item in slist] # flatten list in list
        merged_dict["name"] = "Merged Linklist"
    else:
        merged_dict = all_dicts 

    target.append(merged_dict)




def parseGraphJSON_linkcolors(files,target):
    if len(files) > 0: 
        #for file in files: 
        for ix,file in enumerate(files):
            
            #print("C_DEBUG: file in linkcolors: ", file)
            #print("C_DEBUG  -  file.keys(): ", file.keys())
            
            # old JSON format (no "layout" key)
            if "graph" in file:
                name_of_file = file["graph"]["name"] #+"_linksRGB"
            # with new "layout" key -> get layout name           
            elif "layoutname" in file:
                name_of_file = file["layoutname"] #+"_linksRGB"
            else:
                name_of_file = "Automatic-LayoutID"+str(ix) #+"_linksRGB"

            # catch if there are linkcolors
            if "links" in file.keys():
                
                num_of_links = len(file["links"])

                linkcolor_rgba = []
                for i in range(0,num_of_links):
                    color = file["links"][i]["linkcolor"]

                    if isinstance(color, str):
                        #print("C_DEBUG: color is string")


                        # if HEX FORMAT
                        if re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color):
                            #print("C_DEBUG: link color is hex")
                            _r, _g, _b = hex_to_rgb(color)
                            rgba_color = (_r, _g, _b, 100)
                            linkcolor_rgba.append(rgba_color)

                        # if HEX FORMAT with alpha
                        elif re.match(r'^#([A-Fa-f0-9]{8})$', color):
                            #print("C_DEBUG: link color is hex with alpha")
                            rgba_color = hex_to_rgba(color)
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
            else: 
                linkcolor_rgba = list()

            vecList = {}
            vecList["data"] = linkcolor_rgba
            vecList["name"] = name_of_file

            target.append(vecList)
            #print("C_DEBUG: LINKCOLORS:", vecList)


def parseGraphJSON_nodeinfo(files):
    # check if files is a list
    file = files[0]
    out = []
    num_of_nodes = len(file["nodes"])
    for i in range(num_of_nodes):
        node_info = {}
        node_info["annotation"] = file["nodes"][i].get("annotation", "")
        node_info["name"] = file["nodes"][i].get("name", "node" + str(i))
        out.append(node_info)

    return out


def parseGraphJSON_nodecolors(files,target):
    if len(files) > 0: 
        for ix,file in enumerate(files):
            
            # old JSON format (no "layout" key)
            if "graph" in file:
                name_of_file = file["graph"]["name"]  
            # with new "layout" key -> get layout name           
            elif "layoutname" in file:
                name_of_file = file["layoutname"]  
            else:
                name_of_file = "Automatic-LayoutID"+str(ix)  

            num_of_nodes = len(file["nodes"])
            nodecolor_rgba = []

            for i in range(0, num_of_nodes):
                # to do: add catch for nodecolor key 
                color = file["nodes"][i]["nodecolor"]
                
                # if color is string 
                if isinstance(color, str):
                    # if HEX FORMAT
                    if re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color):
                        _r, _g, _b = hex_to_rgb(color)                        
                        rgba_color = (_r, _g, _b, 100)
                        nodecolor_rgba.append(rgba_color)

                    # if HEX FORMAT with alpha
                    elif re.match(r'^#([A-Fa-f0-9]{8})$', color):
                        rgba_color = hex_to_rgba(color)
                        nodecolor_rgba.append(rgba_color)
                    
                    # if RGBA string
                    elif re.match(r'^rgba\((\d+),(\d+),(\d+),(\d+)\)$', color) or re.match(r'^RGBA\((\d+),(\d+),(\d+),(\d+)\)$', color):
                        rgba = re.findall(r'\d+', color)
                        rgba_color = tuple(map(int, rgba))
                        nodecolor_rgba.append(rgba_color)

                # if color is tuple
                elif isinstance(color, tuple) and len(color) == 4:
                    #print("C_DEBUG : color is rgba tuple")
                    nodecolor_rgba.append(color)

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
        for ix, file in enumerate(files):

            # old JSON format (no "layout" key)
            if "graph" in file:
                name_of_file = file["graph"]["name"]  
            # with new "layout" key -> get layout name           
            elif "layoutname" in file:
                name_of_file = file["layoutname"]  
            else:
                name_of_file = "Automatic-LayoutID"+str(ix)  



            # get cluster labels from one file only (file i.e. layout)
            one_file = file #s[0]
            num_of_nodes = len(file["nodes"])

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
        

# graph desciption
def parseGraphJSON_graphinfo(files,target):
    if len(files) > 0: 
        for file in files:
            
            # new json format
            if "info" in file.keys():
                descr_of_graph = file["info"] # former "graphdesc"
            # old (multiple) json files
            elif "graph" in file.keys():
                descr_of_graph = file["graph"]["graphdesc"]  
            
            else:
                descr_of_graph = "Graph decription not specified."
            #print("C_DEBUG: descr_of_graph :", descr_of_graph)
                
            vecList = {}
            vecList["info"] = descr_of_graph 
            target.append(vecList)


# graph layoutnames 
def parseGraphJSON_layoutnames(files, target):
    if len(files) > 0: 
        l_layoutnames = []
        for ix,file in enumerate(files):            
            # get layout names
            try:
                # if files = layout key in one JSON file
                if "layoutname" in file.keys(): 
                    name_of_file = file["layoutname"] # ["layouts"]["layoutname"]
                # if files = separate json files 
                elif "graph" in file.keys():  
                    name_of_file = file["graph"]["name"]

            except:
                name_of_file = "Automatic-LayoutID"+str(ix)

            l_layoutnames.append(name_of_file)
            
        vecList = l_layoutnames 
        #print("C_DEBUG getting layoutnames: ", vecList)
        target.append(vecList)



