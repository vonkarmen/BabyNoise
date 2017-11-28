from flask import Flask
from flask_mpdPlayer import PersistentMPDClient

app = Flask(__name__)
app.config.from_object('config')
music = PersistentMPDClient(app)

from app import views
