"""
Functions for Layout  Module
"""
import GlobalData as GD
import networkx as nx
from PIL import Image
import util
import numpy as np
import scipy.sparse as sp_sp
import umap
from cartoGRAPHs import generate_layout as carto_gen_layout
import random



# constants, important to keep the order
LAYOUT_IDS = ["random", "eigen", "local", "global", "importance", "spectral"] # ids used in session data
LAYOUT_NAMES = ["Random Layout", "EigenUMAPLayout", "cartoGRAPHsLocal", "cartoGRAPHsImportance", "Spectral"] # names used for texture generation  !!! not implemented yet !!!
LAYOUT_TABS = ["Random", "Eigenlayout", "cartoGRAPHs Local", "cartoGRAPHs Global", "cartoGRAPHs Importance", "Spectral"] # names used in panel display and in connect_socketIO_main.js to switch tabs



"""
Layout functions are designed to return objects to allow the user to debug code more efficiently and guides the user in VR/WebPreview
The return object will look like this:

{
    "success": bool, used to see if the algorithm successfully generated textures
    "error": str, printed to console only to show at which step the error occured
    "log": dict, will be redirected to the front end to show the user in log panel 
    {
        "type": str, ("log", "warning"), tells the html generator how to handle the log
        "msg": str, message to display
    },
    "textures": list, contains texture objects as the front end needs it to process
    [
        {
            "channel": str, ("nodeRGB", "linkRGB", "layoutNodeHi", "layoutNodeLow"), type of texture
            "path": str, path to texture
        }
    ],
    "content": misc, any result data 
}
"""



def init_client_display_log()->bool:
    # initialize the display of layout log if a new client joins
    # returns if the log is already shown or not
    if "layout" not in GD.session_data.keys():
        GD.session_data["layout"] = {}
    if "show_log" not in GD.session_data["layout"].keys():
        GD.session_data["layout"]["show_log"] = False
    return GD.session_data["layout"]["show_log"]

def init_client_layout_exists()->bool:
    # initialize the display of rerun and save buttons
    # returns if the selected layout algorithm was already successfully performed
    if "layout" not in GD.session_data.keys():
        GD.session_data["layout"] = {}
    if "results" not in GD.session_data["layout"].keys():
        GD.session_data["layout"]["results"] = {}
    selected_layout_generated = False
    if "layoutModule" in GD.pdata.keys():
        layout_index = int(GD.pdata["layoutModule"])
        if LAYOUT_IDS[layout_index] in GD.session_data["layout"]["results"].keys():
            if GD.session_data["layout"]["results"][LAYOUT_IDS[layout_index]] is not None:
                selected_layout_generated = True
    return selected_layout_generated

def check_layout_exists()->bool:
    # check if selected layout exists
    if "layout" not in GD.session_data.keys():
        GD.session_data["layout"] = {}
    if "results" not in GD.session_data["layout"].keys():
        GD.session_data["layout"]["results"] = {}
    selected_layout_generated = False
    if "layoutModule" in GD.pdata.keys():
        layout_index = int(GD.pdata["layoutModule"])
        if LAYOUT_IDS[layout_index] in GD.session_data["layout"]["results"].keys():
            if GD.session_data["layout"]["results"][LAYOUT_IDS[layout_index]] is not None:
                selected_layout_generated = True
    return selected_layout_generated

def show_log():
    if "layout" not in GD.session_data.keys():
        GD.session_data["layout"] = {}
    GD.session_data["layout"]["show_log"] = True

def hide_log():
    if "layout" not in GD.session_data.keys():
        GD.session_data["layout"] = {}
    GD.session_data["layout"]["show_log"] = False


def save_layout_temp():...


def adjust_point_positions(points, displacement_factor=3e-2):
    return {key: [coord + random.gauss(0, displacement_factor) for coord in coords]
            for key, coords in points.items()}


def scale_positions(positions, node_order: list, pos_type: type = int)->list:
    """ 
    function to scale positions of nodes based on their order into [0, 1] space
    positions: dict, key: pos_type, node_id; value: list(floats), x, y, z coordiantes
    node_order: list, order of nodes in graph
    pos_type: type, optional, default = int, how to handle keying for positions
    returns: list(lists(floats)), scaled positions in order of graph
    """
    x, y, z = [], [], []

    for node_id in node_order:
        x.append(positions[pos_type(node_id)][0])
        y.append(positions[pos_type(node_id)][1])
        z.append(positions[pos_type(node_id)][2])
    max_x, min_x = max(x), min(x)
    max_y, min_y = max(y), min(y)
    max_z, min_z = max(z), min(z)
    scaled_positions = [[
        (x[int(node_id)] - min_x) / (max_x - min_x),
        (y[int(node_id)] - min_y) / (max_y - min_y),
        (z[int(node_id)] - min_z) / (max_z - min_z)
    ] for node_id in node_order]
    return scaled_positions

