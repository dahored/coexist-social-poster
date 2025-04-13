import os
import sys


def get_base_dir():
    """Returns the base directory where the main script (index.py) is located."""
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def get_path_from_base(*path_segments):
    """
    Builds an absolute path from the project base directory
    by joining the given path segments.
    
    Example: get_path_from_base("public", "json", "file.json")
    """
    return os.path.join(get_base_dir(), *path_segments)
