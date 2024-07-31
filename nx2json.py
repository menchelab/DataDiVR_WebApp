import json
import os

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
def merge_graphs(graphs):
    all_nodes = []
    all_links = []
    layouts = []

    seen_nodes = set()  # To track seen node IDs
    seen_links = set()  # To track seen links by a tuple of (source, target)

    for graph in graphs:
        # Process nodes for global and layout-specific lists
        for node, attrs in graph.nodes(data=True):
            if node not in seen_nodes:
                annotation = attrs.get('annotation', [])
                anntation_mod = {}
                
                # Adding catch for annotation types (dict = new, list = old, anything else = no annotations found)
                if isinstance(annotation, dict):
                    for k, v in annotation.items():
                        if is_json_serializable(v):
                            anntation_mod[k] = v
                        else:
                            anntation_mod[k] = str(v)  # Convert to string if not JSON serializable
                elif isinstance(annotation, list):
                    for i in range(len(annotation)):
                        if is_json_serializable(annotation[i]):
                            anntation_mod['annotation'+str(i)] = annotation[i]
                        else:
                            anntation_mod['annotation'+str(i)] = str(annotation[i])  # Convert to string if not JSON serializable
                else:
                    anntation_mod['annotation'] = " - no annotation found."  # Blank annotation

                if not is_json_serializable(node):
                    node = str(node)  # Convert to string if not JSON serializable
                
                all_nodes.append({
                    'id': node,
                    'name': node,
                    'annotation': anntation_mod
                })
                seen_nodes.add(node)

        # Process links for global list, now with separate source and target
        for ix, (source, target, attrs) in enumerate(graph.edges(data=True)):
            if (source, target) not in seen_links:
   
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
        layout_nodes = [{
            'nodecolor': attrs.get('nodecolor', ''),
            'pos': attrs.get('pos', []),
            'cluster': attrs.get('cluster', '') if attrs.get('cluster', '') != "" else None,
            'id': str(node) if not is_json_serializable(node) else node
        } for node, attrs in graph.nodes(data=True)]

        layout_links = [{
            'linkcolor': attrs.get('linkcolor', ''),
            'source': to_int_or_str(source) if not is_json_serializable(source) else source,
            'target': to_int_or_str(target) if not is_json_serializable(target) else target
        } for source, target, attrs in graph.edges(data=True)]

        layouts.append({'layoutname': graph.name, 'nodes': layout_nodes, 'links': layout_links})

    # Assuming the structure of the graphs are similar, and using the first graph as the base
    merged_structure = {
        'directed': graphs[0].is_directed(),
        'multigraph': graphs[0].is_multigraph(),
        'projectname': graphs[0].graph.get("projectname", "Template"),
        'info': graphs[0].graph.get("info", "No description specified."),
        'graphlayouts': [graph.name for graph in graphs],  # CONSIDER REMOVING!!!
        'annotationTypes': True,
        'nodes': all_nodes,
        'links': all_links,
        'layouts': layouts
    }

    # Ensure the merged structure is JSON serializable
    merged_structure = ensure_json_serializable(merged_structure)
    

    # store merged json 
    current_wd = os.getcwd()
    
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