def pos_to_textures(positions)->dict:
    # takes scaled positions list and generates layout textures for nodes
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
        return {"success": True, "textures":
            [
                {"channel": "layoutNodesLow", "path": path_low}, 
                {"channel": "layoutNodesHi", "path": path_hi}
            ]
        }
    
    except: 
        return {"success": False, "error": "Texture generation failed.", "log": {"type": "warning", "msg": "Layout texture generation failed."}} 


def layout_random(ordered_graph)->dict:
    """
    Random Layout Generation Function
    """
    # integrety checks
    if not isinstance(ordered_graph, util.OrderedGraph):
        return {"success": False, "error": "Graph is not instance of OrderedGraph class."}
    
    # boundary checks
    # no check set yet

    # actual layout to get node positions
    try:
        layout = nx.random_layout(G=ordered_graph, dim=3, seed=None)
        positions = []
        for node in ordered_graph.node_order:
            pos = layout[node]
            positions.append([pos[0], pos[1], pos[2]])
        
        # scale positions
        scaled_pos = scale_positions(positions=positions, node_order=ordered_graph.node_order)

        # return positions
        return {"success": True, "content": scaled_pos}
    except:
        return {"success": False, "error": "Random layout algorithm failed.", "log": {"type": "log", "msg": "Random layout generation failed."}}

def layout_eigen(ordered_graph)->dict:
    """
    Random Layout Generation Function
    """
    def eigenlayout(G, dim=3, n_lam=18, n_neighs=10, spread=1.0, method="cosine"):
        """
        Compute the UMAP layout of a graph based on its normalized Laplacian matrix.

        Parameters:
        -----------
        G : NetworkX graph object
            The input graph.
        dim : int, optional (default=3)
            The number of dimensions in the UMAP projection.
        n_lam : int, optional (default=18)
            The number of eigenvalues and eigenvectors to use in the spectral dimensionality reduction.
        n_neighs : int, optional (default=10)
            The number of nearest neighbors to use in the UMAP algorithm.
        spread : float, optional (default=1.0)
            The spread of the UMAP projection.
        method: : str, default: 'cosine', also possible "manhattan", "euclidean"
        Returns:
        --------
        d_umap_pos : dictionary with graph nodes as keys and aray - shape: (n_nodes, dim) as values
            The UMAP projection of the graph nodes as a numpy array.
        """
        if n_lam > G.number_of_nodes()-1:
            print('The number of Eigenvectors must be smaller than the number of nodes - 1!')
            print('Please provide a smaller number. (Not more than 0.1xnumber_of_nodes recommended)')

        # Compute the normalized Laplacian matrix
        M_laplace = nx.normalized_laplacian_matrix(G, sorted(G.nodes()))

        # Construct the matrix M_ImL = I - L where L is the normalized Laplacian matrix and I is the identity matrix
        n_nodes = G.number_of_nodes()
        Id = sp_sp.identity(n_nodes)
        M_ImL = Id - M_laplace

        # Compute the n_lam smallest eigenvalues and eigenvectors of M_ImL
        # M_V: #rows = #nodes and #cols = #eigenvls 
        Lam,M_V = sp_sp.linalg.eigsh(M_ImL,k=n_lam)

        # FEATURE VECTOR
        # re-sort M_V by desc Lam - 1st column: eigenvec for largest Eigenvalue ...
        N = n_lam

        rev_ordered_idx = np.argsort(Lam)
        # spectral dimensional reduction:
        f_vec_1 = [x.real for x in M_V[:,rev_ordered_idx[-1]]]
        arr = f_vec_1

        for m in range(2,N+1):
            f_vec_2 = [x.real for x in M_V[:,rev_ordered_idx[-m]]]
            arr = np.vstack((arr,f_vec_2))

        # # UMAP
        FX = arr.transpose().astype(np.float64)
        mind = .2
        reducer = umap.UMAP(
            n_components=dim,
            n_neighbors=n_neighs,
            metric=method,
            min_dist=mind,
            spread=spread,
            low_memory=True,
            force_approximation_algorithm=True,
            verbose=True
        )

        umap_pos = reducer.fit_transform(FX)
        d_node_pos = {}

        for i, node in enumerate(sorted(G.nodes())):
            d_node_pos[node] = umap_pos[i,:]

        return d_node_pos


    # integrety checks
    if not isinstance(ordered_graph, util.OrderedGraph):
        return {"success": False, "error": "Graph is not instance of OrderedGraph class."}
    
    # boundary checks
    # no check set yet

    # actual layout to get node positions
    try:
        method = "cusine"
        try:
            layout = eigenlayout(G=ordered_graph, dim=3, n_lam=18, n_neighs=10, spread=1.0, method=method)
        except:
            method = "euclidean"
            layout = eigenlayout(G=ordered_graph, dim=3, n_lam=18, n_neighs=10, spread=1.0, method=method)
        
        positions = []
        for node in ordered_graph.node_order:
            pos = layout[node]
            positions.append([pos[0], pos[1], pos[2]])
        
        # scale positions
        scaled_pos = scale_positions(positions=positions, node_order=ordered_graph.node_order)

        # return positions
        return {"success": True, "content": scaled_pos}
    except:
        return {"success": False, "error": "Eigenlayout algorithm failed.", "log": {"type": "warning", "msg": "Eigenlayout generation failed."}}
    

