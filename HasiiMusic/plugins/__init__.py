# ==============================================================================
# __init__.py - Plugin Auto-Discovery Module
# ==============================================================================
# This file automatically discovers all plugin files in subdirectories.
# It scans the plugins/ folder recursively and builds a list of module paths.
# 
# Example output: ['admin-controles.broadcast', 'events.callbacks', 'playback-controls.play']
# 
# This list is used by __main__.py to dynamically load all plugins at startup,
# making it easy to add new commands without manual registration.
# ==============================================================================

from pathlib import Path


def _list_modules():
    """
    List all Python module filenames (without extension) in the current directory
    and subdirectories, excluding the __init__.py file.

    Returns:
        list: A list of module names as strings with relative paths (e.g., 'admin-controles.broadcast').
    """
    mod_dir = Path(__file__).parent
    modules = []
    
    # Get all Python files in subdirectories
    for file in mod_dir.rglob("*.py"):
        if file.is_file() and file.name != "__init__.py":
            # Get relative path from plugins directory
            relative_path = file.relative_to(mod_dir)
            # Convert path to module format: folder/file.py -> folder.file
            module_path = str(relative_path.with_suffix('')).replace('\\', '.').replace('/', '.')
            modules.append(module_path)
    
    return modules


all_modules = frozenset(sorted(_list_modules()))
