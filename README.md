# musicmind

This python code is used to download music lyrics and metadata to Database

run main0.py, type in an artist's name, hit enter.

All data flows into mongoDB

Mongo Data Structure

                tracking = {u'lyrics': lyric, u'album':album, u'artist':ar, u'featured_artists': featured_artists, 
                            u'track':tr, u'popularity': track_popularity, u'genres': genres, u'followers': followers, 
                            u'artist_popularity': artist_popularity, u'explicit': explicit, u'feature':feature} 
