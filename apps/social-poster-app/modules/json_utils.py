import json
import os
import aiofiles

class JSONHandler:
    def __init__(self, json_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, json_path)  
        self.json_path = json_path

    async def load_json(self):
        """Carga el archivo JSON de manera asíncrona"""
        if os.path.exists(self.json_path):
            async with aiofiles.open(self.json_path, "r", encoding="utf-8") as file:
                content = await file.read()
                return json.loads(content)
        return None

    async def save_json(self, data):
        """Guarda el archivo JSON de manera asíncrona"""
        async with aiofiles.open(self.json_path, "w", encoding="utf-8") as file:
            await file.write(json.dumps(data, indent=4, ensure_ascii=False))
