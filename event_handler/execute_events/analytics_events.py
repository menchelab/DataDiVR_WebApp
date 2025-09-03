from flask_socketio import emit

import analytics
import GlobalData as GD
import util
import clipboad


def degree_run_event(message, room, project):
    """
    Processes the degree distribution analytics event.
    Retrieves and processes the degree distribution data from the project graph,
    generates plot data, and sends the results to the client.
    
    Args:
        message (dict): Event data containing user and function details.
        room (str): Socket connection room identifier.
        project (str): Project name to retrieve the graph from.
    """
    
    if "analyticsDegreeRun" not in GD.session_data.keys():
        ### "expensive" stuff
        if "graph" not in GD.session_data.keys():
            GD.session_data["graph"] = util.project_to_graph(project)
        graph = GD.session_data["graph"]

        result = analytics.analytics_degree_distribution(graph)
        ###
        GD.session_data["analyticsDegreeRun"] = result
    arr = GD.session_data["analyticsDegreeRun"]

    highlight = None
    if "highlight" in message.keys():
        highlight = int(message["highlight"])
        

    plot_data, highlighted_degrees = analytics.plotly_degree_distribution(
        arr, highlight
    )

    response = {
        "fn": message["fn"],
        "usr": message["usr"],
        "id": "analyticsDegreePlot",
        "target": "analyticsContainer",
        "val": plot_data,
    }
    emit("ex", response, room=room, namespace = "/main") # added namespace explicitly

    # setup new texture
    if highlight is None:
        return
    
    analytics.update_analytics_highlight(message["event"], analytics.get_node_ids_from_highlight_sequence(arr, highlighted_degrees))

    degree_distribution_textures = analytics.analytics_color_degree_distribution(
        arr, highlighted_degrees
    )
    if degree_distribution_textures["textures_created"] is False:
        print("Failed to create textures for Analytics/Shortest Path.")
        return

    textures = [
        {
            "channel": "nodeRGB",
            "path": degree_distribution_textures["path_nodes"],
        },
        {
            "channel": "linkRGB",
            "path": degree_distribution_textures["path_links"],
        },
    ]
    response = {"usr": message["usr"], "fn": "updateTempTex", "textures": textures}

    emit("ex", response, room=room, namespace = "/main") # added namespace explicitly




def closeness_run_event(message, room, project):
    """
    Processes the closeness centrality analytics event.
    Retrieves and processes closeness centrality data from the project graph,
    generates plot data, and sends the results to the client.
    
    Args:
        message (dict): Event data containing user and function details.
        room (str): Socket connection room identifier.
        project (str): Project name to retrieve the graph from.
    """

    if "analyticsClosenessRun" not in GD.session_data.keys():
        ### "expensive" stuff
        if "graph" not in GD.session_data.keys():
            GD.session_data["graph"] = util.project_to_graph(project)
        graph = GD.session_data["graph"]
        result = analytics.analytics_closeness(graph)
        ###
        GD.session_data["analyticsClosenessRun"] = result
    arr = GD.session_data["analyticsClosenessRun"]

    highlight = None
    if "highlight" in message.keys():
        highlight = float(message["highlight"])

    plot_data, highlighted_closeness = analytics.plotly_closeness(arr, highlight)

    response = {
        "fn": message["fn"],
        "usr": message["usr"],
        "id": "analyticsClosenessPlot",
        "target": "analyticsContainer",
        "val": plot_data,
    }
    emit("ex", response, room=room, namespace= "/main")  # added namespace explicitly


    # setup new texture
    if highlight is None:
        return

    analytics.update_analytics_highlight(message["event"], analytics.get_node_ids_from_highlight_bounds(arr, highlighted_closeness))

    closeness_textures = analytics.analytics_color_continuous(
        arr, highlighted_closeness
    )
    if closeness_textures["textures_created"] is False:
        print("Failed to create textures for Analytics/Closeness.")
        return

    textures = [
        {"channel": "nodeRGB", "path": closeness_textures["path_nodes"]},
        {"channel": "linkRGB", "path": closeness_textures["path_links"]},
    ]
    response = {"usr": message["usr"], "fn": "updateTempTex", "textures": textures}
    emit("ex", response, room=room, namespace = "/main")  # added namespace explicitly




