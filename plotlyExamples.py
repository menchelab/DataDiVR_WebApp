
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

import matplotlib
matplotlib.use('Agg') # this stops matplotlib from running in error
import matplotlib.pyplot as plt

pio.templates.default = "plotly_dark"





def networkGraphRT(nlist, alist, llist):

    '''
    nlist = [111,2,3,49,5,6]
    alist = ["peter","klaus","anne","lukas","felix","marion"]
    llist = [(0,1),(1, 1), (0, 2), (0, 3), (0, 4), (0, 5),(2, 1), (3, 2), (5, 3), (1, 4), (1, 5)]
    '''

# Get the list of all files and directories
    path = "static/CAT_thumbs"
    dir_list = os.listdir(path)
    images=[]
    for i in range(len(dir_list)-1):
        images.append("http://127.0.0.1:5000/static/CAT_thumbs/" + str(i)+".png")
    #print(images)
    
    nxlist = [] # need a nodelist like [0,1,2...] for nx, so we use meta attr to provide node id's
    for i in range(len(alist)):
        nxlist.append(i)

    G=nx.random_geometric_graph(len(alist),0.3)
    G.add_nodes_from(nxlist)
    G.remove_edges_from(G.edges())
    G.add_edges_from(llist)
    pos = nx.spring_layout(G)
    
    #print(G.nodes(data=True))

    edge_x = []
    edge_y = []
    for edge in G.edges():

        edge_x.append(pos[edge[0]][0])
        edge_x.append(pos[edge[1]][0])
        edge_x.append(None)
        edge_y.append(pos[edge[0]][1])
        edge_y.append(pos[edge[1]][1])
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        #x, y = G.nodes[node]['pos']
        node_x.append(pos[node][0])
        node_y.append(pos[node][1])
    marker ='markers'

    #if len(alist) < 30:
    marker ="markers+text"       

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        meta = nlist, # this can be used to pass custom info, here nodeIDs to the graph which can be retrived in js
        text = alist,
        textposition="top center",
        mode=marker,
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=8,
            colorbar=dict(
                thickness=5,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        #node_text.append('# of connections: '+str(len(adjacencies[1])))
        node_text.append(alist[node])
    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
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
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.update_layout(height= 800, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=40, b=10))
    
    
    xVals = fig['data'][1]['x']
    yVals = fig['data'][1]['y']
    ids = fig['data'][1]["meta"]
    #print(fig['data'][1])

    for i in range(0, len(xVals)):
        
        fig.add_layout_image(dict(
            source=images[ids[i]],
            x=xVals[i] - 0.01,
            y=yVals[i] + 0.01,
            xref="x",
            yref="y",
            #sizex=0.03,
            #sizey=0.03,
            #layer='above'
            sizex=0.2,
            sizey=0.2,
            #sizing="stretch",
            opacity=0.5,
            layer="below"
        ))
 
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)  










def networkGraph():

    #elist = [(0,1),(1,2),(1,3),(1,4),(5,4),(5,7),(3,7)]
    #nodelabels = ["3RT","DFH","8UJ","GHJ","SGH","OUU","MDE","reee","reee","reee"]
    #G = nx.random_geometric_graph(200, 0.125)
    i = int(GD.pdata["activeNode"])
    seed = [i]
    nlist = []
    alist = []
    llist = []
    #todo: limit inputs to reasonable values
    
    for s in seed:
        if s not in nlist:
            nlist.append(GD.nodes["nodes"][s]["id"])
            alist.append(GD.nodes["nodes"][s]["n"])
        for x in GD.nchildren[s]:
            if x not in nlist:
                
                nlist.append(x)
                alist.append(GD.nodes["nodes"][x]["n"])
    #print(nlist)
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
    pos = nx.spring_layout(G)
    
    #print(G.nodes(data=True))

    edge_x = []
    edge_y = []
    for edge in G.edges():

        edge_x.append(pos[edge[0]][0])
        edge_x.append(pos[edge[1]][0])
        edge_x.append(None)
        edge_y.append(pos[edge[0]][1])
        edge_y.append(pos[edge[1]][1])
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        #x, y = G.nodes[node]['pos']
        node_x.append(pos[node][0])
        node_y.append(pos[node][1])
    marker ='markers'
    if len(alist) < 30:
        marker ="markers+text"       

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        meta = nlist, # this can be used to pass custom info, here nodeIDs to the graph which can be retrived in js
        text = alist,
        textposition="top center",
        mode=marker,
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=8,
            colorbar=dict(
                thickness=5,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        #node_text.append('# of connections: '+str(len(adjacencies[1])))
        node_text.append(alist[node])
    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
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
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.update_layout(height= 420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=40, b=10))
 
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)   
    #fig.show()
