"""Entrypoint for Anytown Mapper web application."""

from flask import flash
from flask import Flask
from flask import g
from flask import render_template
from flask import request
from flask import send_file
from flask import session
from flask import redirect
from flask import url_for

import cStringIO
import facebook
import requests
import sqlite3
import urllib

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


def get_facebook_client_id_and_secret():
    """Get Facebook client ID and client secret."""
    cur = get_db().cursor()
    stmt = 'SELECT api_key FROM credentials WHERE provider="{0}"'
    client_id = cur.execute(stmt.format('facebook_client_id')).fetchone()[0]
    client_secret = cur.execute(
        stmt.format('facebook_client_secret')).fetchone()[0]
    return client_id, client_secret


@app.route('/', methods=['GET'])
def index():
    """Index handler."""
    name = session.get('name')
    return render_template(
        'index.html', stylesheet_href=url_for('static', filename='style.css'),
        script_src=url_for('static', filename='script.js'),
        api_key=get_google_maps_api_key(), name=name)


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


@app.route('/login', methods=['GET'])
def login():
    """Login handler that initiates Facebook OAuth2 flow."""
    client_id, client_secret = get_facebook_client_id_and_secret()
    redirect_uri = ('https://www.facebook.com/v2.8/dialog/oauth?client_id={0}'
                    '&display=popup&redirect_uri={1}'.format(
                        client_id, urllib.quote_plus(
                            request.url_root + 'login/callback')))
    return redirect(redirect_uri)


@app.route('/login/callback', methods=['GET'])
def login_callback():
    """Login callback handler from Facebook OAuth2 flow."""
    error = request.args.get('error')
    if error:
        flash('You denied the request to sign in.')
        return redirect('/')
    code = request.args.get('code')
    if code is None:
        flash('Error in logging in')
        return redirect('/')
    client_id, client_secret = get_facebook_client_id_and_secret()
    exchange_url = ('https://graph.facebook.com/v2.8/oauth/access_token'
                    '?client_id={0}&redirect_uri={1}'
                    '&client_secret={2}&code={3}'.format(
                        client_id, urllib.quote_plus(
                            request.url_root + 'login/callback'),
                        client_secret, code))
    exchange_request = requests.get(exchange_url)
    exchange_response = exchange_request.json()
    session['access_token'] = exchange_response['access_token']
    graph = facebook.GraphAPI(access_token=exchange_response['access_token'])
    user_profile = graph.get_object('me')
    session['name'] = user_profile['name']
    # TODO: upsert into db
    return redirect('/')


@app.route('/logout', methods=['GET'])
def logout():
    """Logout callback handler."""
    session.pop('access_token', None)
    session.pop('name', None)
    return redirect('/')


if __name__ == '__main__':
    with app.app_context():
        # Use facebook client ecret as app secret key
        app.secret_key = get_facebook_client_id_and_secret()[1]
    app.run(port=5000, debug=True)
