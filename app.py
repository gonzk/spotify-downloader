import json
import os
import secrets
import string
from urllib.parse import urlencode

import requests
from flask import (
    abort,
    Flask,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

import songs

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

# Spotify API endpoints
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
ME_URL = 'https://api.spotify.com/v1/me/tracks'

# Start 'er up
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


# Home Page to Login to Spotify
@app.route('/')
def index():
    return render_template('index.html')


# Login/out to/of Spotify
@app.route('/<loginout>')
def login(loginout):
    """
    Login or logout user.
    Note:
        Login and logout process are essentially the same. Logout forces
        re-login to appear, even if their token hasn't expired.
    """
    state = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
    )

    # Request authorization from user
    scope = 'user-library-read user-read-private playlist-modify-private playlist-modify-public'

    if loginout == 'logout':
        payload = {
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'state': state,
            'scope': scope,
            'show_dialog': True,
        }
    elif loginout == 'login':
        payload = {
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'state': state,
            'scope': scope,
        }
    else:
        abort(404)

    res = make_response(redirect(f'{AUTH_URL}/?{urlencode(payload)}'))
    res.set_cookie('spotify_auth_state', state)

    return res


@app.route('/callback')
def callback():
    error = request.args.get('error')
    code = request.args.get('code')
    state = request.args.get('state')
    stored_state = request.cookies.get('spotify_auth_state')

    # Check state
    if state is None or state != stored_state:
        app.logger.error('Error message: %s', repr(error))
        app.logger.error('State mismatch: %s != %s', stored_state, state)
        abort(400)

    # Request tokens with code we obtained
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }

    res = requests.post(TOKEN_URL, auth=(CLIENT_ID, CLIENT_SECRET), data=payload)
    res_data = res.json()

    if res_data.get('error') or res.status_code != 200:
        app.logger.error(
            'Failed to receive token: %s',
            res_data.get('error', 'No error information received.'),
        )
        abort(res.status_code)

    # Load tokens into session
    session['tokens'] = {
        'access_token': res_data.get('access_token'),
        'refresh_token': res_data.get('refresh_token'),
    }

    return redirect(url_for('lib'))


@app.route('/lib')
def lib():
    """
    App
    """

    # Check for tokens
    if 'tokens' not in session:
        app.logger.error('No tokens in session.')
        abort(400)

    headers = {'Authorization': f"Bearer {session['tokens'].get('access_token')}",
               'Content-Type': 'application/json'}

    res = requests.get(ME_URL, headers=headers)
    res_data = res.json()

    if res.status_code != 200:
        app.logger.error(
            'Failed to get profile info: %s',
            res_data.get('error', 'No error message returned.'),
        )
        abort(res.status_code)

    return render_template('lib.html')


@app.route('/download', methods=['GET', 'POST'])
def download():
    """
    Download songs
    :return:
    """
    if 'tokens' not in session:
        app.logger.error('No tokens in session.')
        abort(400)

    if request.method == 'POST':
        headers = {'Authorization': f"Bearer {session['tokens'].get('access_token')}"}
        uri = request.form.get('uri')

        res = requests.get(ME_URL, headers=headers)
        res_data = res.json()

        if res.status_code != 200:
            app.logger.error(
                'Failed to get profile info: %s',
                res_data.get('error', 'No error message returned.'),
            )
            abort(res.status_code)

        tracks = songs.get_playlist_songs(headers, uri[len('spotify:playlist:'):])
        song = songs.get_song_and_artist(tracks)
        ids = songs.find_songs(song)
        # songs.write_songs_to_file(ids)

        songs.download_songs(ids)
        # response = make_response(render_template('download.html', file="Spotify-Downloads.zip"))
        # response.headers["Content-Disposition"] = f'inline; filename=Spotify-Downloads.zip'
    return render_template('download.html')


@app.route('/refresh_token')
def refresh_token():
    """
    Refresh access token
    """

    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': session.get('tokens').get('refresh_token'),
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    res = requests.post(
        TOKEN_URL, auth=(CLIENT_ID, CLIENT_SECRET), data=payload, headers=headers
    )
    res_data = res.json()

    # Load new token into session
    session['tokens']['access_token'] = res_data.get('access_token')

    return json.dumps(session['tokens'])