def histRugGraph():
    x1 = np.random.randn(200) - 2
    x2 = np.random.randn(200)
    x3 = np.random.randn(200) + 2

    hist_data = [x1, x2, x3]

    group_labels = ['Group 1', 'Group 2', 'Group 3']
    colors = ['#393E46', '#2BCDC1', '#F66095']

    fig = ff.create_distplot(hist_data, group_labels, colors=colors,
                            bin_size=[0.3, 0.2, 0.1], show_curve=False)

    # Add title
    fig.update_layout(font_color = 'rgb(200,200,200)', paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=40, b=10))
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def boxPlotGraph():
    N = 30     # Number of boxes

# generate an array of rainbow colors by fixing the saturation and lightness of the HSL
# representation of colour and marching around the hue.
# Plotly accepts any CSS color format, see e.g. http://www.w3schools.com/cssref/css_colors_legal.asp.
    c = ['hsl('+str(h)+',50%'+',50%)' for h in np.linspace(0, 360, N)]

    # Each box is represented by a dict that contains the data, the type, and the colour.
    # Use list comprehension to describe N boxes, each with a different colour and with different randomly generated data:
    fig = go.Figure(data=[go.Box(
        y=3.5 * np.sin(np.pi * i/N) + i/N + (1.5 + 0.5 * np.cos(np.pi*i/N)) * np.random.rand(10),
        marker_color=c[i]
        ) for i in range(int(N))])

    # format the layout
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(zeroline=False, gridcolor='white'),

    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def sankeyGraph():
    fig = go.Figure(go.Sankey(
        arrangement='snap',
        node=dict(
            label=['A', 'B', 'C', 'D', 'E', 'F'],
            x=[0.2, 0.1, 0.5, 0.7, 0.3, 0.5],
            y=[0.7, 0.5, 0.2, 0.4, 0.2, 0.3],
            pad=10  
        ),
        link=dict(
            arrowlen=15,
            source=[0, 0, 1, 2, 5, 4, 3, 5],
            target=[5, 3, 4, 3, 0, 2, 2, 3],
            value=[1, 2, 1, 1, 1, 1, 1, 2]  
        )
    ))
    fig.update_layout(font_color = 'rgb(200,200,200)', paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10))
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def barGraph(data):
    names = []
    val = []
    ids =[]

    for i in data:
        names.append(i["name"])
        val.append(i["val"])
        ids.append(i["id"])

    fig = go.Figure(go.Bar(
                meta = ids, # the meta value is used to attatch a callback to the graphs nodes in .js when the graph is created
                x=val,
                y=names,
                marker=dict(color='midnightblue'),
                text=names,
                textposition='inside',
                name='SF Zoo',
                orientation='h'
                ))
    
    bar_height = 16*len(names)+500
    print("C_DEBUG: bar height = ", bar_height)

    #fig.show()
    fig.update_layout(height = bar_height,
        	font_color = 'rgb(200,200,200)', paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=40, b=10))
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='show')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def connectionBarGraph():
    data = []
    i = int(GD.pdata["activeNode"])
    for n in GD.nchildren[i]:
        
        elem = {}
        elem["name"] = GD.nodes["nodes"][n]["n"]
        elem["id"]= n
        elem["val"]=len(GD.nchildren[n])
        data.append(elem)
    # sort by val
    data = sorted(data, key=lambda k: k.get("val"), reverse=False)
    
    return barGraph(data)



