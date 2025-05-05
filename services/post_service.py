import os
from fastapi import HTTPException
from utils.json_utils import JSONHandler
from utils.file_utils import FileHandler
from services.image.image_service import ImageServiceHandler
from services.files.remote_upload_service import RemoteUploadService

class PostService:
    def __init__(self):
        self.json_handler = JSONHandler(os.getenv("POSTS_JSON_FILE"))
        self.file_handler = FileHandler()
        self.image_service_handler = ImageServiceHandler()
        self.upload_service = RemoteUploadService()

    async def get_next_post(self, status_key = "status", status_value = "not_posted"):
        data = await self.json_handler.load_json()
        if not data:
            return None

        for post in data["posts"]:
            if post[status_key] == status_value:
                return post
        return None

    async def update_post_status(self, post_id, status="posted", status_key = "status"):
        data = await self.json_handler.load_json()
        if not data:
            return

        for post in data["posts"]:
            if post["id"] == post_id:
                post[status_key] = status
                break

        await self.json_handler.save_json(data)

    async def update_post_media_path(self, post_id, media_path):
        data = await self.json_handler.load_json()
        if not data:
            return

        for post in data["posts"]:
            if post["id"] == post_id:
                post["media_path"] = media_path
                break

        await self.json_handler.save_json(data)

    async def update_background_path(self, post_id, background_path):
        data = await self.json_handler.load_json()
        if not data:
            return

        for post in data["posts"]:
            if post["id"] == post_id:
                post["metadata_to_media"]["background"] = background_path
                break

        await self.json_handler.save_json(data)

    async def delete_background_image(self, post_id, background_path):
        data = await self.json_handler.load_json()
        if not data:
            return

        for post in data["posts"]:
            if post["id"] == post_id:
                if os.path.exists(background_path):
                    os.remove(background_path)
                    post["metadata_to_media"]["background"] = ""
                break

        await self.json_handler.save_json(data)

    async def save_updated_post(self, post_data):
        if not post_data:
            return

        json_data = await self.json_handler.load_json()
        if "posts" not in json_data:
            json_data["posts"] = []

        for i, existing_post in enumerate(json_data["posts"]):
            if existing_post["id"] == post_data["id"]:
                json_data["posts"][i] = post_data
                break
        else:
            json_data["posts"].append(post_data)

        await self.json_handler.save_json(json_data)

    async def preprocess_post_data(self, post_data):
        if not post_data:
            return None

        async def process_single(data, base_id=None, thread_index=None):
            if len(data["x_content"]) > 280:
                raise HTTPException(status_code=400, detail="Content too long")
            
            if len(data["ig_content"]) > 2200:
                raise HTTPException(status_code=400, detail="Instagram content too long")
            
            if len(data["fb_content"]) > 63206:
                raise HTTPException(status_code=400, detail="Facebook content too long")

            if base_id and thread_index is not None:
                data["id"] = base_id * 100000 + (thread_index + 1)

            if data.get("media_path"):
                data["media_path"] = self.file_handler.get_media_path(data["media_path"])

                if not data.get("media_path_remote"):
                    remote_url = self.upload_service.upload_file(data["media_path"])
                    data["media_path_remote"] = remote_url

            elif data.get("prompt_to_media"):
                file_data = await self.image_service_handler.generate_media_by_prompt(data["prompt_to_media"], data["id"])
                if file_data:
                    data["media_path"] = file_data["full_path"]
                    await self.update_post_media_path(data["id"], file_data["relative_path"])

                    if not data.get("media_path_remote"):
                        remote_url = self.upload_service.upload_file(data["media_path"])
                        data["media_path_remote"] = remote_url

            elif data.get("metadata_to_media"):
                if data["metadata_to_media"].get("prompt_to_background") and not data["metadata_to_media"].get("background"):
                    bg_file = await self.image_service_handler.generate_media_by_prompt(
                        data["metadata_to_media"]["prompt_to_background"], data["id"], "background.png", "background"
                    )
                    if bg_file:
                        data["metadata_to_media"]["background"] = bg_file["full_path"]
                        await self.update_background_path(data["id"], bg_file["relative_path"])

                img_file = await self.image_service_handler.generate_image(
                    data["metadata_to_media"], data["id"], data.get("theme", "light")
                )
                if img_file:
                    data["media_path"] = img_file["full_path"]
                    await self.update_post_media_path(data["id"], img_file["relative_path"])

                    if not data.get("media_path_remote"):
                        remote_url = self.upload_service.upload_file(data["media_path"])
                        data["media_path_remote"] = remote_url

                if data["metadata_to_media"].get("background"):
                    await self.delete_background_image(data["id"], data["metadata_to_media"]["background"])
                    data["metadata_to_media"]["background"] = ""

            return data

        post_data = await process_single(post_data)
        if not post_data:
            return None

        if post_data.get("is_thread") and post_data.get("threads"):
            base_id = post_data["id"]
            processed_threads = []
            for idx, thread in enumerate(post_data["threads"]):
                processed = await process_single(thread, base_id, idx)
                if processed:
                    processed_threads.append(processed)
            post_data["threads"] = processed_threads

        return post_data
    
    async def process_posts(self):
        post_data = await self.get_next_post("is_processed", False)
        if not post_data:
            return None

        post_data = await self.preprocess_post_data(post_data)
        if not post_data:
            return None

        post_data["is_processed"] = True
        await self.save_updated_post(post_data)
        return post_data
