import GlobalData as GD



def addNodeToClipboard(nodeId):
    if not "cbnode" in GD.pdata.keys():
        GD.pdata["cbnode"] = []
        
    
    for n in GD.pdata["cbnode"]:
        if nodeId == int(n["id"]):
            return
        
    node_to_add = {}
    node_to_add["id"] = nodeId
    node_to_add["color"] = GD.pixel_valuesc[nodeId]
    node_to_add["name"] = GD.nodes["nodes"][nodeId]["n"]
    GD.pdata["cbnode"].append(node_to_add)
    GD.savePD()
    return

def addNodesToClipboard(nodeIds):
    if not "cbnode" in GD.pdata.keys():
        GD.pdata["cbnode"] = []
        
    for nodeId in nodeIds:
        for n in GD.pdata["cbnode"]:
            if nodeId == int(n["id"]):
                return
        node_to_add = {}
        node_to_add["id"] = nodeId
        node_to_add["color"] = GD.pixel_valuesc[nodeId]
        node_to_add["name"] = GD.nodes["nodes"][nodeId]["n"]
        GD.pdata["cbnode"].append(node_to_add)
        
        GD.pdata["cbnode"].append(node_to_add)
    GD.savePD()
    return


def clearClipboard():
    GD.pdata["cbnode"] = []
    GD.savePD()
    return