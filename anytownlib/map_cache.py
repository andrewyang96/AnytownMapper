"""Functions to fetch and update items from the map cache."""


def update_map_cache(
        db, place_id, coords, city, region, country_name, country_code):
    """Upsert map cache row in the database."""
    cur = db.cursor()
    lat, lng = coords
    cur.execute(
        '''UPDATE map_cache SET lat=?, lng=?, city=?, region=?,
        country_name=?, country_code=? WHERE place_id=?''',
        (lat, lng, city, region, country_name, country_code, place_id))
    db.commit()
