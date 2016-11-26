"""Test suits for Anytown Mapper."""

import math
import unittest

from anytownlib.kavrayskiy import coords_to_kavrayskiy
from anytownlib.kavrayskiy import make_global_level_image


class TestAnytownLibKavrayskiy(unittest.TestCase):
    """Test anytownlib kavrayskiy functions."""

    def setUp(self):
        """Setup method."""
        self.error_margin = 0.01
        self.resize_factor = 0.05

    def test_coords_to_kavrayskiy(self):
        """Test coords_to_kavrayskiy method."""
        x, y = coords_to_kavrayskiy((0, 0))
        assert x == 0
        assert y == 0
        x, y = coords_to_kavrayskiy((90, 0))
        assert x == 0
        assert abs(y - (math.pi / 2)) < self.error_margin
        x, y = coords_to_kavrayskiy((-90, 90))
        assert abs(x - (math.pi * math.sqrt(3) / 8)) < self.error_margin
        assert abs(y - (- math.pi / 2)) < self.error_margin
        x, y = coords_to_kavrayskiy((0, -45))
        assert abs(x - (-math.pi * math.sqrt(3) / 8)) < self.error_margin
        assert y == 0

    def test_make_global_level_image(self):
        """Test make_global_level_image method."""
        map_0_0_im = make_global_level_image(
            (0, 0), resize_factor=self.resize_factor)
        assert map_0_0_im.getpixel(
            (int(1732 * self.resize_factor), int(1000 * self.resize_factor))
        ) == (255, 0, 0, 255)
        map_south_pole = make_global_level_image(
            (-90, 0), resize_factor=self.resize_factor)
        assert map_south_pole.getpixel(
            (int(1732 * self.resize_factor), int(1999 * self.resize_factor))
        ) == (255, 0, 0, 255)
        map_cu = make_global_level_image(
            (40.1164, -88.2434), resize_factor=self.resize_factor)
        assert map_cu.getpixel(
            (int(948.72 * self.resize_factor),
                int(554.26 * self.resize_factor))
        ) == (255, 0, 0, 255)


class TestAnytownLibMapCache(unittest.TestCase):
    """Test anytownlib map_cache functions."""

    pass


class TestAnytownLibMapmaker(unittest.TestCase):
    """Test anytownlib mapmaker functions."""

    pass


class TestAnytownLibMaps(unittest.TestCase):
    """Test anytownlib maps functions."""

    def setUp(self):
        """Setup method."""
        self.mock_api_key = 'APIKEY'


class TestAnytownLibUserProfiles(unittest.TestCase):
    """Test anytownlib user_profiles functions."""

    pass
