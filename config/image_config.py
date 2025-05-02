import os
from utils.base_utils import get_path_from_base

# Base directories
BASE_PUBLIC = get_path_from_base("public")
BASE_UPLOADS_DIR = get_path_from_base("public", "uploads")
BASE_ASSETS_DIR = get_path_from_base("assets")

# Upload subfolders
IMAGES_DIR = os.path.join(BASE_UPLOADS_DIR, "images")
VIDEOS_DIR = os.path.join(BASE_UPLOADS_DIR, "videos")
TEMPS_DIR = os.path.join(BASE_UPLOADS_DIR, "temps")

# Asset subfolders
FONTS_DIR = os.path.join(BASE_ASSETS_DIR, "fonts")
LOGOS_DIR = os.path.join(BASE_ASSETS_DIR, "images", "logos")
BACKGROUNDS_DIR = os.path.join(BASE_ASSETS_DIR, "images", "backgrounds")

# Watermark config
WATERMARK_NAME = os.getenv("WATERMARK_NAME", "Coexist")
WATERMARK_WIDTH_DIVIDER = int(os.getenv("WATERMARK_WIDTH_DIVIDER", 8))
WATERMARK_MARGIN_BOTTOM = int(os.getenv("WATERMARK_MARGIN_BOTTOM", 40))
WATERMARK_IMAGE_CENTER = os.getenv("WATERMARK_IMAGE_CENTER", "false").lower() == "true"

DEFAULT_WATERMARK_LIGHT = os.getenv("WATERMARK_IMAGE_LIGHT", "logo_coexist_white_watermark.png")
DEFAULT_WATERMARK_DARK = os.getenv("WATERMARK_IMAGE_DARK", "logo_coexist_black_watermark.png")
DEFAULT_BACKGROUND_IMAGE_LIGHT = os.getenv("DEFAULT_BACKGROUND_IMAGE_LIGHT", "background_coexist_dark.png")
DEFAULT_BACKGROUND_IMAGE_DARK = os.getenv("DEFAULT_BACKGROUND_IMAGE_DARK", "background_coexist_light.png")

# Fonts and text
FONT_FAMILY = os.getenv("FONT_FAMILY", "CascadiaMonoPL.ttf")
FONT_SIZE = int(os.getenv("FONT_SIZE", "36"))
LINE_SPACING = int(os.getenv("LINE_SPACING", "10"))

# Feature toggles
SHOW_WATERMARK = os.getenv("SHOW_WATERMARK", "true").lower() == "true"
SHOW_WATERMARK_NAME = os.getenv("SHOW_WATERMARK_NAME", "true").lower() == "true"

RANDOM_BACKGROUND = os.getenv("RANDOM_BACKGROUND", "false").lower() == "true"

