import os
import requests
from fastapi import HTTPException
from dotenv import load_dotenv

from services.post_service import PostService
from utils.json_utils import JSONHandler
from utils.file_utils import FileHandler
from utils.path_utils import get_public_image_url


class InstagramAPI:
    def __init__(self):
        load_dotenv()
        self.api_url = os.getenv("INSTAGRAM_API")
        self.access_token = os.getenv("IG_ACCESS_TOKEN").strip()
        self.instagram_account_id = os.getenv("IG_ACCOUNT_ID")
        self.allow_posting = os.getenv("ALLOW_POSTING", "false").lower() == "true"

        self.file_handler = FileHandler()
        self.json_handler = JSONHandler(os.getenv("POSTS_JSON_FILE"))
        self.post_service = PostService()

    async def get_user_data(self):
        print(f"Loaded token: {self.access_token}")
        url = f'{self.api_url}/{self.instagram_account_id}?fields=username&access_token={self.access_token}'
        response = requests.get(url)
        return response.json()

    async def single(self, caption, media_path):
        """Publishes a single image post to Instagram"""

        if not self.allow_posting:
            raise HTTPException(status_code=403, detail="Posting is disabled by configuration.")

        image_url = get_public_image_url(media_path)
        print(f"Image URL: {image_url}")

        media_url = f"{self.api_url}/{self.instagram_account_id}/media"
        media_payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }

        media_response = requests.post(media_url, data=media_payload)
        media_data = media_response.json()

        if media_response.status_code != 200 or 'id' not in media_data:
            raise HTTPException(status_code=500, detail=f"Error creating media container: {media_data}")

        creation_id = media_data['id']
        print(f"✅ Media container created: {creation_id}")

        # Step 2: Publish the post
        publish_url = f"{self.api_url}/{self.instagram_account_id}/media_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": self.access_token
        }

        publish_response = requests.post(publish_url, data=publish_payload)
        publish_data = publish_response.json()

        if publish_response.status_code != 200 or 'id' not in publish_data:
            raise HTTPException(status_code=500, detail=f"Error publishing post: {publish_data}")

        post_id = publish_data['id']
        print(f"✅ Post published successfully: {post_id}")

        return {
            "message": "Instagram post published successfully",
            "post_id": post_id
        }

    async def run_posts(self):
        """Main function to process and publish posts"""
        if not self.allow_posting:
            raise HTTPException(status_code=403, detail="Posting is disabled by configuration.")

        post_data = await self.post_service.get_next_post('ig_status')
        if not post_data:
            raise HTTPException(status_code=404, detail="No Instagram posts found to publish.")

        caption = post_data.get("content")
        media_path = post_data.get("media_path")
        is_carousel = post_data.get("is_thread")
        threads = post_data.get("threads")

        if is_carousel:
            # Placeholder: Implement carousel publishing here
            pass
        else:
            result = await self.single(caption, media_path)

        await self.post_service.update_post_status(post_data["id"], status_key="ig_status")
        return result
