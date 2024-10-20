import os
import platform
import traceback
from importlib import import_module

import flask

IGNORE_DIRS = ["__pycache__", ".ds_store"]


def import_blueprint(app: flask.Flask, ext: str, extensions_path: str) -> bool:
    try:
        if not os.path.isfile(os.path.join(extensions_path, ext, "src", "app.py")):
            raise ImportError(f"No app.py found in '/extension/{ext}/src'.")

        module = f"extensions.{ext}.src.app"
        module = import_module(module)

        if not hasattr(module, "blueprint") or not hasattr(module, "url_prefix"):
            raise AttributeError(
                f"Attributes 'blueprint' or 'url_prefix' not found in module {ext}."
            )

        app.register_blueprint(module.blueprint, url_prefix=module.url_prefix)
        print(f"\033[1;32mLoaded extension: {ext}")
        return module
    except ImportError:
        print("\u001b[33m", traceback.format_exc())
        print("\u001b[33mMake sure you installed a necessary python modules.")
        print(
            f"\u001b[33mYou can use:\n\npython3 -m pip install -r extensions/{ext}/requirements.txt\n\nTo install all requirements."
        )
    except AttributeError:
        print("\u001b[33m", traceback.format_exc())
        print(
            "\u001b[33mMake sure you have an app.py file in the '/src/' folder of your extension."
        )
        print(
            "\u001b[33mMake sure that you have defined a 'url_prefix' for your in the app.py file."
        )
        print("\u001b[33mMake sure your flask blueprint is called 'blueprint'.")
    return False


def load(main_app: flask.Flask) -> tuple[flask.Flask, dict]:
    """Loads all extensions contained in the directory extensions."""
    _WORKING_DIR = os.path.abspath(os.path.dirname(__file__))
    ignore = []
    loaded_extensions = []
    list_of_ext = []
    possible_tabs = [
        "column_1",
        "column_2",
        "column_3",
        "column_4",
        "upload_tabs",
    ]
    # add_tab_to_nodepanel = []
    if os.path.exists(_WORKING_DIR):
        IGNORE_FILE = os.path.join(_WORKING_DIR, "ignore.txt")
        if os.path.isfile(IGNORE_FILE):
            with open(IGNORE_FILE, "r") as f:
                ignore = f.readlines()

    for ext in os.listdir(_WORKING_DIR):
        if (
            not os.path.isdir(os.path.join(_WORKING_DIR, ext))
            or ext in ignore
            or ext in IGNORE_DIRS
        ):
            continue

        extension_attr = {}
        module = import_blueprint(main_app, ext, _WORKING_DIR)
        if module:
            extension_attr["id"] = ext
            loaded_extensions.append(ext)
            for key in possible_tabs:
                if hasattr(module, key):
                    extension_attr[key] = module.__dict__[key]

            list_of_ext.append(extension_attr)
    print("\033[1;32m" + "=" * 50)
    print("\033[1;32mFinished loading extensions, server is running... \u001b[37m")
    res = {
        "loaded": loaded_extensions,
        "ext": list_of_ext,
    }
    return main_app, res


# Deprecated
# def add_tabs(tabs: list[str], ext: str) -> list[str]:
#     """Add tabs to the list of tabs."""
#     to_add = []
#     for tab in tabs:
#         tab = os.path.join("extensions", ext, "templates", tab)
#         to_add.append(tab)
#     return to_add
