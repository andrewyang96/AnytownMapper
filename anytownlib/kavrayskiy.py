"""Functions that produce a Kavrayskiy VII projection map."""

import math


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
