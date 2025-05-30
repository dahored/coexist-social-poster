import os
import openai
import aiohttp
import uuid
from dotenv import load_dotenv
from config.image_config import TEMPS_DIR

load_dotenv()

class OpenaiServiceHandler:
    def __init__(self):
        self.openai_image_model = os.getenv("OPENAI_IMAGE_MODEL")
        self.content_model = os.getenv("OPENAI_CONTENT_MODEL")
        self.image_size = "1024x1024"

        openai.api_key = os.getenv("OPENAI_API_KEY")

    async def generate_prompt_image_from_idea(self, idea, model=None):
        """Generates a prompt for DALL·E using the OpenAI API"""
        if model:
            self.content_model = model

        print(f"[openai_service] Generating prompt for idea: {idea} with model: {self.content_model}")

        client = openai.AsyncOpenAI()
        response = await client.chat.completions.create(
            model=self.content_model,
            messages=[
                {"role": "system", "content": "You are a creative assistant that generates prompts for AI-generated images."},
                {"role": "user", "content": f"Generate a visual prompt from this idea: {idea}"}
            ],
            temperature=0.9,
        )

        return response.choices[0].message.content
          
    async def generate_prompt_to_media_post(self, idea, model=None, language="english"):
        """Generates a prompt for prompt_to_media using the OpenAI API"""
        if model:
            self.content_model = model

        print(f"[openai_service] Generating prompt_to_media from idea: {idea} with model: {self.content_model}")

        client = openai.AsyncOpenAI()
        response = await client.chat.completions.create(
            model=self.content_model,
            messages=[
                {"role": "system", "content": "You are a creative assistant that generates prompts for AI-service this prompt is necesary to generate a media according to the idea, not translations, this is a prompt to generate a media post."},
                {"role": "user", "content": f"Generate a text prompt from this idea: {idea}, without quotation marks and in {language}."}
            ],
            temperature=0.9,
        )
        print(f"[openai_service] Prompt generated: {response.choices[0].message}")
        return response.choices[0].message.content
    

    async def generate_hashtags(self, idea, total=0, model=None, social_media=None):
        """Generates hashtags using the OpenAI API"""
        if total == 0:
            return ""
        
        if model:
            self.content_model = model

        print(f"[openai_service] Generating hashtags for idea: {idea} with model: {self.content_model}")

        client = openai.AsyncOpenAI()
        response = await client.chat.completions.create(
            model=self.content_model,
            messages=[
                {"role": "system", "content": f"You are a creative assistant that generates hashtags for {social_media} social media "},
                {"role": "user", "content": f"Generate {total} hashtags for this idea: {idea} in spanish and include the # symbol and only respond in a text format. The hashtags should be the recommended tendency hashtags for this idea so search in the web for the best hashtags. For the winning hashtags search in the web for the best hashtags for this idea, do not include any other text, just the hashtags."}
            ],
            temperature=0.9,
        )
        print(f"[openai_service] Hashtags generated: {response.choices[0].message}")
        return response.choices[0].message.content
    
    
    async def generate_post_content(self, idea, limit=1000, extra_message=None, language="spanish", model=None):
        """Generates content using the OpenAI API"""
        if model:
            self.content_model = model

        print(f"[openai_service] Generating content for idea: {idea} with model: {self.content_model}")

        client = openai.AsyncOpenAI()
        messages = [
            {"role": "system", "content": "You are a creative assistant that generates content for social media."},
            {"role": "user", "content": f"Generate a post with a maximum of {limit} characters for this idea: {idea} in {language} and do not include hashtags."}
        ]
        if extra_message:
            messages.append({"role": "user", "content": f"{extra_message} respect the limit of {limit} characters."})

        response = await client.chat.completions.create(
            model=self.content_model,
            messages=messages,
            temperature=0.9,
        )
        print(f"[openai_service] Content generated: {response.choices[0].message}")
        return response.choices[0].message.content
    
    async def generate_default_phrase(self, idea, limit=300, extra_message=None, language="spanish", model=None):
        """Generates a default phrase using the OpenAI API"""
        if model:
            self.content_model = model

        print(f"[openai_service] Generating default phrase for idea: {idea} with model: {self.content_model}")

        client = openai.AsyncOpenAI()
        messages = [
            {"role": "system", "content": "You are a creative assistant that generates default phrases for social media."},
            {"role": "user", "content": f"Generate a default phrase with a maximum of {limit} characters for this idea: {idea} in {language} and do not include hashtags, do not include titles"}
        ]
        if extra_message:
            messages.append({"role": "user", "content": extra_message})

        response = await client.chat.completions.create(
            model=self.content_model,
            messages=messages,
            temperature=0.9,
        )
        print(f"[openai_service] Default phrase generated: {response.choices[0].message}")
        return response.choices[0].message.content
    
    async def generate_image_from_prompt(self, prompt, filename=None):
        """Generates an image using DALL·E and saves it locally"""
        try:
            print(f"[openai_service] Requesting image from prompt: {prompt} with model: {self.openai_image_model}")

            # Create image with DALL·E
            response = await openai.AsyncOpenAI().images.generate(
                model=self.openai_image_model,
                prompt=prompt,
                n=1,
                size=self.image_size,
            )

            image_url = response.data[0].url
            print(f"[openai_service] Image URL received: {image_url}")

            # Download image
            temps_path = TEMPS_DIR
            os.makedirs(temps_path, exist_ok=True)
            if not filename:
                filename = f"temp_{uuid.uuid4().hex}.png"
            temp_file_path = os.path.join(temps_path, filename)

            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as img_response:
                    if img_response.status == 200:
                        with open(temp_file_path, "wb") as f:
                            f.write(await img_response.read())
                        print(f"[openai_service] Image saved to {temp_file_path}")
                        return temp_file_path
                    else:
                        print(f"[openai_service] Failed to download image. Status: {img_response.status}")
                        return ""

        except Exception as e:
            print(f"[openai_service] Error: {e}")
            return ""
      