def path_node1_event(message, room):
    """
    Handles the selection of the first node for shortest path analytics.
    Updates server-side data with the selected node and sends the updated data to the client.
    
    Args:
        message (dict): Event data containing user and function details.
        room (str): Socket connection room identifier.
    """

    # set server data: node +  hex color
    if message["val"] != "init":
        if "analyticsData" not in GD.pdata.keys():
            GD.pdata["analyticsData"] = {}
            print(GD.pdata)
        if "shortestPathNode1" not in GD.pdata["analyticsData"].keys():
            GD.pdata["analyticsData"]["shortestPathNode1"] = {}
        GD.pdata["analyticsData"]["shortestPathNode1"]["id"] = GD.pdata["activeNode"]
        GD.pdata["analyticsData"]["shortestPathNode1"]["color"] = util.rgb_to_hex(
            GD.pixel_valuesc[int(GD.pdata["activeNode"])]
        )
        GD.pdata["analyticsData"]["shortestPathNode1"]["name"] = GD.nodes["nodes"][
            int(GD.pdata["activeNode"])
        ]["n"]
        GD.savePD()

    # send to clients
    response = {}
    response = {
        "fn": "analytics",
        "id": message["id"],
        "usr": message["usr"],
        "val": "init",
    }
    if "analyticsData" in GD.pdata.keys():
        if "shortestPathNode1" in GD.pdata["analyticsData"].keys():
            response["val"] = GD.pdata["analyticsData"]["shortestPathNode1"]
    emit("ex", response, room=room, namespace = "/main") # added namespace explicitly



def path_node2_event(message, room):
    """
    Handles the selection of the second node for shortest path analytics.
    Updates server-side data with the selected node and sends the updated data to the client.
    
    Args:
        message (dict): Event data containing user and function details.
        room (str): Socket connection room identifier.
    """

    # set server data: node +  hex color
    if message["val"] != "init":
        if "analyticsData" not in GD.pdata.keys():
            GD.pdata["analyticsData"] = {}
            print(GD.pdata)
        if "shortestPathNode2" not in GD.pdata["analyticsData"].keys():
            GD.pdata["analyticsData"]["shortestPathNode2"] = {}
        GD.pdata["analyticsData"]["shortestPathNode2"]["id"] = GD.pdata["activeNode"]
        GD.pdata["analyticsData"]["shortestPathNode2"]["color"] = util.rgb_to_hex(
            GD.pixel_valuesc[int(GD.pdata["activeNode"])]
        )
        GD.pdata["analyticsData"]["shortestPathNode2"]["name"] = GD.nodes["nodes"][
            int(GD.pdata["activeNode"])
        ]["n"]
        GD.savePD()

    # send to clients
    response = {}
    response["usr"] = message["usr"]
    response["id"] = message["id"]
    response["fn"] = "analytics"
    response["val"] = "init"
    if "analyticsData" in GD.pdata.keys():
        if "shortestPathNode2" in GD.pdata["analyticsData"].keys():
            response["val"] = GD.pdata["analyticsData"]["shortestPathNode2"]
    emit("ex", response, room=room, namespace = "/main") # added namespace explicitly



# def path_run_old_event(message, room, project):
#     if "analyticsData" not in GD.pdata.keys():
#         print("[Fail] analytics shortest path run: 2 nodes have to be selected.")
#         return
#     if "shortestPathNode1" not in GD.pdata["analyticsData"].keys():
#         print("[Fail] analytics shortest path run: 2 nodes have to be selected.")
#         return
#     if "shortestPathNode1" not in GD.pdata["analyticsData"].keys():
#         print("[Fail] analytics shortest path run: 2 nodes have to be selected.")
#         return

#     node_1 = GD.pdata["analyticsData"]["shortestPathNode1"]["id"]
#     node_2 = GD.pdata["analyticsData"]["shortestPathNode2"]["id"]
#     if "graph" not in GD.session_data.keys():
#         GD.session_data["graph"] = util.project_to_graph(project)
#     graph = GD.session_data["graph"]
#     path = analytics.analytics_shortest_path(graph, node_1, node_2)
#     shortest_path_textures = analytics.analytics_color_shortest_path(path)

#     if shortest_path_textures["textures_created"] is False:
#         print("Failed to create textures for Analytics/Shortest Path.")
#         return
#     response = {}
#     response["usr"] = message["usr"]
#     response["fn"] = "updateTempTex"
#     response["textures"] = []
#     response["textures"].append(
#         {"channel": "nodeRGB", "path": shortest_path_textures["path_nodes"]}
#     )
#     response["textures"].append(
#         {"channel": "linkRGB", "path": shortest_path_textures["path_links"]}
#     )
#     emit("ex", response, room=room)


