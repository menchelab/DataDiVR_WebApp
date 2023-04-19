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

        # Install requirements
        requirements = os.path.join(extensions_path, ext, "requirements.txt")
        if os.path.isfile(requirements):
            if platform.system() != "Windows":
                os.system(
                    f"python3 -m pip install -r {requirements} | grep -v 'already satisfied'"
                )
            else:
                os.system(f"python3 -m pip install -r {requirements}")

        module = import_module(module)

        if not hasattr(module, "blueprint") or not hasattr(module, "url_prefix"):
            raise AttributeError(
                f"Attributes 'blueprint' or 'url_prefix' not found in module {ext}."
            )

        app.register_blueprint(module.blueprint, url_prefix=module.url_prefix)
        print(f"\033[1;32mLoaded extension: {ext}")
        return module
    except ImportError:
        print(f"\u001b[33m", traceback.format_exc())
        print(f"\u001b[33mMake sure you installed a necessary python modules.")
        print(
            f"\u001b[33mYou can use:\n\npython3 -m pip install -r extensions/{ext}/requirements.txt\n\nTo install all requirements."
        )
    except AttributeError:
        print(f"\u001b[33m", traceback.format_exc())
        print(
            f"\u001b[33mMake sure you have an app.py file in the '/src/' folder of your extension."
        )
        print(
            f"\u001b[33mMake sure that you have defined a 'url_prefix' for your in the app.py file."
        )
        print(f"\u001b[33mMake sure your flask blueprint is called 'blueprint'.")
        return False


def load(main_app: flask.Flask) -> tuple[flask.Flask, dict]:
    """Loads all extensions contained in the directory extensions."""
    _WORKING_DIR = os.path.abspath(os.path.dirname(__file__))
    extensions = os.path.join(_WORKING_DIR, "extensions")
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
    if os.path.exists(extensions):
        if os.path.isfile(os.path.join(extensions, "ignore.py")):
            ignore_py = import_module("extensions.ignore")
            if hasattr(ignore_py, "ignore"):
                ignore = ignore_py.ignore
        for ext in os.listdir(extensions):
            if (
                not os.path.isdir(os.path.join(extensions, ext))
                or ext in ignore
                or ext in IGNORE_DIRS
            ):
                continue
            extension_attr = {}
            module = import_blueprint(main_app, ext, extensions)
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
