import os
import requests
from fastapi import HTTPException
from dotenv import load_dotenv

from services.post.post_service import PostService
from utils.path_utils import get_public_image_url

KEY_CONTENT = "meta_content"

class FacebookAPI:
    def __init__(self):
        load_dotenv()
        self.api_url = os.getenv("FACEBOOK_API", "https://graph.facebook.com/v18.0")
        self.access_token = os.getenv("META_ACCESS_TOKEN", "FB_ACCESS_TOKEN").strip()
        self.page_id = os.getenv("FB_PAGE_ID")
        self.allow_posting = os.getenv("ALLOW_POSTING", "false").lower() == "true"

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
        post_id = data.get('post_id')

        print(f"✅ Facebook: Photo posted successfully: photo_id={photo_id}, post_id={post_id}")

        return {"message": "Facebook photo posted successfully", "photo_id": photo_id, "post_id": post_id}

    async def post_album(self, message, media_paths):
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
                "published": False,
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

        print(f"✅ Facebook: Album posted successfully: {data['id']}")
        return {"message": "Facebook album posted successfully", "post_id": data["id"]}

    def combine_captions(self, main_caption, threads, links=None, hashtags=None):
        """
        Combines the main caption with thread captions, links, and hashtags,
        avoiding duplicate hashtags already present in the captions.
        """
        captions = [main_caption.strip()] if main_caption else []
        existing_text = (main_caption or "").lower()
        all_hashtags = set(tag.lstrip('#').lower() for tag in hashtags or [])

        # Recolectar captions, links y hashtags de threads
        for t in threads:
            thread_caption = t.get(KEY_CONTENT, "").strip()
            thread_links = t.get("fb_links", [])
            thread_hashtags = t.get("hashtags", [])

            if thread_caption:
                captions.append(thread_caption)
                existing_text += " " + thread_caption.lower()

            if thread_links:
                links_block = "\n".join(f"{link['description']}: {link['url']}" for link in thread_links)
                captions.append(links_block)

            if thread_hashtags:
                all_hashtags.update(tag.lstrip('#').lower() for tag in thread_hashtags)

        if links:
            root_links_block = "\n".join(f"{link['description']}: {link['url']}" for link in links)
            captions.append(root_links_block)

        # Filtrar hashtags ya presentes en los textos
        unique_hashtags = []
        for tag in all_hashtags:
            hashtag_with_hash = f"#{tag}"
            if hashtag_with_hash not in existing_text:
                unique_hashtags.append(hashtag_with_hash)

        if unique_hashtags:
            hashtags_block = " ".join(unique_hashtags)
            captions.append(hashtags_block)

        return "\n\n".join(captions)

    async def run_posts(self):
        if not self.allow_posting:
            raise HTTPException(status_code=403, detail="Posting is disabled by configuration.")

        post_data = await self.post_service.get_next_post('fb_status', 'not_posted', extra_filters={'is_processed': True})

        if not post_data:
            raise HTTPException(status_code=404, detail="No Facebook posts found to publish.")

        caption = post_data.get(KEY_CONTENT)
        media_path = post_data.get("media_path_remote") or post_data.get("media_path")
        is_album = post_data.get("is_thread")
        threads = post_data.get("threads")
        links = post_data.get("fb_links", [])
        hashtags = post_data.get("hashtags", [])

        if is_album:
            thread_media_paths = [
                t.get("media_path_remote") or t.get("media_path")
                for t in threads
                if t.get("media_path_remote") or t.get("media_path")
            ]
            media_paths = [media_path] + thread_media_paths
            combined_caption = self.combine_captions(caption, threads, links, hashtags)
            result = await self.post_album(combined_caption, media_paths)
        else:
            combined_caption = self.combine_captions(caption, [], links, hashtags)
            result = await self.post_photo(combined_caption, media_path)

        await self.post_service.update_post_status(post_data["id"], status_key="fb_status")
        return result