def path_run_event(message, room, project):
    """
    Executes the shortest path analytics event.
    Generates shortest paths in the graph, applies coloring, and sends the results to the client.
    
    Args:
        message (dict): Event data containing user and function details.
        room (str): Socket connection room identifier.
        project (str): Project name to retrieve the graph from.
    """

    # generate paths
    if "graph" not in GD.session_data.keys():
        GD.session_data["graph"] = util.project_to_graph(project)
    graph = GD.session_data["graph"]

    shortest_path_result_obj = analytics.analytics_shortest_path_run(graph=graph)
    if shortest_path_result_obj["success"] is False:
        print("ERROR: analytics/shortest_path:", shortest_path_result_obj["error"])
        return
    # apply coloring and
    shortest_path_display_obj = analytics.analytics_shortest_path_display()
    if shortest_path_display_obj["textures_created"] is False:
        print("ERROR: analytics/shortest_path: Texture Generation Failed")
        return

    # send to frontend
    response_textures = {}
    response_textures["usr"] = message["usr"]
    response_textures["fn"] = "updateTempTex"
    response_textures["textures"] = []
    response_textures["textures"].append(
        {"channel": "nodeRGB", "path": shortest_path_display_obj["path_nodes"]}
    )
    response_textures["textures"].append(
        {"channel": "linkRGB", "path": shortest_path_display_obj["path_links"]}
    )
    emit("ex", response_textures, room=room, namespace = "/main") # added namespace explicitly


    response_info = {}
    response_info["usr"] = message["usr"]
    response_info["fn"] = "analytics"
    response_info["id"] = "analyticsPathInfo"
    response_info["val"] = {
        "numPathsAll": shortest_path_display_obj["numPathsAll"],
        "numPathCurrent": shortest_path_display_obj["numPathCurrent"],
        "pathLength": shortest_path_display_obj["pathLength"],
    }
    emit("ex", response_info, room=room)



def path_backwards_event(message, project, room):
    """
    Steps backward in the shortest path analytics visualization.
    Updates the graph visualization and sends the updated textures to the client.
    
    Args:
        message (dict): Event data containing user and function details.
        project (str): Project name to retrieve the graph from.
        room (str): Socket connection room identifier.
    """

    # generate paths
    if "graph" not in GD.session_data.keys():
        GD.session_data["graph"] = util.project_to_graph(project)
    graph = GD.session_data["graph"]
    shortest_path_result_obj = analytics.analytics_shortest_path_run(graph=graph)
    if shortest_path_result_obj["success"] is False:
        print("ERROR: analytics/shortest_path:", shortest_path_result_obj["error"])
        return

    # step backwards
    analytics.analytics_shortest_path_backward()

    # apply coloring and
    shortest_path_display_obj = analytics.analytics_shortest_path_display()
    if shortest_path_display_obj["textures_created"] is False:
        print("ERROR: analytics/shortest_path: Texture Generation Failed")
        return

    # send to frontend
    response_textures = {}
    response_textures["usr"] = message["usr"]
    response_textures["fn"] = "updateTempTex"
    response_textures["textures"] = []
    response_textures["textures"].append(
        {"channel": "nodeRGB", "path": shortest_path_display_obj["path_nodes"]}
    )
    response_textures["textures"].append(
        {"channel": "linkRGB", "path": shortest_path_display_obj["path_links"]}
    )
    emit("ex", response_textures, room=room)

    response_info = {}
    response_info["usr"] = message["usr"]
    response_info["fn"] = "analytics"
    response_info["id"] = "analyticsPathInfo"
    response_info["val"] = {
        "numPathsAll": shortest_path_display_obj["numPathsAll"],
        "numPathCurrent": shortest_path_display_obj["numPathCurrent"],
        "pathLength": shortest_path_display_obj["pathLength"],
    }
    emit("ex", response_info, room=room, namespace = "/main") # added namespace explicitly



