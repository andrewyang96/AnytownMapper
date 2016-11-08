"""Function to stitch together the three maps."""

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from .kavrayskiy import make_global_level_image
from .maps import get_continent_level_image
from .maps import get_regional_level_image


def make_image(city_name, coords, api_key):
    """Make the Anytown Mapper image with given city name and coords."""
    global_image = make_global_level_image(coords)  # 173x100
    continent_image = get_continent_level_image(coords, api_key)  # 400x300
    regional_image = get_regional_level_image(coords, api_key)  # 400x300

    background_color = (245, 245, 220)  # beige
    header_color = (0, 0, 0)  # black
    text_color = (64, 64, 64)  # gray

    im = Image.new('RGB', (1000, 500), color=background_color)
    draw = ImageDraw.Draw(im)
    header_font = ImageFont.truetype('arial.ttf', 32)
    regular_font = ImageFont.truetype('arial.ttf', 16)

    im.paste(im=global_image, box=(414, 50))
    im.paste(im=continent_image, box=(50, 150))
    im.paste(im=regional_image, box=(550, 150))
    draw.text((50, 50), city_name, header_color, font=header_font)
    draw.text(
        (700, 50), 'Made by Anytown Mapper', text_color, font=regular_font)
    return im
