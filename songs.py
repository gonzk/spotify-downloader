import os
from urllib.parse import urlencode

import requests
import youtube_dl
from youtubesearchpython import VideosSearch

DEVELOPER_KEY = 'AIzaSyBUiyiLo-BHAF75MRfSOpy_uDAVquc80G0'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def get_liked_tracks(headers):
    """
    :param headers: contains the authorization header
    :return: a list of all the user's liked songs from Spotify
    """
    ep = 'https://api.spotify.com/v1/me/tracks'
    headers = headers
    param = {
        'limit': 50,
    }
    lookup_url = f"{ep}?{urlencode(param)}"
    res = requests.get(url=lookup_url, headers=headers)

    data = res.json()
    tracks = data['items']

    while data["next"]:
        data = requests.get(data["next"], headers=headers).json()
        tracks.extend(data["items"])

    return tracks


def get_playlists(headers):
    ep = "https://api.spotify.com/v1/me/playlists"

    headers = headers
    param = {
        'limit': 50,
    }
    lookup_url = f"{ep}?{urlencode(param)}"
    res = requests.get(url=lookup_url, headers=headers)

    data = res.json()
    response = data['items']

    while data["next"]:
        data = requests.get(data["next"], headers=headers).json()
        response.extend(data["items"])

    pl = []
    for r in response:
        s = {r[0]['name'].lowercase(): r[0]['id']}
        pl.append(s)

    return pl


def get_playlist_songs(headers, playlist_id):
    ep = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'

    headers = headers
    param = {
        'limit': 50,
    }
    lookup_url = f"{ep}?{urlencode(param)}"
    res = requests.get(url=lookup_url, headers=headers)

    data = res.json()
    print(data)
    response = data['items']

    while data["next"]:
        data = requests.get(data["next"], headers=headers).json()
        response.extend(data["items"])

    return response


def get_song_and_artist(tracks):
    """
    :param tracks: a list of song information from the Spotify API
    :return: a list of dictionary of {song : artist}
    """
    songs = []
    for s in tracks:
        song = s['track']['name']
        artist = s['track']['artists'][0]['name']
        pl = {song: artist}
        songs.append(pl)

    print(songs)

    return songs


def find_song(track):
    try: 
        search = VideosSearch(f"{list(track.keys())[0]} - {list(track.values())[0]} Lyrics", limit=1)
        r = search.result()
        #if len(r) < 1:
     #   return
    except:
        search = VideosSearch(f"{list(track.keys())[0]} - {list(track.values())[0]}", limit=1)
        r = search.result()
    return r['result'][0]['id']


def find_songs(songs):
    ids = []
    for s in songs:
        ids.append(find_song(s))

    print('found the songs!')
    return ids


def write_songs_to_file(ids):
    file = open('song_ids.txt', 'w')

    for i in ids:
        file.write(i)
        file.write('\n')
    file.close()

    return None


def hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def download_song(song_id):
    SAVE_PATH = '/'.join(os.getcwd().split('/')[:3]) + '/Spotify-Downloads'
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'progress_hooks': [hook],
        "--no-check-certificate": True,
        'outtmpl': SAVE_PATH + '/%(title)s.%(ext)s'
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={song_id}"])


def download_songs(ids):
    for id in ids:
        download_song(id)
    return True
