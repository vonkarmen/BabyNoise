# BabyNoise
### White noise and music player for babies room on rPi with web gui
Project based off of https://jrowberg.io/2015/09/07/raspberry-pi-baby-white-noise-machine/

Using Flask and MPD

### Ideas/ref:
- https://github.com/jeroendoggen/youtube-to-mpd - convert youtube music/playlists
- https://github.com/MusicPlayerDaemon/mpc - mpc source - not using mpc, instead writing own client:
- http://pythonhosted.org/python-mpd2/topics/commands.html - python-mpd2 reference
- https://github.com/hbenl/mpc-js-node - javascript mpd client lib
- https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
- https://stackoverflow.com/questions/13386681/streaming-data-with-python-and-flask - stream data using flask
- https://github.com/miguelgrinberg/oreilly-flask-apis-video - source for api dev with flask
- https://developer.amazon.com/alexa-voice-service - amazon alexa voice service api

### Extending functionality
-https://www.youtube.com/watch?v=7jJfuP7YgPA - IR filter removal for ps3Eye
-https://learn.adafruit.com/cloud-cam-connected-raspberry-pi-security-camera/overview - cloudCam project


current version using Flask web gui instead of s remote app

Built for Rasbian Jessie - raspberrypi.org

### Requirements
needs mpd, mpc, python-mpd2, and Flask:
''' sudo apt-get install mpd mpc
''' sudo pip install flask
''' sudo pip install python-mpd2

## Concept
web server running on rPi allows music and white noise to be played from rPi, camera feed is displayed on webpage, as well as controls and info from music player.
