#!/usr/bin/env python3

import pandas as pd
import youtube_dl

import re
import os
import glob
import json

def pull_song(search_args, finished_songs, captions=False):
    
    ydl_opts = { 'format': 'bestaudio/best',
                 'outtmpl' : f'./spotify_yt_data/%(id)s.%(ext)s', #replace spotify_yt_data with whatever directory you want to save it in
                 'writesubtitles' : captions,
                 'noplaylist': 'True',
                 'postprocessors': [{
                     'key': 'FFmpegExtractAudio',
                     'preferredcodec': 'flac', # lossless compressed
                     'preferredquality': '192',
                     }],
                 'ignoreerrors': True
                 }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(f"ytsearch:{search_args}", download=False)['entries']
        
        #check for empty list first
        if results:
            info = results[0]
            
            # check if it's already downloaded
            if info:
                if info['id'] in finished_songs:
                    print('Already have this one, continuing...')
                    return
        
                # duration in seconds, also check if exists (if premium can't extract info)
                if info['duration'] <= 480 and not info['is_live']:
                    url = info['webpage_url']
                    print("Video title: ", info['title'], "URL: ", url)
                    ydl.download([url])

 
if __name__ == '__main__':
    
    songs = []
    with open('all_songs.json', encoding='utf-8') as f:
        data = json.load(f)
        for row in data:
            artist = row[0]
            songname = row[1]
            song = artist + ' ' + songname
            songs.append(song)

            
    finished_songs = []
    for fname in glob.glob("./spotify_yt_data/*.flac"):
        fname = fname.split('/')
        song_id = fname[-1][:-5]
        finished_songs.append(song_id)

        
    search_terms = songs
    
    curr_count = 4955
    prev = curr_count
    
    for search in search_terms[curr_count:]:
        print("index: ", prev)
        prev += 1
        pull_song(search, finished_songs)

    print("last index: ", prev)
    

