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
#a = 'lenox'; b = 'whatever'
#q1 = str(raw_input('Lyrics? Y/N ')) 
#q2 = str(raw_input('analysis? Y/N '))
#if q1.upper() == 'Y':
#    a = str(raw_input('Enter Artist: '))
#if q2.upper()== 'Y':
#    b = str(raw_input('Enter Track: '))


if __name__=='__main__':
    time.clock()

#        lyrics = rapperBoy.runner()
#        #import pdb; pdb.set_trace()
#        lyrics = lyrics[0].splitlines()
#        for i,l in enumerate(lyrics):
#            if l=='':
#                lyrics.pop(i)
#        #import pdb; pdb.set_trace()

#        analysis = dumper()
#artist_names = ['jeremih', 'drake', 'eminem', 'jayz', "josh pan"]
    
    
        
    g = audio_features2.dumper(artist=a, track=b, num=1)
    #import pdb; pdb.set_trace()
#    for i,result in enumerate(g):
##            if result in ''.join(artist_names):
#        #q = audio_features1.Query(str(a), str(result), 3)
###track_name = str(raw_input('Track? '))
##f = q.query_return(artist=q.a, num=q.num)
##                for song in q:
#        done = False
##            while not done:
##                time.clock()
##                if time.clock()>1000:
##                    None
##                else:
##                    start = time.clock()
#        #analysis = audio_features1.dumper(artist=a)
    title = a+' '+b
    if g:
        u_title = g['track_title']
        name = u_title
        name = name.partition('_')
        lt = name[-1]; la = name[0]
    #import pdb; pdb.set_trace()
    # f**kin ni**a
#        if '**' in name[-1]:
#            lt = string.replace(name[-1], '**', 'gg')
        
        lyrics = audio_features2.runner(artist=la, track=lt)
        
##        if la not in lyrics and lt not in lyrics:
##            lyrics = None
#        elif lt in lyrics or la in lyrics:
#            lyrics = audio_features2.runner(artist=la, track=lt)
        if lyrics: 
           print(lyrics[-1])
            
            

        
        #import pdb; pdb.set_trace()
    
        for x in u_title:
            if x in '*()"|?\/:<>': 
                title = string.replace(u_title, x, '')
                
    else:
        print "No Spotify Response"
                
    
    json = json
    if title:
        file_name = title
    with open(file_name+'.json', 'w') as fp:
        fp.write((json.dumps({ u'lyrics':lyrics, u'analysis':g, u'song_title':u_title}, indent=4)))
    print 'These lyrics clocked ', time.clock(),
#       
#        f = json.load(fp)
#        #import pdb; pdb.set_trace()
#        json = json.json()
#        f['root']['data']['title'] = json.dumps({u'analysis':analysis, u'lyrics':lyrics}, indent=4)
##        fp['data'] = 
#        #import pdb; pdb.set_trace()
#        fp.writelines(f)
#       #writer()
##       fp.write((json.dumps({f[analysis]['track_title']:{u'analysis':analysis, u'lyrics':lyrics}}, indent=4)))