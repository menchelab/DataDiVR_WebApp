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


def analytics_degree_distribution(graph):
    # nx graph to degree distribution
    degree_sequence = [d for n, d in graph.degree()] # index is node id, value is degree
    return degree_sequence


def plotly_degree_distribution(degrees, highlighted_bar=None):
    # Create a bar chart
    x = list(range(max(degrees) + 1))
    y = [degrees.count(i) for i in x]

    colors = ['#636efa' if i != highlighted_bar else 'orange' for i in x]

    # Set chart layout
    layout = go.Layout(
        xaxis=dict(title='Degree'),
        yaxis=dict(title='Number of Nodes'),
        bargap=0.1
    )

    # Create a Figure object
    fig = go.Figure(data=go.Bar(x=x, y=y, marker=dict(color=colors)), layout=layout)

    fig.update_layout(height= 420, font_color = 'rgb(200,200,200)', paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10))
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='show')
    plotly_json = json.dumps(fig, cls=pu.PlotlyJSONEncoder)

    return plotly_json


def analytics_closeness(graph):
    # nx graph to closeness distribution
    closeness_seq = [nx.closeness_centrality(graph, node) for node in graph.nodes()]
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
        node_colors.append((66, 66, 66, 100))
    
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
            link_colors.append((66, 66, 66, 30))
        
    
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