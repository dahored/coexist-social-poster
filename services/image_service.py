import os
from services.openai_service import OpenaiServiceHandler

class ImageServiceHandler:
    def __init__(self):
        self.openai_service_handler = OpenaiServiceHandler()

    async def generate_image_from_prompt(self, prompt, filename="temp.png"):

        self.allow_openai_content_generation = os.getenv("ALLOW_OPENAI_CONTENT_GENERATION", "false").lower() == "true"
        if self.allow_openai_content_generation:
            prompt = await self.openai_service_handler.generate_prompt_image_from_idea(prompt)

        self.allow_openai = os.getenv("ALLOW_OPENAI_IMAGE_GENERATION", "false").lower() == "true"
        if self.allow_openai:
            return await self.openai_service_handler.generate_image_from_prompt(prompt, filename)
        
        print(f"[image_service] Service not configured. Skipping image generation for prompt: {prompt}")
        return ""
        
        
        