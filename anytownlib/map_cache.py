"""Functions to fetch and update items from the map cache."""


def fetch_from_map_cache(db, place_id):
    """Fetch map cache row from the database."""
    cur = db.cursor()
    map_cache_info = cur.execute(
        'SELECT * FROM map_cache WHERE place_id=?', (place_id, )).fetchone()
    column_names = tuple(description[0] for description in cur.description)
    if map_cache_info is None:
        return None
    return dict(zip(column_names, map_cache_info))


def insert_into_map_cache(
        db, place_id, coords, city, region, country_name, country_code):
    """Insert map cache row in the database.

    Throws sqlite3.Error if row with specified place_id already exists.
    """
    cur = db.cursor()
    lat, lng = coords
    cur.execute(
        '''INSERT INTO map_cache
        (place_id, lat, lng, city, region, country_name, country_code)
        VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (place_id, lat, lng, city, region, country_name, country_code))
    db.commit()


def update_map_cache(
        db, place_id, coords, city, region, country_name, country_code):
    """Update existing map cache row in the database."""
    cur = db.cursor()
    lat, lng = coords
    cur.execute(
        '''UPDATE map_cache SET lat=?, lng=?, city=?, region=?,
        country_name=?, country_code=? WHERE place_id=?''',
        (lat, lng, city, region, country_name, country_code, place_id))
    db.commit()


def fetch_map_from_s3(place_id):
    """Fetch map image from AWS S3 bucket."""
    pass


def upload_map_to_s3(place_id, im):
    """Upload map image to AWS S3 bucket."""
    pass
