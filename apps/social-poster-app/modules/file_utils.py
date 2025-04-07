import os
import shutil
import aiohttp

class FileHandler:
    def __init__(self):
        print("FileHandler initialized")
        self.images_path = "../public/uploads/images"
        self.full_images_path = self.get_file_path(self.images_path)
        
    def get_file_path(self, file_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, file_path)  
        
    def move_temp_file_to_folder(self, temp_file_path, tweet_id):
        """Mueve un archivo temporal a una carpeta específica y lo renombra con tweet_{id}.extension"""

        # Verifica si el archivo existe
        temp_file_path = self.get_file_path(temp_file_path)  

        if not os.path.exists(temp_file_path):
            print(f"El archivo {temp_file_path} no existe.")
            return None
        
        type_file = self.get_type_file(temp_file_path)
        # print(f"Tipo de archivo: {type_file}")

        if type_file in [".jpg", ".png", ".jpeg"]:
            # Crear el nuevo nombre del archivo
            new_filename = f"image_file_tweet_{tweet_id}{type_file}"
            destination_path = os.path.join(self.full_images_path, new_filename)

            # Mover y renombrar el archivo
            # os.rename(temp_file_path, destination_path)
            shutil.copy2(temp_file_path, destination_path)
            print(f"Archivo movido y renombrado a {destination_path}")

            return {
                "filename": new_filename,
                "full_path": destination_path,
                "path": self.images_path,
                "relative_path": os.path.join(self.images_path, new_filename),
            }  # Devuelve la nueva ruta por si la necesitas
        else:
            print(f"El archivo {temp_file_path} no es una imagen válida.")
            return None

    def get_media_path(self, media_path):
        """Verifica si el archivo existe y es válido"""
        media_path = self.get_file_path(media_path)  
        
        if not os.path.exists(media_path):
            print(f"El archivo {media_path} no existe.")
            return None
        else:
            return media_path
        
    def get_type_file(self, file_path):
        """Devuelve el tipo de archivo"""
        _, file_extension = os.path.splitext(file_path)
        return file_extension
        
    async def generate_media_by_prompt(self, prompt, tweet_id):
        """Genera un archivo a partir de un prompt"""
        print(f"Generando archivo para el prompt: {prompt}")
        # Aquí iría la lógica para generar un archivo a partir del prompt
        # Por ahora, solo se devuelve una ruta de ejemplo
        file_path = "../public/uploads/temps/temp.png"
        file_data = self.move_temp_file_to_folder(file_path, tweet_id)
        
        return file_data if file_data else None

    
    

    