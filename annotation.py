"""
Util for Annotation Module
"""
from PIL import Image
import math


class AnnotationTextures:
    def __init__(self, project=None, nodes=None, links=None, annotations=None):
        self.project = project
        self.nodes = nodes
        self.links = links
        self.annotations = annotations

        self.path_nodes = "static/projects/"+ self.project + "/layoutsRGB/temp.png"
        self.path_links = "static/projects/"+ self.project + "/linksRGB/temp.png"
        self.colors = {
            "none": (66, 66, 66, 30),
            "a1": (3, 218, 198, 100),
            "a2": (55, 0, 179, 100),
            "result": (187, 134, 252, 100)
        }

    def __set_union(self, set_a1, set_a2):
        return set_a1.union(set_a2)
    
    def __set_intersection(self, set_a1, set_a2):
        return set_a1.intersection(set_a2)
    
    def __set_subtraction(self, set_a1, set_a2):
        return set_a1.difference(set_a2)

    def gen_textures(self, annotation_1=None, annotation_2=None, operation=None) -> dict:
        # error handling
        if operation not in ("single", "union", "intersection", "subtraction"):
            return {"generated_texture": False}
        if annotation_1 is None:
            return {"generated_texture": False}
        if annotation_2 is None:
            return {"generated_texture": False}

        # generate sets
        set_a1 = set(self.annotations[annotation_1])
        set_a2 = set(self.annotations[annotation_2])

        # perform operartion
        if operation == "union":
            set_result = self.__set_union(set_a1, set_a2)
        elif operation == "intersection":
            set_result = self.__set_intersection(set_a1, set_a2)
        elif operation == "subtraction":
            set_result = self.__set_subtraction(set_a1, set_a2)
        elif operation == "single":
            set_a2.clear()
            set_result = set()
        else:
            return {"generated_texture": False}
            
        # generate node texture
        nodes_colors = []
        for node in self.nodes:
            if node["id"] in set_result:
                nodes_colors.append(self.colors["result"])
                continue
            if node["id"] in set_a1:
                nodes_colors.append(self.colors["a1"])
                continue
            if node["id"] in set_a2:
                nodes_colors.append(self.colors["a2"])
                continue
            nodes_colors.append(self.colors["none"])

        dim_nodes = math.ceil(math.sqrt(len(nodes_colors)))
        texture_nodes = Image.new("RGBA", (dim_nodes, dim_nodes))
        texture_nodes.putdata(nodes_colors)
        texture_nodes.save(self.path_nodes, "PNG")

        # generate link texture
        link_colors = []
        for link in self.links:
            color = self.colors["none"]
            start, end = int(link["s"]), int(link["e"])
            if start in set_a2 and end in set_a2:
                color = self.colors["a2"]
            if start in set_a1 and end in set_a1:
                color = self.colors["a1"]
            if start in set_result and end in set_result:
                color = self.colors["result"]
            link_colors.append(color)
        
        dim_links = math.ceil(math.sqrt(len(link_colors)))
        texture_links = Image.new("RGBA", (dim_links, dim_links))
        texture_links.putdata(link_colors)
        texture_links.save(self.path_links, "PNG")

        
        # return dict as in shortest path
        return {"generated_texture": True, "path_nodes": self.path_nodes, "path_links": self.path_links}

  