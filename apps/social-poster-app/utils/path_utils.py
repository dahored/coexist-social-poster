import os

def get_base_dir():
    """Returns the absolute path to the base of the project (where main.py or app root is)."""
    # return os.path.dirname(os.path.abspath(sys.argv[0]))
    # return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.getcwd()

def get_path_from_base(*path_segments):
    """
    Builds an absolute path from the project base directory
    by joining the given path segments.
    
    Example: get_path_from_base("public", "json", "file.json")
    """
    return os.path.join(get_base_dir(), *path_segments)
