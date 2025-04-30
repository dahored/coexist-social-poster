import os
import shutil

from utils.path_utils import get_path_from_base
from services.image_service import ImageServiceHandler

from config.image_config import (
    IMAGES_DIR,
)


class FileHandler:
    def __init__(self):
        self.images_path = IMAGES_DIR
        self.image_service_handler = ImageServiceHandler()

    def get_file_path(self, relative_path):
        return get_path_from_base(relative_path)

    def move_temp_file_to_folder(self, temp_file_path, id, other_name=""):
        if not os.path.exists(temp_file_path):
            print(f"The file {temp_file_path} does not exist.")
            return None

        type_file = self.get_type_file(temp_file_path)

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

    async def generate_media_by_prompt(self, prompt, id, temp_file_name="temp.png", other_name=""):
        print(f"Generating file from prompt: {prompt}")
        temp_file_path = await self.image_service_handler.generate_image_from_prompt(prompt, temp_file_name)
        return self.move_temp_file_to_folder(temp_file_path, id, other_name)

