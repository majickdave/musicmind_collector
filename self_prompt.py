import spotipy
import json
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.util import prompt_for_user_token

SPOTIPY_CLIENT_ID = "3a883c6b1fc4405ba45608df5e60e09f"
SPOTIPY_CLIENT_SECRET = "3168b907abf54925b8e482797f0eb718"
REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = {"account": "user-read-private", "top": "user-top-read", "email": "user-read-email"}

client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
sp.trace=False

prompt_for_user_token("majickdave", scope=SCOPE, client_id=SPOTIPY_CLIENT_ID,
                                   client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=REDIRECT_URI)