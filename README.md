# MusicApi

The development of this project is supported by grant NSF-1549981.

The app is developed using Flask frame-work and uses MongoDB database for storing the user data.


### Database

The application needs MongoDB connection url stored in `database_link` variable inside `app.py` file.
Connection url format is `mongodb://XXXX:XXXXX15@ds127841.mlab.com:27841/music_exp` where "music_exp" is a collection that
contains all document files of music. Each document in "music_exp" collection contains data related to a music.
Data format is `{"stFeatures": list containing 11 music features, "spotify_id": spotify id in string, "genres": music
genre in string, "url": music url in string}`

### Start API server

For starting the API on a local machine, the supported packages will be needed to be installed. A list of all the
packages required to run the API is documented in requirements.txt
Start the server using `python app.py`.
After starting the API, the front-end music player should be able to access the API. As default setting flask API is available at `127.0.0.0:5000`.
