
from PIL import Image
import os
import math
import shutil
import json
import numpy as np
import networkx as nx 
import socketio
import threading
import time
import random 
from sklearn import preprocessing
import atexit
from math import sqrt
from sklearn.preprocessing import MinMaxScaler

# -----------------------------------------------
# JUPYTER CLIENT CONNECTION 
# -----------------------------------------------
class JupyterClient: # include mac address at some point
    def __init__(self, uid='jupyter-client', server_url='http://127.0.0.1:5000', namespace='/main'):
        self.sio = socketio.Client()
        self.uid = uid
        self.namespace = namespace
        self.server_url = server_url
        self.latest_data = None
        self.message_log = []
        
        atexit.register(self.disconnect)  # Register cleanup function on exit

        # Register handlers
        self.sio.on('ex', self._on_ex, namespace=self.namespace)
        self.sio.on('connect', self._on_connect, namespace=self.namespace)
        
        self.connect() 
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
    def _on_ex(self, data):
        self.latest_data = data
        self.message_log.append({'event': 'ex', 'data': data})

    def _on_connect(self):
        print(f"✅ Connected to {self.namespace}")
        self.sio.emit('join', {'usr': self.uid}, namespace=self.namespace)

    def connect(self):
        self.sio.connect(self.server_url, namespaces=[self.namespace])
        self._start_background_loop()

    def _start_background_loop(self):
        def wait_forever():
            while True:
                time.sleep(1)

        thread = threading.Thread(target=wait_forever, daemon=True)
        thread.start()

    def emit(self, *args, **kwargs):
        self.sio.emit(*args, **kwargs)

    def disconnect(self):
        self.sio.emit('left', {'usr': self.uid}, namespace=self.namespace)
        self.sio.disconnect()

    def send(self, fn=None, val=None, msg=None, id=None, textures=None, channel=None, extra=None, success=None):
        """
        Emits a structured message to the server via 'ex'.
        Use extra={} to pass any custom keys/values.
        """
        data = {'usr': self.uid}
        if fn: data['fn'] = fn
        if val is not None: data['val'] = val
        if msg is not None: data['msg'] = msg
        if id: data['id'] = id
        if textures: data['textures'] = textures
        if channel: data['channel'] = channel
        if extra: data.update(extra)
        if success: data['success'] = success

        self.emit('ex', data, namespace=self.namespace)

    def change_project(self, sel_id, sel_name):
        self.send(fn='dropdown', val=sel_id, msg=sel_name, id='projDD')
        self.send(fn='projectLoaded', id=None, success=True) 


