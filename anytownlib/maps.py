"""Functions to retrieve images for the maps."""

import cStringIO
import json
import requests
from PIL import Image
import urllib


def _retrieve_google_maps_image_url(coords, zoom_level, api_key):
    lat, lng = coords
    width, height = 480, 360
    marker_color = 'ff0000'
    return (
        'http://maps.googleapis.com/maps/api/staticmap?center={0},{1}&zoom={2}'
        '&scale=false&size={4}x{5}&maptype=roadmap&format=png'
        '&key={3}&markers=size:small%7Ccolor:0x{6}%7Clabel:%7C{0},{1}'
    ).format(lat, lng, zoom_level, api_key, width, height, marker_color)


def _get_image(coords, zoom_level, api_key):
    url = _retrieve_google_maps_image_url(coords, zoom_level, api_key)
    r = requests.get(url)
    stream = cStringIO.StringIO(r.content)
    im = Image.open(stream)
    return im


def get_continent_level_image(coords, api_key):
    """Get the Google Maps image for the continent zoom-level map."""
    return _get_image(coords, 4, api_key)


def get_regional_level_image(coords, api_key):
    """Get the Google Maps image for the regional zoom-level map."""
    return _get_image(coords, 7, api_key)


def geocode_coords(address, api_key):
    """Return a tuple of (coordinates, place_id) for a constructed address."""
    address = unicode(address).encode('utf-8')
    url = ('https://maps.googleapis.com/maps/api/geocode/json?'
           'address={0}&key={1}').format(urllib.quote_plus(address), api_key)
    r = requests.get(url)
    results = json.loads(r.text).get('results')
    try:
        location = results[0]['geometry']['location']
        return (location['lat'], location['lng']), results[0]['place_id']
    except KeyError:
        return None
