


from PIL import Image
import os
import math
import shutil
import json
import numpy as np


# SESSION MANAGER
# managing project and states

class SessionManager:
    def __init__(self, sel_id, sel_name, sio):
        self.sel_id = sel_id
        self.sel_name = sel_name
        self.project_path = f"static/projects/{sel_name}"
        self.graph = None  # loaded graph object
        self.sio = sio
        self.selections = {"vr": set(), "jupyter": set()}
        self.edge_to_index = {}

    def load_graph(self, graph):
        self.graph = graph
        self.edge_to_index = {tuple(edge): i for i, edge in enumerate(graph.edges())}

    def update_selection(self, client, node_ids):
        self.selections[client] = set(node_ids)

    def get_selected_nodes(self):
        return set.union(*self.selections.values())

    def get_edge_index(self, edge):
        return self.edge_to_index.get(tuple(edge))


class TextureGenerator:
    def __init__(self, session: SessionManager):
        self.session = session
        self.generated_types = set()

    def generate_link_texture(self, edges, color, texture_name):
        graph = self.session.graph
        h = 64 * (int(len(graph.edges()) / 32768) + 1)
        tex_data = [(0, 0, 0, 10)] * 512 * h
        img = Image.new('RGBA', (512, h))

        for edge in edges:
            idx = self.session.get_edge_index(edge)
            if idx is not None:
                tex_data[idx] = tuple(color)

        img.putdata(tex_data)
        save_path = os.path.join(self.session.project_path, 'linksRGB', texture_name + '.png')
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path)
        self.generated_types.add("linksRGB")
        return save_path
    
    def generate_node_color_texture(self, node_color_map, texture_name):
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
        return save_path


    def generate_node_position_texture(self, node_position_map, texture_name):
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

        # Get 3D positions; default missing dimensions to 0.0
        positions = []
        for node in graph.nodes():
            pos = node_position_map.get(node, (0.0, 0.0, 0.0))
            if len(pos) == 2:
                pos = (*pos, 0.0)
            positions.append((pos[0], pos[2], pos[1]))  # Reorder as (x, z, y)

        # Normalize if needed
        flat = [coord for p in positions for coord in p]
        min_val, max_val = min(flat), max(flat)
        if not (0.0 <= min_val and max_val <= 1.0):
            range_val = max_val - min_val or 1.0
            positions = [((x - min_val)/range_val, (y - min_val)/range_val, (z - min_val)/range_val)
                        for x, y, z in positions]

        for i, (x, y, z) in enumerate(positions):
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

        path = self.session.project_path
        path_high = os.path.join(path, 'layouts', texture_name + '.bmp')
        path_low = os.path.join(path, 'layoutsl', texture_name + 'l.bmp')

        os.makedirs(os.path.dirname(path_high), exist_ok=True)
        os.makedirs(os.path.dirname(path_low), exist_ok=True)

        img_h.save(path_high)
        img_l.save(path_low)

        # Register these as generated
        self.generated_types.add("layouts")
        self.generated_types.add("layoutsl")

        return path_high, path_low
    
    def get_generated_types(self):
        return self.generated_types
    


    
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



# VISUAL SYNCH
class VisualizerSyncer:
    def __init__(self, session: SessionManager):
        self.session = session

    def emit_texture_update(self, texture_name, channel='linkRGB'):
        self.session.sio.emit('ex', {
            'usr': 'jupyter-client',
            'fn': "updateTempTex",
            'id': 'linksRGBDD',
            'textures': [{
                "channel": channel,
                'path': f"static/projects/{self.session.sel_name}/linksRGB/{texture_name}.png"
            }]
        }, namespace="/main")

    def reload_project(self):
        self.session.sio.emit('ex', {
            'usr': 'jupyter-client',
            'fn': 'dropdown',
            'val': self.session.sel_id,
            'msg': self.session.sel_name,
            'id': 'projDD',
        }, namespace="/main")

