"""
Functions for Analytics Module
"""
import GlobalData as GD
import networkx as nx
from PIL import Image
import math
import json
import plotly.graph_objs as go
import plotly.utils as pu
from joblib import Parallel, delayed
import igraph as ig
import numpy as np
import util


def analytics_degree_distribution(graph):
    # nx graph to degree distribution
    degree_sequence = [d for n, d in graph.degree()] # index is node id, value is degree
    return degree_sequence


def plotly_degree_distribution_OLD(degrees, highlighted_bar=None):
    # Create a bar chart
    x = list(range(max(degrees) + 1))
    y = [degrees.count(i) for i in x]

    colors = ['#636efa' if i != highlighted_bar else 'orange' for i in x]

    # Set chart layout
    layout = go.Layout(
        xaxis=dict(title='Degree'),
        yaxis=dict(title='Number of Nodes'),
        bargap=0.1,
        title=None if highlighted_bar is None else f"Selected Node Degree: {highlighted_bar}",
        title_y=0.97
    )

    # Create a Figure object
    fig = go.Figure(data=go.Bar(x=x, y=y, marker=dict(color=colors)), layout=layout)

    fig.update_layout(height= 420, font_color = 'rgb(200,200,200)', paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=30, t=30, b=10))
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='show')
    plotly_json = json.dumps(fig, cls=pu.PlotlyJSONEncoder)

    return plotly_json



def plotly_degree_distribution(degrees, highlighted_bar=None):
    maximum_amount_of_bars = 10

    highlighted_degrees = []

    maximum_degree = max(degrees)
    if maximum_degree <= maximum_amount_of_bars:
        num_bins = maximum_degree
    else:
        num_bins = min(int(maximum_degree ** 0.5) + 1, maximum_amount_of_bars)
    bin_width = math.ceil(maximum_degree / num_bins)
    bin_counts = {i: 0 for i in range(num_bins)}

    for degree in degrees:
        bin_index = min(int(degree // bin_width), num_bins - 1)
        bin_counts[bin_index] += 1

    # bar chart   
    if maximum_degree <= maximum_amount_of_bars:
        x = list(range(num_bins))
        y = [bin_counts[i] for i in range(num_bins)]
        colors = ['#636efa' if i != highlighted_bar else 'orange' for i in x]
        
        layout = go.Layout(
            xaxis=dict(title='Degree'),
            yaxis=dict(title='Number of Nodes'),
            bargap=0.1,
            title=None if highlighted_bar is None else f"Selected Node Degree: {highlighted_bar}",
            title_y=0.97
        )
        
        highlighted_degrees = [highlighted_bar]

        fig = go.Figure(data=go.Bar(x=x, y=y, marker=dict(color=colors)), layout=layout)

    
    # hist
    else:
        # convert highlighted_bar to actual bin index
        if highlighted_bar is not None:
            highlighted_bar = math.floor(highlighted_bar / bin_width)

        colors = ['#636efa' if i != highlighted_bar else 'orange' for i in range(num_bins)]

        if highlighted_bar is not None:
            min_degree_selected = int(highlighted_bar * bin_width)
            max_degree_selected = int((highlighted_bar + 1) * bin_width - 1) if int((highlighted_bar + 1) * bin_width - 1) <= maximum_degree else maximum_degree
            highlighted_degrees = list(range(min_degree_selected, max_degree_selected + 1))

        layout = go.Layout(
            xaxis=dict(title='Degree Range'),
            yaxis=dict(title='Number of Nodes'),
            bargap=0.1,
            title=None if highlighted_bar is None else f"Selected Node Degrees: {min_degree_selected} to {max_degree_selected}",
            title_y=0.97
        )
        
        fig = go.Figure(data=go.Histogram(x=degrees, xbins=dict(size=bin_width, start=min(degrees), end=max(degrees)), marker=dict(color=colors)), layout=layout)

    fig.update_layout(width=400, height=400, font_color='rgb(200,200,200)', paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=40, t=30, b=10))
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='show')
    plotly_json = json.dumps(fig, cls=pu.PlotlyJSONEncoder)

    return (plotly_json, highlighted_degrees)


