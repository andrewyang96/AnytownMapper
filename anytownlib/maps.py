"""Functions to retrieve images for the maps."""


def _retrieve_google_maps_image_url(coords, zoom_level, api_key):
    lat, lng = coords
    return (
        'http://maps.googleapis.com/maps/api/staticmap?center={0},{1}&zoom={2}'
        '&scale=false&size=600x300&maptype=roadmap&format=png'
        '&key={3}&markers=size:small%7Ccolor:0xff0000%7Clabel:%7C{0},{1}'
    ).format(lat, lng, zoom_level, api_key)


def retrieve_continent_level_image_url(coords, api_key):
    """Get the Google Maps URL for a continent zoom-level map image."""
    return _retrieve_google_maps_image_url(coords, 4, api_key)


def retrieve_regional_level_image_url(coords, api_key):
    """Get the Google Maps URL for a regional zoom-level map image."""
    return _retrieve_google_maps_image_url(coords, 7, api_key)