# -----------------------------------------------
# SESSION MANAGER - manages session states and transforms vis / data 
# -----------------------------------------------
class SessionManager:
    def __init__(self, sel_id, sel_name, client: JupyterClient):
        self.sel_id = sel_id
        self.sel_name = sel_name
        self.graph = None
        self.project_path = f"static/projects/{sel_name}" 
        self.client = client
        self.selections = {"vr": set(), "jupyter": set()} # useful if both VR and jupyter clients select nodes, then combine them to one set and save for further steps/calculations
        self.edge_to_index = {} # used by TextureGenerator to know which pixel corresponds to which edge 
        self.active_layoutsRGB = None
        self.active_layout = None
        self.active_linksRGB = None


    def load_graph_from_project(self):
        node_path = os.path.join(self.project_path, "nodes.json")
        link_path = os.path.join(self.project_path, "links.json")

        if not os.path.exists(node_path) or not os.path.exists(link_path):
            raise FileNotFoundError("Missing nodes.json or links.json in project folder.")

        G = nx.Graph()

        # --- Load nodes ---
        with open(node_path, "r") as f:
            node_data = json.load(f)

        for node in node_data.get("nodes", []):
            node_id = node.get("id")
            node_name = node.get("n")
           
            #-----------------------------------
            # Collect all attributes available in the node
            node_attrs = {"name": node_name}
            for key, value in node.items():
                if key not in ["id", "n"]:  # Exclude id and name as they are already handled
                    node_attrs[key] = value  
            #-----------------------------------
            G.add_node(node_id,**node_attrs)

        # --- Load links ---
        with open(link_path, "r") as f:
            link_data = json.load(f)

        for link in link_data.get("links", []):
            source = int(link.get("s"))
            target = int(link.get("e"))
            link_id = link.get("id")

            G.add_edge(source, target, id=link_id)

        self.load_graph(G)

        print("Session Graph loaded from project folder. Data: Nodes:", len(G.nodes()), "Links:", len(G.edges()))
        return G

    def update_selection(self, client, node_ids):
        self.selections[client] = set(node_ids)

    def get_selected_nodes(self):
        return set.union(*self.selections.values())

    def get_edge_index(self, edge):
        return self.edge_to_index.get(tuple(edge))

    def load_graph(self, graph):
        """Optional injection of a pre-built graph."""
        self.graph = graph
        self.edge_to_index = {tuple(edge): i for i, edge in enumerate(graph.edges())}

    def reload_project(self):
        self.client.change_project(self.sel_id, self.sel_name)

    def update_active_texture(self, layout_type, texture_name):
        if layout_type == "layouts":
            self.active_layout = texture_name
            #print("C_DEBUG: active layout set to", texture_name)

        elif layout_type == "layoutsRGB":
            self.active_layoutsRGB = texture_name
            #print("C_DEBUG: active layoutsRGB set to", texture_name)

        elif layout_type == "linksRGB":
            self.active_linksRGB = texture_name
            #print("C_DEBUG: active linksRGB set to", texture_name)

    def get_layouts_in_pfile(self):
        pfile_path = os.path.join(self.project_path, 'pfile.json')
        layout_list = []

        with open(pfile_path, 'r') as f:
            pfile_data = json.load(f)
        layout_list = pfile_data.get("layouts", [])
        return layout_list

    def retrieve_active_layout_info(self, layout_type, index_override=None):
        try:
            pdata_path = os.path.join(self.project_path, 'pdata.json')
            layout_list = self.get_layouts_in_pfile()

            dropdown_key = layout_type + "DD"
            if index_override is not None:
                selected_index = index_override
            else:
                with open(pdata_path, 'r') as f:
                    pdata_data = json.load(f)
                selected_index = int(pdata_data.get(dropdown_key, 0))
            print("Layout:", layout_list[selected_index], "Selected index:", selected_index)
        except:
            selected_index = 0
            layout_list = self.get_layouts_in_pfile()

        self.update_active_texture(layout_type, layout_list[selected_index])

        return layout_list[selected_index] 

    def get_active_layouts(self, data):
        fn = data.get("fn")
        id = data.get("id")
        
        layout_list = self.get_layouts_in_pfile()
        #print("layout_list: ", layout_list)

        if fn == "dropdown" and id == "projDD":
            self.retrieve_active_layout_info("layouts")
            self.retrieve_active_layout_info("layoutsRGB")
            self.retrieve_active_layout_info("linksRGB")
            #print("C_DEBUG: get active layout in project loaded")

        elif fn == "dropdown" and id == "layouts":
            self.retrieve_active_layout_info("layouts")
            #print("C_DEBUG: get active layout in dropdown layouts")

        elif fn == "dropdown" and id == "layoutsRGB":
            self.retrieve_active_layout_info("layoutsRGB")
            #print("C_DEBUG: get active layout in dropdown layoutsRGB")

        elif fn == "dropdown" and id == "linksRGB":
            self.retrieve_active_layout_info("linksRGB")
            #print("C_DEBUG: get active layout in dropdown linksRGB")

        elif fn == "ue4" and id=="forwardstep":
            if len(layout_list) == 0: # quick fix if only 1 layout
                new_idx = 0
            else:
                new_idx = int(data.get("val", 0)) + 1 # needs to be added since retrieve will get index from DD message which is old /since not sent new
            self.retrieve_active_layout_info("layouts", new_idx)
            self.retrieve_active_layout_info("layoutsRGB", new_idx)
            self.retrieve_active_layout_info("linksRGB", new_idx)
            #print("C_DEBUG: get active layout in forwardstep")

        elif fn == "ue4" and id=="backwardstep":
            if len(layout_list) == 0: # quick fix if only 1 layout
                new_idx = 0
            else:
                new_idx = int(data.get("val", 0)) - 1 # needs to be added since retrieve will get index from DD message which is old /since not sent new
            self.retrieve_active_layout_info("layouts", new_idx)
            self.retrieve_active_layout_info("layoutsRGB", new_idx)
            self.retrieve_active_layout_info("linksRGB", new_idx)
            #print("C_DEBUG: get active layout in backwardstep")

        else: 
            self.retrieve_active_layout_info("layouts")
            self.retrieve_active_layout_info("layoutsRGB")
            self.retrieve_active_layout_info("linksRGB")
            #print("C_DEBUG: get active layout in else")
            

