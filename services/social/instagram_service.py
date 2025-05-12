import os
import requests
from fastapi import HTTPException
from dotenv import load_dotenv

from services.post.post_service import PostService
from utils.path_utils import get_public_image_url

KEY_CONTENT = "meta_content"

class InstagramAPI:
    def __init__(self):
        load_dotenv()
        self.api_url = os.getenv("INSTAGRAM_API", "https://graph.instagram.com/v21.0")
        self.access_token = os.getenv("IG_ACCESS_TOKEN").strip()
        self.instagram_account_id = os.getenv("IG_ACCOUNT_ID")
        self.allow_posting = os.getenv("ALLOW_POSTING", "false").lower() == "true"

        self.post_service = PostService()

    async def get_user_data(self):
        url = f'{self.api_url}/{self.instagram_account_id}?fields=username&access_token={self.access_token}'
        response = requests.get(url)
        return response.json()

    async def single(self, caption, media_path):
        """Publishes a single image post to Instagram"""

        if not self.allow_posting:
            raise HTTPException(status_code=403, detail="Posting is disabled by configuration.")

        if media_path.startswith("http://") or media_path.startswith("https://"):
            image_url = media_path
        else:
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
        print(f"✅ Instagram: Post published successfully: {post_id}")

        return {
            "message": "Instagram post published successfully",
            "post_id": post_id
        }
    
    async def carousel(self, caption, media_paths):
        print(f"Publishing carousel with caption: {caption}")
        print(f"Media paths: {media_paths}")
        """Publishes a carousel (multi-image post) to Instagram"""

        if not self.allow_posting:
            raise HTTPException(status_code=403, detail="Posting is disabled by configuration.")

        # Filter out empty paths
        media_paths = [p for p in media_paths if p]
        if len(media_paths) < 2:
            raise HTTPException(status_code=400, detail="Carousel needs at least 2 media items")

        if len(media_paths) > 10:
            print("⚠️ Limiting carousel to 10 items")
            media_paths = media_paths[:10]

        children_ids = []

        for media_path in media_paths:
            if media_path.startswith("http://") or media_path.startswith("https://"):
                image_url = media_path
            else:
                image_url = get_public_image_url(media_path)

            print(f"Image URL: {image_url}")

            if not image_url:
                print(f"⚠️ Skipping empty or invalid media path: {media_path}")
                continue

            print(f"⬆ Uploading image for carousel: {image_url}")

            media_url = f"{self.api_url}/{self.instagram_account_id}/media"
            media_payload = {
                "image_url": image_url,
                "is_carousel_item": True,
                "access_token": self.access_token
            }

            try:
                media_response = requests.post(media_url, data=media_payload)
                media_data = media_response.json()

                if media_response.status_code != 200 or 'id' not in media_data:
                    print(f"❌ Failed to create carousel item: {media_data}")
                    continue

                creation_id = media_data['id']
                print(f"✅ Carousel media container created: {creation_id}")
                children_ids.append(creation_id)

            except Exception as e:
                print(f"❌ Exception uploading media: {e}")
                continue

        if not children_ids:
            raise HTTPException(status_code=500, detail="No valid carousel items created")

        # Step 2: Create the carousel container
        carousel_url = f"{self.api_url}/{self.instagram_account_id}/media"
        carousel_payload = {
            "caption": caption,
            "media_type": "CAROUSEL",
            "children": children_ids,
            "access_token": self.access_token
        }

        carousel_response = requests.post(
            carousel_url,
            json=carousel_payload
        )
        carousel_data = carousel_response.json()

        if carousel_response.status_code != 200 or 'id' not in carousel_data:
            raise HTTPException(status_code=500, detail=f"Error creating carousel container: {carousel_data}")

        carousel_id = carousel_data['id']
        print(f"✅ Carousel container created: {carousel_id}")

        # Step 3: Publish the carousel
        publish_url = f"{self.api_url}/{self.instagram_account_id}/media_publish"
        publish_payload = {
            "creation_id": carousel_id,
            "access_token": self.access_token
        }

        publish_response = requests.post(publish_url, data=publish_payload)
        publish_data = publish_response.json()

        if publish_response.status_code != 200 or 'id' not in publish_data:
            raise HTTPException(status_code=500, detail=f"Error publishing carousel: {publish_data}")

        post_id = publish_data['id']
        print(f"✅ Instagram: Carousel published successfully: {post_id}")

        return {
            "message": "Instagram carousel published successfully",
            "post_id": post_id
        }

    def combine_captions(self, main_caption, threads, links=None, hashtags=None):
        """
        Combina el caption principal, los captions de los threads, los links y hashtags,
        evitando duplicar hashtags que ya aparezcan en los textos.
        """
        captions = [main_caption.strip()] if main_caption else []
        existing_text = (main_caption or "").lower()
        all_hashtags = set(tag.lstrip('#').lower() for tag in hashtags or [])

        # Recorrer threads y acumular captions, links y hashtags
        for t in threads:
            thread_caption = t.get(KEY_CONTENT, "").strip()
            thread_links = t.get("ig_links", [])
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
        """Main function to process and publish posts"""
        if not self.allow_posting:
            raise HTTPException(status_code=403, detail="Posting is disabled by configuration.")

        post_data = await self.post_service.get_next_post('ig_status', 'not_posted', extra_filters={'is_processed': True})

        if not post_data:
            raise HTTPException(status_code=404, detail="No Instagram posts found to publish.")

        caption = post_data.get(KEY_CONTENT)
        media_path = post_data.get("media_path_remote") or post_data.get("media_path")
        is_carousel = post_data.get("is_thread")
        threads = post_data.get("threads")
        links = post_data.get("ig_links", [])
        hashtags = post_data.get("hashtags", [])

        if is_carousel:
            thread_media_paths = [
                t.get("media_path_remote") or t.get("media_path")
                for t in threads
                if t.get("media_path_remote") or t.get("media_path")
            ]

            media_paths = [media_path] + thread_media_paths
            combined_caption = self.combine_captions(caption, threads, links, hashtags)

            result = await self.carousel(combined_caption, media_paths)
        else:
            combined_caption = self.combine_captions(caption, [], links, hashtags)
            result = await self.single(combined_caption, media_path)

        await self.post_service.update_post_status(post_data["id"], status_key="ig_status")
        return result
