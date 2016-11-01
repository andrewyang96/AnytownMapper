"""Functions that produce a Kavrayskiy VII projection map."""

import math
from PIL import Image, ImageDraw


def coords_to_kavrayskiy(coords):
    """Convert geographical coordinates to Kavrayskiy VII coordinates.

    A Kavrayskiy VII map is defined with the following dimensions:
    - Height: pi units
    - Width: sqrt(3) * pi units
    """
    # convert degrees to radians
    lat, lng = map(lambda deg: deg * math.pi / 180, coords)
    x = (3 * lng / 2) * math.sqrt((1 / 3.) - (lat / math.pi)**2)
    y = lat
    return (x, y)


def draw_red_dot_on_map(im, coords, color='red', radius=20):
    """Draw a red dot at the given geographical coordinates on the image."""
    width, height = im.size
    x, y = coords_to_kavrayskiy(coords)
    x = (x / (math.sqrt(3) * math.pi)) + 0.5
    x *= width
    y = (-y / math.pi) + 0.5
    y *= height

    draw = ImageDraw.Draw(im)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius),
                 fill=color, outline=color)


def make_global_level_image(coords):
    """Make a global level image and put a red dot on the given geocoords."""
    im = Image.open('kav7.png')
    draw_red_dot_on_map(im, coords)
    im.show()