# -----------------------------------------------
# TEXTURE GENERATOR
# -----------------------------------------------
class TextureGenerator:
    def __init__(self, session: SessionManager):
        self.session = session
        self.generated_types = set()


    def normalize_xyz(self, coords):
        """
        Normalize a list of 3D coordinates to the range [0, 1] using sklearn's preprocessing.

        Args:
            coords (list of tuples): List of (x, y, z) coordinates.

        Returns:
            list of tuples: Normalized coordinates in the range [0, 1].
        """

        scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))
        normalized_coords = scaler.fit_transform(coords)
        return [tuple(coord) for coord in normalized_coords]

    

    # Note: added "save" option for textures; TO DO  add check / raise if pfile keys contain different number of files!! 


    def generate_link_color_texture(self, edge_color_map, texture_name, save=False):
        graph = self.session.graph
        h = 64 * (int(len(graph.edges()) / 32768) + 1)
        tex_data = [(0, 0, 0, 10)] * 512 * h
        img = Image.new('RGBA', (512, h))

        for edge in graph.edges():
            idx = self.session.get_edge_index(edge)
            if idx is not None:
                color = edge_color_map.get(edge, (0, 0, 0, 10))  # fallback: semi-transparent black
                tex_data[idx] = tuple(color)

        img.putdata(tex_data)

        save_path = os.path.join(self.session.project_path, 'linksRGB', texture_name + '.png')
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path)
        self.generated_types.add("linksRGB")

        if save == True: 
            # save path to pfile key "linksRGB"
            pfile_path = os.path.join(self.session.project_path, 'pfile.json')
            with open(pfile_path, 'r') as f:
                data = json.load(f)
                
                # overwrite by default 
                if texture_name not in data["linksRGB"]:
                    data["linksRGB"].append(texture_name)
                else:
                    # Remove the old entry and append the new one
                    data["linksRGB"].remove(texture_name)
                    data["linksRGB"].append(texture_name)
            
                # sort alphabetically
                data["linksRGB"].sort()

            with open(pfile_path, 'w') as f:
                json.dump(data, f, indent=4)

        return save_path
    
    def generate_node_color_texture(self, node_color_map, texture_name, save=False):
        """
        Creates an RGBA texture representing per-node colors.
        Texture is saved to layoutsRGB/ as 128xH PNG, matching vis engine expectations.
        
        node_color_map: dict {node_id: (R, G, B, A)} with 0–255 values
        """
        graph = self.session.graph
        total_nodes = len(graph.nodes())
        h = 128 * ((total_nodes // 16384) + 1)
        size = 128 * h

        tex = [(0, 0, 0, 10)] * size

        for i, node in enumerate(graph.nodes()):
            color = node_color_map.get(node, (0, 0, 0, 10))  # fallback: semi-transparent black
            tex[i] = tuple(map(int, color))  # ensure integers

        img = Image.new('RGBA', (128, h))
        img.putdata(tex)

        save_path = os.path.join(self.session.project_path, 'layoutsRGB', texture_name + '.png')
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path, format='PNG')

        self.generated_types.add("layoutsRGB")

        
        if save == True: 
            # save path to pfile key "linksRGB"
            pfile_path = os.path.join(self.session.project_path, 'pfile.json')
            with open(pfile_path, 'r') as f:
                data = json.load(f)

                # overwrite by default
                if texture_name not in data["layoutsRGB"]:
                    data["layoutsRGB"].append(texture_name)
                else:
                    # Remove the old entry and append the new one
                    data["layoutsRGB"].remove(texture_name)
                    data["layoutsRGB"].append(texture_name)
            
                # sort alphabetically
                data["layoutsRGB"].sort()

            with open(pfile_path, 'w') as f:
                json.dump(data, f, indent=4)

        return save_path



    def generate_node_position_texture(self, node_position_map, texture_name, save=False, normalize_flag=True):
        """
        Generates two RGB textures:
        - One for high bits of x, y, z
        - One for low bits of x, y, z

        Texture dimensions: 128 x H (based on node count)
        Saved into:
        - layouts/texture_name.bmp   (high bits)
        - layoutsl/texture_namel.bmp (low bits)
        """
        graph = self.session.graph
        total_nodes = len(graph.nodes())
        h = 128 * ((total_nodes // 16384) + 1)
        size = 128 * h

        texh = [(0, 0, 0)] * size
        texl = [(0, 0, 0)] * size

        positions = list(node_position_map.values())  # Get positions from the map
        
        # Normalize if needed

        if normalize_flag == True:
            positions_n = self.normalize_xyz(positions)
            #print("C_DEBUG: Normalizing node positions")
        else:
            positions_n = positions
            #print("C_DEBUG: Do not normalize node positions")

        l_x = []
        l_y = []
        l_z = []
        for i, (x, y, z) in enumerate(positions_n):           
            x = float(positions_n[i][0])
            y = float(positions_n[i][1])
            z = float(positions_n[i][2])
            l_x.append(x)
            l_y.append(y)
            l_z.append(z)

        for i, (x, y, z) in enumerate(positions_n):
            x_int = int(x * 65280)
            y_int = int(y * 65280)
            z_int = int(z * 65280)

            xh, xl = divmod(x_int, 255)
            yh, yl = divmod(y_int, 255)
            zh, zl = divmod(z_int, 255)

            texh[i] = (xh, yh, zh)
            texl[i] = (xl, yl, zl)

        # Create and save images
        img_h = Image.new('RGB', (128, h))
        img_l = Image.new('RGB', (128, h))

        img_h.putdata(texh)
        img_l.putdata(texl)

        #path = self.session.project_path
        path_high = f"static/projects/{self.session.sel_name}/layouts/{texture_name}.bmp" # os.path.join(path, 'layouts', texture_name + '.bmp')
        path_low = f"static/projects/{self.session.sel_name}/layoutsl/{texture_name}l.bmp" # os.path.join(path, 'layoutsl', texture_name + 'l.bmp')

        os.makedirs(os.path.dirname(path_high), exist_ok=True)
        os.makedirs(os.path.dirname(path_low), exist_ok=True)

        img_h.save(path_high)
        img_l.save(path_low)


        if save == True: 
            # save path to pfile key "linksRGB"
            pfile_path = os.path.join(self.session.project_path, 'pfile.json')
            with open(pfile_path, 'r') as f:
                data = json.load(f)

                # overwrite by default 
                if texture_name not in data["layouts"]:
                    data["layouts"].append(texture_name)
                else:
                    # Remove the old entry and append the new one
                    data["layouts"].remove(texture_name)
                    data["layouts"].append(texture_name)
               
                # sort alphabetically
                data["layouts"].sort()

            with open(pfile_path, 'w') as f:
                json.dump(data, f, indent=4)


        return path_high, path_low
    

    def get_generated_types(self):
        return self.generated_types
    

# -----------------------------------------------
# PROJECT FILE MANAGER
# -----------------------------------------------
class ProjectFileManager:
    def __init__(self, session: SessionManager):
        self.session = session

    def update_pfile(self, texture_name):
        pfile_path = os.path.join(self.session.project_path, 'pfile.json')
        with open(pfile_path, 'r') as f:
            data = json.load(f)

        for key in ['linksRGB', 'layouts', 'layoutsRGB']:
            if texture_name not in data.get(key, []):
                data[key].append(texture_name)

        with open(pfile_path, 'w') as f:
            json.dump(data, f, indent=4)
            

    def sync_layout_files(self, texture_name, generated_types=None, overwrite=True):
        if generated_types is None:
            generated_types = set()

        folder_map = {
            'layouts':      {'ext': '.bmp', 'suffix': ''},
            'layoutsRGB':   {'ext': '.png', 'suffix': ''},
            'layoutsl':     {'ext': '.bmp', 'suffix': 'l'},
        }

        for folder, cfg in folder_map.items():
            folder_path = os.path.join(self.session.project_path, folder)
            dst_name = texture_name + cfg['suffix'] + cfg['ext']
            dst = os.path.join(folder_path, dst_name)

            if folder in generated_types:
                continue  # Skip folders that were actively generated

            files = [f for f in os.listdir(folder_path) if f.endswith(cfg['ext'])]
            if not files:
                continue  # Nothing to copy from

            src = os.path.join(folder_path, files[0])

            if os.path.abspath(src) == os.path.abspath(dst):
                continue  # Avoid copying onto itself

            if os.path.exists(dst) and not overwrite:
                continue  # File exists and overwrite not allowed

            shutil.copy(src, dst)


# -----------------------------------------------
# VISUAL SYNCH
# -----------------------------------------------
class VisualizerSyncer:
    def __init__(self, session: SessionManager):
        self.session = session



        # response_textures = {}
        # response_textures["usr"] = message["usr"]
        # response_textures["fn"] = "updateTempTex"
        # response_textures["textures"] = []
        # response_textures["textures"].append(
        #     {"channel": "nodeRGB", "path": shortest_path_display_obj["path_nodes"]}
        # )
        # response_textures["textures"].append(
        #     {"channel": "linkRGB", "path": shortest_path_display_obj["path_links"]}
        # )
        # emit("ex", response_textures, room=room)






# -----------------------------------------------
# ANALYSIS TOOLKIT
# -----------------------------------------------
class AnalysisToolkit:
    def __init__(self, session: SessionManager, tex_gen: TextureGenerator, syncer: VisualizerSyncer, file_mgr:ProjectFileManager):
        self.session = session
        self.tex_gen = tex_gen
        self.syncer = syncer
        self.file_mgr = file_mgr



# TO DO 
# move texture functions into texture generator class
# rewrite emit textures alike _gen_highlight_textures in enrichment_module
        



    def highlight_node_withlinks(self, node_id, temp_name="temp_node_highlight"):
        """ 
        Creates temporary textures to highlight a selected node and its connected links
        using the currently active layoutsRGB and graph.
        """
        highlight_color=(255, 255, 0, 255)
        graph = self.session.graph

        #if node_id not in graph:
        #    raise ValueError("Selected node does not exist in the graph.")

        #----------------------------------
        # PUT INTO TEXTURE CLASS

        # NODES
        layoutsRGB_name = self.session.active_layoutsRGB
        layoutsRGB_path = f"static/projects/{self.session.sel_name}/layoutsRGB/{layoutsRGB_name}.png"

        if not os.path.exists(layoutsRGB_path):
            raise FileNotFoundError(f"Cannot find active layoutsRGB texture: {layoutsRGB_path}")

        img = Image.open(layoutsRGB_path).convert("RGBA")
        pixels = list(img.getdata())

        total_nodes = len(graph.nodes())
        h = 128 * ((total_nodes // 16384) + 1)
        width = 128

        tex_index = node_id  # Assuming node ID == index
        if tex_index < len(pixels):
            pixels[tex_index] = highlight_color  # Override only the selected node

        temp_img = Image.new("RGBA", (width, h))
        temp_img.putdata(pixels)

        nodeRGB_path = os.path.join(self.session.project_path, 'layoutsRGB', f'{temp_name}.png')
        temp_img.save(nodeRGB_path)

        # LINKS 
        connected_edges = list(graph.edges(node_id))
        total_edges = len(graph.edges())
        h_links = 64 * (int(total_edges / 32768) + 1)
        tex_link_data = [(0, 0, 0, 10)] * (512 * h_links)

        edge_to_index = self.session.edge_to_index
        for edge in connected_edges:
            i = edge_to_index.get(tuple(sorted(edge))) # to pick up both directions s,e and e,s
            if i is not None:
                tex_link_data[i] = highlight_color

        link_img = Image.new("RGBA", (512, h_links))
        link_img.putdata(tex_link_data)

        linksRGB_path = os.path.join(self.session.project_path, 'linksRGB', f'{temp_name}.png')
        link_img.save(linksRGB_path)
        #----------------------------------

        subgraph = nx.from_edgelist(connected_edges)

        #----------------------------------
        # PUT INTO FUNCTION / VIS SYNCER CLASS

        # Emit to server
        nodeRGB_path_rel = f"static/projects/{self.session.sel_name}/layoutsRGB/{temp_name}.png"
        linksRGB_path_rel = f"static/projects/{self.session.sel_name}/linksRGB/{temp_name}.png"

        self.session.client.emit("ex", {
            "usr": self.session.client.uid,
            "id":None,
            "fn": "updateTempTex",
            "textures": [
                {"channel": "nodeRGB", "path": nodeRGB_path_rel},
                {"channel": "linkRGB", "path": linksRGB_path_rel}
            ]
        }, namespace=self.session.client.namespace)


        # show node info + label in 3D 
        self.session.client.emit("ex", {
            "usr": self.session.client.uid,
            "id":None,
            "fn": "node",
            "msg": node_id,
            "val": node_id
        }, namespace=self.session.client.namespace)
        #----------------------------------

        return (print("Found Links : ", len(connected_edges)), print("Subgraph: ", nx.draw(subgraph, node_size=10, with_labels=True)))
    

    def extract_and_highlight_subnetwork(self, node_id, color=(255, 255, 0, 255), relayout=False):
        """
        Extracts the node and its 1-hop neighbors into a subgraph,
        highlights all nodes and links in that subgraph.
        """
        graph = self.session.graph
        if node_id not in graph:
            return

        neighbors = list(graph.neighbors(node_id))
        sub_nodes = [node_id] + neighbors
        subgraph = graph.subgraph(sub_nodes)

        temp_name = "temp_subnet_highlight"
        
        #layoutsRGB_name = self.session.active_layoutsRGB
        layoutsRGB_name = self.session.get_layouts_in_pfile()[0]
        layoutsRGB_path = f"static/projects/{self.session.sel_name}/layoutsRGB/{layoutsRGB_name}.png"

        #----------------------------------
        # PUT INTO TEXTURE CLASS - NODE COLORS 
            
        if not os.path.exists(layoutsRGB_path):
            raise FileNotFoundError(f"Cannot find active layoutsRGB texture: {layoutsRGB_path}")

        img = Image.open(layoutsRGB_path).convert("RGBA")
        pixels = list(img.getdata())

        total_nodes = len(graph.nodes())
        h = 128 * ((total_nodes // 16384) + 1)
        width = 128

        for n in sub_nodes:
            tex_index = n  # Assuming node ID == index
            if tex_index < len(pixels):
                pixels[tex_index] = color  # Override only the selected node

        temp_img = Image.new("RGBA", (width, h))
        temp_img.putdata(pixels)

        nodeRGB_path = f"static/projects/{self.session.sel_name}/layoutsRGB/{temp_name}.png"
        temp_img.save(nodeRGB_path)
        
        # -----------------------------------------------------
        # ---- Highlight links for the selected node ---
        connected_edges = list(subgraph.edges())

        total_edges = len(graph.edges())
        h_links = 64 * (int(total_edges / 32768) + 1)
        tex_link_data = [(0, 0, 0, 10)] * (512 * h_links)

        edge_to_index = self.session.edge_to_index
        for edge in connected_edges:
            i = edge_to_index.get(tuple(sorted(edge))) # to pick up both directions s,e and e,s 
            if i is not None:
                tex_link_data[i] = color

        link_img = Image.new("RGBA", (512, h_links))
        link_img.putdata(tex_link_data)

        linksRGB_path = os.path.join(self.session.project_path, 'linksRGB', f'{temp_name}.png')
        link_img.save(linksRGB_path)

        # Emit to server
        nodeRGB_path_rel = f"static/projects/{self.session.sel_name}/layoutsRGB/{temp_name}.png"
        linksRGB_path_rel = f"static/projects/{self.session.sel_name}/linksRGB/{temp_name}.png"

        # POSITIONS
        if relayout == True:
            node_pos = self.layout_subnetwork_with_periphery(sub_nodes, temp=True, layout_name=temp_name)
            nodeXYZ_path_rel_high, nodeXYZ_path_rel_low = self.tex_gen.generate_node_position_texture(node_pos, temp_name)

            l_textures = [
                {"channel": "layoutNodesLow", "path": nodeXYZ_path_rel_low}, 
                {"channel": "layoutNodesHi", "path": nodeXYZ_path_rel_high},
                {"channel": "nodeRGB", "path": nodeRGB_path_rel},
                {"channel": "linkRGB", "path": linksRGB_path_rel}
            ]

        elif relayout == False:
            #nodeXYZ_path_rel_high = f"static/projects/{self.session.sel_name}/layouts/{layoutsRGB_name}.bmp"
            #nodeXYZ_path_rel_low = f"static/projects/{self.session.sel_name}/layoutsl/{layoutsRGB_name}l.bmp"
    
            l_textures = [
                {"channel": "nodeRGB", "path": nodeRGB_path_rel},
                {"channel": "linkRGB", "path": linksRGB_path_rel}
            ]

        # PUT INTO FUNCTION / same as in highlight_node_withlinks
        # Emit to server
        self.session.client.emit("ex", {
            "usr": self.session.client.uid,
            "id":None,
            "fn": "updateTempTex",
            "textures": l_textures
        }, namespace=self.session.client.namespace)

        # show node info + label in 3D 
        self.session.client.emit("ex", {
            "usr": self.session.client.uid,
            "id":None,
            "fn": "node",
            "msg": node_id,
            "val": node_id
        }, namespace=self.session.client.namespace)
        #----------------------------------
    
        return (print(nx.draw(subgraph, node_size=10, with_labels=True)))
    


    def layout_subnetwork_with_periphery(self, sub_nodes, scale_center = 0.1, outer_range=(0.8, 1.0), temp=True, layout_name="temp_layout"):
        """
        Generates a new layout with the subnetwork centered and outer nodes arranged on a sphere.
        Saves and registers the layout if temp=False.
        """
        graph = self.session.graph
        all_nodes = list(graph.nodes())

        subgraph = graph.subgraph(sub_nodes)
        layout_sub = nx.spring_layout(list(subgraph.nodes()), dim=3, center = (0,0,0), scale = scale_center)
        layout_sub_sorted = {node: layout_sub[node] for node in subgraph.nodes()}
        layout_sub = dict(zip(subgraph.nodes(), list(layout_sub_sorted.values())))  # Ensure order matches sub_nodes
        
        # Place outer nodes on a sphere in outer_range
        full_layout_positions = {} # TO DO - replace with Felix' function 
        radius = random.uniform(*outer_range)
        for node in all_nodes:
            if node not in sub_nodes:
                theta = random.uniform(0, 2 * np.pi)
                phi = random.uniform(0, np.pi)
                x = radius * np.sin(phi) * np.cos(theta)
                y = radius * np.sin(phi) * np.sin(theta)
                z = radius * np.cos(phi)
                full_layout_positions[node] = (x, y, z)
            elif node in subgraph.nodes():
                full_layout_positions[node] = layout_sub[node]

        #full_layout_positions = {**layout_sub_scaled, **layout_outer}

        return full_layout_positions


