# -*- coding: utf-8 -*-
"""
Created on Mon Mar 06 00:20:05 2017

@author: david
"""
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import json
import string
import spotipy
import requests
from spotipy.oauth2 import SpotifyClientCredentials
import sys
from unidecode import unidecode
from audio_features2 import runner
from pymongo.mongo_client import MongoClient

URI = "mongodb://MusicMind:Dsam456$%^@metamind-shard-00-00-edm1t.mongodb.net:27017,metamind-shard-00-01-edm1t.mongodb.net:27017,metamind-shard-00-02-edm1t.mongodb.net:27017/MetaMind?ssl=true&replicaSet=MetaMind-shard-0&authSource=admin"
client = MongoClient(URI)
db = client['MetaMind']
posts = db.posts



#Genius
base_url = "https://api.genius.com"
headers = {'Authorization': 'Bearer zoQKrP1yTyzy04I_DaXzOSqWXPR32YPXyolLER1rCAvqxefu2Zcea-pqs5REBixt'}

#Spotify#
SPOTIPY_CLIENT_ID = "3a883c6b1fc4405ba45608df5e60e09f"
SPOTIPY_CLIENT_SECRET = "eb76bde0a9924f9eb109bcefa37400fc"

client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
sp.trace=False


#seeds = [sp.search(x, limit=30) for x in['jeremih', 'drake', 'eminem', 'jayz', "josh pan"]]
#seeds = [x['tracks']['items'][0]['uri'] for x in seeds]
#recs=[x in sp.recommendation_genre_seeds for x in seeds]
#
#s = sp.recommendations(seed_artists=recs, seed_genres=['hip-hop'], limit=20)
#import pdb;pdb.set_trace()


# Search class
class Query:
    num = 0
    def __init__(self, artist, track, num):
        self.artist=artist
        self.track=track
        self.num=num
        
    @classmethod
    def query_track(self, artist='', track='', num=10):
        return sp.search(artist+' '+track, type='track', limit=num) 
    
    @classmethod
    def query_artist(self, artist='', num=50):
        return sp.search(artist, type='track', limit=num) 
    
    @classmethod
    def query_user(self, user='', num=5):
        return sp.search()
    
    def ask(self, artist='', track='', num=0):

        self.artist = str(raw_input('Artist Name? '))
        if len(sys.argv) > 1:
            self.artist = ' '.join(sys.argv[1:])
        self.track = str(raw_input('Track? '))
        
        #self.num = int(raw_input('how many songs? '))
        if self.artist not in string.printable or self.track not in string.printable:
            q = self
            return q
        



# Lyrics from rap genius
def lyrics_from_song_api_path(song_api_path):
    
    song_url = base_url + song_api_path.encode('utf-8')
    response = requests.get(song_url, headers=headers)
    json = response.json()
    path = json["response"]["song"]["path"]
    
      #gotta go regular html scraping... come on Genius
    page_url = "https://genius.com" + path
    page = requests.get(page_url)
    html = BeautifulSoup(page.text, "html.parser")
    #remove script tags that they put in the middle of the lyrics
    #import pdb; pdb.set_trace(); 
    [h.extract() for h in html('script')]
    #at least Genius is nice and has a tag called 'lyrics'!
    lyrics = html.find("lyrics").get_text()
    title = html.find("title").get_text()
    #import pdb; pdb.set_trace()
    return [title, lyrics]


#data analysis package
def framer(lyric):
    h = np.array(lyric.split(' '))
    hook = pd.Series(h)
    h = pd.DataFrame(hook.value_counts())
    return h


#Package Query 
def grabber(artist='', track='', num=0):
       
    q = Query(artist, track, num)

    track_results = None
    name_results = None

    if q.artist!='' and q.track!='':

        track_results = sp.search(q=str(q.track), limit=q.num)
        return track_results
    elif q.artist!='':

        name_results = sp.search(q=str(q.artist), limit=q.num)
        return name_results
    
    else:

        name_results = sp.search(q=str(q.artist), limit=1)
        return name_results

# Query spotify and Genius for Metadata and lyrics -Final API to be developed with Spotify Approval   
def dumper_artist(artist='', num=50):
    time.clock()
    g = grabber(artist=artist, num=num)

    if g:
        
        for results in g['tracks']['items']:
            #track_json = json                                   # Instantiate JSON if needed 
            lyric = runner(artist=artist, track=results['name']) # instantiate lyrics

            ar = results['artists'][0]['name']                   # set artist from spotify       
            ar = ar.encode('utf-8')                              # Fix Encoding                 - may need work
            tr = results['name']                                 # set track from spotify
            tr = tr.encode('utf-8')
            featured_artists = []                                # start featured artists list
            track_popularity = results['popularity']             # Get track popularity
            features = sp.audio_features([results['uri']])       # Get audio features
            
            album = results['album']['name']                     # Get album

            queryed = sp._get(results['album']['artists'][0][u'href']) # Query the other related artists
            
                             #*************** TO BE DEVELOPED *******************
#            genres = results[u'genres']
            genres = queryed[u'genres']                                 # Genres

            artist_popularity = queryed[u'popularity']
            explicit = results['explicit']
            
#            followers = results[u'followers'][u'total']                       # maybe later
            followers = queryed['followers']['total']
            
            print ar + ' has '+str(followers)+' followers, is rated '+str(artist_popularity)+' and their track, '+ tr + ' got a '+ str(track_popularity),
            print ', and contains genres: ', genres,
            
            for i, feature in enumerate(features):
                
                analysis = sp._get(feature[u'analysis_url'])

                for singer in results[u'artists']:
                    if ar not in singer[u'name']:
                        featured_artists.append(singer[u'name'])
                
                if "(" in tr:
                    new = tr.partition(" (")
                    feats = new[2]
                    feats = feats.strip(" )")
                    feats = feats.strip("feat. ")
                    featured_artists.append(feats)

            tracking = {u'lyrics': lyric, u'album':album, u'artist':ar, u'featured_artists': featured_artists, 
                        u'track':tr, u'popularity': track_popularity, u'genres': genres, u'followers': followers, u'followers': followers, 
                        u'artist_popularity': artist_popularity, u'explicit': explicit, u'feature':feature, u'analysis':analysis}
        
             
     
            u_title = artist+' - '+album+' - '+tr
            for x in u_title:
                if x in '*()"|?\/:<>': 
                    u_title = string.replace(u_title, x, '')
                    
            #file_name = u_title
            ##################   MONGO DB ###################
            
            post_id = posts.insert_one(tracking).inserted_id
            print "mongo post id:", post_id,
            # We can save this somewhere else for reference
                                  
#            with open(file_name+'_'+post_id+'.json', 'w') as fp:
#                fp.write((track_json.dumps(tracking, indent=4)))
                    
    
    
    
            
            
            
            
            
            