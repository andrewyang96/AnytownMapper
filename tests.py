"""Test suits for Anytown Mapper."""

import math
import os
import unittest
import sqlite3
import tempfile

from main import app
from main import get_db
from main import init_db

from anytownlib.kavrayskiy import coords_to_kavrayskiy
from anytownlib.kavrayskiy import make_global_level_image
from anytownlib.map_cache import fetch_from_map_cache
from anytownlib.map_cache import insert_into_map_cache
from anytownlib.map_cache import update_map_cache
from anytownlib.mapmaker import format_coords
from anytownlib.user_profiles import get_user_info
from anytownlib.user_profiles import update_user
from anytownlib.user_profiles import update_user_location_history


class TestAnytownLibKavrayskiy(unittest.TestCase):
    """Test anytownlib kavrayskiy functions."""

    def setUp(self):
        """Setup method."""
        self.resize_factor = 0.05

    def test_coords_to_kavrayskiy(self):
        """Test coords_to_kavrayskiy method."""
        x, y = coords_to_kavrayskiy((0, 0))
        self.assertEquals(x, 0)
        self.assertEquals(y, 0)
        x, y = coords_to_kavrayskiy((90, 0))
        self.assertEquals(x, 0)
        self.assertAlmostEquals(y, math.pi / 2)
        x, y = coords_to_kavrayskiy((-90, 90))
        self.assertAlmostEquals(x, math.pi * math.sqrt(3) / 8)
        self.assertAlmostEquals(y, -math.pi / 2)
        x, y = coords_to_kavrayskiy((0, -45))
        self.assertAlmostEquals(x, -math.pi * math.sqrt(3) / 8)
        self.assertEquals(y, 0)

    def test_make_global_level_image(self):
        """Test make_global_level_image method."""
        map_0_0_im = make_global_level_image(
            (0, 0), resize_factor=self.resize_factor)
        self.assertEquals(map_0_0_im.getpixel(
            (int(1732 * self.resize_factor), int(1000 * self.resize_factor))
        ), (255, 0, 0, 255))
        map_south_pole = make_global_level_image(
            (-90, 0), resize_factor=self.resize_factor)
        self.assertEquals(map_south_pole.getpixel(
            (int(1732 * self.resize_factor), int(1999 * self.resize_factor))
        ), (255, 0, 0, 255))
        map_cu = make_global_level_image(
            (40.1164, -88.2434), resize_factor=self.resize_factor)
        self.assertEquals(map_cu.getpixel(
            (int(948.72 * self.resize_factor),
                int(554.26 * self.resize_factor))
        ), (255, 0, 0, 255))


class TestAnytownLibMapCacheAndUserProfiles(unittest.TestCase):
    """Test anytownlib map_cache and user_profiles functions."""

    def setUp(self):
        """Setup method."""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        self.app = app.test_client()
        with app.app_context():
            init_db()

        self.place1 = {
            'place_id': u'PID1',
            'coords': (-12, 34),
            'city': u'Kaningina Reserve',
            'region': u'Nkhata Bay',
            'country_name': u'Malawi',
            'country_code': u'MW'
        }
        self.place1_updated_city = u'Village'
        self.place1_updated_region = u'Deforested Area'
        self.place2 = {
            'place_id': u'PID2',
            'coords': (56, -78.9),
            'city': u'Flaherty Island',
            'region': u'Nunavut',
            'country_name': u'Canada',
            'country_code': u'CA'
        }

        self.user1 = {
            'user_id': '1',
            'name': 'Al Bert',
            'email': 'albert@big.al'
        }
        self.user2 = {
            'user_id': '2',
            'name': 'Can Dee',
            'email': 'ilove@candee.ee'
        }

    def tearDown(self):
        """Teardown method."""
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_functions(self):
        """Test functions in the map_cache and user_profiles modules.

        First test fetch, insert, update methods from map_cache.
        Then test get_user_info, update_user, and update_user_location_history
        from user_profiles.
        """
        with app.app_context():
            # START map_cache testing
            self.assertIsNone(
                fetch_from_map_cache(get_db(), self.place1['place_id']))
            self.assertIsNone(
                fetch_from_map_cache(get_db(), self.place2['place_id']))

            insert_into_map_cache(get_db(), **self.place1)
            place1 = fetch_from_map_cache(get_db(), self.place1['place_id'])
            self.assertIsNotNone(place1)
            self.assertEquals(place1['city'], self.place1['city'])
            self.assertEquals(place1['region'], self.place1['region'])
            self.assertIsNone(
                fetch_from_map_cache(get_db(), self.place2['place_id']))

            insert_into_map_cache(get_db(), **self.place2)
            self.assertIsNotNone(
                fetch_from_map_cache(get_db(), self.place1['place_id']))
            place2 = fetch_from_map_cache(get_db(), self.place2['place_id'])
            self.assertIsNotNone(place2)
            self.assertEquals(place2['city'], self.place2['city'])
            self.assertEquals(place2['region'], self.place2['region'])

            self.place1['city'] = self.place1_updated_city
            self.place1['region'] = self.place1_updated_region
            update_map_cache(get_db(), **self.place1)
            place1 = fetch_from_map_cache(get_db(), self.place1['place_id'])
            self.assertIsNotNone(place1)
            self.assertEquals(place1['city'], self.place1_updated_city)
            self.assertEquals(place1['region'], self.place1_updated_region)
            self.assertIsNotNone(
                fetch_from_map_cache(get_db(), self.place2['place_id']))

            self.assertRaises(
                sqlite3.IntegrityError,
                lambda: insert_into_map_cache(get_db(), **self.place2))

            # START user_profile testing
            self.assertIsNone(get_user_info(get_db(), self.user1['user_id']))
            self.assertIsNone(get_user_info(get_db(), self.user2['user_id']))

            update_user(get_db(), **self.user1)
            self.assertIsNotNone(get_user_info(get_db(), '1'))
            self.assertIsNone(get_user_info(get_db(), '2'))

            update_user_location_history(
                get_db(), self.user1['user_id'], self.place1['place_id'])
            self.assertRaises(
                sqlite3.IntegrityError,
                lambda: update_user_location_history(
                    get_db(), self.user1['user_id'], 'THIS DOESNT EXIST'))
            self.assertRaises(
                sqlite3.IntegrityError,
                lambda: update_user_location_history(
                    get_db(), self.user2['user_id'], self.place1['place_id']))

            update_user(get_db(), **self.user2)
            self.assertIsNotNone(get_user_info(get_db(), '1'))
            self.assertIsNotNone(get_user_info(get_db(), '2'))

            update_user_location_history(
                get_db(), self.user1['user_id'], self.place2['place_id'])
            update_user_location_history(
                get_db(), self.user2['user_id'], self.place2['place_id'])
            self.assertRaises(
                sqlite3.IntegrityError,
                lambda: update_user_location_history(
                    get_db(), self.user1['user_id'], 'THIS DOESNT EXIST'))
            self.assertRaises(
                sqlite3.IntegrityError,
                lambda: update_user_location_history(
                    get_db(), self.user2['user_id'], 'THIS DOESNT EXIST'))


class TestAnytownLibMapmaker(unittest.TestCase):
    """Test anytownlib mapmaker functions."""

    def test_format_coords(self):
        """Test format_coords method."""
        self.assertEquals(format_coords((0, 0)), u'0.0\u00b0 N, 0.0\u00b0 E')
        self.assertEquals(format_coords(
            (44.9, -93.5)), u'44.9\u00b0 N, 93.5\u00b0 W')
        self.assertEquals(format_coords(
            (-37.8, 145)), u'37.8\u00b0 S, 145.0\u00b0 E')
