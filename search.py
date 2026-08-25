import json
import os

import csv
import re

import GlobalData as GD

def search(term):

    project = GD.data["actPro"]
    if project != "none":

        term = term.replace("\n", "")

        #term = str(term)

        results = []
        nodes = GD.nodes["nodes"]
        for node in nodes:

            # search for term in node name
            if "n" in node:
                nodename = node["n"] 

                # catch if n is not a string
                if not isinstance(nodename, str):
                    nodename = str(nodename)
                    
                if term.lower() in nodename.lower():
                    res = {"id": node["id"], "name": node["n"], "color": GD.pixel_valuesc[node["id"]] }
                    results.append(res)
                    #break
                
            # search for term in attributes
            if "attrlist" in node:
                # check if attribute structure is a list or a dict
                if isinstance(node["attrlist"], list):
                    for attr in node["attrlist"]:
                        if term.lower() in attr.lower() or attr.lower() in term.lower() or re.search(r'\b'+term.lower()+r'\b', attr.lower()):
                            res = {"id": node["id"], "name": node["n"], "color": GD.pixel_valuesc[node["id"]] }
                            results.append(res)
                            #break

                if isinstance(node["attrlist"], dict):
                    for key,value in node["attrlist"].items():
                        if isinstance(value, list):
                            for v in value:
                                try:
                                    if term.lower() in v.lower() or v.lower() in term.lower() or re.search(r'\b'+term.lower()+r'\b', v.lower()):
                                        res = {"id": node["id"], "name": node["n"], "color": GD.pixel_valuesc[node["id"]] }
                                        results.append(res)
                                        #break
                                except Exception as e:
                                    print("Error processing value:", e)
                                    continue
                                   

                        elif isinstance(value, str):
                            if term.lower() in value.lower():
                                res = {"id": node["id"], "name": node["n"], "color": GD.pixel_valuesc[node["id"]] }
                                results.append(res)
                                #break  
        # make sure no duplicates are in the results
        results = [dict(t) for t in {tuple(d.items()) for d in results}]
        
    return results


def _dedupe_preserve_order(results):
    """
    Remove duplicate result dicts while preserving the order they were found in.
    (A plain `{tuple(d.items()) for d in results}` set comprehension would also
    dedupe, but sets have no defined order, so it silently scrambles the results.)
    """
    seen = set()
    deduped = []
    for res in results:
        key = tuple(res.items())
        if key not in seen:
            seen.add(key)
            deduped.append(res)
    return deduped


def _rank_by_match_quality(results, term):
    """
    Sort search results so the best-fitting match comes first:
    exact name match, then name starts with the term, then everything else.
    The relative order within each of those groups is left as-is (unordered).
    """
    term_lower = term.lower()

    def match_rank(res):
        name = str(res.get("name", "")).lower()
        if name == term_lower:
            return 0
        if name.startswith(term_lower):
            return 1
        return 2

    return sorted(results, key=match_rank)


def search_id(term):
    """
    Search for nodes by their ID in the current project.
    Args:
        term (int): The ID of the node to search for.
    Returns:
        list: A list of dictionaries containing the nodes' ID, name, and color if found, otherwise an empty list.
    """
    if not isinstance(term, int):
        raise ValueError("The term must be an integer.")

    project = GD.data["actPro"]
    if project != "none":
        results = []
        nodes = GD.nodes["nodes"]

        for node in nodes:
            if "id" in node and term == node["id"]:
                res = {"id": node["id"], "name": node["n"], "color": GD.pixel_valuesc[node["id"]]}
                results.append(res)

        # make sure no duplicates are in the results
        results = _dedupe_preserve_order(results)

    print("C_DEBUG: search_id results:", results)

    return results


def search_name(term):
    """
    Search for a node by its name in the current project.
    Args:
        term (str): The name of the node to search for.
    Returns:
        list: A list of dictionaries containing the nodes' ID, name, and color if found, otherwise an empty list.
            The best-fitting match (exact name match, then name-starts-with-term)
            is returned first; the rest of the matches are unordered.
    """
    project = GD.data["actPro"]
    if project != "none":
        term = term.replace("\n", "")
        results = []
        nodes = GD.nodes["nodes"]

        for node in nodes:
            # Ensure the node has the key "n" and search for the term in the node name
            if "n" in node:
                nodename = node["n"]
                if isinstance(nodename, str) and term.lower() in nodename.lower():
                    res = {"id": node["id"], "name": node["n"], "color": GD.pixel_valuesc[node["id"]]}
                    results.append(res)

        # Remove duplicates from the results, then float the best-fitting match to the top
        results = _dedupe_preserve_order(results)
        results = _rank_by_match_quality(results, term)

    print("C_DEBUG: search_name results:", results)

    return results



