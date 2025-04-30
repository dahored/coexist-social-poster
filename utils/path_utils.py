import os

def get_base_dir():
    base = os.getenv("PROJECT_ROOT", os.getcwd())
    if not os.path.exists(base):
        raise RuntimeError(f"Base directory does not exist: {base}")
    return base

def get_path_from_base(*path_segments):
    """
    Builds an absolute path from the project base directory
    by joining the given path segments.
    
    Example: get_path_from_base("public", "json", "file.json")
    """
    return os.path.join(get_base_dir(), *path_segments)
