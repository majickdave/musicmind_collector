# -*- coding: utf-8 -*-
"""
Created on Sun Feb 05 20:42:19 2017

@author: david
"""
import audio_features2
import string
import json
import time

#Enter Artist Track and confirm lyrics and analysis
a = raw_input('Artist: ') ; b = raw_input('Track: ')
#a = 'rihanna'; b = 'desperado'

if __name__=='__main__':
    time.clock()

    g = audio_features2.dumper(artist=a, track=b, num=1)

    if g:
        u_title = g['track']
        u_artist = g['artist']
        u_album = g['album']
        u_featured_artists = g['featured_artists']
        #import pdb; pdb.set_trace()
        print u_artist+' '+','.join(u_featured_artists)+' sing '+u_title

        
        lyrics = audio_features2.runner(artist=u_artist, track=u_title)

        if lyrics: 
           print(lyrics[-1])

        for x in u_title:
            if x in '*()"|?\/:<>': 
                title = string.replace(u_title, x, '')
                
    else:
        print "No Spotify Response"
                
    json = json

    file_name = u_artist+'-'+u_album+'-'+u_title
    with open(file_name+'.json', 'w') as fp:
        fp.write((json.dumps({ u'lyrics':lyrics, u'features':g}, indent=4)))
    print 'These lyrics clocked ', time.clock(),
#       
#      