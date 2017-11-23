from flask import Flask, render_template, request, Response, redirect, url_for, abort
from mpdPlayer import mpdPlayer

# test
host, port = 'localhost', 5000
mpdHost, mpdPort = '192.168.2.118', 6600

# deploy:
#host, port = '0.0.0.0', 80
#mpdHost, mpdPort = 'localhost', 6600

app = Flask(__name__)
Music = mpdPlayer(mpdHost, mpdPort)
Music.Reset()
navigation = ['MiriamPi', 'EyeCam', 'WhiteNoise', 'Music']
template_data = {'navigation': navigation}


@app.route("/")
@app.route("/<activeTab>")
def landing(activeTab='MiriamPi'):
    template_data['activeTab'] = activeTab
    if activeTab == 'Music':
        playlistnames = [row['playlist'] for row in Music.listplaylists()]
        template_data['playlistnames'] = playlistnames

    return render_template(activeTab + '.html', **template_data)


@app.route("/Tab/<nav>")
def navTab(nav):
    return redirect("/" + nav)


@app.route("/Play/<listName>")
def startPlay(listName):
    Music.PlaylistPlay(listName)
    return Response('OK', mimetype="text/plain"), 204


if __name__ == "__main__":
    app.run(host=host, port=port, debug=True)
