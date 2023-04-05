
import json
import plotly
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import networkx as nx
import numpy as np
import GlobalData as GD
import random
import os
import warnings
import cartoGRAPHs as cg
#from tqdm import tqdm 
#import time 

import matplotlib
matplotlib.use('Agg') # this stops matplotlib from running in error
import matplotlib.pyplot as plt

pio.templates.default = "plotly_dark"


###############################################
# CREATE SUB GRAPH FROM NODE SELECTED 
###############################################
def get_graph():
    if 'activeNode' in GD.pdata.keys():
        i = int(GD.pdata["activeNode"])
        seed = [i]
        nlist = []
        alist = []
        llist = []
        
        for s in seed:
            if s not in nlist:
                nlist.append(GD.nodes["nodes"][s]["id"])
                alist.append(GD.nodes["nodes"][s]["n"])
            for x in GD.nchildren[s]:
                if x not in nlist:
                    
                    nlist.append(x)
                    alist.append(GD.nodes["nodes"][x]["n"])

        for n in range(len(nlist)) :
            for  item in GD.nchildren[nlist[n]]:
                if item in nlist:
                    
                    if n < nlist.index(item):
                        link = (n,nlist.index(item))
                    else:
                        link = (nlist.index(item),n)
                    if link not in llist:
                        llist.append(link)
        

        nxlist = [] # need a nodelist like [0,1,2...] for nx, so we use meta attr to provide node id's
        for i in range(len(alist)):
            nxlist.append(i)

        G=nx.random_geometric_graph(len(alist),0.3)
        G.add_nodes_from(nxlist)
        G.remove_edges_from(G.edges())
        G.add_edges_from(llist)
        
        return G, alist, nlist

    else: 
        pass

###############################################
# LAYOUTS FROM CARTOGRAPHS
###############################################

def get_pos_local2D(G):
    # TO DO (later stage): umap parameters in case they should be implemented to be set by the user
    # n_n = 10
    # spr = 1
    # md = 0.1
    pos = cg.generate_layout(G,dim=2,layoutmethod='local',dimred_method='umap') #nx.spring_layout(G,iterations = 1000)
    return pos
    
def get_pos_global2D(G):
    pos = cg.generate_layout(G,dim=2,layoutmethod='global',dimred_method='umap')
    return pos

def get_pos_importance2D(G):
    pos = cg.generate_layout(G,dim=2,layoutmethod='importance',dimred_method='umap')#nx.spectral_layout(G)
    return pos 

def get_pos_local3D(G):
    pos = cg.generate_layout(G,dim=3,layoutmethod='local',dimred_method='umap') #nx.spring_layout(G,iterations = 1000) nx.spring_layout(G, dim=3, iterations = 1000)
    return pos
    
def get_pos_global3D(G):
    pos = cg.generate_layout(G,dim=3,layoutmethod='global',dimred_method='umap')  #nx.circular_layout(G, dim=3)
    return pos

def get_pos_importance3D(G):
    pos = cg.generate_layout(G,dim=3,layoutmethod='importance',dimred_method='umap')  #nx.spectral_layout(G, dim=3)
    return pos 


###############################################
# FIGURE OUTPUT
###############################################
def draw_figure_cartographs(data):
    fig = go.Figure()
    for i in data:
        fig.add_trace(i)
        
    fig.layout = go.Layout(
                    title='',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text='',
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    )
    fig.update_layout(height= 420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10), 
                      scene=dict(
                                    xaxis=dict(ticks='',showticklabels=False),
                                    yaxis=dict(ticks='',showticklabels=False),
                                    zaxis=dict(ticks='',showticklabels=False)
                                )
                        )
    return fig


###############################################
# THIS IS THE MAIN DRAWING cartographs FUNCTION 
###############################################
def cartoGraphs():

    # predefining colors of nodes and sizes
    # TO DO (maybe consider at later stage): could be interactive through e.g. sliders 
    d_nodecol = dict(nx.degree(get_graph()[0]))#dict(nx.closeness_centrality(get_graph()[0]))

    col_scale = 'YlOrRd'
    node_colors = list(cg.color_nodes_from_dict(get_graph()[0], d_nodecol, palette = col_scale).values())

    if "CGlayouts" in GD.pdata.keys() and "CGvis" in GD.pdata.keys():        
        layout_selected = int(GD.pdata["CGlayouts"])
        vis_selected = int(GD.pdata["CGvis"])

        G,alist,nlist = get_graph()
        # visual general settings 
        linkcolor = '#888'
        linkopac = 0.6
        
        if vis_selected == 0: 
            # for 2D make larger nodes 
            node_sizes = 7.5

            if layout_selected == 0:
                pos = get_pos_local2D(G)
                node_trace = cg.get_trace_nodes_2D(pos, list(pos.keys()), node_colors, node_sizes, 0.9)
                edge_trace = cg.get_trace_edges_2D(G, pos, color = linkcolor, opac = linkopac)

            elif layout_selected == 1:
                pos = get_pos_global2D(G)
                node_trace = cg.get_trace_nodes_2D(pos, list(pos.keys()), node_colors, node_sizes, 0.9)
                edge_trace = cg.get_trace_edges_2D(G, pos, color = linkcolor, opac = linkopac)

            elif layout_selected == 2:
                pos = get_pos_importance2D(G)
                node_trace = cg.get_trace_nodes_2D(pos, list(pos.keys()), node_colors, node_sizes, 0.9)
                edge_trace = cg.get_trace_edges_2D(G, pos, color = linkcolor, opac = linkopac)

        elif vis_selected == 1:
            # for 3D make smaller nodes 
            node_sizes = 3.5 #list(cg.draw_node_degree_3D(get_graph()[0], scalef = 0.5))

            if layout_selected == 0:
                pos = get_pos_local3D(G)
                node_trace = cg.get_trace_nodes_3D(pos, list(pos.keys()), node_colors, node_sizes, 0.9)
                edge_trace = cg.get_trace_edges_3D(G, pos, color = linkcolor, opac = linkopac)

            elif layout_selected == 1:
                pos = get_pos_global3D(G)
                node_trace = cg.get_trace_nodes_3D(pos, list(pos.keys()), node_colors, node_sizes, 0.9)
                edge_trace = cg.get_trace_edges_3D(G, pos, color = linkcolor, opac = linkopac)

            elif layout_selected == 2:
                pos = get_pos_importance3D(G)
                node_trace = cg.get_trace_nodes_3D(pos, list(pos.keys()), node_colors, node_sizes, 0.9)
                edge_trace = cg.get_trace_edges_3D(G, pos, color = linkcolor, opac = linkopac)



        # elif vis_selected == 2: # TOPOGRAPHIC 

        # elif vis_selected == 3: # GEODESIC 
        
        node_text = []
        for node, adj in enumerate(G.adjacency()):
            node_text.append(alist[node])
        node_trace.text = node_text

        data = [edge_trace,node_trace]
        fig = draw_figure_cartographs(data)
       
        # update trace to show legend color palette right side of plot
        fig.update_traces(marker=dict(
                    showscale=True,
                    cmax=max(d_nodecol.values()),
                    cmin=min(d_nodecol.values()),
                    colorscale=col_scale,
                    colorbar=dict(
                        thickness=5,
                        title='Node Degree',
                        xanchor='left',
                        titleside='right'
                    ),
                )
            )
        # degree only should be displayed in legend as integers
        fig.update_layout(coloraxis={"colorbar":{"dtick":1}})
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)   