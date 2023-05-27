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
        node_colors.append((33, 33, 33, 100))
    # get links

    link_colors = []
    try:
        with open("static/projects/"+ GD.data["actPro"] + "/links.json", "r") as links_file:
            links = json.load(links_file)
        # set link colors
        link_colors = [(33, 33, 33, 30) for _ in links["links"]]

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
        link_colors = [(33, 33, 33, 30) for _ in links["links"]]

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
        node_colors.append((33, 33, 33, 100))
    
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
            link_colors.append((33, 33, 33, 30))
        
    
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