def analytics_color_degree_distribution(degrees, highlight):
    # get nodes to highlight
    highlighted_degrees = set(highlight)
    highlight_nodes = [i for i in range(len(degrees)) if degrees[i] in highlighted_degrees]

    # gen textures
    node_colors = []
    for node in range(len(GD.pixel_valuesc)):
        if node in highlight_nodes:
            node_colors.append((255, 166, 0, 100))
            continue
        node_colors.append((55, 55, 55, 100))
    # get links

    link_colors = []
    try:
        with open("static/projects/"+ GD.data["actPro"] + "/links.json", "r") as links_file:
            links = json.load(links_file)
        # set link colors
        link_colors = [(55, 55, 55, 30) for _ in links["links"]]

        # create images
        texture_nodes_active = Image.open("static/projects/" + GD.data["actPro"] + "/layoutsRGB/" + GD.pfile["layoutsRGB"][int(GD.pdata["layoutsRGBDD"])] + ".png", "r")
        texture_links_active = Image.open("static/projects/" + GD.data["actPro"] + "/linksRGB/" + GD.pfile["linksRGB"][int(GD.pdata["linksRGBDD"])] + ".png", "r")

        texture_nodes = texture_nodes_active.copy()
        texture_links = texture_links_active.copy()
        texture_nodes.putdata(node_colors)
        texture_links.putdata(link_colors)
        path_nodes = "static/projects/" + GD.data["actPro"] + "/layoutsRGB/temp.png"
        path_links = "static/projects/" + GD.data["actPro"] + "/linksRGB/temp.png"
        texture_nodes.save(path_nodes, "PNG")
        texture_links.save(path_links, "PNG")

        texture_links_active.close()
        texture_nodes_active.close()
        texture_links.close()
        texture_nodes.close()

        return {"textures_created": True, "path_nodes": path_nodes, "path_links": path_links}
    except:
        return {"textures_created": False}
    

def update_network_colors(node_colors, link_colors=None):
    """

    node_colors: list where index correspond to node id and value is color in (r, g, b) format

    incorporate as following:
        generated_textures = analytics.update_network_colors(...)
        if generated_textures["textures_created"] is False:
            print("Failed to create textures for Analytics/Shortest Path.")
            return
        response_nodes = {}
        response_nodes["usr"] = message["usr"]
        response_nodes["fn"] = "updateTempTex"
        response_nodes["channel"] = "nodeRGB"
        response_nodes["path"] = generated_textures["path_nodes"]
        emit("ex", response_nodes, room=room)

        response_links = {}
        response_links["usr"] = message["usr"]
        response_links["fn"] = "updateTempTex"
        response_links["channel"] = "linkRGB"
        response_links["path"] = generated_textures["path_links"]
        emit("ex", response_links, room=room)
    """

    #try:
    with open("static/projects/"+ GD.data["actPro"] + "/links.json", "r") as links_file:
        links = json.load(links_file)
    # set link colors
    if link_colors is None:
        link_colors = [(55, 55, 55, 30) for _ in links["links"]]

    # create images
    texture_nodes_active = Image.open("static/projects/" + GD.data["actPro"] + "/layoutsRGB/" + GD.pfile["layoutsRGB"][int(GD.pdata["layoutsRGBDD"])] + ".png", "r")
    texture_links_active = Image.open("static/projects/" + GD.data["actPro"] + "/linksRGB/" + GD.pfile["linksRGB"][int(GD.pdata["linksRGBDD"])] + ".png", "r")

    texture_nodes = texture_nodes_active.copy()
    texture_links = texture_links_active.copy()
    texture_nodes.putdata(node_colors)
    texture_links.putdata(link_colors)
    path_nodes = "static/projects/" + GD.data["actPro"] + "/layoutsRGB/temp.png"
    path_links = "static/projects/" + GD.data["actPro"] + "/linksRGB/temp.png"
    texture_nodes.save(path_nodes, "PNG")
    texture_links.save(path_links, "PNG")

    texture_links_active.close()
    texture_nodes_active.close()
    texture_links.close()
    texture_nodes.close()

    return {"textures_created": True, "path_nodes": path_nodes, "path_links": path_links}
    # except:
        # return {"textures_created": False}

def analytics_closeness_OLD(graph):
    def _compute_closeness(node, graph):
        return nx.closeness_centrality(graph, wf_improved=True)[node]
    
    if len(graph.nodes()) <= 10000 or len(graph.edges()) <= 100000:
        closeness_seq = list(nx.closeness_centrality(graph, wf_improved=True).values())
    else:
        num_cores = min(8, len(graph.nodes()))  # number of cores available
        closeness_seq = Parallel(n_jobs=num_cores)(
            delayed(_compute_closeness)(node, graph) for node in graph.nodes()
        )
    return closeness_seq


