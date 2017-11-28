from flask import render_template, flash, redirect, Response
from app import app
from app import music

navigation = ['MiriamPi', 'EyeCam', 'WhiteNoise', 'Music']
template_data = {'navigation': navigation}

# SSE "protocol" is described here: http://mzl.la/UPFyxY


class ServerSentEvent(object):

    def __init__(self, event, data):
        self.data = data
        self.event = event
        self.id = None
        self.desc_map = {
            self.data: "data",
            self.event: "event",
            self.id: "id"
        }

    def encode(self):
        if not self.data:
            return ""
        lines = ["%s: %s" % (v, k)
                 for k, v in self.desc_map.iteritems() if k]

        return "%s\n\n" % "\n".join(lines)


@app.route('/')
@app.route('/index')
@app.route('/<activeTab>')
def landing(activeTab='MiriamPi'):
    template_data['activeTab'] = activeTab
    if activeTab == 'Music':
        playlistnames = music.getStoredPlaylists()
        template_data['playlistnames'] = playlistnames

    return render_template(activeTab + '.html', **template_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for OpenID="%s", remember_me=%s' %
              (form.openid.data, str(form.remember_me.data)))
        return redirect('/index')
    return render_template('login.html',
                           title='Sign In',
                           form=form)


@app.route('/Tab/<nav>')
def navTab(nav):
    return redirect("/" + nav)


@app.route('/Play/<listName>')
def startPlaylist(listName):
    music.playlistPlay(listName)
    return redirect('/Music/NowPlaying')


@app.route('/Music/NowPlaying')
def nowPlaying():
    dataStream = MusicPlayer.getNowPlayingStream()
    song = None
    for line in dataStream:
        if line['song'] != song:
            song = line['song']
            ev = ServerSentEvent('newSong', MusicPlayer.getSongDataByID(line['songid']))
            # print(MusicPlayer.getSongDataByID(line['songid']))
            yield ev.encode()

        # print(data['time'])
        ev = ServerSentEvent('songTimer', line['time'])
        yield ev.encode()
        sleep(1)

    return Response(nowPlaying(), mimetype='text/event-stream')
