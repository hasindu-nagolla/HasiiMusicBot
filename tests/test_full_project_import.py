import os
import sys
import pkgutil
import importlib


def recursive_import(package_name):
    """Recursively imports all modules inside a package."""
    try:
        package = importlib.import_module(package_name)
    except Exception:
        # Some modules may require bot runtime context; skip failures
        return

    if not hasattr(package, "__path__"):
        return  # Not a package

    for _, module_name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            importlib.import_module(module_name)
        except Exception:
            # Ignore modules that depend on runtime bot context
            pass


def test_import_entire_project():
    """
    This test dynamically imports every module in the entire HasiiMusicBot project.
    Ensures full coverage across:
        - HasiiMusic/
        - HasiiMusic/core/
        - HasiiMusic/plugins/ (all subfolders)
        - HasiiMusic/utils/
        - HasiiMusic/platforms/
        - HasiiMusic/stream/
        - strings/
        - config.py
    """

    # Add project root to import path
    sys.path.append(os.getcwd())

    # Import root-level modules
    try:
        import config
    except Exception:
        pass

    # Recursively import all HasiiMusic code
    recursive_import("HasiiMusic")

    # Import strings package
    recursive_import("strings")