# import base64
# import io
# import json
# import os
# import pathlib
# import secrets
# import string
# import zipfile
# from urllib.parse import urlencode
#
# import flask
# import requests
#
# from flask import (
#     abort,
#     Flask,
#     make_response,
#     redirect,
#     render_template,
#     request,
#     session,
#     url_for,
# )
#
# # COMMENT THIS OUT when spotify is no longer in development
#
#
# # os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
#
#
# # Client info
# CLIENT_ID = os.getenv('CLIENT_ID')
# CLIENT_SECRET = os.getenv('CLIENT_SECRET')
# REDIRECT_URI = os.getenv('REDIRECT_URI')
#
# # Spotify API endpoints
# AUTH_URL = 'https://accounts.spotify.com/authorize'
# TOKEN_URL = 'https://accounts.spotify.com/api/token'
# ME_URL = 'https://api.spotify.com/v1/me/tracks'
#
# # Start 'er up
# app = Flask(__name__)
# app.secret_key = os.getenv('SECRET_KEY')
# import songs
#
#
# # Home Page to Login to Spotify
# @app.route('/')
# def index():
#     return render_template('index.html')
#
#
# # Login/out to/of Spotify
# @app.route('/<loginout>')
# def login(loginout):
#     """
#     Login or logout user.
#     Note:
#         Login and logout process are essentially the same. Logout forces
#         re-login to appear, even if their token hasn't expired.
#     """
#     state = ''.join(
#         secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
#     )
#
#     # Request authorization from user
#     scope = 'user-library-read user-read-private'
#
#     if loginout == 'logout':
#         payload = {
#             'client_id': CLIENT_ID,
#             'response_type': 'code',
#             'redirect_uri': REDIRECT_URI,
#             'state': state,
#             'scope': scope,
#             'show_dialog': True,
#         }
#     elif loginout == 'login':
#         payload = {
#             'client_id': CLIENT_ID,
#             'response_type': 'code',
#             'redirect_uri': REDIRECT_URI,
#             'state': state,
#             'scope': scope,
#         }
#     else:
#         abort(404)
#
#     res = make_response(redirect(f'{AUTH_URL}/?{urlencode(payload)}'))
#     res.set_cookie('spotify_auth_state', state)
#
#     return res
#
#
# @app.route('/callback')
# def callback():
#     error = request.args.get('error')
#     code = request.args.get('code')
#     state = request.args.get('state')
#     stored_state = request.cookies.get('spotify_auth_state')
#
#     # Check state
#     if state is None or state != stored_state:
#         app.logger.error('Error message: %s', repr(error))
#         app.logger.error('State mismatch: %s != %s', stored_state, state)
#         abort(400)
#
#     # Request tokens with code we obtained
#     payload = {
#         'grant_type': 'authorization_code',
#         'code': code,
#         'redirect_uri': REDIRECT_URI,
#     }
#
#     res = requests.post(TOKEN_URL, auth=(CLIENT_ID, CLIENT_SECRET), data=payload)
#     res_data = res.json()
#
#     if res_data.get('error') or res.status_code != 200:
#         app.logger.error(
#             'Failed to receive token: %s',
#             res_data.get('error', 'No error information received.'),
#         )
#         abort(res.status_code)
#
#     # Load tokens into session
#     session['tokens'] = {
#         'access_token': res_data.get('access_token'),
#         'refresh_token': res_data.get('refresh_token'),
#     }
#
#     return redirect(url_for('lib'))
#
#
# @app.route('/lib')
# def lib():
#     """
#     App
#     """
#
#     # Check for tokens
#     if 'tokens' not in session:
#         app.logger.error('No tokens in session.')
#         abort(400)
#
#     headers = {'Authorization': f"Bearer {session['tokens'].get('access_token')}"}
#
#     res = requests.get(ME_URL, headers=headers)
#     res_data = res.json()
#
#     if res.status_code != 200:
#         app.logger.error(
#             'Failed to get profile info: %s',
#             res_data.get('error', 'No error message returned.'),
#         )
#         abort(res.status_code)
#
#     return render_template('lib.html', data=res_data, tokens=session.get('tokens'))
#
#

#
#
# @app.route('/refresh_token')
# def refresh_token():
#     """
#     Refresh access token
#     """
#
#     payload = {
#         'grant_type': 'refresh_token',
#         'refresh_token': session.get('tokens').get('refresh_token'),
#     }
#     headers = {'Content-Type': 'application/x-www-form-urlencoded'}
#
#     res = requests.post(
#         TOKEN_URL, auth=(CLIENT_ID, CLIENT_SECRET), data=payload, headers=headers
#     )
#     res_data = res.json()
#
#     # Load new token into session
#     session['tokens']['access_token'] = res_data.get('access_token')
#
#     return json.dumps(session['tokens'])
#
#
# def download_songs(tracks):
#     """
#     """
#     # song_ids = find_songs(songs=songs)
#     song_ids = ['57vrqCENNPc']
#
#     for s in song_ids:
#         songs.download_song(s)
#
#     # shutil.make_archive('Spotify-Downloads', 'zip', '/'.join(os.getcwd().split('/')[:3]) + '/Downloads/Spotify2YT')
#     base_path = pathlib.Path('/'.join(os.getcwd().split('/')[:3]) + '/Downloads/Spotify2YT')
#     data = io.BytesIO()
#     with zipfile.ZipFile(data, mode='w') as z:
#         for f_name in base_path.iterdir():
#             z.write(f_name)
#     data.seek(0)
#     return flask.send_file(
#         data,
#         mimetype='application/zip',
#         as_attachment=True,
#         attachment_filename='data.zip'
#     )
#     print("All songs have been downloaded")
