# %% [markdown]
# # HOW TO CREATE A PROJECT from scratch
# 
# + this notebook is a template to generate Backend-required files to view a project with the DataDiVR (preview or VR)
# + STEP 1 and the "create a graph" section contains a template graph writing a required format (json) to then use the generate-project functions of the DataDiVR backend
# 
# + STEP 2 to actually generate BACKEND project files.

# %%
import networkx as nx
import json 
import os

# these are the two functions one needs to create a JSON file to upload and create the project in the backend 
import nx2json as nx2j
import uploaderGraph as uG

# %% [markdown]
# 
# ## How this is meant to be used:
# + Create an nx.Graph Object 
# 
# + set attributes in the nx.Graph (optional, all can be empty) e.g. node positions ("pos") and colors ("nodecolor") and link colors ("linkcolor")
# 
# + use the "create_project" function (down below to generate your project for the platform)

# %% [markdown]
# # CREATE A NX.GRAPH OBJECT per layout

# %% [markdown]
# ### nx.Graph

# %%
G = nx.circular_ladder_graph(200)
print("Number of nodes: ", len(G.nodes()))
print("Number of Links: ", len(G.edges()))

# ===============================================
# GRAPH NAME AND DESCRIPTION - a string each
# ===============================================

G.graph['projectname'] = "CircularLadderGraph"
G.graph['info'] = "A toy graph for testing purposes. Number of nodes: "+str(len(G.nodes()))+", Links: "+ str(len(G.edges()))+"."

# %%
#nx.draw(G)

# %% [markdown]
# ### create node anntotations

# %%
import random 
def generate_random_words(num):
    words = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "theta", "lambda", "mu", "nu"]
    return random.sample(words, num)

# Create a list to hold annotations in JSON format
l_annotations_json = []

# Process each node in the graph
for g in G.nodes():
    # Generate random annotations
    annotations = {
        "annot1": generate_random_words(random.randint(3, 4)),
        "annot2": generate_random_words(random.randint(1, 2)),
        "annot3": generate_random_words(random.randint(2, 3))
    }
    
    l_annotations_json.append(annotations)

# Create a dictionary mapping nodes to their annotations
d_annotations = dict(zip(G.nodes(), l_annotations_json))

# Set the node attributes in the graph
nx.set_node_attributes(G, d_annotations, name="annotation")

# %%
# set node names (optional)
for n in G.nodes():
    G.nodes[n]['name'] = "Node_"+str(n)

# %% [markdown]
# ### create node positions and set as "pos" Graph attribute 
# here are 3 different layouts, which all are stored in unique nx.Graph-objects (G_rgba, G_hex, ....)

# %%
# First layout (i.e. Graph 1)
G_rgba = G.copy()
G_rgba.graph["layoutname"] ='layout1-spring'
posG3D_1_pre = nx.spring_layout(G_rgba, dim=3, k=0.1, iterations=50)
posG3D_1 = {key: value.tolist() for key, value in posG3D_1_pre.items()}
nx.set_node_attributes(G_rgba, posG3D_1, name="pos")


# Second layout (i.e. Graph 2)
G_hex = G.copy()
G_hex.graph["layoutname"] = 'layout2-spring'
posG3D_2_pre = nx.spring_layout(G_hex, dim=3, k=0.1, iterations=50)
posG3D_2 = {key: value.tolist() for key, value in posG3D_2_pre.items()}
nx.set_node_attributes(G_hex, posG3D_2, name="pos")

# Third layout (i.e. Graph 3)
G_hex8 = G.copy()
G_hex8.graph["layoutname"] = 'layout3-spring'
posG3D_3_pre = nx.spring_layout(G_hex8, dim=3, k=0.1, iterations=50)
posG3D_3 = {key: value.tolist() for key, value in posG3D_3_pre.items()}
nx.set_node_attributes(G_hex8, posG3D_3, name="pos")


# Fourth layout (i.e. Graph 4) - with clusters
G_clusters = G.copy()
G_clusters.graph["layoutname"] = 'layout4-clusters'
clustername_1 = 'cluster group 1'
clustername_2 = 'cluster group 2'
clustername_3 = 'cluster group 3'

# nodes into groups
for g in G_clusters.nodes():
    if g < len(G_clusters.nodes()) / 3:
        G_clusters.nodes[g]['cluster'] = clustername_1
    elif g < 2 * len(G_clusters.nodes()) / 3:
        G_clusters.nodes[g]['cluster'] = clustername_2
    else:
        G_clusters.nodes[g]['cluster'] = clustername_3

nx.set_node_attributes(G_clusters, posG3D_1, name="pos")

# %% [markdown]
# #### node and link colors 

# %%
# 3 Formats of colors values are supported: hex, rgba, hex8

# FIRST GRAPH - rgba color values
d_nodecolors_rgba = dict(zip(G_rgba.nodes(),[(0,0,255,200)]*len(G_rgba.nodes())))
nx.set_node_attributes(G_rgba, d_nodecolors_rgba, name="nodecolor")
l_linkcolors_rgba = (0,0,255,200)
nx.set_edge_attributes(G_rgba, l_linkcolors_rgba, name="linkcolor")


# SECOND GRAPH - hex color values 
d_nodecolors_hex = dict(zip(G_hex.nodes(),['#ff0000']*len(G_hex.nodes())))
nx.set_node_attributes(G_hex, d_nodecolors_hex, name="nodecolor")
l_linkcolors_hex = '#ff0000' # in rgba = (255,0,0,100)
nx.set_edge_attributes(G_hex, l_linkcolors_hex, name="linkcolor")


