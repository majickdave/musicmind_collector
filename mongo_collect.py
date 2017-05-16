# -*- coding: utf-8 -*-
"""
Created on Thu Mar 09 07:25:30 2017

@author: david
"""

import pprint
from pymongo.mongo_client import MongoClient
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import json
from datetime import datetime
import urllib
import string


USERNAME = raw_input('Enter Spotify Username:')
# USERNAME = 'majickdave'

URI = "mongodb://MusicMind:6jlewvwvuBVqJls4@features-shard-00-00-edm1t.mongodb.net:27017,features-shard-00-01-edm1t.mongodb.net:27017,features-shard-00-02-edm1t.mongodb.net:27017/features?ssl=true&replicaSet=features-shard-0&authSource=admin"
client = MongoClient(URI)
db = client['MetaMind']
posts = db.posts

#Spotify#
SPOTIPY_CLIENT_ID = "3a883c6b1fc4405ba45608df5e60e09f"
SPOTIPY_CLIENT_SECRET = "3168b907abf54925b8e482797f0eb718"
REDIRECT_URI = "http://localhost:8888/"
userScope = {"account": "user-read-private", "top": "user-top-read", "email": "user-read-email"}

client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
sp.trace=False


token = util.prompt_for_user_token(USERNAME, scope=userScope['account'], client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=REDIRECT_URI)

top_tracks = []

if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_saved_tracks(limit=50)
    for item in results['items']:
        track = item['track']
        #import pdb;pdb.set_trace()
        track_image_url = track['album']['images'][0]['url']
        artist_name = track['artists'][0]['name']
        track_name = track['name']
        album_name = track['album']['name']
        artist_url = track['artists'][0]['href']

        track_popularity = track['popularity']
        features = sp.audio_features([track['id']])

        related_popularity = {}
        related_genres = {}
        related_followers = {}
        for x in [artist_name, track_name, album_name]:
            	for y in x:
            		for letter in y:
		            	if letter in '*()"|?\/:<>': 
		                	x = string.replace(y, letter, '')

        for artist in track['artists']:
        	artist_href = sp.artist(artist['id'])
        	#import pdb;pdb.set_trace()
        	try:
        		image_url = artist_href['images'][0]['url']
        		urllib.urlretrieve(image_url, '/Users/majic/NetBeansProjects/OrbPlot/build/classes/data/'+artist['id']+'.jpeg')
        	except IOError as e:
        		#print artist['name']
        		#import pdb;pdb.set_trace()
        		pass
        	except IndexError as e1:
        		pass

        	related_popularity[artist['name']] = artist_href['popularity']
        	related_genres[artist['name']] = artist_href['genres']
        	related_followers[artist['name']] = artist_href['followers']
            
        	

        #import pdb;pdb.set_trace()

        urllib.urlretrieve(track_image_url, '/Users/majic/NetBeansProjects/OrbPlot/build/classes/data/'+track['id']+'.jpeg')

        top_tracks.append({"track_name": track_name, "artist_name" : artist_name, 
        	"album_name": album_name, "track_popularity": track_popularity, "artist_popularity": related_popularity[artist_name],
        	"related_artist_popularity": related_popularity, "features": features, "followers": related_followers[artist_name], 
            "genres": related_genres[artist_name], "artistID": track['artists'][0], "trackID": track['id']})

else:
    print "Can't get token for", username


#import pdb;pdb.set_trace()

json = json

# file_name = USERNAME+str(datetime.now())

with open('/Users/majic/NetBeansProjects/OrbPlot/build/classes/data/planets.json', 'w') as fp:
    fp.write(json.dumps(top_tracks, indent=4))



# pprint.pprint(collection)





