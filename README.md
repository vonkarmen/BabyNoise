# BabyNoise
White noise and music player for babies room on rPi with web gui


Project based off of https://jrowberg.io/2015/09/07/raspberry-pi-baby-white-noise-machine/

ideas/ref:
https://github.com/jeroendoggen/youtube-to-mpd - convert youtube music/playlists
https://github.com/MusicPlayerDaemon/mpc - mpc source
https://github.com/hbenl/mpc-js-node - javascript mpd client lib

https://www.youtube.com/watch?v=7jJfuP7YgPA - IR filter removal for ps3Eye
https://learn.adafruit.com/cloud-cam-connected-raspberry-pi-security-camera/overview - cloudCam project

current version using Flask web gui instead of s remote app

Rasbian Jessie

needs mpd/mpc and Flask:
sudo apt-get install mpd mpc
sudo pip install flask