def path_forwards_event(message, room, project):
    """
    Steps forward in the shortest path analytics visualization.
    Updates the graph visualization and sends the updated textures to the client.
    
    Args:
        message (dict): Event data containing user and function details.
        room (str): Socket connection room identifier.
        project (str): Project name to retrieve the graph from.
    """
     
    # generate paths
    if "graph" not in GD.session_data.keys():
        GD.session_data["graph"] = util.project_to_graph(project)
    graph = GD.session_data["graph"]
    shortest_path_result_obj = analytics.analytics_shortest_path_run(graph=graph)
    if shortest_path_result_obj["success"] is False:
        print("ERROR: analytics/shortest_path:", shortest_path_result_obj["error"])
        return

    # step forwards
    analytics.analytics_shortest_path_forward()

    # apply coloring and
    shortest_path_display_obj = analytics.analytics_shortest_path_display()
    if shortest_path_display_obj["textures_created"] is False:
        print("ERROR: analytics/shortest_path: Texture Generation Failed")
        return

    # send to frontend
    response_textures = {}
    response_textures["usr"] = message["usr"]
    response_textures["fn"] = "updateTempTex"
    response_textures["textures"] = []
    response_textures["textures"].append(
        {"channel": "nodeRGB", "path": shortest_path_display_obj["path_nodes"]}
    )
    response_textures["textures"].append(
        {"channel": "linkRGB", "path": shortest_path_display_obj["path_links"]}
    )
    emit("ex", response_textures, room=room)

    response_info = {}
    response_info["usr"] = message["usr"]
    response_info["fn"] = "analytics"
    response_info["id"] = "analyticsPathInfo"
    response_info["val"] = {
        "numPathsAll": shortest_path_display_obj["numPathsAll"],
        "numPathCurrent": shortest_path_display_obj["numPathCurrent"],
        "pathLength": shortest_path_display_obj["pathLength"],
    }
    emit("ex", response_info, room=room, namespace = "/main") # added namespace explicitly



def eigenvector_run_event(message, room, project):
    """
    Processes the eigenvector centrality analytics event.
    Retrieves and processes eigenvector centrality data from the project graph,
    generates plot data, and sends the results to the client.
    
    Args:
        message (dict): Event data containing user and function details.
        room (str): Socket connection room identifier.
        project (str): Project name to retrieve the graph from.
    """

    if "analyticsEigenvectorRun" not in GD.session_data.keys():
        ### "expensive" stuff
        if "graph" not in GD.session_data.keys():
            GD.session_data["graph"] = util.project_to_graph(project)
        graph = GD.session_data["graph"]
        result = analytics.analytics_eigenvector(graph)
        ###
        GD.session_data["analyticsEigenvectorRun"] = result
    arr = GD.session_data["analyticsEigenvectorRun"]  # index: visual 1, original 0

    highlight = None
    if "highlight" in message.keys():
        highlight = float(message["highlight"])

    plot_data, highlighted_ev = analytics.plotly_eigenvector(arr, highlight)

    response = {}
    response["fn"] = message["fn"]
    response["usr"] = message["usr"]
    response["id"] = "analyticsEigenvectorPlot"
    response["target"] = "analyticsContainer"  # container to render plot in
    response["val"] = plot_data
    emit("ex", response, room=room, namespace = "/main") # added namespace explicitly


    # setup new texture
    if highlight is None:
        return


    analytics.update_analytics_highlight(message["event"], analytics.get_node_ids_from_highlight_bounds(arr, highlighted_ev))


    closeness_textures = analytics.analytics_color_continuous(
        arr, highlighted_ev
    )
    if closeness_textures["textures_created"] is False:
        print("Failed to create textures for Analytics/Eigenvector.")
        return

    response = {}
    response["usr"] = message["usr"]
    response["fn"] = "updateTempTex"
    response["textures"] = []
    response["textures"].append(
        {"channel": "nodeRGB", "path": closeness_textures["path_nodes"]}
    )
    response["textures"].append(
        {"channel": "linkRGB", "path": closeness_textures["path_links"]}
    )
    emit("ex", response, room=room, namespace = "/main") # added namespace explicitly



