import os
import shutil
import uuid
import random

from PIL import Image, ImageDraw, ImageFont, ImageEnhance

from utils.path_utils import get_path_from_base
from services.main_service import MainServiceHandler


class FileHandler:
    def __init__(self):
        # Define the uploads folder and its subfolders using the path helper
        self.uploads_dir = get_path_from_base("public", "uploads")

        self.images_path = os.path.join(self.uploads_dir, "images")
        self.videos_path = os.path.join(self.uploads_dir, "videos")
        self.temps_path = os.path.join(self.uploads_dir, "temps")
        self.logos_base_path = get_path_from_base("public", "assets", "images", "logos")

        self.backgrounds_base_path = get_path_from_base("public", "assets", "images", "backgrounds")


        self.main_service_handler = MainServiceHandler()

    def get_file_path(self, relative_path):
        """Returns an absolute path relative to the project root (index.py)"""
        return get_path_from_base(relative_path)

    def move_temp_file_to_folder(self, temp_file_path, id):
        """Moves a temporary file to the images folder and renames it to_{id}.extension"""

        if not os.path.exists(temp_file_path):
            print(f"The file {temp_file_path} does not exist.")
            return None

        type_file = self.get_type_file(temp_file_path)

        if type_file in [".jpg", ".png", ".jpeg"]:
            new_filename = f"image_file_{id}{type_file}"
            destination_path = os.path.join(self.images_path, new_filename)

            # shutil.copy2(temp_file_path, destination_path)
            shutil.move(temp_file_path, destination_path)
            print(f"File moved and renamed to {destination_path}")

            return {
                "filename": new_filename,
                "full_path": destination_path,
                "path": self.images_path,
                "relative_path": os.path.join("public", "uploads", "images", new_filename),
            }
        else:
            print(f"The file {temp_file_path} is not a valid image.")
            return None

    def get_media_path(self, media_path):
        """Checks if the file exists and is valid"""
        absolute_path = self.get_file_path(media_path)

        if not os.path.exists(absolute_path):
            print(f"The file {absolute_path} does not exist.")
            return None
        return absolute_path

    def get_type_file(self, file_path):
        """Returns the file type/extension"""
        _, file_extension = os.path.splitext(file_path)
        return file_extension

    async def generate_media_by_prompt(self, prompt, id):
        """Generates a file from a prompt"""
        print(f"Generating file from prompt: {prompt}")
        
        temp_file_path = await self.main_service_handler.generate_image_from_prompt(prompt, "temp.png")
        return self.move_temp_file_to_folder(temp_file_path, id)
    
    def resolve_background_path(self, theme, data_background):
        if data_background:
            absolute_background_path = self.get_file_path(data_background)
            if os.path.exists(absolute_background_path):
                return absolute_background_path

        random_background = os.getenv("RANDOM_BACKGROUND", "false").lower() == "true"

        if random_background:
            folder = "light" if theme == 'light' else "dark"
            folder_path = os.path.join(self.backgrounds_base_path, folder)

            if os.path.exists(folder_path):
                valid_extensions = ['.png', '.jpg', '.jpeg']
                files = [
                    f for f in os.listdir(folder_path)
                    if os.path.isfile(os.path.join(folder_path, f)) and os.path.splitext(f)[1].lower() in valid_extensions
                ]
                if files:
                    chosen_file = random.choice(files)
                    return os.path.join(folder_path, chosen_file)

        # fallback default using self.backgrounds_base_path
        if theme == 'light':
            return os.path.join(self.backgrounds_base_path, 'dark', os.getenv("DEFAULT_BACKGROUND_IMAGE_LIGHT", "background_coexist_dark.png"))
        else:
            return os.path.join(self.backgrounds_base_path, 'light', os.getenv("DEFAULT_BACKGROUND_IMAGE_DARK", "background_coexist_light.png"))

    
    def create_text_image(self, text, font_path, font_size, text_color, text_scale=1.0, max_width_ratio=2/3, image_width=1024):
        line_spacing = int(os.getenv('LINE_SPACING', '10'))

        try:
            font = ImageFont.truetype(font_path, size=font_size)
        except:
            font = ImageFont.load_default()

        max_text_width = int(image_width * max_width_ratio)
        dummy_img = Image.new('RGBA', (10, 10), (0, 0, 0, 0))
        draw = ImageDraw.Draw(dummy_img)

        paragraphs = text.split('\n')
        lines = []

        for paragraph in paragraphs:
            words = paragraph.split(' ')
            current_line = ""

            for word in words:
                test_line = current_line + (' ' if current_line else '') + word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                test_width = bbox[2] - bbox[0]

                if test_width <= max_text_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

        line_height = (font.getbbox('Ay')[3] - font.getbbox('Ay')[1]) + line_spacing
        text_img_width = max_text_width
        text_img_height = line_height * len(lines)

        text_img_width = int(text_img_width * text_scale)
        text_img_height = int(text_img_height * text_scale)
        scaled_font_size = max(1, int(font_size * text_scale))

        try:
            scaled_font = ImageFont.truetype(font_path, size=scaled_font_size)
        except:
            scaled_font = ImageFont.load_default()

        text_img = Image.new('RGBA', (text_img_width, text_img_height), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)

        y = 0
        for line in lines:
            bbox = text_draw.textbbox((0, 0), line, font=scaled_font)
            line_width = bbox[2] - bbox[0]
            x = (text_img_width - line_width) // 2
            text_draw.text((x, y), line, font=scaled_font, fill=text_color)
            y += line_height

        return text_img

    def add_watermark(self, canvas, watermark_path, width, height, show_watermark_name=False, theme='light'):
        try:
            watermark_name = os.getenv("WATERMARK_NAME", "Coexist")
            font_path = get_path_from_base(f"public/assets/fonts/{os.getenv('FONT_FAMILY', 'CascadiaMonoPL.ttf')}")
            watermark_width_divider = int(os.getenv("WATERMARK_WIDTH_DIVIDER", 8))
            watermark_margin_bottom = int(os.getenv("WATERMARK_MARGIN_BOTTOM", 40))

            watermark = Image.open(watermark_path).convert('RGBA')
            new_watermark_width = width // watermark_width_divider
            resize_factor = new_watermark_width / watermark.width
            new_watermark_height = int(watermark.height * resize_factor)
            watermark = watermark.resize((new_watermark_width, new_watermark_height))

            alpha = watermark.split()[3]
            brightness = ImageEnhance.Brightness(alpha)
            alpha = brightness.enhance(0.8)
            watermark.putalpha(alpha)

            watermark_center = os.getenv("WATERMARK_IMAGE_CENTER", "false").lower() == "true"

            draw = ImageDraw.Draw(canvas)
            try:
                font = ImageFont.truetype(font_path, size=width // 40)
            except:
                font = ImageFont.load_default()

            text_bbox = draw.textbbox((0, 0), watermark_name, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            total_height = new_watermark_height + (text_height + 10 if show_watermark_name else 0)

            if watermark_center:
                pos_x = (width - new_watermark_width) // 2
                pos_y = height - total_height - watermark_margin_bottom
            else:
                pos_x = width - new_watermark_width - watermark_margin_bottom
                pos_y = height - total_height - watermark_margin_bottom

            canvas.paste(watermark, (pos_x, pos_y), watermark)

            if show_watermark_name:
                if theme == 'dark':
                    watermark_text_color = (255, 255, 255, int(0.8 * 255))
                else:
                    watermark_text_color = (0, 0, 0, int(0.6 * 255))

                text_x = (width - text_width) // 2 if watermark_center else (pos_x + (new_watermark_width - text_width) // 2)
                text_y = pos_y + new_watermark_height + 5
                draw.text((text_x, text_y), watermark_name, font=font, fill=watermark_text_color)

        except FileNotFoundError:
            print("Watermark not found. Continuing without watermark.")

    async def generate_image(self, data, id, theme='light', width=1024, height=1024, font_size=None, font_ratio=24, text_scale=1.0):
        text = data["text"]
        background_path = self.resolve_background_path(theme, data.get("background"))

        background = Image.open(background_path).convert('RGBA')
        background = background.resize((width, height))

        canvas = Image.new('RGBA', (width, height))
        canvas.paste(background, (0, 0))

        overlay_color = (0, 0, 0, 150) if theme == 'dark' else (255, 255, 255, 100)
        overlay = Image.new('RGBA', (width, height), overlay_color)
        canvas = Image.alpha_composite(canvas, overlay)

        if theme == 'dark':
            watermark_path = self.get_file_path(f'public/assets/images/logos/{os.getenv("WATERMARK_IMAGE_LIGHT", "logo_coexist_white_watermark.png")}')
        else:
            watermark_path = self.get_file_path(f'public/assets/images/logos/{os.getenv("WATERMARK_IMAGE_DARK", "logo_coexist_black_watermark.png")}')

        text_img = self.create_text_image(
            text,
            font_path=get_path_from_base(f"public/assets/fonts/{os.getenv('FONT_FAMILY', 'CascadiaMonoPL.ttf')}"),
            font_size=font_size or int(os.getenv('FONT_SIZE', width // font_ratio)),
            text_color=(255, 255, 255) if theme == 'dark' else (0, 0, 0),
            text_scale=text_scale,
            max_width_ratio=2/3,
            image_width=width
        )

        text_width, text_height = text_img.size
        text_position = ((width - text_width) // 2, (height - text_height) // 2)
        canvas.paste(text_img, text_position, text_img)

        show_watermark = os.getenv("SHOW_WATERMARK", "true").lower() == "true"
        show_watermark_name = os.getenv("SHOW_WATERMARK_NAME", "true").lower() == "true"
        if show_watermark:
            self.add_watermark(canvas, watermark_path, width, height, show_watermark_name=show_watermark_name, theme=theme)

        os.makedirs(self.temps_path, exist_ok=True)
        temp_filename = f"temp_{uuid.uuid4().hex}.png"
        temp_file_path = os.path.join(self.temps_path, temp_filename)
        canvas.save(temp_file_path, format='PNG')

        result = self.move_temp_file_to_folder(temp_file_path, id)
        return result