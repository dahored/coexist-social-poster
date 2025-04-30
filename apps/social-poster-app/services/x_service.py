import tweepy
import os
from utils.json_utils import JSONHandler
from utils.file_utils import FileHandler
from services.image_generator import ImageGeneratorHandler
from dotenv import load_dotenv
from fastapi import HTTPException

class XAPI:
    def __init__(self):
        """Loads credentials from .env and initializes the API"""
        load_dotenv()
        consumer_key = os.getenv("X_CONSUMER_KEY")
        consumer_secret = os.getenv("X_CONSUMER_SECRET")
        access_token = os.getenv("X_ACCESS_TOKEN")
        access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

        self.allow_posting = os.getenv("X_ALLOW_POSTING", "false").lower() == "true"

        self.client = tweepy.Client(
            consumer_key=consumer_key, 
            consumer_secret=consumer_secret,
            access_token=access_token, 
            access_token_secret=access_token_secret
        )

        self.auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
        self.api = tweepy.API(self.auth)
        
        self.json_handler = JSONHandler(os.getenv("POSTS_JSON_FILE"))
        self.file_handler = FileHandler()
        self.image_generator_handler = ImageGeneratorHandler()

    def upload_media_tweet(self, media_path):
        """Uploads an image and returns its ID"""
        media = self.api.media_upload(media_path)
        return media.media_id

    async def post_tweet(self, message, media_path=None, in_reply_to_tweet_id=None):
        """Posts a single tweet with or without an image"""
        if not self.allow_posting:
            raise HTTPException(status_code=403, detail="Posting is disabled by config.")

        media_id = self.upload_media_tweet(media_path) if media_path else None
        result = self.client.create_tweet(
            text=message, 
            media_ids=[media_id] if media_id else None, 
            in_reply_to_tweet_id=in_reply_to_tweet_id
        )
        return {"message": "Tweet posted successfully", "tweet_id": result.data["id"]}

    async def post_thread(self, tweets):
        """Posts a thread of tweets with optional images"""
        if not tweets:
            raise HTTPException(status_code=400, detail="The thread is empty.")

        if not self.allow_posting:
            raise HTTPException(status_code=403, detail="Thread posting is disabled by config.")

        first_text, first_media = tweets[0]
        first_response = await self.post_tweet(first_text, first_media)
        tweet_id = first_response["tweet_id"]

        for text, media in tweets[1:]:
            response = await self.post_tweet(text, media, in_reply_to_tweet_id=tweet_id)
            tweet_id = response["tweet_id"]

        return {"message": "Thread posted successfully", "thread_root_id": first_response["tweet_id"]}

    async def update_status_to_post_json(self, post_id):
        data = await self.json_handler.load_json()
        if not data:
            return

        for post in data["posts"]:
            if post["id"] == post_id:
                post["status"] = "posted"
                break

        await self.json_handler.save_json(data)

    async def update_media_path_in_json(self, post_id, media_path):
        data = await self.json_handler.load_json()
        if not data:
            return

        for post in data["posts"]:
            if post["id"] == post_id:
                post["media_path"] = media_path
                break

        await self.json_handler.save_json(data)

    async def update_background_path_in_json(self, post_id, background_path):
        data = await self.json_handler.load_json()
        if not data:
            return

        for post in data["posts"]:
            if post["id"] == post_id:
                post["metadata_to_media"]["background"] = background_path
                break

        await self.json_handler.save_json(data)

    async def delete_background_image_and_json(self, post_id, background_path):
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
        if os.path.exists(background_path):
            os.remove(background_path)

    async def save_tweet_data_to_json(self, tweet_data):
        if not tweet_data:
            return
        
        json_data = await self.json_handler.load_json()
        if "posts" not in json_data:
            json_data["posts"] = []

        for i, existing_tweet in enumerate(json_data["posts"]):
            if existing_tweet["id"] == tweet_data["id"]:
                json_data["posts"][i] = tweet_data
                break
        else:
            json_data["posts"].append(tweet_data)

        await self.json_handler.save_json(json_data)

    async def get_tweet_to_post(self):
        data = await self.json_handler.load_json()
        if not data:
            return None

        for post in data["posts"]:
            if post["status"] == "not_posted":
                return {
                    "id": post["id"],
                    "content": post["content"],
                    "prompt_to_media": post.get("prompt_to_media"),
                    "media_path": post["media_path"],
                    "hashtags": post["hashtags"],
                    "metadata_to_media": post["metadata_to_media"],
                    "status": post["status"],
                    "is_thread": post["is_thread"],
                    "theme": post["theme"],
                    "ai_content": post["ai_content"],
                    "threads": post["threads"],
                }

        return None

    def get_thread_list(self, threads):
        thread_list = []
        for thread in threads:
            thread_list.append((thread["content"], thread["media_path"]))
        return thread_list

    async def preprocess_tweet_data(self, tweet_data):
        if not tweet_data:
            return None

        async def process_single_tweet(data, base_id=None, thread_index=None):
            if len(data["content"]) > 280:
                raise HTTPException(status_code=400, detail=f"Tweet with ID {data.get('id', 'unknown')} exceeds 280 characters.")

            if base_id is not None and thread_index is not None:
                data["id"] = base_id * 100000 + (thread_index + 1)

            media_path = data.get("media_path")
            if media_path:
                data["media_path"] = self.file_handler.get_media_path(media_path)

            elif data.get("prompt_to_media"):
                file_data = await self.file_handler.generate_media_by_prompt(data["prompt_to_media"], data["id"])
                if file_data:
                    data["media_path"] = file_data.get("full_path")
                    await self.update_media_path_in_json(data["id"], file_data.get("relative_path"))

            elif data.get("metadata_to_media"):
                if data["metadata_to_media"].get("prompt_to_background") and not data["metadata_to_media"].get("background"):
                    file_data = await self.file_handler.generate_media_by_prompt(data["metadata_to_media"]["prompt_to_background"], data["id"], "background.png", "background")
                
                    if file_data:
                        data["metadata_to_media"]["background"] = file_data.get("full_path")
                        await self.update_background_path_in_json(data["id"], file_data.get("relative_path"))

                file_data = await self.image_generator_handler.generate_image(data["metadata_to_media"], data["id"], data["theme"])
                if file_data:
                    data["media_path"] = file_data.get("full_path")
                    await self.update_media_path_in_json(data["id"], file_data.get("relative_path"))
                
                if data["metadata_to_media"].get("background"):
                    await self.delete_background_image_and_json(data["id"], data["metadata_to_media"]["background"])
                    data["metadata_to_media"]["background"] = ""

            else:
                print(f"Tweet with ID {data.get('id', 'unknown')} doesn’t have media")

            return data

        tweet_data = await process_single_tweet(tweet_data)
        if tweet_data is None:
            return None

        if "threads" in tweet_data:
            base_id = tweet_data["id"]
            processed_threads = []

            for index, thread in enumerate(tweet_data["threads"]):
                processed_thread = await process_single_tweet(thread, base_id, index)
                if processed_thread:
                    processed_threads.append(processed_thread)

            tweet_data["threads"] = processed_threads

        return tweet_data

    async def run_posts(self):
        tweet_data = await self.get_tweet_to_post()
        if not tweet_data:
            raise HTTPException(status_code=404, detail="No tweets to post.")

        tweet_data = await self.preprocess_tweet_data(tweet_data)
        if not tweet_data:
            raise HTTPException(status_code=400, detail="Tweet data could not be preprocessed.")

        await self.save_tweet_data_to_json(tweet_data)

        tweet_text = tweet_data.get("content")
        media_path = tweet_data.get("media_path")
        is_thread = tweet_data.get("is_thread")
        threads = tweet_data.get("threads")

        if is_thread:
            first_tweet = (tweet_text, media_path)
            thread_list = self.get_thread_list(threads)
            threads_tweet = [first_tweet] + thread_list
            result = await self.post_thread(threads_tweet)
        else:
            result = await self.post_tweet(tweet_text, media_path)

        await self.update_status_to_post_json(tweet_data["id"])
        return result
