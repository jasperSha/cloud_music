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

`chmod u+x scrape_youtube.py`

now we simply run it to begin downloading Youtube files; this script will create a directory called spotify_yt_data/ and then download Youtube audio in flac format into that directory for storage

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