# def search_attribute(term):
#     """
#     Search for a node by an attribute in the current project.
#     Args:
#         term (str): The attribute to search for.
#     Returns:
#         list: A list of dictionaries containing the node's ID, name, and color if found, otherwise an empty list.
#     """
#     project = GD.data["actPro"]
#     results = []
#     if project != "none":
#         term = term.replace("\n", "")
#         nodes = GD.nodes["nodes"]
    
#         print("C_DEBUG: Searching for ATTRIBUTE:", term)

#         for node in nodes:
#             if "attrlist" in node:
#                 # check if attribute structure is a list or a dict
#                 if isinstance(node["attrlist"], list):
#                     for attr in node["attrlist"]:
#                         if term.lower() in attr.lower() or attr.lower() in term.lower() or re.search(r'\b'+term.lower()+r'\b', attr.lower()):
#                             res = {"id": node["id"], "name": node["n"], "color": GD.pixel_valuesc[node["id"]]}
#                             results.append(res)

#                 elif isinstance(node["attrlist"], dict):
#                     for key, value in node["attrlist"].items():
#                         if isinstance(value, list):
#                             for v in value:
#                                 if term.lower() in v.lower() or v.lower() in term.lower() or re.search(r'\b'+term.lower()+r'\b', v.lower()):
#                                     res = {"id": node["id"], "name": node["n"], "color": GD.pixel_valuesc[node["id"]]}
#                                     results.append(res)

#                         elif isinstance(value, str):
#                             if term.lower() in value.lower():
#                                 res = {"id": node["id"], "name": node["n"], "color": GD.pixel_valuesc[node["id"]]}
#                                 results.append(res)
#         # make sure no duplicates are in the results
#         results = [dict(t) for t in {tuple(d.items()) for d in results}]
#     return results





def search_by_termtype(term):
    """
    Search for a node by its term type and term in the current project.
    Args:
        term (Union[int, str]): The term to search for.
    Returns:
        list: A list of dictionaries containing the node's ID, name, and color if found, otherwise an empty list.
    """

    #try:
    #    term = int(term)
    #except:
    #    term = str(term)

    # try to make input an int if possible, otherwise keep it as a string
    try:
        term = int(term)
        print("C_DEBUG : In search.py - search_by_termtype(term): term is int", term)
        return search_id(term)
    
    except ValueError:
        term = str(term)
        print("C_DEBUG : In search.py - search_by_termtype(term): term is str", term)
        return search_name(term)

    # if isinstance(term, int):
    #     print("C_DEBUG : In search.py - search_by_termtype(term): term is int", term)
    #     return search_id(term)
    
    # elif isinstance(term, str):
    #     print("C_DEBUG : In search.py - search_by_termtype(term): term is str", term)
    #     return search_name(term)
 
    # else:
    #     print("Error: Unknown term type or invalid term format. Please provide a valid term type (id, name, attribute) and ensure the term matches the expected format.")
    #     return []










from typing import Union
def get_structure_scale(uniprot, mode) -> Union[float, str]:
    """Return the scale of the structure as a float. If the structure is not found (or not provided), the size file is not available or the mode is not given, the function will return an error message as string. To provide the UniProtID add the 'uniprot=<UniProtID>', for the mode add 'mode=<mode>' to the URL. Currently available modes are 'cartoon' and 'electrostatic'. The default mode is 'cartoon'."""


    if mode is None:
        print("Error: No mode provided. Will use default mode 'cartoon'.")
        mode = "cartoon"

    if uniprot is None:
        return "Error: No UniProtID provided."

    possible_files = {
        "cartoon": os.path.join(".", "static", "example_files", "protein_structure_info", "scales_Cartoon.csv"),
        "electrostatic": os.path.join(
            ".", "static", "example_files", "protein_structure_info", "scales_electrostatic_surface.csv"
        ),
    }
    scale_file = possible_files.get(mode)

    # Prevent FileNotFound errors.
    if scale_file is None:
        return "Error: Mode not available."
    if not os.path.exists(scale_file):
        return "Error: File not found."

    # Search for size of structure.
    with open(scale_file, "r") as f:
        csv_file = csv.reader(f)
        for row in csv_file:
            if row[0] == uniprot:
                scale = row[1]
                return scale

    # Structure not found in the scale file -> no available.
    return "Error: No structure available for this UniProtID."




def search_nodeid_by_name(nodename):
    project = GD.data["actPro"]
    if project != "none":
        nodes = GD.nodes["nodes"]
        for node in nodes:
            if "n" in node:
                if nodename.lower() == node["n"].lower():
                    return node["id"]
    return None