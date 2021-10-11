Instructions for running the script to pull youtube songs

First we create our virtual environment in the project directory.

So make sure we're currently in the cloud_music directory, cloud_music/

These commands assume you're running in a Linux command line environment

# Run these commands in command line as is

let's create a new virtual environment

`python3 -m venv env`

now we have our virtual env running and we can install python libraries contained only within this environment

`source env/bin/activate`

let's install the libraries outlined by the requirements.txt file

`pip install -r requirements.txt`

here we set our python script to be executable

```
chmod u+x scrape_youtube.py
chmod u+x update_finished_songs.py
```

now we simply run it to begin downloading Youtube files; this script will create a directory called spotify_yt_data/ and then download Youtube audio in flac format into that directory for storage

note: first download the finished_songs.csv file from the repo, either with git pull or just manually downloading from the repo(probably just do this tbh)

`./scrape_youtube.py`


note: the curr_count variable on line 77 are the last index up to which I've downloaded. Each download iteration prints the last index, so curr_count needs to be changed to that index if you need to interrupt the program at any time; then the next time the script is run, it will start from that index in the all_songs list


also, after every download session, please run the update_finished_songs script in order to append all new songs that have been downloaded to the finished_songs.csv file. After that, please git push the finished_songs.csv to the repo

so first:

```
./update_finished_songs.py

git add finished_songs.csv
git commit -m 'updated finished songs'
git pull
git push
```


Features to extract

```
zero crossing rate: number of times the soundwave crosses zero (dynamic songs like rock/metal have larger zero crossing rates)

spectral centroid: weighted mean of the frequences present in the signal, calculated with an FFT

rolloff frequency: the center frequency of a spectrogram bin such that some percentage(default=0.85) of the energy of the spectrum lies within this range(with roll_percent=1 or 0, this gives us the max or min frequency of the song)

mel frequency cepstral coefficients(mfcc) that describe the overall shape of a spectral envelope, in music known as the timbre of a segment of a song

spectral contrast: considers spectral peak, valley, and difference in each frequency subband

spectral bandwidth computes the order- p spectral bandwidth, with p=2, it's a weighted standard deviation of the frequencies

spectral flatness: ratio of the geometric mean to the arithmetic mean of a power spectrum

chromagram of the power spectrogram
silence counting
```

These features are extremely large wrt the songs, as their size==the number of frames in the signal. So we can just look at the max, min, std dev, mean, kurtosis, and skew of each feature





