Instructions for running the script to pull youtube songs

First we create our virtual environment in the project directory.

So make sure we're currently in the cloud_music directory, cloud_music/

These commands assume you're running in a Linux Ubuntu v20.04 command line environment

# Run Project

### Create python env

Run this command to create the environment

`python3 -m venv env`

Activate the environments so necassary libraries can be installed

`source env/bin/activate`

Install the requirements

`pip install -r req.txt`

Going forward all commands will be made assuming the env is active.

### Start Server

enter the server directory and run the following command

`python3 server.py`

The server will tell the user whether a new model is being generated or loading in.  If the model is being generated it will take roughly two minutes to complete.  The server will be operational when the address and port number are print to the console.  As requests are made to the server, the server will output the requests and its contents. To stop the server, issue a keyboard interrupt with crtl + c.  For any reason, if the server were to crash, there was a bug trying to restart the server because the OS still has the addressed to reserved to the prior instance.  The best solution found was to restart command line.  All progress on the model when the server stops running.

### Start the client

Enter the client directory on seperate command line window than the server program and run the following command.

`python3 client.py`

Directions on the screen will pop up, when selecting simulate user the client will make a request to initialize a new user. From here we can print the intial nodes sent to the user in the form of song ids.  Requesting a playlist will cause the user to enter the feedback loop, a song id will be displayed on the screen. To play the song enter the following into the browser replacing songid with the song id given by the program. 

`https://www.youtube.com/watch?v=songid`

Give feedback based on preference. Once enough dislikes is given, the program will initiate an update once the current tree options are exhausted.  The update will be shown to the user, to see the effects, initialize a new user and check the differnce of the initial roots given to the two users.
# Run these commands in command line as is to get songs from YouTube

let's create a new virtual environment

`python3 -m venv env`

now we have our virtual env running and we can install python libraries contained only within this environment

`source env/bin/activate`

let's install the libraries outlined by the requirements.txt file

`pip install -r old_req.txt`

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


Current workflow:
```
Download song data --> flac files
run flac_to_array script to convert flac files into numpy arrays and write to csv, and gather some additional metadata
numpy array csv files will be batched to run through librosa to convert to images(mel spec or CQT)
numpy array csv files batched to gather frequency features as mentioned above
finally, images run through deep clustering to get our clusters/classifications of unlabeled data

Possible requirement:
    run song id's through spotify API to get genre and some other labels spotify uses such as danceability
    use this labeled data as a metric for the performance of our deep unsupervised clustering
```


