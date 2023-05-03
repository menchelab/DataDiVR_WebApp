"""
Functions for Annotation Module
"""
from PIL import Image
import math

class AnnotationTextures:
    def __init__(self) -> None:
        self.project = None
        self.nodes = None
        self.links = None
        self.annotation_1 = None
        self.annotation_2 = None
        self.colors = {
            "none": "",
            "a1": "",
            "a2": "",
            "result": ""
        }

    def __prepare_data():...
    def __gen_node_texture():...
    def __gen_link_texture():...

    def check_if_project_changes() -> bool:...
    # check if project changes to keep data stored to generate textures faster
    def set_union():...
    def set_intersection():...
    def set_subtraction():...
    def gen_textures() -> dict:...
