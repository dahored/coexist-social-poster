import os
import random
from utils.json_utils import JSONHandler
from utils.file_utils import FileHandler
from services.post.post_service import PostService
from services.ai.openai_service import OpenaiServiceHandler
from services.files.remote_upload_service import RemoteUploadService
from services.image.image_service import ImageServiceHandler

from utils.array_utils import split_array, join_array
from utils.string_utils import count_characters

SEQUENCE = [
    "prompt_to_media", #0
    "metadata_to_media", #1
    "prompt_to_media", #3
    "metadata_to_media", #4
    "metadata_to_media_with_background", #5
    "metadata_to_media" #6
]

class PostGeneratorService:
    def __init__(self):
        self.json_handler = JSONHandler()
        self.file_handler = FileHandler()
        self.post_service = PostService()
        self.image_service_handler = ImageServiceHandler()
        self.openai_service = OpenaiServiceHandler()
        self.upload_service = RemoteUploadService()


        self.processed_posts = []
        self.unprocessed_posts = []

    def get_base_post(self):
        return {
            "id": 0,
            "x_content": "",
            "meta_content": "",
            "prompt_to_media": "",
            "media_path": "",
            "media_path_remote": "",
            "default_phrase": "",
            "hashtags": [],
            "metadata_to_media": {
                "background_path": "",
                "prompt_to_background": "",
                "text": ""
            },
            "x_links": [],
            "ig_links": [],
            "fb_links": [],
            "theme": "",
        }

    async def get_current_id(self):
        data = await self.json_handler.load_json(os.getenv("APP_DATA_JSON_FILE"))

        if not data:
            return 0
        
        return data["posts_data"].get("consecutive_id", 0)
    
    def get_post_type(self, index):
        """
        Get the post type based on the index.
        - prompt_to_media
        - metadata_to_media
        - metadata_to_media_with_background
        """
        return SEQUENCE[index]

    def get_theme(self, new_id):
        theme = "light"
        if new_id % 2 == 0:
            theme = "dark"
        return theme

    def get_generated_threads(self, is_thread, parent_id=0, post_type="metadata_to_media"):
        """
        Get random generated threads for the post.
        """
        total_random_threads = random.randint(1, 5)
        if is_thread:
            threads = []
            for i in range(total_random_threads):
                base_post = self.get_base_post()
                thread_post = base_post.copy()

                thread_post["id"] = self.generate_thread_id(parent_id, i)
                thread_post["theme"] = self.get_theme(thread_post["id"])
                thread_post["post_type"] = post_type
                threads.append(thread_post)
            return threads

        return []


    async def get_unprocessed_posts_from_json(self):
        print("Loading unprocessed posts from JSON file...")
        data = await self.json_handler.load_json(os.getenv("UNPROCESSED_POSTS_JSON_FILE"))

        if not data:
            return None
        
        self.unprocessed_posts = data["posts"]
    
    async def get_generated_post(self, post, new_id, index = 0):
        """
        Process the post and return a new post object.
        """
        # Implement the logic to process the post
        base_post = self.get_base_post()
        processed_post = base_post.copy()
        post_type = self.get_post_type(index)

        processed_post["id"] = new_id
        processed_post["post_type"] = post_type
        processed_post["default_phrase"] = post["phrase"]
        processed_post["topic"] = post["topic"]
        processed_post["is_processed"] = False
        processed_post["x_status"] = "not_posted"
        processed_post["ig_status"] = "not_posted"
        processed_post["fb_status"] = "not_posted"
        processed_post["is_thread"] = post["is_thread"]
        processed_post["theme"] = self.get_theme(new_id)
        processed_post["ai_content"] = True
        processed_post["threads"] = self.get_generated_threads(post["is_thread"], new_id, post_type)
        processed_post["copied"] = False

        return processed_post

    async def process_posts(self):
        current_id = await self.get_current_id()

        index = 0

        for post in self.unprocessed_posts:
            new_post = await self.get_generated_post(post, current_id, index)
            current_id += 1
            index += 1
            if index >= len(SEQUENCE):
                index = 0
            self.processed_posts.append(new_post)

        await self.save_processed_posts_to_json()

    async def generate_posts(self):
        """
        Generate posts json with shcema of unprocessed posts.
        """
        # Implement the logic to generate posts
        await self.get_unprocessed_posts_from_json()
        await self.process_posts()

    async def generate_threads_content(self, post_data):
        """
        Generate threads content for a single post.
        """
        index = 0

        if post_data["is_thread"]:
            threads = post_data["threads"]
            for thread in threads:
                limit_default_phrase = os.getenv("DEFAULT_PHRASE_LIMIT", "250")

                prompt_default_phrase = f"Generate a phrase with the limit of {limit_default_phrase} characters and that this continues with the idea as thread"

                if(index == 0):
                    last_phrase = post_data["default_phrase"]
                else:
                    last_phrase = threads[index - 1]["default_phrase"]

                if not thread.get("default_phrase"):
                    thread["default_phrase"] = await self.openai_service.generate_default_phrase(last_phrase, limit_default_phrase, prompt_default_phrase)

                thread = await self.generate_data_post(thread, is_thread=True)

        return post_data

    async def generate_data_post(self, post_data, is_thread=False):
        """
        Generate data for a single post.
        """
        post_data = await self.generate_media_by_post_type(post_data)
        if not is_thread:
            post_data = await self.generate_post_hashtags(post_data)

        post_data = await self.generate_post_content(post_data, "x_content", is_thread)
        post_data = await self.generate_post_content(post_data, "meta_content", is_thread)

        if not is_thread:
            post_data = await self.generate_threads_content(post_data)

        return post_data

    async def process_existing_media(self, data):
        full_path = self.file_handler.get_media_path(data["media_path"])
        if not self.file_handler.file_exists(full_path):
            print(f"File {full_path} does not exist.")
            return False  # archivo no existe, necesita regeneración
        data["media_path"] = full_path
        if not data.get("media_path_remote"):
            remote_url = await self.upload_service.upload_file(data["media_path"])
            data["media_path_remote"] = remote_url
        return True
    
    async def generate_media_by_metadata_to_media(self, data):
        if data["metadata_to_media"].get("prompt_to_background") and not data["metadata_to_media"].get("background_path"):
            bg_file = await self.image_service_handler.generate_media_by_prompt(
                data["metadata_to_media"]["prompt_to_background"], data["id"], "background.png", "background_path"
            )
            if bg_file:
                data["metadata_to_media"]["background_path"] = bg_file["full_path"]

        img_file = await self.image_service_handler.generate_image(
            data["metadata_to_media"], data["id"], data.get("theme", "light")
        )
        if img_file:
            data["media_path"] = img_file["full_path"]
            if not data.get("media_path_remote"):
                remote_url = await self.upload_service.upload_file(data["media_path"])
                data["media_path_remote"] = remote_url

        if data["metadata_to_media"].get("background_path"):
            await self.file_handler.delete_file(data["metadata_to_media"]["background_path"])
            data["metadata_to_media"]["background_path"] = ""

        return data

    async def generate_media_by_prompt_to_media(self, data):
        file_data = await self.image_service_handler.generate_media_by_prompt(data["prompt_to_media"], data["id"])

        if file_data:
            data["media_path"] = file_data["full_path"]
            if not data.get("media_path_remote"):
                remote_url = await self.upload_service.upload_file(data["media_path"])
                data["media_path_remote"] = remote_url

        return data
    
    async def generate_media_by_post_type(self, post_data):
        post_type = post_data["post_type"]

        regenerate = False

        if post_type == "prompt_to_media" and not post_data["prompt_to_media"]:
            post_data["prompt_to_media"] = await self.openai_service.generate_prompt_to_media_post(post_data["default_phrase"])

        if (post_type == "metadata_to_media" or post_type == "metadata_to_media_with_background") and not post_data["metadata_to_media"]["text"]:
            post_data["metadata_to_media"]["text"] = post_data["default_phrase"]

        if post_type == "metadata_to_media_with_background" and not post_data["metadata_to_media"]["prompt_to_background"]:
           post_data["metadata_to_media"]["prompt_to_background"] = await self.openai_service.generate_prompt_to_media_post(post_data["default_phrase"])

        if not post_data.get("media_path") and (post_data["metadata_to_media"].get("text") or post_data.get("prompt_to_media")):
            print(f"Post {post_data['id']} has no media files")
            regenerate = True

        if post_data.get("media_path"):
            regenerate = not await self.process_existing_media(post_data)

        if regenerate:    
            print(f"Regenerating media for post {post_data['id']}") 
            post_data["media_path_remote"] = ""  
            if post_data.get("metadata_to_media") and post_data["metadata_to_media"].get("text"): 
                post_data = await self.generate_media_by_metadata_to_media(post_data)
            elif post_data.get("prompt_to_media"):
                post_data = await self.generate_media_by_prompt_to_media(post_data)

        return post_data
    
    async def generate_post_hashtags(self, post_data):
        """
        Generate hashtags for a single post.
        """
        if not len(post_data["hashtags"]) > 0:
            hashtags = await self.openai_service.generate_hashtags(post_data["default_phrase"])
            post_data["hashtags"] = split_array(hashtags)
        return post_data
    
    async def generate_post_content(self, post_data, content_type, is_thread=False):
        """
        Generate content for a single post.
        """
        post_type = post_data["post_type"]
        hashtags_string = join_array(post_data["hashtags"])
        characters_hashtags = count_characters(hashtags_string) + 3
        x_content_limit = int(os.getenv("X_CONTENT_LIMIT", "288"))
        meta_content_limit = int(os.getenv("META_CONTENT_LIMIT", "1000"))
        if is_thread:
            x_content_limit = int(os.getenv("X_CONTENT_LIMIT_THREAD", "1000")) / 5
        
        message = f"the idea must be in the in-depth content"

        if post_type == "prompt_to_media":
            if content_type == "x_content" and not post_data["x_content"]:
                limit = str(x_content_limit - characters_hashtags)

                post_data["x_content"] = await self.openai_service.generate_post_content(post_data["default_phrase"], limit, message)

            elif content_type == "meta_content" and not post_data["meta_content"]:
                limit = str(meta_content_limit - characters_hashtags)

                post_data["meta_content"] = await self.openai_service.generate_post_content(post_data["default_phrase"], limit, message)

        elif post_type == "metadata_to_media":

            if not is_thread:
                message = f"Generate an invitation to follow, you can include emojis, or phrases that motivate or invite the user to follow the page"

            if content_type == "x_content" and not post_data["x_content"]:
                limit = str(x_content_limit - characters_hashtags)

                post_data["x_content"] = await self.openai_service.generate_post_content(post_data["default_phrase"], limit, message)

            elif content_type == "meta_content" and not post_data["meta_content"]:
                limit = str((meta_content_limit/2) - characters_hashtags)

                post_data["meta_content"] = await self.openai_service.generate_post_content(post_data["default_phrase"], limit, message)

        return post_data

    async def generate_post(self):
        """
        Process a single post and return the processed data.
        """
        json_file = os.getenv("PROCESSED_POSTS_JSON_FILE")
        post_data = await self.post_service.get_next_post("is_processed", False, json_file=json_file)
        if not post_data:
            return None

        post_data = await self.generate_data_post(post_data)

        post_data["is_processed"] = True
        await self.post_service.save_updated_post(post_data, json_file=json_file)
        await self.post_service.save_updated_post(post_data)
        print(f"Post {post_data['id']} processed successfully.")
        return post_data
    
    def generate_thread_id(self, parent_id, index):
        print("Generating thread ID...")
        print(f"Parent ID: {parent_id}, Index: {index}")
        return (parent_id * 100000) + index
    
    async def save_processed_posts_to_json(self):
        print("Saving processed posts to JSON file...")
        await self.json_handler.save_json({"posts": self.processed_posts}, os.getenv("PROCESSED_POSTS_JSON_FILE"))

