import json
import os
import aiofiles
from utils.base_utils import get_path_from_base

class JSONHandler:
    async def load_json(self, json_filename):
        """Asynchronously loads the JSON file"""
        json_path = get_path_from_base("json", json_filename)
        if os.path.exists(json_path):
            async with aiofiles.open(json_path, "r", encoding="utf-8") as file:
                content = await file.read()
                return json.loads(content)
        return None

    async def save_json(self, data, json_filename):
        """Asynchronously saves the JSON file"""
        json_path = get_path_from_base("json", json_filename)
        async with aiofiles.open(json_path, "w", encoding="utf-8") as file:
            await file.write(json.dumps(data, indent=4, ensure_ascii=False))