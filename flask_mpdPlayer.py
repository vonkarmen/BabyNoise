from __future__ import print_function
import warnings
from mpd import MPDClient
from time import sleep, strftime, gmtime

__version__ = '0.0.1'


class mpdPlayer(MPDClient):
    Host = None
    Port = None

    def __init__(self, app=None, Host='192.168.2.118', Port=6600):
        super(mpdPlayer, self).__init__()
        self.app = app
        if app is not None:
            self.init_app(app)
        else:
            self.Host = Host
            self.Port = Port

    def init_app(self, app):
        if (
            'MPD_HOST' not in app.config and
            'MPD_PORT' not in app.config
        ):
            warnings.warn(
                'Neither MPD_HOST nor MPD_PORT is set. '
                'Defaulting to localhost:6600.'
            )

        app.config.setdefault('MPD_HOST', 'localhost')
        app.config.setdefault('MPD_PORT', 6600)

        self.Host = app.config['MPD_HOST']
        self.Port = app.config['MPD_PORT']

        app.extensions['mpdPlayer'] = _mpdPlayerState(self)

        #@app.teardown_appcontext
        #def shutdown_mpdPlayer(exec_or_respond):
        #    self.Reset()

    def connect(self):
        super(mpdPlayer, self).connect(self.Host, self.Port)

    def Reset(self):
        self.connect()
        self.stop()
        self.clear()
        self.close()
        #print('mpd player ready')

    def AddSongs(self, playlist, fnames):
        """Adds list of song files to playlist and saves playlist"""
        for f in fnames:
            self.playlistadd(playlist, f)

        return self.listplaylist(playlist)

    def GetStoredPlaylists(self):
        self.connect()
        data = [{'name': row['playlist'], 'songs': self.listplaylist(row['playlist'])} for row in self.listplaylists()]
        self.close()
        return data

    def PlaylistPlay(self, playlist, songPos=0):
        """load specified playlist name and start playing it"""
        self.connect()
        self.clear()
        self.load(playlist)
        self.play(songPos)
        self.close()
        return 'Playing playlist ' + playlist

    def GetNowPlayingStream(self):
        """gen text stream of now playing info in dict with 'song' and 'time' keys"""
        self.connect()
        while True:
            rcv = self.status()
            data = {'song': None, 'time': None}
            if rcv['state'] == 'play':
                # print(rcv)
                data['time'] = self._FormatTime(rcv['time'])
                data['song'] = int(rcv['song'])
                data['songid'] = int(rcv['songid'])
                yield data
            else:
                self.close()
                print('playback stopped')
                break

    def _FormatTime(self, strTime):
        return '/'.join([strftime("%M:%S", gmtime(int(t))) for t in strTime.split(':')])

    def GetSongDataByID(self, songID):
        """raw = [{'file': 'Hard_Love.mp3', 'last-modified': '2017-11-08T00:32:13Z', 'artist': 'NEEDTOBREATHE', 'albumartist': 'NEEDTOBREATHE', 'title': 'HARD LOVE', 'album': 'H A R D L O V E', 'track': '2/12', 'genre': 'Rock', 'composer': 'Composer Information Unavailable', 'time': '215', 'pos': '0', 'id': '1'}]"""
        self.connect()
        raw = self.playlistid(songID)[0]
        # print(raw)
        self.close()
        sReturn = 'Now playing ' + raw['title'] + ' from ' + raw['album'] + ' by ' + raw['artist']
        return sReturn

    def MPD_worker(self, q):
        while True:
            msg = q.get()

            if msg == 'something':
                # do some things
                print(q)
            else:
                self.status()
                sleep(1)


def get_state(app):
    """Gets the state for the application"""
    assert 'mpdPlayer' in app.extensions, \
        'The sqlalchemy extension was not registered to the current ' \
        'application.  Please make sure to call init_app() first.'
    return app.extensions['mpdPlayer']


class _mpdPlayerState(object):
    """Remembers configuration for the (mpdPlayer, app) tuple."""

    def __init__(self, mpdPlayer):
        self.player = mpdPlayer


if __name__ == '__main__':

    # local config options
    smpdConfig = ("192.168.2.118", 6600)  # ("192.168.2.118", 6601)]
    songAdd = ['Hard_Love.mp3', '03_MONEY_FAME.mp3']

    # connect to client
    add, p = smpdConfig
    MusicPlayer = mpdPlayer(add, p)

    # reset mpd state for testing
    MusicPlayer.stop()
    MusicPlayer.clear()
    # MusicPlayer.rm('testing2')

    # add some songs to a playlist
    lnewlist = MusicPlayer.AddSongs('testing2', songAdd)
    print(':----Test add songs----:')
    print(lnewlist)

    # options for getting song/playlist info
    # print(mpd.status())
    # print(mpd.playlist())
    # print(mpd.listplaylist('testing'))
    # print(mpd.listplaylists())
    # print(mpd.playlistid())
    # print(mpd.listplaylistinfo('testing'))

    # get playlists availible
    lPlaylists = MusicPlayer.GetStoredPlaylists()
    print(':-----------Stored playlist info------------:')
    [print(str(item)) for item in lPlaylists]
    print(':-----------Stored playlist info------------:')

    # get songs in playlist
    picked = 'testing2'
    print('<' + MusicPlayer.PlaylistPlay(picked) + '>')

    # MusicPlayer.clear()
    # MusicPlayer.load(picked)
    # MusicPlayer.play()

    # stream now playing data while playlist is playing
    dataStream = MusicPlayer.GetNowPlayingStream()
    song = None
    for data in dataStream:
        if data['song'] != song:
            song = data['song']
            #print(song, data['songid'])
            print(MusicPlayer.GetSongDataByID(data['songid']))

        print(data['time'])
        sleep(1)

    # close
    print('closing connection')
    MusicPlayer.close()
