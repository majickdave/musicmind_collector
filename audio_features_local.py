# -*- coding: utf-8 -*-
"""
Created on Fri Feb 03 13:32:45 2017

@author: david
"""


# shows acoustic features for tracks for the given artist
#from __future__ import print_function    # (at top of module)

from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import json
import string
import spotipy
import requests
from spotipy.oauth2 import SpotifyClientCredentials
import time
import sys
from unidecode import unidecode
from pymongo.mongo_client import MongoClient

URI = "mongodb://MusicMind:Dsam456$%^@features-shard-00-00-edm1t.mongodb.net:27017,features-shard-00-01-edm1t.mongodb.net:27017,features-shard-00-02-edm1t.mongodb.net:27017/features?ssl=true&replicaSet=features-shard-0&authSource=admin"
client = MongoClient(URI)
db = client['MetaMind']
posts = db.posts

#Genius
base_url = "https://api.genius.com"

headers = {'Authorization': 'Bearer tQoh0aD9H5Od9EmoORVzKkki48MEG4K6Kyy8zCQvO8lq1Rjx1IVqEqUQMUgqJTHv'}

#Spotify#
SPOTIPY_CLIENT_ID = "3a883c6b1fc4405ba45608df5e60e09f"
SPOTIPY_CLIENT_SECRET = "3168b907abf54925b8e482797f0eb718"

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


#Dump Query into JSON
def dumper(artist='', track='', num=1):
    g = grabber(artist=artist, num=num)

    if g:
        
        for results in g['tracks']['items']:
            #track_json = json
            try:                                   # Instantiate JSON if needed 
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
                print features,
                
                for i, feature in enumerate(features):
                    
                    analysis = sp._get(feature[u'analysis_url'])
                    # Send to Hadoop, or Big Store
    
                    for singer in results[u'artists']:
                        if ar not in (singer[u'name']).encode('utf-8'):
                            featured_artists.append((singer[u'name']).encode('utf-8'))
                    
                    if "(" in tr:
                        new = tr.partition(" (")
                        feats = new[2]
                        feats = feats.strip(" )")
                        feats = feats.strip("feat. ")
                        featured_artists.append(feats)
    
                tracking = {u'lyrics': lyric, u'album':album, u'artist':ar, u'featured_artists': featured_artists, 
                            u'track':tr, u'popularity': track_popularity, u'genres': genres, u'followers': followers, 
                            u'followers': followers, u'artist_popularity': artist_popularity, u'explicit': explicit, 
                            u'feature':feature} 
            except ValueError as e:
                print e,
                dumped = dumper(artist=ar, track=tr, num=1)
                tracking = dumped
                pass
            
            # Use analysis later
            # u'analysis':analysis
        
            # SAVE LOCAL IF NEED
            #################################################
            #            u_title = artist+' - '+album+' - '+tr
            #            for x in u_title:
            #                if x in '*()"|?\/:<>': 
            #                    u_title = string.replace(u_title, x, '')
                    
            #
            #            with open(file_name+'_'+post_id+'.json', 'w') as fp:
            #                fp.write((track_json.dumps(tracking, indent=4)))
            ##################   MONGO DB ###################
            
            post_id = posts.insert_one(tracking).inserted_id
            print "mongo post id:", post_id,

                                  

                    
    
    

def runner(artist='', track=''):

    search_url = base_url + "/search"
    response = None
    data = None
    #title = track.split('_')[-1]; names = None
    featured_artist = None
    featured = None
    artist_choice = artist; track_choice = track
    #print artist_choice, track_choice
    

    # Manual Override
#    artist_choice = "21 savage & metro boomin"; track_choice = "x"
    # Manual Override

    if '-' in track:
        extras = track_choice.partition(' -')
        track_choice = extras[0]
        featured = extras[2]
        print artist, track_choice, "featured", featured
    if '(' in track:
        #import pdb; pdb.set_trace()
        extras = track_choice.partition(' (')
        track_choice = extras[0]
        featured_artist = '('+extras[2]
        print artist, track_choice, "featuring", featured
    
         
    if '21 savage' in artist.lower():
        artist_choice = '21 savage & metroboomin'
        
    n = None
    data = {'q': artist_choice+' '+track_choice}
    response = requests.get(search_url, data=data, headers=headers) 
    #print data, response==True
    
    if not response:
        try:
            artist_choice = artist.encode('utf-8')

        except UnicodeDecodeError as e:
            
            byte = e[1]
            if byte in artist:
                #import pdb; pdb.set_trace()
                artist_choice = unidecode(byte.decode('utf-8'))
                print artist_choice,
        
        #import pdb; pdb.set_trace()
        track_choice = unidecode(track.decode('utf-8'))
        choices = track_choice.split(' ')
        new = choices
        for i,number in enumerate(choices): 
            
            for j,letter in enumerate(number):
                if letter not in string.digits and letter not in string.ascii_letters:
                    new.append(string.replace(number, letter, ''))
                    n=i
        if n:
            
            track_choice = new[n:]

    data = {'q': artist_choice+' '+track_choice}
    response = requests.get(search_url, data=data, headers=headers)
    #print data, response==True

    #print artist_choice, track_choice

    artists = string.split(artist_choice, ' ', 1)