# THIRD GRAPH - hex8 color values
d_nodecolors_hex8 = dict(zip(G_hex8.nodes(),['#00ff0080']*len(G_hex8.nodes())))
nx.set_node_attributes(G_hex8, d_nodecolors_hex8, name="nodecolor")
l_linkcolors_hex8 = '#00ff0080' 
nx.set_edge_attributes(G_hex8, l_linkcolors_hex8, name="linkcolor")


# FOURTH GRAPH - clusters assigned 

# node colors 
d_nodecolors_clusters = {}
nodes_group1 = []
nodes_group2 = []
nodes_group3 = []
for n in G_clusters.nodes(): 
    if G_clusters.nodes[n]['cluster'] == clustername_1:
        d_nodecolors_clusters[n] = '#0000ff'
        nodes_group1.append(n)
    elif G_clusters.nodes[n]['cluster'] == clustername_2:
        d_nodecolors_clusters[n] = '#00ff00'
        nodes_group2.append(n)
    elif G_clusters.nodes[n]['cluster'] == clustername_3:
        d_nodecolors_clusters[n] = '#ff0000'
        nodes_group3.append(n)

# link colors
d_linkcolors_clusters = {}
for edge in G_clusters.edges():
    if edge[0] in nodes_group1 and edge[1] in nodes_group1:
        d_linkcolors_clusters[edge] = '#0000ff'
       
    elif edge[0] in nodes_group2 and edge[1] in nodes_group2:
        d_linkcolors_clusters[edge] = '#00ff00'
       
    elif edge[0] in nodes_group3 and edge[1] in nodes_group3:
        d_linkcolors_clusters[edge] = '#ff0000'


l_linkcolors_clusters = list(d_linkcolors_clusters.values())

nx.set_node_attributes(G_clusters, d_nodecolors_clusters, name="nodecolor")
nx.set_edge_attributes(G_clusters, {edge: color for edge, color in zip(G_clusters.edges(), l_linkcolors_clusters)}, "linkcolor")


'''
num_links_to_drop = int(len(list(G_rgba.edges()))*0.25) # delete 90% of links in vis
links_to_drop = random.sample(list(G_rgba.edges()), num_links_to_drop)
G_rgba.remove_edges_from(links_to_drop)
print("Number of links after dropping: ", len(G_rgba.edges()))

num_links_to_drop = int(len(list(G_hex.edges()))*0.3) # delete 70% of links in vis
links_to_drop = random.sample(list(G_hex.edges()), num_links_to_drop)
G_hex.remove_edges_from(links_to_drop)
print("Number of links after dropping: ", len(G_hex.edges()))

num_links_to_drop = int(len(list(G_clusters.edges()))*0.5) # delete 50% of links in vis
links_to_drop = random.sample(list(G_clusters.edges()), num_links_to_drop)
G_clusters.remove_edges_from(links_to_drop)
print("Number of links after dropping: ", len(G_clusters.edges()))
'''
Graphs = [G_rgba, G_hex, G_hex8, G_clusters]

nx2j.create_project(Graphs)

'''

{
----------------------------------------
THIS IS THE GENERAL GRAPH INFO SECTION
----------------------------------------
  "directed": false,
  "multigraph": false,
  "projectname": "Testgraph",
  "info": "A toy graph for testing purposes. Number of nodes: 10, Links: 43.",
  "graphlayouts": [
      "layout1-spring",
      "layout2-spring",
      "layout3-spring",
      "layout4-clusters"
  ],
  "annotationTypes": true,
  "nodes": [
   ----------------------------------------
   contains all nodes of the project
   ----------------------------------------
      {
          "id": 0,
          "name": 0,
          "annotation": 
                {
                    "annot1": [
                        "lambda",
                        "alpha",
                        "zeta",
                        "theta"
                    ],
                    "annot2": [
                        "delta",
                        "nu"
                    ],
                    "annot3": [
                        "mu",
                        "gamma"
                    ]
          }
      },....
  ],
  "links": [
   ----------------------------------------
   contains all links of the project
   ----------------------------------------
      {
          "id": 0,
          "source": 0,
          "target": 1
      },
      {
          "id": 1,
          "source": 0,
          "target": 2
      },...
       ],
  "layouts": [
   ----------------------------------------
   contains all layouts of the project
   only contains nodes and links as well as colors specific to the layout
   ----------------------------------------
       {  "layoutname" : "name of first layout",
          "nodes": [
              {
                  "nodecolor": [
                      255,
                      35,
                      0,
                      120
                  ],
                  "pos": [
                      -0.5618057865250979,
                      0.1467411221839164,
                      0.49656801102094605
                  ],
                  "id": 0
               },...
        	],
          "links": [
              {
                  "linkcolor": [
                      0,
                      255,
                      0,
                      100
                  ],
                  "source": 0,
                  "target": 1
              },...
         	],
   	  }, {
          "layoutname" : "name of second layout",
          "nodes": [
              {
                  "nodecolor": "#0000ffaa",
                  "pos": [
                      -0.35948900932978317,
                      0.6255258442839948,
                      -0.04209289102217994
                  ],
                  "cluster": "cluster group 1",
                  "id": 0
               },... 
],
          "links": [
              {
                  "linkcolor": "#0000ff",
                  "source": 0,
                  "target": 1
              },
],
  	   }, { . . .  
 	},
}

'''
