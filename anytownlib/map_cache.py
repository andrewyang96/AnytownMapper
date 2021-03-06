"""Functions to fetch and update items from the map cache."""

import cStringIO

import boto3
from PIL import Image

S3_BUCKET_NAME = 'anytown-mapper'


def fetch_from_map_cache(db, place_id, test=False):
    """Fetch map cache row from the database."""
    cur = db.cursor()
    map_cache_info = None
    if test:
        map_cache_info = cur.execute(
            'SELECT * FROM map_cache WHERE place_id=?', (place_id, )
        ).fetchone()
    else:
        cur.execute("SELECT * FROM map_cache WHERE place_id=%s", (place_id, ))
        map_cache_info = cur.fetchone()
    column_names = tuple(description[0] for description in cur.description)
    cur.close()
    if map_cache_info is None:
        return None
    return dict(zip(column_names, map_cache_info))


def insert_into_map_cache(
        db, place_id, coords, city, region, country_name, country_code,
        test=False):
    """Insert map cache row in the database.

    Throws sqlite3.Error if row with specified place_id already exists.
    """
    cur = db.cursor()
    lat, lng = coords
    if test:
        cur.execute(
            '''INSERT INTO map_cache
            (place_id, lat, lng, city, region, country_name, country_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (place_id, lat, lng, city, region, country_name, country_code))
    else:
        cur.execute(
            """INSERT INTO map_cache
            (place_id, lat, lng, city, region, country_name, country_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (place_id, lat, lng, city, region, country_name, country_code))
    db.commit()
    cur.close()


def update_map_cache(
        db, place_id, coords, city, region, country_name, country_code,
        test=False):
    """Update existing map cache row in the database."""
    cur = db.cursor()
    lat, lng = coords
    if test:
        cur.execute(
            '''UPDATE map_cache SET lat=?, lng=?, city=?, region=?,
            country_name=?, country_code=? WHERE place_id=?''',
            (lat, lng, city, region, country_name, country_code, place_id))
    else:
        cur.execute(
            """UPDATE map_cache SET lat=%s, lng=%s, city=%s, region=%s,
            country_name=%s, country_code=%s, WHERE place_id=%s""",
            (lat, lng, city, region, country_name, country_code, place_id))
    db.commit()
    cur.close()


def fetch_map_from_s3(place_id, aws_access_key_id, aws_secret_access_key):
    """Fetch map image from AWS S3 bucket."""
    aws_session = boto3.session.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)
    s3 = aws_session.resource('s3')
    try:
        obj = s3.Object(S3_BUCKET_NAME, '{0}.png'.format(place_id))
        stream = cStringIO.StringIO(obj.get()['Body'].read())
        im = Image.open(stream)
        return im
    except Exception:
        return None


def upload_map_to_s3(place_id, im, aws_access_key_id, aws_secret_access_key):
    """Upload map image to AWS S3 bucket."""
    aws_session = boto3.session.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)
    s3 = aws_session.resource('s3')
    stream = cStringIO.StringIO()
    im.save(stream, 'PNG')
    stream.seek(0)
    s3.Object(
        S3_BUCKET_NAME, '{0}.png'.format(place_id)
    ).put(Body=stream.getvalue())
