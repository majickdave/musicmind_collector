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
#    g = grabber(artist=artist, track=track, num=num)
    q = Query(artist, track, num)  
    tids = []
    #g = grabber()
    results = q.query_track(artist=q.artist, track=q.track, num=q.num)
    #import pdb; pdb.set_trace()
#    if not results:
#        if 'love' in q.track:
#            track = 'luv'
#        elif 'luv' in q.track:
#            track = 'love'
#        q2 = Query(q.artist, track, 1)
#        results = q2.query_track(artist=q2.artist, track=q2.track, num=q2.num)
        
    if results:
        for i, t in enumerate(results['tracks']['items']):
            #import pdb; pdb.set_trace()
            print(i, t['artists'][0]['name'], t['name'])
            tids.append(t['uri'])
                
            
        start = time.time()
        #import pdb; pdb.set_trace()
        features = sp.audio_features(tids)
        #import pdb; pdb.set_trace()
        delta = time.time() - start
        #print("Loaded '%s' features in %s minutes")
        data = {}
        
        for feature in features:
            
            data[u'feature'] = json.dumps(feature, indent=4)
            #import pdb; pdb.set_trace()
            #analysis = sp._get(feature['analysis_url'])
            #import pdb; pdb.set_trace()
            #data['analysis'] = json.dumps(analysis, indent=4)
            data[u'name'] = json.dumps(t['name'], indent=4) # track name
           
            data[u'artist'] = json.dumps(t['artists'][0]['name'])
            a = data['artist'].encode('utf-8') 
            t = data['name'].encode('utf-8')
            track_title = '{}'.format(a)+'_'+'{}'.format(t)
#            final = {u'track_title':track_title, u'feature':feature,
#                         u'analysis':analysis}
            print track_title
            #import pdb; pdb.set_trace()
            return data
            

def dumper_artist(artist='', num=50):

    time.clock()
    g = grabber(artist=artist, num=num)
    #import pdb; pdb.set_trace()
    # Set Destination folder for analysis    
    artist_track_results = []
    
    q = Query(artist, '', num)
    
    # get query results from Query object
    results = g
    
    # for each of num tracks
    if results:
        tids = []
        for i, t in enumerate(results['tracks']['items']):
            #import pdb; pdb.set_trace()
            featured_artists = None
#                if type(t)==type(dict()):
#                
#                    #artist = t['artists']['name']
            # if more than 1 artist
            if type(t['artists'])==type(dict()):
                artist = t['artists']['name']
                
            # if 1 artist   
            else:
                if type(t)==type(dict()):
                    artistry = t['artists']
                    
                    # for multiple singers
                    for k,singer in enumerate(artistry):
                        if artist in artistry[k]:
                            # Set featured artists
                            featured_artists = artistry
                            artist = t['artists'][k]['name']
                        else:
                            # Set main artist
                            artist = t['artists'][0]['name']
            
            # Set name of track
            t_name = results['tracks']['items'][i]['name']
            name = artist
            print i, name

            # Set data dictionary to be encoded to JSON
            data = {}                    
            a = artist.encode('utf-8') 
            tr = t_name.encode('utf-8')
            f = featured_artists
            
            # featured artist title naming
            if f:
                track_title = '{}'.format(a)+'_'+'{}'.format(f)+' '+'{}'.format(tr)
            else:
                track_title = '{}'.format(a)+'_'+'{}'.format(f)+' '+'{}'.format(tr)
                
            # Set title as a track title string
            data[u'track_title'] = '{}'.format(track_title)
            
            # set track id for feature search
            tids.append(t['id'])
            #import pdb; pdb.set_trace()
            # Query features


            #import pdb; pdb.set_trace()
            features = sp.audio_features(tids)
            
            for feature in features:
                #import pdb; pdb.set_trace()
                data[u'feature'] = json.dumps(feature, indent=4)
                analysis = sp._get(feature['analysis_url'])
        
                data[u'analysis'] = json.dumps(analysis, indent=4)
                #import pdb; pdb.set_trace()
        
                data[u'track_title'] =  track_title
            #import pdb; pdb.set_trace()
                    #print data
            with open('{}'.format(track_title)+'.json', 'w') as fp:
                import pdb; pdb.set_trace()
                fp.write(json.dumps(data), indent=4)
                        
            artist_track_results.append(data)
            print a, tr, f

            #import pdb; pdb.set_trace()
         
    print 'Analysis took', time.clock()                
#    return [artist, artist_track_results]
                    
#Executes Genius Operation
def runner(artist='', track=''):

    search_url = base_url + "/search"
    response = None
    data = None
    #title = track.split('_')[-1]; names = None
    featured_artists = None
    artist_choice = artist; track_choice = track
    print artist_choice, track_choice

    n = None
    data = {'q': artist_choice+' '+track_choice}
    response = requests.get(search_url, data=data, headers=headers) 
    print data, response==True
    
    if not response:
        try:
            artist_choice = artist.encode('utf-8')

        except UnicodeDecodeError as e:
            
            byte = e[1]
            if byte in artist:
                import pdb; pdb.set_trace()
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
    print data, response==True

    print artist_choice, track_choice

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
    print data, response==True
    
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
    print data, response==True 
    
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
    print data, response==True, '\n'             
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
                print "artist and track matched"
                break
            
     
            elif track_choice.lower() in track_listings.lower():
                song_info = hit
                print "track matched"
                break
            
            elif artist_choice.lower() in artist_listings.lower(): # and "remastered" in  track_listings.lower()
                song_info = hit
                print "artist matched"
                break
            
            elif "-" in track_choice:
                for word in track_choice.partition(" "):
                    if word in artist_listings:
                        song_info = hit
                        print "artist - track matched"
                        break
                
            else:
                print "match"
#                print "go to azlyrics"
                song_info = hit
#                print "No match"
                break
    
    if song_info:
        #import pdb;pdb.set_trace()
        song_api_path = song_info["result"]["api_path"]
        l = lyrics_from_song_api_path(song_api_path)
        #import pdb;pdb.set_trace()
        return l
    
    else:
        print "Couldn't Find The Lyrics"
        
def runner_artist(artist='', track=''):

    search_url = base_url + "/search"
    response = None
    data = None
    #title = track.split('_')[-1]; names = None
    featured_artists = None
    artist_choice = artist; track_choice = track
    print artist_choice, track_choice

    n = None
    data = {'q': artist_choice+' '+track_choice}
    response = requests.get(search_url, data=data, headers=headers) 
    print data, response==True
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
    print data, response==True

    print artist_choice, track_choice

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
    print data, response==True
    
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
    print data, response==True 
    
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
    
    print data, response==True, '\n'             
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
                print "artist and track matched"
                break
            
     
            elif track_choice.lower() in track_listings.lower():
                song_info = hit
                print "track matched"
                break
            
            elif artist_choice.lower() in artist_listings.lower(): # and "remastered" in  track_listings.lower()
                song_info = hit
                print "artist matched"
                break
            
            elif "-" in track_choice:
                for word in track_choice.partition(" "):
                    if word in artist_listings:
                        song_info = hit
                        print "artist - track matched"
                        break
                
            else:
                print "go to azlyrics"
                song_info = hit
                print "No match"
                break
    
    if song_info:
        #import pdb;pdb.set_trace()
        song_api_path = song_info["result"]["api_path"]
        l = lyrics_from_song_api_path(song_api_path)
        #import pdb;pdb.set_trace()
        return l
    
    else:
        print "Couldn't Find The Lyrics"

        



        
