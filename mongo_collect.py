# -*- coding: utf-8 -*-
"""
Created on Thu Mar 09 07:25:30 2017

@author: david
"""

import pprint
from pymongo.mongo_client import MongoClient

URI = "mongodb://MusicMind:Dsam456$%^@metamind-shard-00-00-edm1t.mongodb.net:27017,metamind-shard-00-01-edm1t.mongodb.net:27017,metamind-shard-00-02-edm1t.mongodb.net:27017/MetaMind?ssl=true&replicaSet=MetaMind-shard-0&authSource=admin"
client = MongoClient(URI)
db = client['MetaMind']
posts = db.posts



collection = db.test_collection

pprint.pprint(posts.find_one())
