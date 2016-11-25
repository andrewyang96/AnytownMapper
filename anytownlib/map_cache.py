"""Functions to fetch and update items from the map cache."""


def update_map_cache(
        db, place_id, coords, city, region, country_name, country_code):
    """Upsert map cache row in the database."""
    lat, lng = coords
