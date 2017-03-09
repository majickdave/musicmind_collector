# -*- coding: utf-8 -*-
"""
Created on Sun Feb 05 20:42:19 2017

@author: david
"""
from audio_features0 import dumper_artist
import time

#Enter Artist Track and confirm lyrics and analysis
artist = raw_input('Artist: ')
#number = int(raw_input('number: '))
#artist = 'PARTYNEXTDOOR'
number = 50

if __name__=='__main__':
    
    time.clock()
    
    pull = dumper_artist(artist=artist, num=number)
    #import pdb; pdb.set_trace()
    
    
    print 'These lyrics clocked ', time.clock()

    #import pdb; pdb.set_trace()
                    

