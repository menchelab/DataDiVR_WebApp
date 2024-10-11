import json
from uploaderGraph import *
import random


with open('CircularLadderGraph.json',) as json_data:
    
    d = json.load(json_data)
    d["projectname"] = "xyz1235" 
    '''
 
      
    d["annotationTypes"] = "true"
    d["nodes"] = []
    d["links"] = []
    d["layouts"] = []
    d["graphlayouts"] = ["test"]
    newLayout = {}
    newLayout["layoutname"] = "test"
    newLayout["nodes"] = []
    d["layouts"].append(newLayout)

    for i in range (20):
        newnode = {}
        newnode["id"] = i
        newnode["name"] = "node_" + str(i)
        

        newLayoutNode = {
                    "nodecolor": [
                        0,
                        0,
                        255,
                        200
                    ],
                    "pos": [
                        random.uniform(-1, 1),
                        random.uniform(-1, 1),
                        random.uniform(-1, 1)
                    ],
                    "id": i
                }
        d["layouts"][0]["nodes"].append(newLayoutNode)
        d["nodes"].append(newnode)
    print(d)
    '''
    upload_filesJSON(d)
    json_data.close()
    

    