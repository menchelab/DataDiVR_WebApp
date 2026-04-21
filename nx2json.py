import json
import os
import networkx as nx 
import numpy as np 


try:
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    from uploaderGraph import upload_filesJSON
   
except:
    print("Error: Could not import the uploaderGraph module. \n Only importing the necessary functions for the function 'make_json' to run. \n Please ensure the uploader module is in the same directory as this script.")


# TO DO: a catch & error message if types are converted , e.g. positions from float to str
def ensure_json_serializable(obj):
    if isinstance(obj, dict):
        return {k: ensure_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [ensure_json_serializable(i) for i in obj]
    elif isinstance(obj, tuple):
        return tuple(ensure_json_serializable(i) for i in obj)
    elif isinstance(obj, set):
        return [ensure_json_serializable(i) for i in obj]
    else:
        try:
            json.dumps(obj)
            return obj
        except (TypeError, OverflowError):
            return str(obj)

def to_int_or_str(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return str(value)
    

def is_json_serializable(value):
    try:
        json.dumps(value)
        return True
    except (TypeError, OverflowError):
        return False

def ensure_json_serializable(obj):
    if isinstance(obj, dict):
        return {k: ensure_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [ensure_json_serializable(i) for i in obj]
    elif isinstance(obj, tuple):
        return tuple(ensure_json_serializable(i) for i in obj)
    elif isinstance(obj, set):
        return [ensure_json_serializable(i) for i in obj]
    else:
        try:
            json.dumps(obj)
            return obj
        except (TypeError, OverflowError):
            return str(obj)


# the actual merging function to create a json file in the required structure for the newest uploading procedure (state july 2024)
def make_json(graphs, save_json=False): # former: merge_graphs(graphs):
    
    all_nodes = []
    all_links = []
    layouts = []
    l_layoutnames = []
    
    seen_nodes = set()  # To track seen node IDs
    seen_links = set()  # To track seen links by a tuple of (source, target)

    # add check if a list or a single nx.graph object
    if not isinstance(graphs, list):
        graphs = [graphs]
    
    # order graphs alphabetically 
    # catch if not layoutname in keys
    for graph in graphs:
        try:
            graph.graph["layoutname"]
            #print("Layoutname found: ", graph.graph["layoutname"])
        except KeyError:
            graph.graph["layoutname"] = "layoutname_" + str(graphs.index(graph))
            #print("NO Layoutname found: ", graph.graph["layoutname"])
        
    graphs = sorted(graphs, key=lambda x: x.graph["layoutname"])
    
    for graph in graphs:
        #print("Processing graph: ", graph.graph["layoutname"])
        
        # Remap node IDs to integers
        mapping = {node: idx for idx, node in enumerate(graph.nodes())}
        graph_remapped = nx.relabel_nodes(graph, mapping) 
        
        # Process nodes for global and layout-specific lists
        for node, attrs in graph.nodes(data=True):
   
            if node not in seen_nodes:
                
                # ANNOTATIONS
                annotation = attrs.get('annotation', [])
                annotation_mod = {}
                
                # Adding catch for annotation types (dict = new, list = old, anything else = no annotations found)
                if isinstance(annotation, dict):
                    for k, v in annotation.items():
                        if is_json_serializable(v):
                            annotation_mod[k] = v
                        else:
                            annotation_mod[k] = str(v)  # Convert to string if not JSON serializable
                elif isinstance(annotation, list):
                    for i in range(len(annotation)):
                        if is_json_serializable(annotation[i]):
                            annotation_mod['annotation'+str(i)] = annotation[i]
                        else:
                            annotation_mod['annotation'+str(i)] = str(annotation[i])  # Convert to string if not JSON serializable
                else:
                    annotation_mod['annotation'] = " - no annotation found."  # Blank annotation

                # NODE ID
                nodeid = mapping[node]
                
                if not is_json_serializable(node):
                    nodeid = str(nodeid)  # Convert to string if not JSON serializable

                # NODENAME 
                try:
                    nodename = attrs.get('name', node)
                except:
                    nodename = node

                all_nodes.append({
                    'id': nodeid,
                    'name': nodename,
                    'annotation': annotation_mod
                })
                seen_nodes.add(node)

        # Process links for global list, now with separate source and target
        for ix, (source, target, attrs) in enumerate(graph.edges(data=True)):
            if (source, target) not in seen_links:
    
                # get node id from mapping of source and target
                source = mapping[source]
                target = mapping[target]
                
                if not is_json_serializable(source):
                    try:
                        source = int(source)
                    except:
                        source = str(source)  # quick fix: Convert to string if not JSON serializable
                if not is_json_serializable(target):
                    try:
                        target = int(target)
                    except:
                        target = str(target)  # quick fix: Convert to string if not JSON serializable

                all_links.append({
                    'id': ix,  #
                    'source': source,
                    'target': target
                })
                seen_links.add((source, target))

        # Prepare layout-specific nodes and links
        layout_nodes = []
        for node, attrs in graph_remapped.nodes(data=True):
            
            if isinstance(attrs.get('pos', []), np.ndarray):
                #print("C_DEBUG NPARRAY: positions are numpy array, converting to list.")
                pos = attrs.get('pos', []).tolist()
            elif isinstance(attrs.get('pos', []), list) or isinstance(attrs.get('pos', []), tuple):
                #print("C_DEBUG LIST/TUPLE: positions are LIST/TUPLE, using as is.")
                pos = attrs.get('pos', [])
            else:
                #print("C_DEBUG: empty positions or incorrect datatype.")
                pos = [0, round(node * 0.1, 1), 0] # make random position based on node id, if no position is given or if the datatype is incorrect (e.g. string)

            layout_nodes.append({
            'nodecolor': attrs.get('nodecolor', ''),
            'pos': pos,
            'cluster': attrs.get('cluster', '') if attrs.get('cluster', '') != "" else None,
            'id': str(node) if not is_json_serializable(node) else node
            })

        # # add check for pos types (float, int, str)
        # for i in range(len(layout_nodes)):
        #     if isinstance(layout_nodes[i]['pos'], (list)): # and len(layout_nodes[i]['pos']) >= 2 and len(layout_nodes[i]['pos']) <= 3:
        #         individual_node = layout_nodes[i]['pos']
        #         for j in range(len(individual_node)):
        #             if isinstance(individual_node[j], (float)):
        #                 individual_node[j] = float(individual_node[j])
        #             else:
        #                 raise ValueError("Positions must be class type float.")

        #if len(individual_node) < 2 or len(individual_node) > 3:
        #    raise ValueError("Position must have 2 or 3 dimensions.")

        #print("Layout nodes: ", layout_nodes)
        #print("Layout pos types: ", [type(node['pos'][0]) for node in layout_nodes])

        layout_links = [{
            'linkcolor': attrs.get('linkcolor', ''),
            'source': to_int_or_str(source) if not is_json_serializable(source) else source,
            'target': to_int_or_str(target) if not is_json_serializable(target) else target
        } for source, target, attrs in graph_remapped.edges(data=True)]

        # check if "layoutname" exists
        try:
            layout_name = graph.graph["layoutname"]
            l_layoutnames.append(layout_name)
        except KeyError:
            layout_name = "layoutname_" + str(graphs.index(graph))
            l_layoutnames.append(layout_name)
                
        layouts.append({'layoutname': layout_name, 'nodes': layout_nodes, 'links': layout_links})


    # Assuming the structure of the graphs are similar, and using the first graph as the base
    merged_structure = {
        'directed': graphs[0].is_directed(),
        'multigraph': graphs[0].is_multigraph(),
        'projectname': graphs[0].graph.get("projectname", "Template"),
        'info': graphs[0].graph.get("info", "No description specified."),
        'graphlayouts': l_layoutnames,
        'annotationTypes': True,
        'nodes': all_nodes,
        'links': all_links,
        'layouts': layouts
    }

    # Ensure the merged structure is JSON serializable
    merged_structure = ensure_json_serializable(merged_structure)
    
    # store merged json 
    current_wd = os.getcwd()
    
    if save_json == True: 
        try:
            # Ensure a proper path separator between directory and file name
            file_path = os.path.join(current_wd, merged_structure["projectname"] + '.json')
            with open(file_path, 'w') as f:
                json.dump(merged_structure, f, indent=4)
            
            print("Merged JSON file saved as: ", file_path)
        
        except Exception as e:
            print("Error: Could not save merged JSON file.")
            print("Exception:", e)
    
    return merged_structure

def create_project(graphs):
    merged_structure = make_json(graphs)
    upload_filesJSON(merged_structure)
    #return merged_structure

