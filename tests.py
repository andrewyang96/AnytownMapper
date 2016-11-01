"""Test suits for Anytown Mapper."""

import unittest

from anytownlib.maps import retrieve_continent_level_image_url
from anytownlib.maps import retrieve_regional_level_image_url


class TestAnytownLibMaps(unittest.TestCase):
    """Test anytownlib maps functions."""

    def setUp(self):
        """Setup method."""
        self.mock_api_key = 'APIKEY'

    def test_retrieve_continent_level_image_url(self):
        """Test retrieve_continent_level_image_url method."""
        url = retrieve_continent_level_image_url((-10, 10), self.mock_api_key)
        expected_url = (
            'http://maps.googleapis.com/maps/api/staticmap?center=-10,10'
            '&zoom=4&scale=false&size=600x300&maptype=roadmap&format=png'
            '&key={0}&markers=size:small%7Ccolor:0xff0000%7Clabel:%7C-10,10'
        ).format(self.mock_api_key)
        assert url == expected_url

    def test_retrieve_regional_level_image_url(self):
        """Test retrieve_regional_level_image_url method."""
        url = retrieve_regional_level_image_url((-10, 10), self.mock_api_key)
        expected_url = (
            'http://maps.googleapis.com/maps/api/staticmap?center=-10,10'
            '&zoom=7&scale=false&size=600x300&maptype=roadmap&format=png'
            '&key={0}&markers=size:small%7Ccolor:0xff0000%7Clabel:%7C-10,10'
        ).format(self.mock_api_key)
        assert url == expected_url