def clusteringcoefficient_run_event(message, room, project):
    """
    Processes the clustering coefficient analytics event.
    Retrieves and processes clustering coefficient data from the project graph,
    generates plot data, and sends the results to the client.
    
    Args:
        message (dict): Event data containing user and function details.
        room (str): Socket connection room identifier.
        project (str): Project name to retrieve the graph from.
    """

    if "analyticsClusteringcoefficientRun" not in GD.session_data.keys():
        ### "expensive" stuff
        if "graph" not in GD.session_data.keys():
            GD.session_data["graph"] = util.project_to_graph(project)
        graph = GD.session_data["graph"]
        result = analytics.analytics_clusteringcoefficient(graph)
        ###
        GD.session_data["analyticsClusteringcoefficientRun"] = result
    arr = GD.session_data["analyticsClusteringcoefficientRun"]

    highlight = None
    if "highlight" in message.keys():
        highlight = float(message["highlight"])

    plot_data, highlighted_closeness = analytics.plotly_clustering_coefficient(
        arr, highlight
    )

    response = {}
    response["fn"] = message["fn"]
    response["usr"] = message["usr"]
    response["id"] = "analyticsClusteringCoeffPlot"
    response["target"] = "analyticsContainer"  # container to render plot in
    response["val"] = plot_data
    emit("ex", response, room=room, namespace = "/main") # added namespace explicitly


    # setup new texture
    if highlight is None:
        return


    analytics.update_analytics_highlight(message["event"], analytics.get_node_ids_from_highlight_bounds(arr, highlighted_closeness))

    closeness_textures = analytics.analytics_color_continuous(
        arr, highlighted_closeness
    )
    if closeness_textures["textures_created"] is False:
        print("Failed to create textures for Analytics/Clustering Coefficient.")
        return

    response = {}
    response["usr"] = message["usr"]
    response["fn"] = "updateTempTex"
    response["textures"] = []
    response["textures"].append(
        {"channel": "nodeRGB", "path": closeness_textures["path_nodes"]}
    )
    response["textures"].append(
        {"channel": "linkRGB", "path": closeness_textures["path_links"]}
    )
    emit("ex", response, room=room, namespace = "/main") # added namespace explicitly



def mod_community_run_event(message, room, project):
    """
    Processes the modularity-based community detection event.
    Detects communities in the graph, updates textures, and sends the results to the client.
    
    Args:
        message (dict): Event data containing user and function details.
        room (str): Socket connection room identifier.
        project (str): Project name to retrieve the graph from.
    """

    if "analyticsModcommunityRun" not in GD.session_data.keys():
        ### "expensive" stuff
        if "graph" not in GD.session_data.keys():
            GD.session_data["graph"] = util.project_to_graph(project)
        graph = GD.session_data["graph"]
        result = analytics.modularity_community_detection(graph)
        ###
        GD.session_data["analyticsModcommunityRun"] = result
    arr = GD.session_data["analyticsModcommunityRun"]

    node_colors = analytics.color_mod_community_det(arr)

    flattened_colors = analytics.flattened_colors(arr, node_colors)
    
    generated_textures = analytics.update_network_colors(
        node_colors=node_colors
    )  # link_colors stays None for grey
    if generated_textures["textures_created"] is False:
        print("Failed to create textures for Analytics/Mod-based Communities")
        return
    response = {}
    response["usr"] = message["usr"]
    response["fn"] = "updateTempTex"
    response["textures"] = []
    response["textures"].append(
        {"channel": "nodeRGB", "path": generated_textures["path_nodes"]}
    )
    response["textures"].append(
        {"channel": "linkRGB", "path": generated_textures["path_links"]}
    )
    emit("ex", response, room=room, namespace = "/main") # added namespace explicitly

    response2 = {}
    response2["usr"] = message["usr"]
    response2["fn"] = "community_detection"
    response2["data"] = flattened_colors
    emit("ex", response2, room=room, namespace = "/main") # added namespace explicitly


def mod_community_layout_event(message, room, project):
    """
    Generates and applies a layout for modularity-based community detection.
    Updates the graph layout and sends the results to the client.
    
    Args:
        message (dict): Event data containing user and function details.
        room (str): Socket connection room identifier.
        project (str): Project name to retrieve the graph from.
    """

    if "analyticsModcommunityRun" not in GD.session_data.keys():
        ### "expensive" stuff
        if "graph" not in GD.session_data.keys():
            GD.session_data["graph"] = util.project_to_graph(project)
        graph = GD.session_data["graph"]
        result = analytics.modularity_community_detection(graph)
        ###
        GD.session_data["analyticsModcommunityRun"] = result
    communities_list = GD.session_data["analyticsModcommunityRun"]

    if "analyticsModcommunityLayout" not in GD.session_data.keys():
        ### "expensive" stuff
        if "graph" not in GD.session_data.keys():
            GD.session_data["graph"] = util.project_to_graph(project)
        graph = GD.session_data["graph"]
        result = analytics.generate_layout_community_det(
            communities_arr=communities_list, ordered_graph=graph
        )
        ###
        GD.session_data["analyticsModcommunityLayout"] = result
    positions = GD.session_data["analyticsModcommunityLayout"]

    generated_layout = analytics.generate_temp_layout(positions=positions)
    if generated_layout["layout_created"] is False:
        print("Failed to create layout for Analytics/Mod-based Communities")
        return
    response = {}
    response["usr"] = message["usr"]
    response["fn"] = "updateTempTex"  # updateTempLayout
    response["textures"] = []
    response["textures"].append(
        {"channel": "layoutNodesHi", "path": generated_layout["layout_hi"]}
    )
    response["textures"].append(
        {"channel": "layoutNodesLow", "path": generated_layout["layout_low"]}
    )
    emit("ex", response, room=room, namespace = "/main") # added namespace explicitly



