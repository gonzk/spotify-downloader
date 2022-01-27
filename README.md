# Spotify Downloader

This web server application allows users to log into their Spotify and download any of their playlists, 
so they can listen to them offline

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

The following command will install the packages according to the configuration file requirements.txt

```
$ pip install -r requirements.txt
```

### Installing
Step 1: Upload your `client_secret.json` file and store your Spotify credentials into an `.env` file

Step 2: In the terminal run:
```
flask run
```

This should produce a similar output to:
````
* Serving Flask app "<app_name>.py" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: <pin number>
````


## Built With

* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - The web framework used
* [PythonAnywhere](https://www.pythonanywhere.com/) - Web hosting used


## License
MIT License

## Acknowledgments

* Spotify Auth Code Flow examples from https://github.com/kylepw/spotify-api-auth-examples
