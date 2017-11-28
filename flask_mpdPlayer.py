from __future__ import print_function
import warnings
import socket
from mpd import MPDClient
from time import sleep, strftime, gmtime

__version__ = '0.1.2'

# PersistentMPDClient from https://github.com/schamp/PersistentMPDClient/blob/master/PersistentMPDClient.py


class PersistentMPDClient(MPDClient):
    Host = None
    Port = None

    def __init__(self, app=None, Host='localhost', Port=6600):
        super(PersistentMPDClient, self).__init__()
        self.app = app
        self.socket = None
        if app is not None:
            self.init_app(app)
        else:
            self.Host = Host
            self.Port = Port

        self.do_connect()
        # get list of available commands from client
        self.command_list = self.commands()

        # commands not to intercept
        self.command_blacklist = ['ping']

        # wrap all valid MPDClient functions
        # in a ping-connection-retry wrapper
        for cmd in self.command_list:
            if cmd not in self.command_blacklist:
                if hasattr(super(PersistentMPDClient, self), cmd):
                    super_fun = super(PersistentMPDClient, self).__getattribute__(cmd)
                    new_fun = self.try_cmd(super_fun)
                    print("Setting interceptor for {}".format(cmd))
                    setattr(self, cmd, new_fun)
                else:
                    print("Attr {} not available!".format(cmd))

    # create a wrapper for a function (such as an MPDClient
    # member function) that will verify a connection (and
    # reconnect if necessary) before executing that function.
    # functions wrapped in this way should always succeed
    # (if the server is up)
    # we ping first because we don't want to retry the same
    # function if there's a failure, we want to use the noop
    # to check connectivity
    def try_cmd(self, cmd_fun):
        def fun(*pargs, **kwargs):
            try:
                #                print("Attemping to ping...")
                self.ping()
            except (mpd.ConnectionError, OSError) as e:
                #                print("lost connection.")
                #                print("trying to reconnect.")
                self.do_connect()
            return cmd_fun(*pargs, **kwargs)
        return fun

    # needs a name that does not collide with parent connect() function
    def do_connect(self):
        try:
            try:
                #                print("Attempting to disconnect.")
                self.disconnect()
            # if it's a TCP connection, we'll get a socket error
            # if we try to disconnect when the connection is lost
            except mpd.ConnectionError as e:
                #                print("Disconnect failed, so what?")
                pass
            # if it's a socket connection, we'll get a BrokenPipeError
            # if we try to disconnect when the connection is lost
            # but we have to retry the disconnect, because we'll get
            # an "Already connected" error if we don't.
            # the second one should succeed.
            except BrokenPipeError as e:
                #                print("Pipe closed, retrying disconnect.")
                try:
                    #                    print("Retrying disconnect.")
                    self.disconnect()
                except Exception as e:
                    print("Second disconnect failed, yikes.")
                    print(e)
                    pass
            if self.socket:
                #                print("Connecting to {}".format(self.socket))
                self.connect(self.socket, None)
            else:
                #                print("Connecting to {}:{}".format(self.host, self.port))
                self.connect(self.Host, self.Port)
        except socket.error as e:
            print("Connection refused.")

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
        # def shutdown_mpdPlayer(exec_or_respond):
        #    self.Reset()

    def reset(self):
        self.stop()
        self.clear()
        #print('mpd player ready')

    def addSongs(self, playlist, fnames):
        """Adds list of song files to playlist and saves playlist"""
        for f in fnames:
            self.playlistadd(playlist, f)

        return self.listplaylist(playlist)

    def getStoredPlaylists(self):
        """get list of stored playlist names"""
        return [row['playlist'] for row in self.listplaylists()]

    def getSongDataInPlaylist(self, playlist, keys=['title', 'album', 'artist']):
        """get list of 'key' items in 'playlist'"""
        return [{k: row[k] for k in keys} for row in self.listplaylistinfo(playlist)]

    def playlistPlay(self, playlist, songPos=0):
        """load specified playlist name and start playing it"""
        self.clear()
        self.load(playlist)
        self.play(songPos)
        return 'Playing playlist "' + playlist + '"'

    def getNowPlayingStream(self):
        """gen text stream of now playing info in dict with 'song' and 'time' keys"""
        while True:
            rcv = self.status()
            data = {'song': None, 'time': None}
            if rcv['state'] == 'play':
                # print(rcv)
                data['time'] = self._formatTime(rcv['time'])
                data['song'] = int(rcv['song'])
                data['songid'] = int(rcv['songid'])
                yield data
            else:
                print('playback stopped')
                break

    def _formatTime(self, strTime):
        return '/'.join([strftime("%M:%S", gmtime(int(t))) for t in strTime.split(':')])

    def getSongDataByID(self, songID):
        """raw = [{'file': 'Hard_Love.mp3', 'last-modified': '2017-11-08T00:32:13Z', 'artist': 'NEEDTOBREATHE', 'albumartist': 'NEEDTOBREATHE', 'title': 'HARD LOVE', 'album': 'H A R D L O V E', 'track': '2/12', 'genre': 'Rock', 'composer': 'Composer Information Unavailable', 'time': '215', 'pos': '0', 'id': '1'}]"""
        raw = self.playlistid(songID)[0]
        # print(raw)
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
    MPD_HOST = '192.168.2.118'

    # connect to client
    MusicPlayer = PersistentMPDClient(None, MPD_HOST)
    print('Timeout: ' + str(MusicPlayer.timeout) + ', Idle Timeout: ' + str(MusicPlayer.idletimeout))
    print('mpd version: ' + str(MusicPlayer.mpd_version))
    # reset mpd state for testing
    MusicPlayer.reset()

    # add some songs to a playlist
    #lnewlist = MusicPlayer.AddSongs('testing2', songAdd)
    #print(':----Test add songs----:')
    # print(lnewlist)

    # options for getting song/playlist info
    testname = 'testing'
    # MusicPlayer.load(testname)
    # print(':----song/playlist info format for ' + testname + ' playlist----:')
    # print(MusicPlayer.status())

    # print('.playlist()')
    # print(MusicPlayer.playlist())
    # #['file: Hard_Love.mp3', 'file: 03_MONEY_FAME.mp3']

    # print('.listplaylist(<name>)')
    # print(MusicPlayer.listplaylist(testname))
    # #['Hard_Love.mp3', '03_MONEY_FAME.mp3']

    # print('.listplaylists()')
    # print(MusicPlayer.listplaylists())
    # #[{'playlist': 'testing2', 'last-modified': '2017-11-23T06:36:35Z'}, {'playlist': 'testing', 'last-modified': '2017-11-23T02:24:47Z'}]

    # print('.playlistid()')
    # print(MusicPlayer.playlistid())
    # #[{'file': 'Hard_Love.mp3', 'last-modified': '2017-11-08T00:32:13Z', 'artist': 'NEEDTOBREATHE', 'albumartist': 'NEEDTOBREATHE', 'title': 'HARD LOVE', 'album': 'H A R D L O V E', 'track': '2/12', 'genre': 'Rock', 'composer': 'Composer Information Unavailable', 'time': '215', 'pos': '0', 'id': '71'}, {'file': '03_MONEY_FAME.mp3', 'last-modified': '2017-11-08T00:32:24Z', 'artist': 'NEEDTOBREATHE', 'albumartist': 'NEEDTOBREATHE', 'title': 'MONEY & FAME', 'album': 'H A R D L O V E', 'track': '3/12', 'genre': 'Rock', 'composer': 'Composer Information Unavailable', 'time': '192', 'pos': '1', 'id': '72'}]

    # print('listplaylistinfo(<name>)')
    # print(MusicPlayer.listplaylistinfo(testname))
    # #[{'file': 'Hard_Love.mp3', 'last-modified': '2017-11-08T00:32:13Z', 'artist': 'NEEDTOBREATHE', 'albumartist': 'NEEDTOBREATHE', 'title': 'HARD LOVE', 'album': 'H A R D L O V E', 'track': '2/12', 'genre': 'Rock', 'composer': 'Composer Information Unavailable', 'time': '215'}, {'file': '03_MONEY_FAME.mp3', 'last-modified': '2017-11-08T00:32:24Z', 'artist': 'NEEDTOBREATHE', 'albumartist': 'NEEDTOBREATHE', 'title': 'MONEY & FAME', 'album': 'H A R D L O V E', 'track': '3/12', 'genre': 'Rock', 'composer': 'Composer Information Unavailable', 'time': '192'}]
    # print('\n')

    # get playlists availible
    lPlaylists = MusicPlayer.getStoredPlaylists()
    print(':-----------Stored playlist info------------:')
    [print(str(item)) for item in lPlaylists]
    print(':-----------Stored playlist info------------:')

    # get songs in playlist
    picked = 'testing2'
    lsongs = MusicPlayer.getSongDataInPlaylist(picked)
    print('<' + MusicPlayer.playlistPlay(picked) + '>')
    [print(str(item)) for item in lsongs]

    print('\n')
    # stream now playing data while playlist is playing
    dataStream = MusicPlayer.getNowPlayingStream()
    song = None
    for data in dataStream:
        if data['song'] != song:
            song = data['song']
            #print(song, data['songid'])
            print(MusicPlayer.getSongDataByID(data['songid']))

        print(data['time'])
        sleep(1)

    # close
    print('closing connection')
    MusicPlayer.close()
    MusicPlayer.disconnect()
