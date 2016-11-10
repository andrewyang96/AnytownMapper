"""Entrypoint for Anytown Mapper web application."""

from flask import Flask
from flask import g
from flask import render_template
from flask import request
from flask import send_file
from flask import url_for

import cStringIO
import sqlite3

from anytownlib.mapmaker import make_image
from anytownlib.maps import geocode_coords

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
    return render_template(
        'index.html', stylesheet_href=url_for('static', filename='style.css'),
        script_src=url_for('static', filename='script.js'),
        api_key=get_google_maps_api_key())


@app.route('/map', methods=['GET'])
def get_map():
    """Map generator handler given city, region, country_name, country_code."""
    city = request.args.get('city').strip() or ''
    if len(city) == 0:
        return 'city parameter is not present', 400
    region = request.args.get('region').strip() or ''
    if len(region) == 0:
        return 'region parameter is not present', 400
    country_name = request.args.get('country_name').strip() or ''
    if len(country_name) == 0:
        return 'country_name parameter is not present', 400
    country_code = request.args.get('country_code').strip() or ''
    if len(country_code) == 0:
        return 'country_code parameter is not present', 400
    search_query = ' '.join((city, region, country_code))
    api_key = get_google_maps_api_key()
    coords, place_id = geocode_coords(search_query, api_key)

    im = make_image(city, coords, api_key)
    buffer = cStringIO.StringIO()
    im.save(buffer, 'PNG')
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png')


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
    coords = (lat, lng)
    im = make_image('Test City', coords, api_key)
    buffer = cStringIO.StringIO()
    im.save(buffer, 'PNG')
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png')


if __name__ == '__main__':
    app.run(port=5000, debug=True)
