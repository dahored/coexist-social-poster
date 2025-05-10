import os
from fastapi import HTTPException
from utils.json_utils import JSONHandler
from utils.file_utils import FileHandler
from services.image.image_service import ImageServiceHandler
from services.files.remote_upload_service import RemoteUploadService

POST_JSON_FILE = os.getenv("POSTS_JSON_FILE")

class PostService:
    def __init__(self):
        self.json_handler = JSONHandler()
        self.file_handler = FileHandler()
        self.image_service_handler = ImageServiceHandler()
        self.upload_service = RemoteUploadService()

    async def get_next_post(self, status_key="status", status_value="not_posted", extra_filters=None, json_file=POST_JSON_FILE):
        data = await self.json_handler.load_json(json_file)
        if not data:
            return None

        for post in data["posts"]:
            if post[status_key] == status_value:
                if extra_filters:
                    if all(post.get(k) == v for k, v in extra_filters.items()):
                        return post
                else:
                    return post
        return None

    async def update_post_status(self, post_id, status="posted", status_key = "status", json_file=POST_JSON_FILE):
        data = await self.json_handler.load_json(json_file)
        if not data:
            return

        for post in data["posts"]:
            if post["id"] == post_id:
                post[status_key] = status
                break

        await self.json_handler.save_json(data, json_file)

    async def save_updated_post(self, post_data, json_file=POST_JSON_FILE):
        if not post_data:
            return
        json_data = await self.json_handler.load_json(json_file)
        if "posts" not in json_data:
            json_data["posts"] = []
        for i, existing_post in enumerate(json_data["posts"]):
            if existing_post["id"] == post_data["id"]:
                json_data["posts"][i] = post_data
                break
        else:
            json_data["posts"].append(post_data)
        await self.json_handler.save_json(json_data, json_file)

   
