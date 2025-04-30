import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import uuid

from utils.path_utils import get_path_from_base
from config.image_config import (
    BACKGROUNDS_DIR,
    FONTS_DIR,
    DEFAULT_BACKGROUND_IMAGE_LIGHT,
    DEFAULT_BACKGROUND_IMAGE_DARK,
    DEFAULT_WATERMARK_LIGHT,
    DEFAULT_WATERMARK_DARK,
    WATERMARK_NAME,
    WATERMARK_WIDTH_DIVIDER,
    WATERMARK_MARGIN_BOTTOM,
    WATERMARK_IMAGE_CENTER,
    FONT_FAMILY,
    LINE_SPACING,
    SHOW_WATERMARK,
    SHOW_WATERMARK_NAME,
    RANDOM_BACKGROUND,
    TEMPS_DIR,
    LOGOS_DIR
)
from utils.file_utils import FileHandler

class ImageGeneratorHandler:
    def __init__(self):
        self.file_handler = FileHandler()
        
    def resolve_background_path(self, theme, data_background):
        if data_background:
            absolute_background_path = self.file_handler.get_file_path(data_background)
            if os.path.exists(absolute_background_path):
                return absolute_background_path

        if RANDOM_BACKGROUND:
            folder = "light" if theme == 'light' else "dark"
            folder_path = os.path.join(BACKGROUNDS_DIR, folder)
            if os.path.exists(folder_path):
                valid_extensions = ['.png', '.jpg', '.jpeg']
                files = [
                    f for f in os.listdir(folder_path)
                    if os.path.isfile(os.path.join(folder_path, f)) and os.path.splitext(f)[1].lower() in valid_extensions
                ]
                if files:
                    chosen_file = random.choice(files)
                    return os.path.join(folder_path, chosen_file)

        if theme == 'light':
            return os.path.join(BACKGROUNDS_DIR, 'dark', DEFAULT_BACKGROUND_IMAGE_LIGHT)
        else:
            return os.path.join(BACKGROUNDS_DIR, 'light', DEFAULT_BACKGROUND_IMAGE_DARK)

    def create_text_image(self, text, font_path, font_size, text_color, text_scale=1.0, max_width_ratio=2/3, image_width=1024):
        line_spacing = LINE_SPACING
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
        text_img_width = int(max_text_width * text_scale)
        text_img_height = int(line_height * len(lines) * text_scale)
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
            watermark_name = WATERMARK_NAME
            font_path = os.path.join(FONTS_DIR, FONT_FAMILY)
           
            watermark_margin_bottom = WATERMARK_MARGIN_BOTTOM
            watermark = Image.open(watermark_path).convert('RGBA')
            new_watermark_width = width // WATERMARK_WIDTH_DIVIDER
            resize_factor = new_watermark_width / watermark.width
            new_watermark_height = int(watermark.height * resize_factor)
            watermark = watermark.resize((new_watermark_width, new_watermark_height))
            alpha = watermark.split()[3]
            brightness = ImageEnhance.Brightness(alpha)
            alpha = brightness.enhance(0.8)
            watermark.putalpha(alpha)
            watermark_center = WATERMARK_IMAGE_CENTER
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
                watermark_text_color = (255, 255, 255, int(0.8 * 255)) if theme == 'dark' else (0, 0, 0, int(0.6 * 255))
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
        overlay_color = (0, 0, 0, 100) if theme == 'dark' else (255, 255, 255, 100)
        overlay = Image.new('RGBA', (width, height), overlay_color)
        canvas = Image.alpha_composite(canvas, overlay)
        if theme == 'dark':
            watermark_path = os.path.join(LOGOS_DIR, DEFAULT_WATERMARK_LIGHT)
        else:
            watermark_path = os.path.join(LOGOS_DIR, DEFAULT_WATERMARK_DARK)
        print(f"Watermark path: {watermark_path}")
        text_img = self.create_text_image(
            text,
            font_path=os.path.join(FONTS_DIR, FONT_FAMILY),
            font_size=font_size or int(os.getenv('FONT_SIZE', width // font_ratio)),
            text_color=(255, 255, 255) if theme == 'dark' else (0, 0, 0),
            text_scale=text_scale,
            max_width_ratio=2/3,
            image_width=width
        )

        text_width, text_height = text_img.size
        text_position = ((width - text_width) // 2, (height - text_height) // 2)
        canvas.paste(text_img, text_position, text_img)

        if SHOW_WATERMARK:
            self.add_watermark(canvas, watermark_path, width, height, show_watermark_name=SHOW_WATERMARK_NAME, theme=theme)

        os.makedirs(TEMPS_DIR, exist_ok=True)
        temp_filename = f"temp_{uuid.uuid4().hex}.png"
        temp_file_path = os.path.join(TEMPS_DIR, temp_filename)
        canvas.save(temp_file_path, format='PNG')

        result = self.file_handler.move_temp_file_to_folder(temp_file_path, id)
        return result
