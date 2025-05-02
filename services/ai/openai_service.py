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

    async def generate_prompt_image_from_idea(self, idea):
        """Generates a prompt for DALL·E using the OpenAI API"""
        print(f"[openai_service] Generating prompt for idea: {idea}")
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
        

    async def generate_image_from_prompt(self, prompt, filename=None):
        """Generates an image using DALL·E and saves it locally"""
        try:
            print(f"[openai_service] Requesting image from prompt: {prompt}")

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