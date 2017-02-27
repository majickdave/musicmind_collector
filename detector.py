# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 23:50:55 2017

@author: david
"""

import string
import json
import pandas as pd
import nltk
import matplotlib.pyplot as plt
import seaborn as sns
from unidecode import unidecode
 

file_name = "post malone go flex.json"

def detect():
    with open(file_name, 'r') as fp:
        heater = 0
        cooler = 0100
        x = json.load(fp)
        #import pdb; pdb.set_trace()
        for y in x['lyrics'][0].split('\n'):

            lyrical = y.decode('utf-8')
            import pdb; pdb.set_trace()
##                except UnicodeDecodeError as e:
##                    byte = e[1]
##                    if byte in lyrical:
#                    #import pdb; pdb.set_trace()
#            #lyrical = unidecode(y.decode('utf-8'))
#
#            import pdb; pdb.set_trace()
#            tokens = nltk.word_tokenize(lyrical)
#            print tokens
#            for i,w in enumerate(tokens.upper().split(' ')):
#                #[string.replace(w,y,'') for q in string.printable]
#                for letter in w:
#                    if letter not in string.ascii_letters:
#                        w = string.replace(w,letter,'') 
#                if w.upper() in z.encode('utf-8'):
#                
#                    #print w, " "
#                    heater += 1
#                
#    #                elif (any(['shit', 'trap', 'nigga'])==w.lower())==True:
#    #                    print w, " profanity"
#                
#                else:
#                    print w #" heater"
#                    cooler += 1
#                print            
#                print 'HOT:', heater
#                print 'COLD:', cooler
#    
#                y = y.encode('utf-8')
#                for z in y:
#                    
#                    print count
#                for z in w.split(' '):
#                    import pdb; pdb.set_trace()
#                    for z in all([y not in string.ascii_letters for y in w]):
#                        strings = string.split(z)
#                        for s in strings:
#                            s.replace(x, z, '')
#            
#                heat = ' '.join(strings)
#                print heat
#        #    
#detect()    
#        #    with open('words.txt', 'r') as f:
#        
#                    