def add_community_to_clipborad(message, room, project):
    """
    Adds a community to the clipboard.
    Retrieves community data from the graph and updates the clipboard with the selected nodes.
    
    Args:
        message (dict): Event data containing user and function details.
        room (str): Socket connection room identifier.
        project (str): Project name to retrieve the graph from.
    """

    community = message["val"]
    
    # get graph
    if "graph" not in GD.session_data.keys():
        GD.session_data["graph"] = util.project_to_graph(project)
    graph = GD.session_data["graph"]
    
    # get community data
    if "analyticsModcommunityRun" not in GD.session_data.keys():
        result = analytics.modularity_community_detection(graph)
        GD.session_data["analyticsModcommunityRun"] = result
    communities_list = GD.session_data["analyticsModcommunityRun"]
    
    # update clipboard
    clipboad.addNodesToClipboard(analytics.get_nodes_from_community(community, communities_list))
    
    response = {
        "usr": message["usr"],
        "id": message["id"],
        "fn": "cbaddNode",
        "val": GD.pdata["cbnode"],
    }
    emit("ex", response, room=room, namespace = "/main") # added namespace explicitly



def update_clipboard_from_highlight_event(message: dict, room):
    """
    Updates the clipboard with highlighted nodes.
    Processes the highlighted nodes and sends the updated clipboard data to the client.
    
    Args:
        message (dict): Event data containing user and function details.
        room (str): Socket connection room identifier.
    """

    if not "val" in message.keys():
        return

    analytics.update_clipboard_from_highlight(message["val"])

    response = {
        "usr": message["usr"],
        "id": message["id"],
        "fn": "cbaddNode",
        "val": GD.pdata["cbnode"],
    }
    emit("ex", response, room=room, namespace = "/main") # added namespace explicitly


def main(message, room, project):
    """
    Routes analytics events to the appropriate handler function.
    Based on the event ID in the message, calls the corresponding analytics function.
    
    Args:
        message (dict): Event data containing user and function details.
        room (str): Socket connection room identifier.
        project (str): Project name to retrieve the graph from.
    """


    if message["id"] == "analyticsDegreeRun":
        degree_run_event(message, room, project)

    if message["id"] == "analyticsClosenessRun":
        closeness_run_event(message, room, project)

    if message["id"] == "analyticsPathNode1":
        path_node1_event(message, room)

    if message["id"] == "analyticsPathNode2":
        path_node2_event(message, room)

    #if message["id"] == "analyticsPathRunOLD":
    #    path_run_old_event(message, room, project)

    # following 3 cases are for shortest Path buttons
    if message["id"] == "analyticsPathRun":
        path_run_event(message, room, project)

    if message["id"] == "analyticsPathBackw":
        path_backwards_event(message, room, project)

    if message["id"] == "analyticsPathForw":
        path_forwards_event(message, room, project)

    if message["id"] == "analyticsEigenvectorRun":
        eigenvector_run_event(message, room, project)

    if message["id"] == "analyticsClusteringcoefficientRun":
        clusteringcoefficient_run_event(message, room, project)

    if message["id"] == "analyticsModcommunityRun":
        mod_community_run_event(message, room, project)

    if message["id"] == "analyticsModcommunityLayout":
        mod_community_layout_event(message, room, project)
    
    # copy selections in clipboard 
    if message["id"] == "analyticsDegreeClipboard":
        update_clipboard_from_highlight_event(message, room)
        
    if message["id"] == "analyticsClosenessClipboard":
        update_clipboard_from_highlight_event(message, room)
        
    if message["id"] == "analyticsEigenvectorClipboard":
        update_clipboard_from_highlight_event(message, room)
        
    if message["id"] == "analyticsClusteringCoeffClipboard":
        update_clipboard_from_highlight_event(message, room)