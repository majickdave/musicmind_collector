# -*- coding: utf-8 -*-
"""
Created on Sun Feb 05 20:42:19 2017

@author: david
"""
from audio_features0 import dumper_album
import time

#Enter Artist Track and confirm lyrics and analysis
artist = raw_input('Artist: '); number = raw_input('Number of Albums: ')
# artist = 'RZA'; albumName = ''; number = 10

if __name__=='__main__':
    
    time.clock()
    
    pull = dumper_album(artist=artist, num=number)
    #import pdb; pdb.set_trace()
    
    
    print 'These lyrics clocked ', time.clock()

    #import pdb; pdb.set_trace()