def analytics_closeness(graph):
    def _compute_closeness_igraph(graph):
        g = ig.Graph.Adjacency((graph > 0).tolist(), mode="DIRECTED")
        closeness_seq = g.closeness(mode="out")
        closeness_seq = np.where(np.isnan(closeness_seq), 0, closeness_seq)  # Replace NaN values with 0
        return closeness_seq

    if len(graph.nodes()) <= 10000 or len(graph.edges()) <= 80000:
        closeness_seq = [nx.closeness_centrality(graph, node) for node in graph.nodes()]
    else:
        adjacency_matrix = nx.to_numpy_array(graph)
        closeness_seq = _compute_closeness_igraph(adjacency_matrix)
        closeness_seq = list(closeness_seq)  # Convert numpy array to list
    return closeness_seq



def analytics_shortest_path(graph, node_1, node_2):
    node_1, node_2 = str(node_1), str(node_2)
    if not graph.has_node(node_1):
        print(f"ERROR: Node {GD.nodes['nodes'][int(node_1)]} not in network.")
        return []
    if not graph.has_node(node_2):
        print(f"ERROR: Node {GD.nodes['nodes'][int(node_2)]} not in network.")
        return []
    try:
        path = nx.shortest_path(graph, source=node_1, target=node_2, method="dijkstra")
        return path
    except nx.exception.NetworkXNoPath:
        print(f"ERROR: Node {GD.nodes['nodes'][int(node_1)]} and node {GD.nodes['nodes'][int(node_2)]} are not connected.")
        return []

def analytics_color_shortest_path(path):
    # might include this into shortest_path function
    path = [int(node) for node in path]
    node_colors = []
    for node in range(len(GD.pixel_valuesc)):
        if node in path:
            node_colors.append((255, 166, 0, 100))
            continue
        node_colors.append((55, 55, 55, 100))
    
    # get links
    link_colors = []
    try:
        with open("static/projects/"+ GD.data["actPro"] + "/links.json", "r") as links_file:
            links = json.load(links_file)
        # set link colors
        for link in links["links"]:
            if int(link["s"]) in path and int(link["e"]) in path:
                link_colors.append((244, 255, 89, 150))
                continue
            link_colors.append((55, 55, 55, 30))
        
    
        # create images
        texture_nodes_active = Image.open("static/projects/"+ GD.data["actPro"]  + "/layoutsRGB/"+ GD.pfile["layoutsRGB"][int(GD.pdata["layoutsRGBDD"])]+".png","r")
        texture_links_active = Image.open("static/projects/"+ GD.data["actPro"]  + "/linksRGB/"+ GD.pfile["linksRGB"][int(GD.pdata["linksRGBDD"])]+".png","r")

        texture_nodes = texture_nodes_active.copy()
        texture_links = texture_links_active.copy()
        texture_nodes.putdata(node_colors)
        texture_links.putdata(link_colors)
        path_nodes = "static/projects/"+ GD.data["actPro"]  + "/layoutsRGB/temp.png"
        path_links = "static/projects/"+ GD.data["actPro"]  + "/linksRGB/temp.png"
        texture_nodes.save(path_nodes, "PNG")
        texture_links.save(path_links, "PNG")

        texture_links_active.close()
        texture_nodes_active.close()
        texture_links.close()
        texture_nodes.close()

        return {"textures_created": True, "path_nodes": path_nodes, "path_links": path_links}
    except:
        return {"textures_created": False}


def analytics_eigenvector(graph):
    def _compute_eigenvector_centrality_nx(graph):
        centrality = nx.eigenvector_centrality_numpy(graph)
        return list(centrality.values())

    def _compute_eigenvector_centrality_igraph(graph):
        g = ig.Graph.Adjacency((graph > 0).tolist(), mode="DIRECTED")
        centrality = g.eigenvector_centrality(directed=True)
        return centrality
    def _scale(centrality_seq):
        min_value = min(centrality_seq)
        max_value = max(centrality_seq)
        scaled_seq = [(x - min_value) / (max_value - min_value) for x in centrality_seq]
        return scaled_seq

    if len(graph.nodes()) <= 10000 or len(graph.edges()) <= 80000:
        centrality_seq = _compute_eigenvector_centrality_nx(graph)
    else:
        adjacency_matrix = nx.to_numpy_array(graph)
        centrality_seq = _compute_eigenvector_centrality_igraph(adjacency_matrix)

    visual_centrality_seq = _scale(centrality_seq)
    

    return (centrality_seq, visual_centrality_seq)


