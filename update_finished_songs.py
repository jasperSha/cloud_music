#!/usr/bin/env python3
import pandas as pd
import glob

def update_finished_songs():
    '''
        runs through all flac audio file ids, compiles them, then updates the csv file of songs that have been downloaded

    '''

    finished = []
    for fname in glob.glob('./spotify_yt_data/*.flac'):
        fname = fname.split('/')
        song_id = fname[-1][:-5]
        finished.append(song_id)
    
    df = pd.DataFrame(finished)
    df.to_csv("finished_songs.csv", encoding='utf-8',sep='\n', index=False,header=False,mode='a')

if __name__ == '__main__':
    update_finished_songs()
    


    
