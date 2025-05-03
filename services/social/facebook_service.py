import os
import requests
from fastapi import HTTPException
from dotenv import load_dotenv

from services.post_service import PostService
from utils.json_utils import JSONHandler
from utils.file_utils import FileHandler
from utils.path_utils import get_public_image_url


class FacebookAPI:
    def __init__(self):
        load_dotenv()
        self.api_url = os.getenv("FACEBOOK_API", "https://graph.facebook.com/v18.0")
        self.access_token = os.getenv("META_ACCESS_TOKEN", "FB_ACCESS_TOKEN").strip()
        self.page_id = os.getenv("FB_PAGE_ID")
        self.allow_posting = os.getenv("ALLOW_POSTING", "false").lower() == "true"

        self.file_handler = FileHandler()
        self.json_handler = JSONHandler(os.getenv("POSTS_JSON_FILE"))
        self.post_service = PostService()

    async def get_user_data(self):
        url = f'{self.api_url}/{self.page_id}?fields=name,username,about&access_token={self.access_token}'
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Error fetching user data: {data}")

        return data
    
    async def get_page_access_token(self):
        url = f"{self.api_url}/me/accounts?access_token={self.access_token}"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            raise Exception(f"Error fetching page access tokens: {data}")

        for page in data.get("data", []):
            print(f"Page: {page['name']} ({page['id']})")
            print(f"Access Token: {page['access_token']}")
            print("---------------")

        return data.get("data", [])

    async def post_photo(self, message, media_path):
        """Posts a single photo to Facebook Page"""

        if not self.allow_posting:
            raise HTTPException(status_code=403, detail="Posting is disabled by configuration.")

        if media_path.startswith("http://") or media_path.startswith("https://"):
            image_url = media_path
        else:
            image_url = get_public_image_url(media_path)
        print(f"Facebook image URL: {image_url}")

        post_url = f"{self.api_url}/{self.page_id}/photos"
        payload = {
            "url": image_url,
            "caption": message,
            "access_token": self.access_token
        }

        response = requests.post(post_url, data=payload)
        data = response.json()

        if response.status_code != 200 or 'id' not in data:
            raise HTTPException(status_code=500, detail=f"Error posting photo: {data}")

        photo_id = data['id']
        post_id = data.get('post_id')  # Safe: might be missing

        print(f"✅ Photo posted successfully: photo_id={photo_id}, post_id={post_id}")

        return {
            "message": "Facebook photo posted successfully",
            "photo_id": photo_id,
            "post_id": post_id
        }

    async def post_album(self, message, media_paths):
        """Posts an album (multiple photos) to Facebook Page"""

        if not self.allow_posting:
            raise HTTPException(status_code=403, detail="Posting is disabled by configuration.")

        media_paths = [p for p in media_paths if p]
        if len(media_paths) < 2:
            raise HTTPException(status_code=400, detail="Album needs at least 2 media items")

        children_ids = []

        for media_path in media_paths:
            image_url = media_path if media_path.startswith("http") else get_public_image_url(media_path)
            print(f"⬆ Uploading photo to album: {image_url}")

            post_url = f"{self.api_url}/{self.page_id}/photos"
            payload = {
                "url": image_url,
                "published": False,  # Upload without publishing immediately
                "access_token": self.access_token
            }

            response = requests.post(post_url, data=payload)
            data = response.json()

            if response.status_code != 200 or 'id' not in data:
                print(f"❌ Failed to upload photo: {data}")
                continue

            children_ids.append(data['id'])
            print(f"✅ Uploaded photo for album: {data['id']}")

        if not children_ids:
            raise HTTPException(status_code=500, detail="No valid album items created")

        # Step 2: Create album (as a post)
        album_url = f"{self.api_url}/{self.page_id}/feed"
        payload = {
            "message": message,
            "attached_media": [{"media_fbid": id} for id in children_ids],
            "access_token": self.access_token
        }

        response = requests.post(album_url, json=payload)
        data = response.json()

        if response.status_code != 200 or 'id' not in data:
            raise HTTPException(status_code=500, detail=f"Error posting album: {data}")

        print(f"✅ Album posted successfully: {data['id']}")
        return {"message": "Facebook album posted successfully", "post_id": data["id"]}

    def combine_captions(self, main_caption, threads):
        captions = [main_caption.strip()] if main_caption else []
        for t in threads:
            thread_caption = t.get("content", "").strip()
            if thread_caption:
                captions.append(thread_caption)
        return "\n\n".join(captions)

    async def run_posts(self):
        if not self.allow_posting:
            raise HTTPException(status_code=403, detail="Posting is disabled by configuration.")

        post_data = await self.post_service.get_next_post('fb_status')
        if not post_data:
            raise HTTPException(status_code=404, detail="No Facebook posts found to publish.")

        caption = post_data.get("content")
        media_path = post_data.get("media_path_remote") or post_data.get("media_path")
        is_album = post_data.get("is_thread")
        threads = post_data.get("threads")

        if is_album:
            thread_media_paths = [
                t.get("media_path_remote") or t.get("media_path")
                for t in threads
                if t.get("media_path_remote") or t.get("media_path")
            ]
            media_paths = [media_path] + thread_media_paths
            combined_caption = self.combine_captions(caption, threads)
            result = await self.post_album(combined_caption, media_paths)
        else:
            result = await self.post_photo(caption, media_path)

        await self.post_service.update_post_status(post_data["id"], status_key="fb_status")
        return result