#            tracks = string.split(track_choice, ' ', 1)
    parens_track = track_choice.partition("(") 
    parens_artist = artist_choice.partition("(")
    bracket_track = track_choice.partition("[") 
    bracket_artist = artist_choice.partition("[")
    
    if "(" in track_choice:
        parens = parens_track
        track_choice = parens[0]
        track_choice = track_choice.rstrip()
    if '[' in track_choice: 
        brackets = bracket_track
        track_choice = brackets[0]
        track_choice = track_choice.rstrip()

    data = {'q': artist_choice+' '+track_choice}
    response = requests.get(search_url, data=data, headers=headers)
    #print data, response==True
    
    if not response:
    
        remix = 'remix'
        for result in track_choice:
            if remix.lower() in track_choice.lower():
                track_choice = track_choice.lower().partition(remix.lower())[0]
            
            elif remix.upper() in track_choice.upper():
                track_choice = track_choice.upper().partition(remix.upper())[0]
                
            elif remix.capitalize() in track_choice.capitalize():
                track_choice = track_choice.capitalize().partition(remix.capitalize())[0]
                
            if '-' in track_choice:
                choices = track_choice.partition('-')
                track_choice = choices[0]
                track_choice = track_choice.rstrip()
            
    data = {'q': artist_choice+' '+track_choice}
    response = requests.get(search_url, data=data, headers=headers) 
    #print data, response==True 
    
    if not response:
        for i,word in enumerate(artists):
            if string.istitle(word):
                artist_choice = string.replace(artist, word, word.lower())
                data = {'q': artist_choice+' '+track_choice}
                response = requests.get(search_url, data=data, headers=headers)
                #import pdb; pdb.set_trace()
            elif string.islower(word):
                artist_choice = string.replace(artist_choice, word, word.capitalize())
                data = {'q': artist_choice+' '+track_choice}
                response = requests.get(search_url, data=data, headers=headers)
                #import pdb; pdb.set_trace()
            else:
                artist_choice = string.replace(artist, word, word.lower())
                data = {'q': artist_choice+' '+track_choice}
                response = requests.get(search_url, data=data, headers=headers)
 
    data = {'q': artist_choice+' '+track_choice}
    response = requests.get(search_url, data=data, headers=headers)
    #***************TO DO*****************************************
    # Check the other artist on the track if not response:
    #***************TO DO*****************************************  
    #print data, response==True, '\n'             
    if not response:
        artist_choice = artist
   
    data = {'q': artist_choice+' '+track_choice}
    response = requests.get(search_url, data=data, headers=headers)     
    
#Related Artists in () or []
#    if not response:
#        for word in track_choice.partition('('):
#            if artist in word:
#                artist_choice = artist
#                
#    data = {'q': artist_choice+' '+track_choice}
#    response = requests.get(search_url, data=data, headers=headers)
#    print data, response==True 
#            
#    if not response:
#        for word in track_choice.partition('['):
#            if artist in word:
#                artist_choice = artist
#                
#    data = {'q': artist_choice+' '+track_choice}
#    response = requests.get(search_url, data=data, headers=headers)
#    print data, response==True
    
    # Need to handle multiple artists in track and artist         
    json = response.json()
    song_info = None
    
    if json:
        for hit in json["response"]["hits"]:
            
            artist_listings = (hit["result"]["primary_artist"]["name"]).encode('utf-8')
            track_listings = unidecode(hit["result"]['full_title'])
            #import pdb; pdb.set_trace()
            if artist_choice.lower() in artist_listings.lower() and track_choice.lower() in track_listings.lower():
                #import pdb; pdb.set_trace()
                song_info = hit
                print "artist and track matched",
                break
            
     
            elif track_choice.lower() in track_listings.lower():
                song_info = hit
                print "track matched",
                break
            
            elif artist_choice.lower() in artist_listings.lower(): # and "remastered" in  track_listings.lower()
                song_info = hit
                print "artist matched",
                break
            
            elif "-" in track_choice:
                for word in track_choice.partition(" "):
                    if word in artist_listings:
                        song_info = hit
                        print "artist - track matched",
                        break
                
            else:
                print "match",
#                print "go to azlyrics"
                song_info = hit
#                print "No match"
                break
    
    if song_info:
        #import pdb;pdb.set_trace()
        song_api_path = song_info["result"]["api_path"]
        l = lyrics_from_song_api_path(song_api_path)
        for line in l:
            print line,
        #import pdb;pdb.set_trace()
        return [l, featured_artist]
    
    else:
        print "Couldn't Find The Lyrics"           

