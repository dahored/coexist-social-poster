import os

def get_base_dir():
    base = os.getenv("PROJECT_ROOT", os.getcwd())
    if not os.path.exists(base):
        raise RuntimeError(f"Base directory does not exist: {base}")
    return base

def get_path_from_base(*path_segments):
    return os.path.join(get_base_dir(), *path_segments)