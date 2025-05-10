import os
import shutil
import requests

from utils.base_utils import get_path_from_base

from config.image_config import (
    IMAGES_DIR,
)


class FileHandler:
    def __init__(self):
        self.images_path = IMAGES_DIR

    def get_file_path(self, relative_path):
        return get_path_from_base(relative_path)

    def move_temp_file_to_folder(self, temp_file_path, id, other_name=""):
        if not os.path.exists(temp_file_path):
            print(f"The file {temp_file_path} does not exist.")
            return None

        print(f"Moving file {temp_file_path} to {self.images_path}")
        type_file = self.get_type_file(temp_file_path)
        if not os.path.exists(self.images_path):
            os.makedirs(self.images_path)

        if type_file in [".jpg", ".png", ".jpeg"]:
            new_filename = f"image_file_{id}{other_name}{type_file}"
            destination_path = os.path.join(self.images_path, new_filename)
            shutil.move(temp_file_path, destination_path)
            print(f"File moved and renamed to {destination_path}")

            return {
                "filename": new_filename,
                "full_path": destination_path,
                "path": self.images_path,
                "relative_path": os.path.join(self.images_path, new_filename),
            }
        else:
            print(f"The file {temp_file_path} is not a valid image.")
            return None

    def get_media_path(self, media_path):
        absolute_path = self.get_file_path(media_path)
        if not os.path.exists(absolute_path):
            print(f"The file {absolute_path} does not exist.")
            return None
        return absolute_path

    def get_type_file(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        return file_extension
    
    def download_media_to_temp(self, url, temp_dir='/tmp'):
        """Descarga una imagen de Cloudinary y guarda un archivo temporal"""
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to download media from {url}")

        filename = os.path.join(temp_dir, os.path.basename(url))
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        return filename
    
    async def clean_uploaded_files(self):
        """Deletes all files inside public/uploads/images without deleting the folder itself."""
        for root, dirs, files in os.walk(self.images_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"✅ Deleted file: {file_path}")
                except Exception as e:
                    print(f"❌ Failed to delete {file_path}: {e}")
        print(f"✅ Cleanup of {self.images_path} completed.")

    async def delete_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"File {file_path} does not exist.")

    def file_exists(self, path):
        """
        Verifica si el archivo existe en el sistema de archivos.
        """
        if not path:
            return False  # Si path es None o vacío, devuelve False
        
        full_path = self.get_media_path(path)
        return os.path.isfile(full_path)