def scatterGraph():
    df = px.data.iris()

    fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species",
                    title="Using The add_trace() method With A Plotly Express Figure")

    fig.add_trace(
        go.Scatter(
            x=[2, 4],
            y=[4, 8],
            mode="lines",
            line=go.scatter.Line(color="gray"),
            showlegend=False)
    )
    #fig.show()
    fig.update_layout(font_color = 'rgb(200,200,200)', paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=40, b=10))
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)





def vectorfieldGraph():
    x1,y1 = np.meshgrid(np.arange(0, 2, .2), np.arange(0, 2, .2))
    u1 = np.cos(x1)*y1
    v1 = np.sin(x1)*y1

    fig = ff.create_quiver(x1, y1, u1, v1)
    #fig.show()
    fig.update_layout(font_color = 'rgb(200,200,200)', paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=40, b=10))
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def triangleGraph():
    df = px.data.election()
    fig = px.scatter_ternary(df, a="Joly", b="Coderre", c="Bergeron", hover_name="district",
    color="winner", size="total", size_max=15,
    color_discrete_map = {"Joly": "blue", "Bergeron": "green", "Coderre":"red"} )
    #fig.show()
    fig.update_layout(font_color = 'rgb(200,200,200)', paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=40, b=10))
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def timeGraph():
 
    df = px.data.gapminder()
    fig = px.scatter(df, x="gdpPercap", y="lifeExp", animation_frame="year", animation_group="country",
           size="pop", color="continent", hover_name="country",
           log_x=True, size_max=55, range_x=[100,100000], range_y=[25,90])
 #   fig.show()
    fig.update_layout(font_color = 'rgb(200,200,200)', paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=40, b=10))
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)






def writeHtml():
    running = False
    if not running:
        running = True
        labels = ['Oxygen','Hydrogen','Carbon_Dioxide','Nitrogen']
        values = [random.randrange(0,500), random.randrange(0,500), random.randrange(0,500), random.randrange(0,500)]
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
        #fig.show()
        script = '<script src="https://cdn.plot.ly/plotly-2.17.1.min.js"></script>'
        htmlstring = script + plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
        text_file = open("C:/Users/spirch/Documents/DataDiVR_WebApp/templates/plotly/TEST111.html", "w", encoding="utf-8")
        text_file.write(htmlstring)
        text_file.close()
        response = {}
        response["fn"] = "plotly"
        running = False
        return response


def matplotsvg(message):
    running = False
    if not running:
        running = True
        
        plt.rcParams['svg.fonttype'] = 'none'
        plt.rcParams["figure.figsize"] = (4,3)
        objects = ('JS','Python', 'C++', 'Java', 'Perl', 'Scala', 'Lisp')
        y_pos = np.arange(len(objects))
        performance = [random.randrange(0,100),random.randrange(0,100),random.randrange(0,100),random.randrange(0,100),random.randrange(0,100),random.randrange(0,100),random.randrange(0,100)]
        plt.bar(y_pos, performance, align='center', alpha=0.5, label="reeeeee")
        plt.xticks(y_pos, objects)
        plt.savefig("x.svg", format="svg", transparent=True)
        plt.clf()
        
        response2 = {}
        response2["id"] = message["id"]
        response2["parent"] = "svgtest"
        response2["fn"] = "svg"
        response2["val"] = []
        with open('x.svg') as f:
            contents = f.read()
            response2["val"] = contents
        f.close()
        os.remove("x.svg")
        
        
        running = False
        return response2


def heatmapGraph():
    # Create random data
    z = np.random.randint(low=0, high=10, size=(50, 50))

    # Create trace
    trace = go.Heatmap(z=z)

    # Create layout
    layout = go.Layout(
        title='My Heatmap',
        xaxis=dict(title='X-axis label'),
        yaxis=dict(title='Y-axis label')
    )

    # Create figure
    fig = go.Figure(data=[trace], layout=layout)
    fig.update_layout(font_color = 'rgb(200,200,200)', paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=40, b=10))

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
