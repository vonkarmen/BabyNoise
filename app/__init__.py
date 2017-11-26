from flask import Flask
from flask_mpdPlayer import mpdPlayer

app = Flask(__name__)
app.config.from_object('config')
music = mpdPlayer(app)

from app import views
