import json
import os
import aiofiles
from utils.path_utils import get_path_from_base

class JSONHandler:
    def __init__(self, json_filename):
        self.json_path = get_path_from_base("json", json_filename)
        print(f"JSON path: {self.json_path}")

    async def load_json(self):
        """Asynchronously loads the JSON file"""
        if os.path.exists(self.json_path):
            async with aiofiles.open(self.json_path, "r", encoding="utf-8") as file:
                content = await file.read()
                return json.loads(content)
        return None

    async def save_json(self, data):
        """Asynchronously saves the JSON file"""
        async with aiofiles.open(self.json_path, "w", encoding="utf-8") as file:
            await file.write(json.dumps(data, indent=4, ensure_ascii=False))