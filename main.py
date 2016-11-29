"""Entrypoint for Anytown Mapper web application."""

from datetime import datetime

from flask import flash
from flask import Flask
from flask import g
from flask import jsonify
from flask import make_response
from flask import render_template
from flask import request
from flask import send_file
from flask import session
from flask import redirect
from flask import url_for

import cStringIO
import facebook
import psycopg2
import os
import requests
import sqlite3
import urlparse
import urllib

from anytownlib.map_cache import fetch_from_map_cache
from anytownlib.map_cache import fetch_map_from_s3
from anytownlib.map_cache import insert_into_map_cache
from anytownlib.map_cache import upload_map_to_s3
from anytownlib.mapmaker import make_image
from anytownlib.maps import geocode_coords
from anytownlib.user_profiles import get_formatted_user_location_history
from anytownlib.user_profiles import get_user_info
from anytownlib.user_profiles import update_user
from anytownlib.user_profiles import update_user_location_history

app = Flask(__name__)
app.config['DATABASE'] = 'anytown-mapper'
app.config['PRODUCTION'] = (True if os.environ.get('HEROKU_PROD', None)
                            else False)
if app.config['PRODUCTION']:
    print 'App in production environment'
    app.config['USER'] = None
    app.config['PASSWORD'] = None
else:
    print 'App in development environment'
    with open('postgres_credentials.txt', 'r') as f:
        app.config['USER'] = f.readline()
        app.config['PASSWORD'] = f.readline()


