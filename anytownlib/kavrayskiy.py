"""Functions that produce a Kavrayskiy VII projection map."""

import math
import os
from PIL import Image
from PIL import ImageDraw


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


def make_global_level_image(coords, resize_factor=0.05):
    """Make a global level image with a red dot on the given geocoords."""
    im = Image.open(os.path.join(os.path.dirname(__file__), 'kav7.png'))
    im = im.resize(map(lambda dim: int(dim * resize_factor), im.size),
                   Image.BICUBIC)
    draw_red_dot_on_map(im, coords, radius=2)
    return im
