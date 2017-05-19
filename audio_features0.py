# -*- coding: utf-8 -*-
"""
Created on Mon Mar 06 00:20:05 2017

@author: david
"""
from bs4 import BeautifulSoup
import webbrowser
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
from audio_features_local import runner, dumper
from pymongo.mongo_client import MongoClient

URI = "mongodb://MusicMind:6jlewvwvuBVqJls4@features-shard-00-00-edm1t.mongodb.net:27017,features-shard-00-01-edm1t.mongodb.net:27017,features-shard-00-02-edm1t.mongodb.net:27017/features?ssl=true&replicaSet=features-shard-0&authSource=admin"
client = MongoClient(URI)
db = client['MetaMind']
posts = db.posts



#Genius
base_url = "https://api.genius.com"
headers = {'Authorization': 'Bearer tQoh0aD9H5Od9EmoORVzKkki48MEG4K6Kyy8zCQvO8lq1Rjx1IVqEqUQMUgqJTHv'}

#Spotify#
SPOTIPY_CLIENT_ID = "3a883c6b1fc4405ba45608df5e60e09f"
SPOTIPY_CLIENT_SECRET = "3168b907abf54925b8e482797f0eb718"
REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = {"account": "user-read-private", "top": "user-top-read", "email": "user-read-email"}

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
    def __init__(self, artist, track, albumName, album, num):
        self.artist=artist
        self.track=track
        self.albumName=albumName
        self.album=album
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

    @classmethod
    def query_album(self, artist='', albumName='', album=True, num=10):
        return sp.search(artist+' '+albumName, type='album', limit=num)      



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
def grabber(artist='', track='', album=False, albumName='', num=10):
       
    query = Query(artist, track, album, albumName, num)

    track_results = None
    name_results = None

    if query.artist!='' and query.track!='':

        track_results = sp.search(q=str(query.track), limit=query.num)
        return track_results
    elif query.track!='' and query.album=='':

        name_results = sp.search(q=str(query.artist), limit=query.num)
        return name_results

    elif query.album!=False and query.artist!='':

        album_results = query.query_album(artist)
        return album_results
    
    else:

        name_results = sp.search(q=str(query.artist), limit=1)
        return name_results


# get a user's tracks

def user_top(url="", num =5, token=False):
	if not token:
		token = spotipy.oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, login_url, state=None, scope=SCOPE['top'], cache_path=None, proxies=None)
	if is_token_expired():
		return False

def user_login(token=False):
	if not token:
		url = spotipy.oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, REDIRECT_URI).get_authorize_url()
		token = True 
	return url

# Query spotify and Genius for Metadata and lyrics -Final API to be developed with Spotify Approval   
def dumper_artist(artist='', num=50):
    time.clock()
    g = grabber(artist=artist, num=num)

    if g:
        
        for i, results in enumerate(g['tracks']['items']):
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
                    
#                   #analysis = sp._get(feature[u'analysis_url'])
                    #Send to Hadoop, or Big Store
    
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
                            u'track':tr, u'popularity': track_popularity, u'genres': genres, u'followers': followers, u'followers': followers, 
                            u'artist_popularity': artist_popularity, u'explicit': explicit, u'feature':feature} 
            except ValueError as e:
                print e,
                dumper(artist=ar, track=tr, num=1)
  
            # u'analysis':analysis
        
             
            #################################################
#            u_title = artist+' - '+album+' - '+tr
#            for x in u_title:
#                if x in '*()"|?\/:<>': 
#                    u_title = string.replace(u_title, x, '')
                    
            #file_name = u_title
            ##################   MONGO DB ###################
            try:
                post_id = posts.insert_one(tracking).inserted_id
                print "mongo post id:", post_id,
            except KeyError as e:
                print "Duplicate!",
                pass


            # We can save this somewhere else for reference
                                  
#            with open(file_name+'_'+post_id+'.json', 'w') as fp:
#                fp.write((track_json.dumps(tracking, indent=4)))

