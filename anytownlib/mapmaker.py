"""Function to stitch together the three maps."""

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from .kavrayskiy import make_global_level_image
from .maps import get_continent_level_image
from .maps import get_regional_level_image


def format_coords(coords):
    """Return a human-readable coordinate."""
    lat, lng = map(lambda num: round(num, 2), coords)
    lat_component = u'{0}\u00b0 {1}'.format(abs(lat), 'N' if lat >= 0 else 'S')
    lng_component = u'{0}\u00b0 {1}'.format(abs(lng), 'E' if lng >= 0 else 'W')
    return u'{0}, {1}'.format(lat_component, lng_component)


def make_image(city_name, coords, api_key):
    """Make the Anytown Mapper image with given city name and coords."""
    global_image = make_global_level_image(coords)  # 173x100
    continent_image = get_continent_level_image(coords, api_key)  # 400x300
    regional_image = get_regional_level_image(coords, api_key)  # 400x300

    background_color = (245, 245, 220)  # beige
    header_color = (0, 0, 0)  # black
    subheader_color = (64, 64, 64)  # gray
    text_color = (64, 64, 64)  # gray

    im = Image.new('RGB', (1000, 500), color=background_color)
    draw = ImageDraw.Draw(im)
    header_font = ImageFont.truetype('arial.ttf', 48)
    subheader_font = ImageFont.truetype('arial.ttf', 32)
    regular_font = ImageFont.truetype('arial.ttf', 16)

    im.paste(global_image, box=(414, 10), mask=global_image)
    im.paste(im=continent_image, box=(10, 130))
    im.paste(im=regional_image, box=(510, 130))
    draw.text((10, 10), city_name, header_color, font=header_font)
    draw.text(
        (10, 60), format_coords(coords), subheader_color, font=subheader_font)
    draw.text(
        (800, 10), 'Made by Anytown Mapper', text_color, font=regular_font)
    return im
