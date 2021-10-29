#!/usr/bin/env python3

import os
from dotenv import load_dotenv
load_dotenv() 

import glob
import json
import pprint as pp

import re
from rapidfuzz import fuzz

import pandas as pd
import requests
import numpy
import youtube_dl

pd.set_option('display.max_columns', 100)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')


def find_dups():
    '''
        no duplicates found so far
    '''
    songs = []
    for fname in glob.glob("../../youtubescraper/spotify_yt_data/*.flac"):
        if fname not in songs:
            songs.append(fname)
        else:
            print(fname)


    print(len(songs))


def get_spotify_token():
    
    spotify_token_url = 'https://accounts.spotify.com/api/token'
    auth = requests.post(spotify_token_url, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
        })

    resp = auth.json()
    access_token = resp['access_token']
    
    return access_token



def append_genre(df):
    '''
        using spotify api to append genre and other spotify generated features to the csv file

    '''
    token = get_spotify_token()
    headers = {
            'Authorization': f'Bearer {token}'
            }

    base_url = 'https://api.spotify.com/v1/'
    
    # search using any term, can modify return type e.g. item_type=track, use dict to get track id
    search_suffix = 'search?' 
    
    # append track id (found using search endpoint) to get dict of features like danceability, energy, etc.
    song_features_suffix = 'audio-features/' 


    # using artist + title, or if artist=None, just title from df as search term (looks like title alone may be effective)
    artists = df.iloc[:10]['artist'].tolist()
    titles = df.iloc[:10]['title'].tolist()

    # get track features and connect them to flac id for concatenating with metadata later
    flac_ids = df.iloc[:10]['id'].tolist()

    # need to remove any non-alphanumeric chars for spotify search to work
    alphanum_artists = []
    alphanum_titles = []

    # youtube video specific references; later we can find all results that produce
    # no spotify results to get any more youtube words that get in the way
    exclusion_youtube_words = ['video', 'official']
    yt_exclusions = '|'.join(exclusion_youtube_words)

    # note, removing words like "ft." or other propositions can also improve search results

    for a, t in list(zip(artists, titles)):
        # remove youtube references
        removed_yt_titles = re.sub(yt_exclusions, '', t, flags=re.IGNORECASE)

        # remove artist from title
        artists = '|'.join(a.split(' '))
        removed_artists_titles = re.sub(artists, '', removed_yt_titles, flags=re.IGNORECASE)
        
        
        new_a = re.sub(r'\W+', ' ', a)
        new_t = re.sub(r'\W+', ' ', removed_artists_titles)
#        print(new_t)
        
        alphanum_artists.append(new_a)
        alphanum_titles.append(new_t)
        
    # for feature reference
    flac_name_to_spotify_ids = []
    for idx, (a, t) in enumerate(list(zip(alphanum_artists, alphanum_titles))):
        a, t = a.lower(), t.lower() # reduce levenshtein distance
        params = {
                'q': t + ' ' + a,
                'type': 'track'
                }
        
        search_url = base_url + search_suffix
        resp = requests.get(search_url, params=params, headers=headers)
        response = resp.json()
        
        print("Searched Spotify for: ", t + ' ' + a)

        tracks = response['tracks'] # keys are href, items, limit, next, offset, previous, total
        items = tracks['items']
        print("Number of results found: ", len(items))
        
        # iterate through first five? items check track name with search query, highest match rate, we then grab the track id
        for item in items[:5]:
            found_artist = item['artists'][0]['name'].lower()
            found_trackname = item['name'].lower()
            
            artist_dist = fuzz.ratio(found_artist, a)
            title_dist = fuzz.ratio(found_trackname, t)
            print('artist distance: ', artist_dist)
            print('title distance: ', title_dist)

            if artist_dist >= 85 and title_dist >= 85:
                flac_to_spot_id = tuple((flac_ids[idx], item['id']))
                print(flac_to_spot_id)
                flac_name_to_spotify_ids.append(flac_to_spot_id)
                break

    # now we have our flac to spotify ids, we can pull from spotify api to get features using id
    # spotify feature api endpoint takes csv, up to 100 tracks at a time
    print(len(flac_name_to_spotify_ids))
    return flac_name_to_spotify_ids
    
            
            
            
    
    


def build_metadata():
    '''
        using df to check for already downloaded metadata for url
        
        build json file for organizing flac files by songs/genre/artist

        use flac filename (append it to youtube.com/watch?v= to get url) to request metadata from youtube-dl

        
    '''
#    finished_songs_ids = df['id'].tolist()

    prepend_yt_url = "https://www.youtube.com/watch?v="
    songs = []
    # CHANGE DIR HERE FOR LOCATION OF DOWNLOADED SONGS 
    for fname in glob.glob("../../youtubescraper/spotify_yt_data/*.flac"):
        fname = fname.split('/')
        url = fname[-1][:-5]
#        if url not in finished_songs_ids: # only songs whose meta has not been pulled
        songs.append(url)

    

    ydl_opts = { 'format': 'bestaudio/best',
#             'outtmpl' : f'./spotify_yt_data/%(id)s.%(ext)s',
             'writesubtitles' : False,
             'noplaylist': 'True',
             'quiet': True, # shut off console output
             'postprocessors': [{
                 'key': 'FFmpegExtractAudio',
                 'preferredcodec': 'flac', # lossless compressed
                 'preferredquality': '192',
                 }],
             'ignoreerrors': True
             }
    metadata = []
    
    
    for song in songs:
        url = prepend_yt_url + song
        artist = None
        
        print("Pulling meta for url: ", url)
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            try:
                tag = info['id']
                title = info['title']
                duration = info['duration']
            except:
                failed_log.append(url)
                continue
            if 'artist' in info.keys():
                artist = info['artist']

            print("Success; grabbing meta of: ", title)
            meta = {
                    'id': tag, #also used as the url
                    'artist': artist,
                    'title': title,
                    'duration': duration,
                    }
            
            metadata.append(meta)
    return metadata
        

if __name__ == '__main__':
    
    
    df = pd.DataFrame(scrape_metadata())
    columns = ['id', 'artist', 'title', 'duration']
    df = df[columns]
    
    df.to_csv('extra_metadata.csv', encoding='utf-8',index=False, header=False)
