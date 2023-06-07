import os

from io_blueprint import IOBlueprint

from . import socket_handlers as u_sh

# Prefix for the extension, as well as the names space of the extension
url_prefix = "/Util"  # MANDATORY
extensions_name = "Util"

# Define where all templates and static files of your extension are located
templates = os.path.abspath("./extensions/Util/templates")
static = os.path.abspath("./extensions/Util/static")

# Create a blueprint for the extension this will be loaded by the main app
blueprint = IOBlueprint(
    extensions_name,
    __name__,
    url_prefix=url_prefix,
    template_folder=templates,  # defaults to static of main app.py
    static_folder=static,  # defaults to static of main app.py
)  # MANDATORY

column_1 = [
    "util_flask_styles.html",
    "util_scripts.html",
]  # List of tab templates to be loaded in the first column of main and preview panel
column_3 = ["util_main_selection.html", "util_main_highlight.html"]


@blueprint.before_app_first_request
def util_setup():
    u_sh.setup(blueprint)


@blueprint.on("annotation")
def util_get_annotation(message):
    u_sh.get_annotation(blueprint, message)


@blueprint.on("select")
def util_select(message):
    u_sh.select(blueprint, message)


@blueprint.on("ex")
def util_highlight(message):
    print("Util received message", message)
    func = message.get("fn")
    if func in ["highlight", "isolate", "bipartite", "store"]:
        u_sh.highlight(blueprint, message)
    elif func == "reset":
        u_sh.reset(blueprint, message)
    elif func == "colorbox":
        u_sh.store_data(message)
    elif func == "dropdown":
        u_sh.dropdown(blueprint, message)
