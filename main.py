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

from anytownlib.map_cache import update_map_cache
from anytownlib.mapmaker import make_image
from anytownlib.maps import geocode_coords
from anytownlib.user_profiles import get_user_info
from anytownlib.user_profiles import update_user
from anytownlib.user_profiles import update_user_location_history

app = Flask(__name__)
app.config['DATABASE'] = 'database.db'


def init_db():
    """Initialize database with schema."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def get_db():
    """Get database object."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys = ON')
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
    stmt = 'SELECT api_key FROM credentials WHERE provider=?'
    client_id = cur.execute(stmt, ('facebook_client_id', )).fetchone()[0]
    client_secret = cur.execute(
        stmt, ('facebook_client_secret', )).fetchone()[0]
    return client_id, client_secret


@app.route('/', methods=['GET'])
def index():
    """Index handler."""
    name = session.get('name')
    user_id = session.get('user_id')
    return render_template(
        'index.html', stylesheet_href=url_for('static', filename='style.css'),
        script_src=url_for('static', filename='script.js'),
        api_key=get_google_maps_api_key(), name=name, user_id=user_id)


@app.route('/user/<int:user_id>', methods=['GET'])
def user_profile(user_id):
    """User profile handler."""
    user_profile = get_user_info(get_db(), user_id)
    if user_profile is None:
        return 'User does not exist', 404
    return render_template(
        'profile.html',
        stylesheet_href=url_for('static', filename='style.css'),
        user_profile=user_profile)


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

    update_map_cache(
        get_db(), place_id, coords, city, region, country_name, country_code)
    user_id = session.get('user_id')
    if user_id:
        update_user_location_history(get_db(), user_id, place_id)

    return send_file(buffer, mimetype='image/png')


@app.route('/login', methods=['GET'])
def login():
    """Login handler that initiates Facebook OAuth2 flow."""
    client_id, client_secret = get_facebook_client_id_and_secret()
    redirect_uri = ('https://www.facebook.com/v2.8/dialog/oauth?client_id={0}'
                    '&display=popup&scope=email&redirect_uri={1}'.format(
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
        flash('Error logging in. Please try again.')
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
    user_profile = graph.get_object('me', fields='name,email')
    session['name'] = user_profile['name']
    session['user_id'] = user_profile['id']

    update_user(
        get_db(), user_profile['id'], user_profile['name'],
        user_profile['email'])
    return redirect('/')


@app.route('/logout', methods=['GET'])
def logout():
    """Logout callback handler."""
    session.pop('access_token', None)
    session.pop('name', None)
    session.pop('user_id', None)
    return redirect('/')


if __name__ == '__main__':
    with app.app_context():
        # Use facebook client ecret as app secret key
        app.secret_key = get_facebook_client_id_and_secret()[1]
    app.run(port=5000, debug=True)