def dumper_track(artist='', track='', num=1):
    time.clock()
    g = grabber(artist=artist, track=track, num=num)

    if g:
        
        for i, results in enumerate(g['tracks']['items']):
            #track_json = json
            #import pdb; pdb.set_trace()
            preview_url = results['preview_url']
            track_imageURL = results['album']['images'][0]['url']

            artistURL = sp.artist(results['artists'][0]['id'])
            artist_imageURL = artistURL['images'][0]['url']

            playURL = results['external_urls']['spotify']

            webbrowser.open_new(artist_imageURL)
            webbrowser.open_new(track_imageURL)
            webbrowser.open_new(playURL)


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
                
                
                for i, feature in enumerate(features):
                    analysis = sp._get(feature[u'analysis_url'])
                    
    #                   
                    #Send to Hadoop, or Big Store

                print features,
                print analysis,

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
                            u'track':tr, u'popularity': track_popularity, u'genres': genres, u'followers': followers, u'followers': followers, 
                            u'artist_popularity': artist_popularity, u'explicit': explicit, u'feature':feature} 
            except ValueError as e:
                print e,
                dumper(artist=ar, track=tr, num=1)

            # u'analysis':analysis
        
             
            #################################################
    #            u_title = artist+' - '+album+' - '+tr
    #            for x in u_title:
    #                if x in '*()"|?\/:<>': 
    #                    u_title = string.replace(u_title, x, '')
                    
            #file_name = u_title
            ##################   MONGO DB ###################
            try:
                post_id = posts.insert_one(tracking).inserted_id
                print "mongo post id:", post_id,
                #webbrowser.open_new(preview_url)
            except KeyError as e:
                print "Duplicate!",
                pass

            


                # We can save this somewhere else for reference
                                      
    #            with open(file_name+'_'+post_id+'.json', 'w') as fp:
    #                fp.write((track_json.dumps(tracking, indent=4)))
                    
def dumper_album(artist='', album=True, albumName='', num=10):
    time.clock()
    g = grabber(artist=artist, album=album, albumName=albumName)

    if g:

        
        for i, results in enumerate(g['albums']['items']):
            albumID = results['id']
            #print album
            albumResults = sp.album(albumID)
            # tracks = albumTracks['tracks']['items'][0]
            # name = tracks['name']
            
                #track_json = json

            recordName = albumResults['name']
            album_popularity = albumResults['popularity'] 
            # import pdb; pdb.set_trace()

            for item in albumResults['tracks']['items']:
                

                            # Get track popularity
                featured_artists = []                                # start featured artists list

                track_name = item['name']

                for j, ar in enumerate(item['artists']):
                    if j > 0:
                        featured_artists.append(ar)

                track_popularity = sp.track(item['uri'])['popularity']

                artist_popularity = sp.artist(item['artists'][0]['id'])['popularity']

                artist_name = item['artists'][0]['name']

                track_result = sp.search(q=artist_name+' '+track_name, type='track', limit=1)       # Get audio features

                features = sp.audio_features(item['uri'])
             
                genres = sp.artist(item['artists'][0]['id'])['genres']

                analysis = sp.audio_analysis(item['uri'])

                explicit = item['explicit']

                    
                if "(" in track_name:
                    new = track_name.partition(" (")
                    feats = new[2]
                    feats = feats.strip(" )")
                    feats = feats.strip("feat. ")
                    featured_artists.append(feats)

                try:                                   # Instantiate JSON if needed 
                    lyric = runner(artist=artist_name, track=track_name) # instantiate lyrics

                    # print analysis
                        # Send to Hadoop, or Big Store
        
                    
                except ValueError as e:
                    print e,
                    lyric = None
                    pass

                print recordName, 
                
                tracking = {u'lyrics': lyric, u'album':recordName, u'artist':artist_name, u'featured_artists': featured_artists, 
                                u'track':track_name, u'popularity': track_popularity, u'genres': genres, 
                                u'artist_popularity': artist_popularity, u'explicit': explicit, u'feature':features} 
                    #dumper_album(artist=ar, track=tr, num=1)
      
                # u'analysis':analysis
            
                 
                ################################################

                #################   MONGO DB ###################
                try:
                    post_id = posts.insert_one(tracking).inserted_id
                    print "mongo post id:", post_id,

                except KeyError as e:
                    print "Duplicate!",
                    print ''
                    pass

                # tracking[u'analysis'] = analysis
                # u_title = artist+' - '+album+' - '+tr
                # for x in u_title:
                #    if x in '*()"|?\/:<>': 
                #        u_title = string.replace(u_title, x, '')
                        
                # file_name = u_title
                # with open(file_name+'_'+post_id+'.json', 'w') as fp:
                #     fp.write((track_json.dumps(tracking, indent=4)))
        
        
                
                
                
                
                
                