def layout_carto_local(ordered_graph)->dict:
    """
    local layout from cartoGRAPHs
    """
    # integrety checks
    if not isinstance(ordered_graph, util.OrderedGraph):
        return {"success": False, "error": "Graph is not instance of OrderedGraph class."}
    
    # boundary checks
    if len(ordered_graph.nodes()) >= 15000 or len(ordered_graph.edges()) >= 80000:
        return {"success": False, "error": "Network too large for real-time computation of cartoGRAPHs Importance layout. (No error!)", "log": {"type": "warning", "msg": "Network too large for real-time computation of cartoGRAPHs Importance layout."}}
    
    # actual layout to get node positions
    try:
        raw_pos = carto_gen_layout(ordered_graph, dim = 3, layoutmethod = 'local', dimred_method='umap')
        jiter_pos = adjust_point_positions(raw_pos, 0.03)

        # scale positions
        scaled_pos = scale_positions(positions=jiter_pos, node_order=ordered_graph.node_order, pos_type=str)

        # return positions
        return {"success": True, "content": scaled_pos}
    except:
        return {"success": False, "error": "cartoGRAPHs Local layout algorithm failed.", "log": {"type": "warning", "msg": "cartoGRAPHs Local layout generation failed."}}
    


def layout_carto_global(ordered_graph)->dict:
    """
    global layout from cartoGRAPHs
    """
    # integrety checks
    if not isinstance(ordered_graph, util.OrderedGraph):
        return {"success": False, "error": "Graph is not instance of OrderedGraph class."}
    
    # boundary checks
    if len(ordered_graph.nodes()) >= 15000 or len(ordered_graph.edges()) >= 80000:
        return {"success": False, "error": "Network too large for real-time computation of cartoGRAPHs Importance layout. (No error!)", "log": {"type": "warning", "msg": "Network too large for real-time computation of cartoGRAPHs Importance layout."}}

    # actual layout to get node positions
    try:
        raw_pos = carto_gen_layout(ordered_graph, dim = 3, layoutmethod = 'global', dimred_method='umap')
        jitter_pos = adjust_point_positions(raw_pos, 0.03)

        # scale positions
        scaled_pos = scale_positions(positions=jitter_pos, node_order=ordered_graph.node_order, pos_type=str)

        # return positions
        return {"success": True, "content": scaled_pos}
    except:
        return {"success": False, "error": "cartoGRAPHs Global layout algorithm failed.", "log": {"type": "warning", "msg": "cartoGRAPHs Global layout generation failed."}}
    



def layout_carto_importance(ordered_graph)->dict:
    """
    importance layout from cartoGRAPHs
    """
    # integrety checks
    if not isinstance(ordered_graph, util.OrderedGraph):
        return {"success": False, "error": "Graph is not instance of OrderedGraph class."}
    
    # boundary checks
    if len(ordered_graph.nodes()) >= 15000 or len(ordered_graph.edges()) >= 80000:
        return {"success": False, "error": "Network too large for real-time computation of cartoGRAPHs Importance layout. (No error!)", "log": {"type": "warning", "msg": "Network too large for real-time computation of cartoGRAPHs Importance layout."}}
    
    # actual layout to get node positions
    try:
        raw_pos = carto_gen_layout(ordered_graph, dim = 3, layoutmethod = 'importance', dimred_method='umap')
        jiter_pos = adjust_point_positions(raw_pos, 0.03)

        # scale positions
        scaled_pos = scale_positions(positions=jiter_pos, node_order=ordered_graph.node_order, pos_type=str)

        # return positions
        return {"success": True, "content": scaled_pos}
    except:
        return {"success": False, "error": "cartoGRAPHs Importance layout algorithm failed.", "log": {"type": "warning", "msg": "cartoGRAPHs Importance layout generation failed."}}
    



def layout_spectral(ordered_graph: util.OrderedGraph)->dict:
    """
    Spectral Layout Generation Function
    """
    # integrety checks
    if not isinstance(ordered_graph, util.OrderedGraph):
        return {"success": False, "error": "Graph is not instance of OrderedGraph class."}
    
    # boundary checks
    # no check set yet

    # actual layout to get node positions
    try:
        layout = nx.spectral_layout(G=ordered_graph, dim=3)
        positions = []
        for node in ordered_graph.node_order:
            pos = layout[node]
            positions.append([pos[0], pos[1], pos[2]])
        
        # scale positions
        scaled_pos = scale_positions(positions=positions, node_order=ordered_graph.node_order)
        print(scaled_pos)
        # return positions
        return {"success": True, "content": scaled_pos}
    except:
        return {"success": False, "error": "Spectral layout algorithm failed.", "log": {"type": "log", "msg": "Spectral layout generation failed."}}
