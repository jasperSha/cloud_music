#!/usr/bin/env python3
import pandas as pd
import glob

def update_finished_songs():
    '''
        runs through all flac audio file ids, compiles them, then updates the csv file of songs that have been downloaded

    '''
    # get previous version of finished songs csv
    prev = pd.read_csv('finished_songs.csv', header=None)
    prev_done = prev[0].values.tolist()

    finished = []
    for fname in glob.glob('./spotify_yt_data/*.flac'):
        fname = fname.split('/')
        song_id = fname[-1][:-5]

        # check if we've already recorded this song id as downloaded
        if song_id not in prev_done:
            finished.append(song_id)
    
    df = pd.DataFrame(finished)
    # append new downloads to finished songs csv file
    df.to_csv("finished_songs.csv", encoding='utf-8',sep='\n', index=False,header=False,mode='a')

if __name__ == '__main__':
    update_finished_songs()
    


    
