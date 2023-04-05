import json
import os

import csv
import re

import GlobalData as GD

def search(term):
    project = GD.data["actPro"]
    if project != "none":
        results = []
        i = 0
        
        nodes = GD.nodes["nodes"]
        for node in nodes:
            if "attrlist" in node:
                for attr in node["attrlist"]:
                    #contains: 
                    match = re.search(term, attr, re.IGNORECASE)
                    #match = re.match(term, attr, re.IGNORECASE)
                    if match:
                        res = {"id": node["id"], "name": node["n"]+ " - " + attr, "color": GD.pixel_valuesc[node["id"]] }
                        results.append(res)
                        break
            else:
                print(str(node["id"]) + " does not have attributes")
        i += 1
    
    
    return results





def get_structure_scale(uniprot, mode) -> float or str:
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

