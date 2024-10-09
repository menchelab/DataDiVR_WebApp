import uploaderGraphS
import json
import random


with open('test.json',) as json_data:
    d = json.load(json_data)
    json_data.close()
    #print(d)
    for x in range(2000):
        thisnode = {
            "club": "Mr. Hi",
            "annotation": [
                "Node: "+ str(x),
                "Club: Mr. Hi"
            ],
            "pos": [
                
                
                random.uniform(-0.1, 1),random.uniform(-1, 1),
                random.uniform(-1, 1)
            ],
            "nodecolor": [random.randint(0, 255),random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)],
            "id": 0
        }
        d["nodes"].append(thisnode)

    for l in range(2000):
        thislink = {
            "weight": 4,
            "linkcolor": [128,0,0,128],
            "source": random.randint(0, 199),
            "target": random.randint(0, 199)
        }
        d["links"].append(thislink)
    uploaderGraphS.upload_filesJSON(d)

#upload_filesNew(nodepositions, nodecolors,links,linkcolors,nodeinfo,labels):