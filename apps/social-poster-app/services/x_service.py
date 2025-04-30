import tweepy
import os
from fastapi import HTTPException
from dotenv import load_dotenv

from services.post_service import PostService
from utils.json_utils import JSONHandler
from utils.file_utils import FileHandler
from services.image_generator import ImageGeneratorHandler

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

        self.file_handler = FileHandler()
        self.json_handler = JSONHandler(os.getenv("POSTS_JSON_FILE"))
        self.image_generator_handler = ImageGeneratorHandler()
        self.post_service = PostService()

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

    def get_thread_list(self, threads):
        return [(thread["content"], thread["media_path"]) for thread in threads]

    async def run_posts(self):
        tweet_data = await self.post_service.get_next_post('x_status')
        if not tweet_data:
            raise HTTPException(status_code=404, detail="No tweets to post.")

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

        await self.post_service.update_post_status(tweet_data["id"], status_key="x_status")
        return result
