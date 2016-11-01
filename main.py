"""Entrypoint for Anytown Mapper web application."""

from flask import Flask
from flask import g
from flask import render_template
from flask import request

import sqlite3

from anytownlib.kavrayskiy import make_global_level_image
from anytownlib.maps import retrieve_continent_level_image
from anytownlib.maps import retrieve_regional_level_image

app = Flask(__name__)
app.config['DATABASE'] = 'database.db'


def get_db():
    """Get database object."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db


def get_google_maps_api_key():
    """Get Google Maps API key."""
    cur = get_db().cursor()
    api_key = cur.execute(
        'SELECT api_key FROM credentials WHERE provider="google"').fetchone()
    return api_key[0]


@app.route('/', methods=['GET'])
def index():
    """Index handler."""
    return 'Anytown Mapper'


@app.route('/coords', methods=['GET'])
def get_coords():
    """Map generator (coords) handler."""
    try:
        lat = float(request.args.get('lat'))
    except ValueError:
        return 'lat parameter is invalid or not present', 400
    try:
        lng = float(request.args.get('lng'))
    except ValueError:
        return 'lng paramenter is invalid or not present', 400
    api_key = get_google_maps_api_key()
    return render_template(
        'test_maps.html',
        regional=retrieve_regional_level_image((lat, lng), api_key),
        continent=retrieve_continent_level_image((lat, lng), api_key),
        global_=make_global_level_image((lat, lng)))


if __name__ == '__main__':
    app.run(port=5000, debug=True)