def init_db():
    """Initialize database with schema."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def get_db():
    """Get database connection object in testing or dev/prod environments."""
    db = getattr(g, '_database', None)
    if db is None:
        with app.app_context():
            if app.config.get('TESTING'):
                db = g._database = sqlite3.connect(app.config['DATABASE'])
                db.row_factory = sqlite3.Row
                db.execute('PRAGMA foreign_keys = ON')
            elif app.config['PRODUCTION']:
                components = urlparse.urlparse(os.environ['DATABASE_URL'])
                db = g._database = psycopg2.connect(
                    database=components.path[1:],
                    user=components.username,
                    password=components.password,
                    host=components.hostname
                )
            else:
                db = g._database = psycopg2.connect(
                    'dbname={0} user={1} password={2}'.format(
                        app.config['DATABASE'], app.config['USER'],
                        app.config['PASSWORD']))
    return db


def get_google_maps_api_key(prod, test=False):
    """Get Google Maps API key."""
    if prod:
        return os.environ.get('GOOGLE_API_KEY', None)
    cur = get_db().cursor()
    api_key = None
    if test:
        api_key = cur.execute(
            'SELECT api_key FROM credentials WHERE provider="google"'
        ).fetchone()
    else:
        cur.execute("SELECT api_key FROM credentials WHERE provider='google'")
        api_key = cur.fetchone()
    return api_key[0]


def get_facebook_client_id_and_secret(prod, test=False):
    """Get Facebook client ID and client secret."""
    if test:
        cur = get_db().cursor()
        stmt = 'SELECT api_key FROM credentials WHERE provider=?'
        client_id = cur.execute(stmt, ('facebook_client_id', )).fetchone()[0]
        client_secret = cur.execute(
            stmt, ('facebook_client_secret', )).fetchone()[0]
        return client_id, client_secret
    if prod:
        return (os.environ.get('FB_CLIENT_ID', None),
                os.environ.get('FB_CLIENT_SECRET', None))

    cur = get_db().cursor()
    stmt = "SELECT api_key FROM credentials WHERE provider=%s"
    cur.execute(stmt, ('facebook_client_id', ))
    client_id = cur.fetchone()[0]
    cur.execute(stmt, ('facebook_client_secret', ))
    client_secret = cur.fetchone()[0]
    return client_id, client_secret


def get_aws_client_id_and_secret(prod, test=False):
    """Get AWS client ID and client secret."""
    if test:
        cur = get_db().cursor()
        stmt = 'SELECT api_key FROM credentials WHERE provider=?'
        client_id = cur.execute(stmt, ('aws_client_id', )).fetchone()[0]
        client_secret = cur.execute(
            stmt, ('aws_client_secret', )).fetchone()[0]
        return client_id, client_secret
    if prod:
        return (os.environ.get('AWS_CLIENT_ID', None),
                os.environ.get('AWS_CLIENT_SECRET', None))

    cur = get_db().cursor()
    stmt = "SELECT api_key FROM credentials WHERE provider=%s"
    cur.execute(stmt, ('aws_client_id', ))
    client_id = cur.fetchone()[0]
    cur.execute(stmt, ('aws_client_secret', ))
    client_secret = cur.fetchone()[0]
    return client_id, client_secret


@app.route('/', methods=['GET'])
def index():
    """Index handler."""
    name = session.get('name')
    user_id = session.get('user_id')
    return render_template(
        'index.html', stylesheet_href=url_for('static', filename='style.css'),
        script_src=url_for('static', filename='script.js'),
        api_key=get_google_maps_api_key(app.config['PRODUCTION']),
        name=name, user_id=user_id)


@app.route('/user/<int:user_id>', methods=['GET'])
def user_profile(user_id):
    """User profile handler."""
    user_profile = get_user_info(get_db(), user_id)
    if user_profile is None:
        return 'User does not exist', 404
    name = session.get('name')
    return render_template(
        'profile.html',
        stylesheet_href=url_for('static', filename='style.css'),
        script_src=url_for('static', filename='user_profile.js'),
        api_key=get_google_maps_api_key(app.config['PRODUCTION']),
        name=name, user_id=user_id, user_profile=user_profile)


@app.route('/user/<int:user_id>/history', methods=['GET'])
def get_user_history(user_id):
    """Get user history handler."""
    unix_timestamp = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
    since_timestamp = unix_timestamp - 604800  # hardcode to one week
    markers = get_formatted_user_location_history(
        get_db(), user_id, since_timestamp)
    return jsonify({'results': markers})


@app.route('/user/<int:user_id>/history', methods=['POST'])
def update_user_history(user_id):
    """Update user history handler."""
    place_id = request.args.get('place_id')
    if place_id is None:
        return 'place_id parameter is not present', 400
    update_user_location_history(get_db(), user_id, place_id)
    return ''


@app.route('/map', methods=['GET'])
def get_map():
    """Map generator handler given city, region, country_name, country_code."""
    city = request.args.get('city').strip() or ''
    if len(city) == 0:
        return 'city parameter is not present', 400
    # region made optional because of Singapore
    region = request.args.get('region')
    if region is not None:
        region = region.strip()
    country_name = request.args.get('country_name').strip() or ''
    if len(country_name) == 0:
        return 'country_name parameter is not present', 400
    country_code = request.args.get('country_code').strip() or ''
    if len(country_code) == 0:
        return 'country_code parameter is not present', 400
    search_query = ' '.join(filter(None, (city, region, country_code)))
    api_key = get_google_maps_api_key(app.config['PRODUCTION'])
    coords, place_id = geocode_coords(search_query, api_key)

    aws_client_id, aws_client_secret = get_aws_client_id_and_secret(
        app.config['PRODUCTION'])

    existing_map_cache = fetch_from_map_cache(get_db(), place_id)
    im = None
    if existing_map_cache is None:
        im = make_image(
            city, region, country_name, country_code, coords, api_key)
        insert_into_map_cache(
            get_db(), place_id, coords, city, region,
            country_name, country_code)
        upload_map_to_s3(place_id, im, aws_client_id, aws_client_secret)
    else:
        im = fetch_map_from_s3(place_id, aws_client_id, aws_client_secret)
    if im is None:
        im = make_image(
            city, region, country_name, country_code, coords, api_key)

    stream = cStringIO.StringIO()
    im.save(stream, 'PNG')
    stream.seek(0)

    response = make_response(send_file(stream, mimetype='image/png'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


@app.route('/login', methods=['GET'])
def login():
    """Login handler that initiates Facebook OAuth2 flow."""
    client_id, client_secret = get_facebook_client_id_and_secret(
        app.config['PRODUCTION'])
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

    client_id, client_secret = get_facebook_client_id_and_secret(
        app.config['PRODUCTION'])
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
        app.secret_key = get_facebook_client_id_and_secret(
            app.config['PRODUCTION'])[1]
    app.run(port=5000)
