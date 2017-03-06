# -*- coding: utf-8 -*-
"""
Created on Mon Mar 06 00:20:05 2017

@author: david
"""
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import json
import string
import spotipy
import requests
from spotipy.oauth2 import SpotifyClientCredentials
import sys
from unidecode import unidecode

from audio_features2 import runner 


#Genius
base_url = "https://api.genius.com"

headers = {'Authorization': 'Bearer -f1FowZVoajVSULxNXkqvtwCzwrxlkWqtozx7cN_aP3CjHGhji6K4ySWiJOj1IH1'}

#Spotify#
SPOTIPY_CLIENT_ID = "3a883c6b1fc4405ba45608df5e60e09f"
SPOTIPY_CLIENT_SECRET = "9d9f70d6ff864760a2503b6e8b622c09"

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
    #q.ask()
    track_results = None
    name_results = None
    #import pdb; pdb.set_trace()
    if q.artist!='' and q.track!='':
        #import pdb; pdb.set_trace()
        #name_results = sp.search(q=str(q.artist), limit=q.num)
        track_results = sp.search(q=str(q.track), limit=q.num)
        return track_results
    elif q.artist!='':
        #import pdb; pdb.set_trace()
        name_results = sp.search(q=str(q.artist), limit=q.num)
        return name_results
    
    else:
        #import pdb; pdb.set_trace()
        name_results = sp.search(q=str(q.artist), limit=1)
        return name_results
    
def dumper_artist(artist='', num=50):  
    g = grabber(artist=artist, num=num)
    
    # Set Destination folder for analysis    
    # get query results from Query object

    final = []
    if g:
        tids = []
        for results in g['tracks']['items']:
            lyric = runner(artist=artist, track=results['name']) 

            tids.append(results['uri']) 
            
            ar = results['artists'][0]['name']
            ar = ar.encode('utf-8') 
            tr = results['name'].encode('utf-8')
            featured_artists = []
            track_popularity = results['popularity']
            
            features = sp.audio_features(tids)
            for i, feature in enumerate(features):
                #import pdb; pdb.set_trace()
    #            data[u'feature'] = json.dumps(feature, indent=4)
                #import pdb; pdb.set_trace()
    #            analysis = sp._get(feature['analysis_url'])
                
                analysis = sp._get(feature[u'analysis_url'])
 
                #import pdb; pdb.set_trace()
                album = results['album']['name']

                #data['analysis'] = json.dumps(analysis, indent=4)
    #            data[u'name'] = json.dumps(t['name'], indent=4) # track name
                queryed = sp._get(results['album']['artists'][0][u'href'])
                
                genres = queryed[u'genres']

                artist_popularity = queryed[u'popularity']
                explicit = results['explicit']
                followers = queryed['followers']['total']
                
                print ar+' has '+str(followers)+ ' followers, and has a '+str(artist_popularity)+"/100"
                print tr + ' got a '+ str(track_popularity)+"/100"
                #import pdb; pdb.set_trace()
    #            data[u'artist'] = json.dumps(t['artists'][0]['name'])
    
                
                for singer in results['artists']:
                    if ar not in singer['name']:
                        featured_artists.append(singer['name'])
                
                if "(" in tr:
                    new = tr.partition(" (")
                    feats = new[2]
                    feats = feats.strip(" )")
                    feats = feats.strip("feat. ")
                    featured_artists.append(feats)
                    #import pdb; pdb.set_trace()
    #            images = feat_artists[u'images']
    #            track_title = '{}'.format(a)+'_'+'{}'.format(t)
                tracking = {u'lyrics': lyric, u'album':album, u'artist':ar, u'featured_artists': featured_artists, u'track':tr, 
                         u'popularity': track_popularity, u'genres': genres, u'artist_popularity': artist_popularity, u'explicit': explicit,
                         u'feature':feature, u'analysis':analysis}
            final.append(tracking)
                 
        #import pdb; pdb.set_trace()       
    return final
    
    
            
            
            
            
            
            