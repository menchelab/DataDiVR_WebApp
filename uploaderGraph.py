
# use functions from CSV-based uploader 
from matplotlib.colors import hex2color
import re 
import math 

from uploader import *



def hex_to_rgb(hx):
    hx = hx.lstrip('#')
    hlen = len(hx)
    return [int(hx[i:i+hlen//3], 16) for i in range(0, hlen, hlen//3)]

def hex_to_rgba(hex_color):
    hex_color = hex_color.lstrip('#')
    rgba_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4, 6))
    return rgba_color


#########################################################################################
#
# U P L O A D I N G 
#
#########################################################################################
def upload_filesJSON(request):

    #-----------------------------------
    # Make Project Folders 
    #-----------------------------------
    if isinstance(request, dict):  #upload via Notebook function 
        #print("C_DEBUG: is dict - Uploading via Notebook function")
        form = request #request.get_json()
        try:
            # old (multiple) json files
            if "graph" in form.keys():
                if "projectname" in form["graph"].keys():
                    namespace = form["graph"]["projectname"]
                elif "graphtitle" in form["graph"].keys():
                    namespace = form["graph"]["graphtitle"]
            # one merged json file (with layout key)
            elif "projectname" in form.keys(): # former graphtitle
                namespace = form["projectname"] # former graphtitle
            elif "graphtitle" in form.keys(): # keep only for "old" files
                namespace = form["graphtitle"] # keep only for "old" files
            else: 
                namespace = "Auto_ProjectName"
        except:
            print("Can not find reference to projectname. Not specified.")

    else: # original processing via uploader / webbrowser
        form = request.form.to_dict()
        namespace = form["namespaceJSON"]


    prolist = GD.plist
    if not namespace:
        return "namespace fail"
    if namespace in prolist:
        print('project exists')
    else:
        makeProjectFolders(namespace)

    #-----------------------------------
    # CREATING PFILE.json
    #-----------------------------------
    folder = 'static/projects/' + namespace + '/'
    pfile = {}
    with open(folder + 'pfile.json', 'r') as json_file:
        pfile = json.load(json_file)
    json_file.close()
    
    #print("C_DEBUG: created folder and pfile.json")
    #print("C_DEBUG: pfile : ", pfile)

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
    else:
        loadGraphJSON(request.files.getlist("graphJSON"), jsonfiles)

    #----------------------------------
    # GRAPH DATA
    #----------------------------------
    #title_of_graph = namespace #[]
    #parseGraphJSON_graphtitle(jsonfiles,graphtitle)
    #if len(graphtitle) > 0:
    #    title_of_graph = graphtitle[0]["graphtitle"]
    #else:
    #    title_of_graph = namespace
    
    graphdesc = []
    parseGraphJSON_graphinfo(jsonfiles,graphdesc)
    if len(graphdesc) > 0 or graphdesc[0]["info"] is not None: #former "graphdesc"
        descr_of_graph = graphdesc[0]["info"] #former "graphdesc"

    pfile["info"] = descr_of_graph
    


    #----------------------------------------------
    # ALL LINKS - for analytics
    #---------------------------------------------- 
    parseGraphJSON_links(jsonfiles, links)  
    pfile["linkcount"] = len(links[0]["data"])


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
        
    pfile["scenes"] = names

    #----------------------------------------------
    # ANNOTATIONS
    #----------------------------------------------
    # decide which annotation type to go with / if complex_annotations is True it uses a dict to store annotations and their types
    # referenced by "annotationTypes" as true in uploaded JSON
    complex_annotations = False
    if "annotationTypes" in jsonfiles[0].keys():
        if jsonfiles[0]["annotationTypes"] is True:
            complex_annotations = True
    if complex_annotations is False:    
        parseGraphJSON_nodeinfo_simple(jsonfiles, nodeinfo)
    else:  # complex_annotations is True
        nodeinfo = parseGraphJSON_nodeinfo_complex(jsonfiles)
    
    numnodes = len(nodepositions[0]["data"])
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
                thisnode["n"] = str(name)
                nodelist["nodes"].append(thisnode)

                #add to pfile
                pfile["selections"].append({"name":name, "nodes":row, "layoutname": labellist["name"]})     

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
    # MAKE TEXTURES - FOR NODEPOSITIONS
    #----------------------------------
    for layout in nodepositions: # for file_index in range(len(nodepositions)):  #
                
        if len(layout["data"]) > 0 and len(layout["data"][int(0)]) == 3:
        
            # if names[file_index] is not None:
            #     # if texture name specified
            #     state =  state + makeXYZTexture(namespace, layout, names[file_index]) + '<br>'
            #     pfile["layouts"].append(names[file_index])    
            #     continue

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


    #----------------------------------
    # processing node colors 
    #----------------------------------
    for color in nodecolors: #for file_index in range(len(nodecolors)):
        
        #color = nodecolors[file_index]

        if len(color["data"]) == 0:
            color["data"] = [[255,0,255,100]] * numnodes
            color["name"] = "nan"
        # if names[file_index] is not None:
        #     # if texture name specified
        #     state =  state + makeNodeRGBTexture(namespace, color, names[file_index]) + '<br>'
        #     pfile["layoutsRGB"].append(names[file_index])    
        #     continue
        state =  state + makeNodeRGBTexture(namespace, color) + '<br>'
        pfile["layoutsRGB"].append(color["name"]+ "RGB")

    #----------------------------------
    # processing Links for ANALYTICS
    #----------------------------------
    
    # all links
    makeLinksjson(namespace, links)
    
    #----------------------------------
    # processing links for VISUALIZATION
    #----------------------------------
    
    # links per layout
    makeLinksjson_multipleLinklists(namespace, linksdicts)
    #print("C_DEBUG: linksdicts: ", linksdicts)

    for sublist in linksdicts:  
        for file_index in range(len(sublist)): 
            linklist = sublist[file_index]

            if len(linklist["data"]) == 0:
                linklist["name"] = "nan"

            # if names[file_index] is not None:
            #     # if texture name specified
            #     state =  state + makeLinkTexNew_withoutJSON(namespace, linklist, names[file_index]) + '<br>'
            #     #pfile["links"].append(names[file_index])    
            #     continue
            state =  state + makeLinkTexNew_withoutJSON(namespace, linklist) + '<br>'
            
            
            pfile["links"].append(linklist["name"]+ "_linksXYZ") #"XYZ"
            #print("C_DEBUG: pfile[links]: ", pfile["links"]) 

    #----------------------------------
    # processing link colors 
    #----------------------------------
    for file_index in range(len(linkcolors)):  # for lcolors in linkcolors:
        lcolors = linkcolors[file_index]

        if len(lcolors["data"]) == 0:
            lcolors["data"] = [[255,0,255,100]] * len(links[0]["data"])
            lcolors["name"] = "nan"

        # if names[file_index] is not None:
        #     # if texture name specified
        #     state =  state + makeLinkRGBTex(namespace, lcolors, names[file_index]) + '<br>'
        #     pfile["linksRGB"].append(names[file_index])    
        #     continue
        state =  state + makeLinkRGBTex(namespace, lcolors) + '<br>'
        pfile["linksRGB"].append(lcolors["name"]+ "_linksRGB")

    pfile["nodecount"] = numnodes
    #pfile["labelcount"] = len(labels[0]["data"])

    #----------------------------------
    # processing labels
    #----------------------------------
    # update new labels
    pfile["labels"] = [pfile["nodecount"], pfile["labelcount"]]


    
    pfile["annotationTypes"] = complex_annotations    # define in pfile if you use annotation types or default flat annotation list


    #----------------------------------
    # processing legends pictures (if any)
    #----------------------------------
    legendfiles = []
    if isinstance(request, dict):
        #os.mkdir(folder+'legends/') # just generate legends folder
        pfile["legendfiles"] = None
    else: 
        loadLegendFiles(request.files.getlist("legendFiles"), folder+'legends/', legendfiles)
        pfile["legendfiles"] = legendfiles


    #----------------------------------
    # make essential json files for DataDiVR
    #----------------------------------
    with open(folder + '/pfile.json', 'w') as outfile:
        json.dump(pfile, outfile)

    with open(folder + '/nodes.json', 'w') as outfile:
        json.dump(nodelist, outfile)
    
    GD.plist = GD.listProjects()
    return state





#########################################################################################
# 
# PARSE GRAPH FUNCTIONS 
#
#########################################################################################

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

                # catch if positions are string 
                if isinstance(pos, str) or isinstance(pos[0], str) or isinstance(pos[1], str) or isinstance(pos[2], str):
                    nodepositions.append([0, 0, 0])
                    raise ValueError("Position values are strings. Set positions to 0,0,0. Please upload a valid JSON file.")
                
                # catch if positions contain "nan" values
                elif math.isnan(pos[0]) or math.isnan(pos[1]) or math.isnan(pos[2]):
                    nodepositions.append([0, 0, 0])
                    raise ValueError("Position values are NaN. Set positions to 0,0,0. Please upload a valid JSON file.")
                
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
            
            num_of_links = len(file["links"])

            links = []
            for i in range(0,num_of_links):
                links.append([str(file["links"][i]["source"]),str(file["links"][i]["target"])])
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

            num_of_links = len(file["links"])

            links = []
            for i in range(0,num_of_links):
                links.append([str(file["links"][i]["source"]),str(file["links"][i]["target"])])
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



# def parseGraphJSON_links_wip(files, target):
#     if len(files) > 0: 

#         for idx,file in enumerate(files):

#             name_of_file = file["layoutname"]+"_linksXYZ"
#             num_of_links = len(file["links"])

#             links = []
#             for i in range(0,num_of_links):
#                 links.append([str(file["links"][i]["source"]),str(file["links"][i]["target"])])
#             vecList = {}
#             vecList["data"] = links
#             vecList["name"] = name_of_file

#             target.append(vecList)


def parseGraphJSON_linkcolors(files,target):
    if len(files) > 0: 
        #for file in files: 
        for ix,file in enumerate(files):

            # old JSON format (no "layout" key)
            if "graph" in file:
                name_of_file = file["graph"]["name"] #+"_linksRGB"
            # with new "layout" key -> get layout name           
            elif "layoutname" in file:
                name_of_file = file["layoutname"] #+"_linksRGB"
            else:
                name_of_file = "Automatic-LayoutID"+str(ix) #+"_linksRGB"

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
        

# REMOVE EVENTUALLY 
# # graph / project title
# def parseGraphJSON_graphtitle(files,target):
#     if len(files) > 0: 
#         for file in files:
#             try:
#                 name_of_graph = file["graph"]["name"]
#             except:
#                 name_of_graph = file["graphtitle"]
#             vecList = {}
#             vecList["graphtitle"] = name_of_graph 
#             target.append(vecList)


# graph desciption
def parseGraphJSON_graphinfo(files,target):
    if len(files) > 0: 
        for file in files:
            
            try:
                # new json format
                if "info" in file.keys():
                    descr_of_graph = file["info"] # former "graphdesc"
                # old (multiple) json files
                elif "graph" in file.keys():
                    descr_of_graph = file["graph"]["graphdesc"]  
            except:
                descr_of_graph = "Graph decription not specified."
            #print("C_DEBUG: descr_of_graph :", descr_of_graph)
                
            vecList = {}
            vecList["info"] = descr_of_graph 
            target.append(vecList)


# # graph layouts / scene -> delete / replace with graph layoutnames function
# def parseGraphJSON_graphlayouts(files,target):
#     if len(files) > 0: 
#         l_graphlayouts = files[0]["graphlayouts"]    
#         vecList = {}
#         vecList["scenes"] = l_graphlayouts
#         target.append(vecList)


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
            #print("C_DEBUG : l_layoutnames: ", l_layoutnames)

        #vecList = {}
        #vecList["scenes"] = l_layoutnames
        vecList = l_layoutnames 
        #print("C_DEBUG getting layoutnames: ", vecList)
        target.append(vecList)


# # this is for what exactly ??? 
# def parseGraphJSON_textureNames(files):
#     out = []

#     for ix,file in enumerate(files):
   
#         if "textureName" not in file.keys():
#             # no texture name specified
#             out.append(None)
#             continue
#         if file["textureName"] in out:
#             # no duplicates allowed
#             out.append(None)
#             continue    
#         out.append(file["textureName"])
#     return out


# # is this obsolete?
# def parseGraphJSON_scene_description(files):
#     out = []
#     for file in files:
#         try:
#             if "scene" in file["graph"].keys():
#                 out.append(file["graph"]["scene"])
#             elif "scene" in file.keys():
#                 out.append(file["scene"])
#         except:
#             out.append(None)
#     if len(out) != len(files):
#         return False
#     return out 
        


