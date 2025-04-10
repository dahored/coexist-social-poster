import os
import shutil

class FileHandler:
    def __init__(self):
        self.images_path = "../public/uploads/images"
        self.full_images_path = self.get_file_path(self.images_path)
        
    def get_file_path(self, file_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, file_path)  
    
    def move_temp_file_to_folder(self, temp_file_path, tweet_id):
        """Moves a temporary file to a specific folder and renames it to tweet_{id}.extension"""

        # Check if the file exists
        temp_file_path = self.get_file_path(temp_file_path)  

        if not os.path.exists(temp_file_path):
            print(f"The file {temp_file_path} does not exist.")
            return None
        
        type_file = self.get_type_file(temp_file_path)
        # print(f"File type: {type_file}")

        if type_file in [".jpg", ".png", ".jpeg"]:
            # Create the new filename
            new_filename = f"image_file_tweet_{tweet_id}{type_file}"
            destination_path = os.path.join(self.full_images_path, new_filename)

            # Move and rename the file
            # os.rename(temp_file_path, destination_path)
            shutil.copy2(temp_file_path, destination_path)
            print(f"File moved and renamed to {destination_path}")

            return {
                "filename": new_filename,
                "full_path": destination_path,
                "path": self.images_path,
                "relative_path": os.path.join(self.images_path, new_filename),
            }  # Returns the new path in case it's needed
        else:
            print(f"The file {temp_file_path} is not a valid image.")
            return None

    def get_media_path(self, media_path):
        """Checks if the file exists and is valid"""
        media_path = self.get_file_path(media_path)  
        
        if not os.path.exists(media_path):
            print(f"The file {media_path} does not exist.")
            return None
        else:
            return media_path
        
    def get_type_file(self, file_path):
        """Returns the file type"""
        _, file_extension = os.path.splitext(file_path)
        return file_extension
        
    async def generate_media_by_prompt(self, prompt, tweet_id):
        """Generates a file from a prompt"""
        print(f"Generating file from prompt: {prompt}")
        # The logic to generate a file from the prompt would go here
        # For now, just return an example path
        file_path = "../public/uploads/temps/temp.png"
        file_data = self.move_temp_file_to_folder(file_path, tweet_id)
        
        return file_data if file_data else None