def modularity_community_detection(ordered_graph):
    if not isinstance(ordered_graph, util.OrderedGraph):
        raise TypeError("The graph should be an instance of OrderedGraph.")

    communities = nx.algorithms.community.modularity_max.greedy_modularity_communities(ordered_graph)
    # some alternatives:
    # communities = nx.algorithms.community.girvan_newman(ordered_graph)
    # communities = nx.algorithms.community.community_louvain(ordered_graph)
    # communities = nx.algorithms.community.label_propagation_communities(ordered_graph)
    # communities = nx.algorithms.community.modularity_max.greedy_modularity_communities(ordered_graph)

    community_assignment = [0] * len(ordered_graph.node_order)

    for i, comm in enumerate(communities):
        for node in comm:
            node_index = ordered_graph.node_order.index(node)
            community_assignment[node_index] = i + 1
    return community_assignment


def color_mod_community_det(communities_arr):
    num_communities = max(communities_arr)
    colors = util.generate_colors(n=num_communities)
    colors.insert(0, (55, 55, 55))  # grey out all non community nodes
    node_colors = [colors[community] for community in communities_arr]
    return node_colors


def generate_layout_community_det(communities_arr, ordered_graph, radius=1.5):
    if not isinstance(ordered_graph, util.OrderedGraph):
        raise TypeError("The graph should be an instance of OrderedGraph.")

    # Create an empty layout dictionary
    layout = {}

    # Store the seed position for each community
    seed_positions = {}

    # Iterate over each node
    for i, node in enumerate(ordered_graph.node_order):
        # Get the community label for the current node
        community_label = communities_arr[i]

        # Calculate the distance from the current node to the seed position of the community
        if community_label not in seed_positions:
            # Generate a random seed position for the new community
            seed_positions[community_label] = (
                np.random.uniform(-10, 10),
                np.random.uniform(-10, 10),
                np.random.uniform(-10, 10),
            )

        seed_position = seed_positions[community_label]
        distance_to_seed = np.random.uniform(0, 3)  # Adjust the distance to your preference

        # Calculate the layout position based on the community seed and distance
        x = seed_position[0] + np.random.uniform(-distance_to_seed, distance_to_seed)
        y = seed_position[1] + np.random.uniform(-distance_to_seed, distance_to_seed)
        z = seed_position[2] + np.random.uniform(-distance_to_seed, distance_to_seed)

        # Add the layout position to the dictionary
        layout[node] = (x, y, z)
    
    # normalize
    x, y, z = [], [], []
    for node_id in range(len(communities_arr)):
        x.append(layout[str(node_id)][0])
        y.append(layout[str(node_id)][1])
        z.append(layout[str(node_id)][2])
    max_x, min_x = max(x), min(x)
    max_y, min_y = max(y), min(y)
    max_z, min_z = max(z), min(z)
    positions = [[
        (x[node_id] - min_x) / (max_x - min_x),
        (y[node_id] - min_y) / (max_y - min_y),
        ((z[node_id] - min_z) / (max_z - min_z)) if min_z != max_z else 0,
    ] for node_id in range(len(communities_arr))]
    
    return positions


def generate_temp_layout(positions):
    try:
        ### low refers to the texture layoutsl !!!!
        # copy old layouts
        current_layout_low = Image.open("static/projects/"+ GD.data["actPro"] + "/layoutsl/"+ GD.pfile["layouts"][int(GD.pdata["layoutsDD"])]+"l.bmp","r")
        current_layout_hi = Image.open("static/projects/"+ GD.data["actPro"] + "/layouts/"+ GD.pfile["layouts"][int(GD.pdata["layoutsDD"])]+".bmp","r")
        updated_layout_low = current_layout_low.copy()
        updated_layout_hi = current_layout_hi.copy()

        # decompose positions
        pos_low = []
        pos_hi = []
        for node_pos in positions:
            x = int(float(node_pos[0]) * 65280)
            y = int(float(node_pos[1]) * 65280)
            z = int(float(node_pos[2]) * 65280)
            x_hi = int(x / 255)
            y_hi = int(y / 255)
            z_hi = int(z / 255)
            x_low = x % 255
            y_low = y % 255
            z_low = z % 255
            pos_low.append((x_low, y_low, z_low))
            pos_hi.append((x_hi, y_hi, z_hi))

        # save new layouts
        updated_layout_low.putdata(pos_low)
        updated_layout_hi.putdata(pos_hi)
        path_low = "static/projects/"+ GD.data["actPro"]  + "/layoutsl/templ.bmp"
        path_hi = "static/projects/"+ GD.data["actPro"]  + "/layouts/temp.bmp"
        updated_layout_low.save(path_low, "BMP")
        updated_layout_hi.save(path_hi, "BMP")

        # close images
        current_layout_low.close()
        current_layout_hi.close()
        updated_layout_low.close()
        updated_layout_hi.close()

        # output texture dictionary
        return {"layout_created": True, "layout_low": path_low, "layout_hi": path_hi}
    except Exception: 
        return {"layout_created": False} 
    