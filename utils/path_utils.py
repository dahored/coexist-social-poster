import os
from config.image_config import (IMAGES_DIR, BASE_PUBLIC)

def get_public_image_url(file_path):
    """
    Converts a local image path to its public URL using only the domain 
    from PUBLIC_URL_BASE and the relative path from the 'public' folder.

    Example:
    file_path = /app/public/uploads/images/image_file_1.png
    IMAGES_DIR = /app/public/uploads/images
    PUBLIC_URL_BASE = https://gorilla-humble-pelican.ngrok-free.app

    Output:
    https://gorilla-humble-pelican.ngrok-free.app/public/uploads/images/image_file_1.png
    """
    base_url = os.getenv("PUBLIC_URL_BASE", "http://localhost:8000")

    # Validate file is under IMAGES_DIR
    abs_file_path = os.path.abspath(file_path)
    abs_images_dir = os.path.abspath(IMAGES_DIR)

    if not abs_file_path.startswith(abs_images_dir):
        raise ValueError(f"File path {file_path} is not under IMAGES_DIR {IMAGES_DIR}")

    # Find the /public directory
    public_folder = BASE_PUBLIC

    # Get relative path from /public → uploads/images/filename.png
    rel_path = os.path.relpath(abs_file_path, public_folder)

    # Build final public URL
    public_url = f"{base_url}/public/{rel_path}"

    return public_url
