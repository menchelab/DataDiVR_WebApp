import json
import os
import shutil

import numpy as np
from PIL import Image

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
PROJECTS_DIR = os.path.join(STATIC_DIR, "projects")
DEFAULT_PFILE = {
    "name": "",
    "layouts": [],
    "layoutsRGB": [],
    "links": [],
    "linksRGB": [],
    "selections": [],
    "stateData": {},
}
DEFAUT_NAMES = {"names": []}
DEFAULT_NODES = {"nodes": []}
DEFAULT_LINKS = {"links": []}
DEFAULT_ANNOTATIONS = {"node": None, "link": None}
LAYOUTS = "layouts"
LAYOUTSL = "layoutsl"
LAYOUTS_RGB = "layoutsRGB"
LINKS = "links"
LINKS_RGB = "linksRGB"
LINK = "link"
NODE = "node"
LAYOUT = "layout"
LAYOUT_LOW = "layout_low"
COLOR = "color"


class Project:
    def __init__(self, name: str, read=True, check_exists=True):
        """Project class for handling project directories and their data.
        Initializes a project object. All variables are initialized and the pfile is read, if it does not exist, it is created.
        Args:
            name (str): Name of the project
            read (bool, optional): If the pfile should be read. Defaults to True.
        """
        if not isinstance(name, str):
            raise TypeError(f"Name must be a string, not {type(name)}")
        self.name = name
        self.location = os.path.join(PROJECTS_DIR, name)
        self.pfile_file = os.path.join(self.location, f"pfile.json")
        self.names_file = os.path.join(self.location, f"names.json")
        self.nodes_file = os.path.join(self.location, f"nodes.json")
        self.links_file = os.path.join(self.location, f"links.json")
        self.layouts_dir = os.path.join(self.location, f"layouts")
        self.layoutsl_dir = os.path.join(self.location, f"layoutsl")
        self.layouts_rgb_dir = os.path.join(self.location, f"layoutsRGB")
        self.links_dir = os.path.join(self.location, f"links")
        self.links_rgb_dir = os.path.join(self.location, f"linksRGB")
        self.annotations_file = os.path.join(self.location, f"annotations.json")

        self.pfile = None
        self.origin = None
        self.names = None
        self.nodes = None
        self.links = None
        self.annotations = None
        self.write_functions = [
            self.write_pfile,
            self.write_names,
            self.write_nodes,
            self.write_links,
            self.write_annotations,
        ]
        self.read_functions = [
            self.read_pfile,
            self.read_names,
            self.read_nodes,
            self.read_links,
            self.read_annotations,
        ]
        self.print_functions = [
            self.print_pfile,
            self.print_names,
            self.print_nodes,
            self.print_links,
            self.print_annotations,
        ]
        self.create_directory_functions = [
            self.create_layouts_dir,
            self.create_layoutsl_dir,
            self.create_layouts_rgb_dir,
            self.create_links_dir,
            self.create_links_rgb_dir,
        ]
        if read:
            if check_exists and not self.exists():
                pass
            else:
                self.read_pfile()

    @staticmethod
    def write_json(file: str, data: object):
        """Generic write function for json files."""
        file_name = os.path.basename(file)
        tmp_name = "tmp_" + file_name
        tmp_name = os.path.join(os.path.dirname(file), tmp_name)
        with open(tmp_name, "w+", encoding="UTF-8") as f:
            json.dump(data, f)
        os.rename(tmp_name, file)

    def read_json(self, file: str, default: object = {}):
        """Generic read function for json files.

        Args:
            file (str): Path to the file to be read.
            default (json, optional): Default value to return if file does not exist. Defaults to None.
        Returns:
            json: Data from file or default value.
        """
        if self.pfile is not None:
            self.origin = self.get_pfile_value("origin")
            if not self.origin and not os.path.exists(file):
                Project.create_directory(os.path.dirname(file))
                Project.write_json(file, default)
                return default
        if "pfile.json" not in file:
            if self.origin and not os.path.exists(file):
                self.origin = Project(self.origin)
                file = os.path.join(self.origin.location, os.path.basename(file))
        if not os.path.exists(file):
            return default
        with open(file, "r", encoding="UTF-8") as f:
            return json.load(f)

    @staticmethod
    def run_functions(
        functions: list, args: list[tuple] = None, kwargs: list[dict] = None
    ):
        """Runs all functions in list functions. For each function, the args and kwargs are passed.

        Args:
            functions (list): _description_
            args (list[tuple], optional): List of tuples with arguments, one tuple for every function. Defaults to None.
            kwargs (list[dict], optional): List of dicts with key word arguments, one for every function. Defaults to None.
        """
        results = []
        if args is None:
            args = [[]] * len(functions)
        if kwargs is None:
            kwargs = [{}] * len(functions)
        for idx, func in enumerate(functions):
            if args[idx] is None:
                args[idx] = []
            if kwargs[idx] is None:
                kwargs[idx] = {}
            results.append(func(*args[idx], **kwargs[idx]))
        return results

    @staticmethod
    def print_data(data: object):
        """Generic print function for json data.

        Args:
            data (json): Data to print, should be in a json format.
        """
        print(json.dumps(data))

    @staticmethod
    def create_directory(dir: str):
        """Generic function for creating directories.

        Args:
            dir (str): Path to the directory to be made.
        """
        os.makedirs(dir, exist_ok=True)

    def get_origin(self):
        if self.exists():
            self.read_pfile()
            if self.origin:
                return self.origin
        return self.name

    def write_pfile(
        self,
    ):
        if self.pfile is not None:
            self.write_json(self.pfile_file, self.pfile)

    def write_names(self):
        if self.names is not None:
            self.write_json(self.names_file, self.names)

    def write_nodes(self):
        if self.nodes is not None:
            self.write_json(self.nodes_file, self.nodes)

    def write_links(self):
        if self.links is not None:
            self.write_json(self.links_file, self.links)

    def write_annotations(self):
        if self.annotations is not None:
            self.write_json(self.annotations_file, self.annotations)

    def write_all_jsons(self):
        self.run_functions(self.write_functions)

    def read_pfile(
        self,
        set_pfile: bool = True,
        set_origin: bool = True,
    ):
        pfile = self.read_json(self.pfile_file, DEFAULT_PFILE)
        origin = pfile.get("origin", None)
        if set_pfile:
            self.pfile = pfile
        if set_origin:
            self.origin = origin
        return pfile, origin

    def read_names(self, set_names: bool = True):
        names = self.read_json(self.names_file, DEFAUT_NAMES)
        if set_names:
            self.names = names
        return names

    def read_nodes(self, set_nodes: bool = True):
        nodes = self.read_json(self.nodes_file, DEFAULT_NODES)
        if set_nodes:
            self.nodes = nodes
        return nodes

    def read_links(self, set_links: bool = True):
        links = self.read_json(self.links_file, DEFAULT_LINKS)
        if set_links:
            self.links = links
        return links

    def read_annotations(
        self,
        data_type: list[str] = ["node", "link"],
        set_annotations: bool = True,
    ):
        annotations = self.read_json(self.annotations_file, DEFAULT_ANNOTATIONS)
        annotations = {
            key: value for key, value in annotations.items() if key in data_type
        }
        if set_annotations:
            self.annotations = annotations
        return annotations

    def read_all_jsons(self, set_all: bool = True):
        kwargs = [
            {"set_pfile": set_all, "set_origin": set_all},
            {"set_names": set_all},
            {"set_nodes": set_all},
            {"set_links": set_all},
            {"set_annotations": set_all},
        ]
        data = self.run_functions(
            self.read_functions,
            kwargs=kwargs,
        )

        if set_all:
            self.pfile, self.origin = data[0]
            self.names = data[1]
            self.nodes = data[2]
            self.links = data[3]
            self.annotations = data[4]
        return data

    def print_pfile(self):
        self.print_data(self.pfile)

    def print_names(self):
        self.print_data(self.names)

    def print_nodes(self):
        self.print_data(self.nodes)

    def print_links(self):
        self.print_data(self.links)

    def print_annotations(self):
        self.print_data(self.annotations)

    def print_all_jsons(self):
        self.run_functions(self.print_functions)

    def get_pfile_value(self, key: str, default: object = None):
        if key not in self.pfile:
            self.pfile[key] = default
        return self.pfile[key]

    def set_pfile_value(self, key: str, value: object):
        self.pfile[key] = value

    def append_pfile_value(self, key: str, value: object):
        if self.pfile is None:
            return
        if key not in self.pfile:
            self.pfile[key] = []
        if type(self.pfile[key]) != list:
            raise TypeError(f"pfile[{key}] is not a list.\n{self.pfile[key]}")
        if value not in self.pfile[key]:
            self.pfile[key].append(value)

    def define_pfile_value(self, key, dict_key, value):
        self.pfile[key][dict_key] = value

    def get_all_layouts(self):
        return self.get_pfile_value("layouts", [])

    def get_all_node_colors(self):
        return self.get_pfile_value("layoutsRGB", [])

    def get_all_links(self):
        return self.get_pfile_value("links", [])

    def get_all_link_colors(self):
        return self.get_pfile_value("linksRGB", [])

    def get_selections(self):
        return self.get_pfile_value("selections", [])

    def get_state_data(self):
        return self.get_pfile_value("stateData", [])

    def get_annotations(self, data_type=["node", "link"]):
        if isinstance(data_type, str):
            data_type = [data_type]
        return self.read_annotations(data_type, False)

    def add_layout(self, layout: str):
        if not layout.endswith("XYZ"):
            layout += "XYZ"
        if layout not in self.get_all_layouts():
            self.append_pfile_value("layouts", layout)

    def add_node_color(self, color: str):
        if not color.endswith("RGB"):
            color += "RGB"
        if color not in self.get_all_node_colors():
            self.append_pfile_value("layoutsRGB", color)

    def add_link(self, link: str):
        if not link.endswith("XYZ"):
            link += "XYZ"
        if link not in self.get_all_links():
            self.append_pfile_value("links", link)

    def add_link_color(self, color: str):
        if not color.endswith("RGB"):
            color += "RGB"
        if color not in self.get_all_link_colors():
            self.append_pfile_value("linksRGB", color)

    def get_pfile(self):
        """Read the pfile of the project and return it. This will not set the pfile variable of this Project instance but will just return the current written state of the pfile json.

        Returns:
            dict: Pfile json of the project.
        """
        return self.read_pfile(False)

    def get_nodes(self):
        """Read the nodes of the project and return them. This will not set the nodes variable of this Project instance but will just return the current written state of the nodes json.

        Returns:
            dict: Nodes json of the project.
        """
        return self.read_nodes(False)

    def get_links(self):
        """Read the links of the project and return them. This will not set the links variable of this Project instance but will just return the current written state of the links json.

        Returns:
            dict: Links json of the project.
        """
        return self.read_links(False)

    def get_names(self):
        """Read the names of the project and return them. This will not set the names variable of this Project instance but will just return the current written state of the names json.

        Returns:
            dict: Names json of the project.
        """
        return self.read_names(False)

    def get_all_data(self):
        """Read all jsons of the project and return them. This will not set the variables of this Project instance but will just return the current written state of the jsons.

        Returns:
            dict: All jsons of the project.
        """
        data = self.read_all_jsons(False)
        return {
            "pfile": self.pfile,
            "names": self.names,
            "nodes": self.nodes,
            "links": self.links,
            "annotations": self.annotations,
        }

    def set_all_layouts(self, layouts):
        self.set_pfile_value("layouts", layouts)

    def set_all_node_colors(self, colors):
        self.set_pfile_value("nodesRGB", colors)

    def set_all_links(self, links):
        self.set_pfile_value("links", links)

    def set_all_link_colors(self, colors):
        self.set_pfile_value("linksRGB", colors)

    def set_selections(self, selections):
        self.set_pfile_value("selections", selections)

    def set_state_data(self, state_data):
        self.set_pfile_value("stateData", state_data)

    def append_layout(self, layout):
        self.append_pfile_value("layouts", layout)

    def append_node_color(self, color):
        self.append_pfile_value("nodesRGB", color)

    def append_link(self, link):
        self.append_pfile_value("links", link)

    def append_link_color(self, color):
        self.append_pfile_value("linksRGB", color)

    def append_selection(self, selection):
        self.append_pfile_value("selections", selection)

    def set_state_data_value(self, key, value):
        self.define_pfile_value("stateData", key, value)

    def get_all_data(self):
        return self.pfile, self.names, self.nodes, self.links

    def create_layouts_dir(self):
        self.create_directory(self.layouts_dir)

    def create_layoutsl_dir(self):
        self.create_directory(self.layoutsl_dir)

    def create_layouts_rgb_dir(self):
        self.create_directory(self.layouts_rgb_dir)

    def create_links_dir(self):
        self.create_directory(self.links_dir)

    def create_links_rgb_dir(self):
        self.create_directory(self.links_rgb_dir)

    def create_all_directories(self):
        self.run_functions(self.create_directory_functions)

    def exists(self):
        return os.path.exists(self.location)

    def get_files_in_dir(self, dir: str):
        return os.listdir(os.path.join(self.location, dir))

    def has_own_nodes(self):
        return os.path.exists(self.nodes_file)

    def has_own_links(self):
        return os.path.exists(self.links_file)

    def remove(self):
        shutil.rmtree(self.location, ignore_errors=True)

    def remove_subdir(self, subdir: str):
        shutil.rmtree(os.path.join(self.location, subdir))

    def copy(self, target: str, *args, ignore=None, **kwargs):
        """Copies the whole directory of the project to the target location."""
        if ignore == True:
            ignore = shutil.ignore_patterns("names.json", "nodes.json", "links.json")
        elif ignore == False:
            ignore = None

        shutil.copytree(
            self.location,
            target,
            *args,
            **kwargs,
            ignore=ignore,
            dirs_exist_ok=True,
        )

    def write_bitmap(
        self,
        bitmap: Image,
        layout_name: str,
        data_type: str,
        bitmap_type: str,
        debug=False,
    ):
        if debug:
            print("writing bitmap: ", layout_name, data_type, bitmap_type)
        file_path = self.get_file_path(
            layout_name,
            data_type,
            bitmap_type,
        )
        if debug:
            print("writing layout to file: ", file_path)
        bitmap.save(file_path)

    def load_bitmap(
        self, layout_name: str, data_type: str, bitmap_type: str, numpy=False
    ):
        file_path = self.get_file_path(
            layout_name,
            data_type,
            bitmap_type,
        )
        if numpy:
            return np.array(Image.open(file_path))
        return Image.open(file_path)

    def delete_bitmap(self, layout_name: str, data_type: str, bitmap_type: str):
        file_path = self.get_file_path(
            layout_name,
            data_type,
            bitmap_type,
        )
        os.remove(file_path)

    @staticmethod
    def make_layout_name(layout_name: str, low=False):
        if low:
            if layout_name.endswith("XYZl.bmp"):
                return layout_name
            if layout_name.endswith("XYZl"):
                return layout_name + ".bmp"
            return layout_name + "XYZl.bmp"

        if layout_name.endswith("XYZ.bmp"):
            return
        if layout_name.endswith("XYZ"):
            return layout_name + ".bmp"
        return layout_name + "XYZ.bmp"

    @staticmethod
    def make_color_name(color_name: str):
        if color_name.endswith("RGB.png"):
            return color_name
        if color_name.endswith("RGB"):
            return color_name + ".png"
        return color_name + "RGB.png"

    def get_file_path(self, layout_name: str, data_type: str, bitmap_type: str = None):
        if bitmap_type is None:
            if layout_name.endswith("XYZ.bmp"):
                bitmap_type = LAYOUT
            elif layout_name.endswith("RGB.png"):
                bitmap_type = COLOR
            elif layout_name.endswith("XYZl.bmp"):
                bitmap_type = LAYOUT_LOW
                data_type = NODE
            else:
                raise ValueError(
                    f"Cannot determine data type of layout {layout_name} and data type is not specified."
                )
        if bitmap_type == LAYOUT:
            layout_name = self.make_layout_name(layout_name)
        elif bitmap_type == LAYOUT_LOW:
            layout_name = self.make_layout_name(layout_name, low=True)
        elif bitmap_type == COLOR:
            layout_name = self.make_color_name(layout_name)

        if data_type == NODE:
            target_dir = {
                LAYOUT: self.layouts_dir,
                LAYOUT_LOW: self.layoutsl_dir,
                COLOR: self.layouts_rgb_dir,
            }
        elif data_type == LINK:
            target_dir = {
                LAYOUT: self.links_dir,
                COLOR: self.links_rgb_dir,
            }

        return os.path.join(target_dir[bitmap_type], layout_name)
