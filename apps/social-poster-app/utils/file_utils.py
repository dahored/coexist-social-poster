import os
import shutil
from utils.path_utils import get_path_from_base


class FileHandler:
    def __init__(self):
        # Define the uploads folder and its subfolders using the path helper
        self.uploads_dir = get_path_from_base("public", "uploads")
        self.images_path = os.path.join(self.uploads_dir, "images")
        self.temps_path = os.path.join(self.uploads_dir, "temps")

    def get_file_path(self, relative_path):
        """Returns an absolute path relative to the project root (index.py)"""
        return get_path_from_base(relative_path)

    def move_temp_file_to_folder(self, temp_file_path, tweet_id):
        """Moves a temporary file to the images folder and renames it to tweet_{id}.extension"""

        temp_file_path = os.path.join(self.temps_path, os.path.basename(temp_file_path))

        if not os.path.exists(temp_file_path):
            print(f"The file {temp_file_path} does not exist.")
            return None

        type_file = self.get_type_file(temp_file_path)

        if type_file in [".jpg", ".png", ".jpeg"]:
            new_filename = f"image_file_tweet_{tweet_id}{type_file}"
            destination_path = os.path.join(self.images_path, new_filename)

            shutil.copy2(temp_file_path, destination_path)
            print(f"File moved and renamed to {destination_path}")

            return {
                "filename": new_filename,
                "full_path": destination_path,
                "path": self.images_path,
                "relative_path": os.path.join("public", "uploads", "images", new_filename),
            }
        else:
            print(f"The file {temp_file_path} is not a valid image.")
            return None

    def get_media_path(self, media_path):
        """Checks if the file exists and is valid"""
        absolute_path = self.get_file_path(media_path)

        if not os.path.exists(absolute_path):
            print(f"The file {absolute_path} does not exist.")
            return None
        return absolute_path

    def get_type_file(self, file_path):
        """Returns the file type/extension"""
        _, file_extension = os.path.splitext(file_path)
        return file_extension

    async def generate_media_by_prompt(self, prompt, tweet_id):
        """Generates a file from a prompt"""
        print(f"Generating file from prompt: {prompt}")
        
        # Simulated generated file
        temp_file = os.path.join(self.temps_path, "temp.png")
        return self.move_temp_file_to_folder(temp_file, tweet_id)
