"""Functions to fetch and update items from the map cache."""


def update_map_cache(
        db, place_id, coords, city, region, country_name, country_code):
    """Upsert map cache row in the database."""
    cur = db.cursor()
    lat, lng = coords
    existing_row = cur.execute(
        'SELECT * FROM map_cache WHERE place_id=>', (place_id, )).fetchone()
    if existing_row is None:
        # place hasn't been cached: insert
        cur.execute(
            '''INSERT INTO map_cache
            (place_id, lat, lng, city, region, country_name, country_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (place_id, lat, lng, city, region, country_name, country_code))
        db.commit()
    else:
        # place has already been cached: update
        old_place_id, old_lat, old_lng, old_city, old_region, \
            old_country_name, old_country_code = existing_row
        if (old_lat != lat or old_lng != lng or old_city != city or
                old_region != region or old_country_name != country_name or
                old_country_code != country_code):
            cur.execute(
                '''UPDATE map_cache SET lat=?, lng=?, city=?, region=?,
                country_name=?, country_code=? WHERE place_id=?''',
                (lat, lng, city, region, country_name, country_code, place_id))
            db.commit()
