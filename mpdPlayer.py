from mpd import MPDClient
from time import sleep, strftime, gmtime


class mpdPlayer(MPDClient):

    def __init__(self, address, port):
        super(mpdPlayer, self).__init__()
        self.connect(address, port)
        print('connected to mpd at ' + address + ':' + str(port))

    def AddSongs(self, playlist, fnames):
        """Adds list of song files to playlist and saves playlist"""
        for f in fnames:
            self.playlistadd(playlist, f)

        return self.listplaylist(playlist)

    def GetStoredPlaylists(self):
        return [{'name': row['playlist'], 'songs': self.listplaylist(row['playlist'])} for row in self.listplaylists()]

    def PlaylistPlay(self, playlist, songPos=0):
        """load specified playlist name and start playing it"""
        self.clear()
        self.load(playlist)
        self.play(songPos)
        return 'Playing playlist ' + playlist

    def GetNowPlaying(self):
        """gen text stream of now playing info in dict with 'song' and 'time' keys"""
        while True:
            rcv = self.status()
            data = {'song': None, 'time': None}
            if rcv['state'] == 'play':
                # print(rcv)
                data['time'] = '/'.join([strftime("%M:%S", gmtime(int(t))) for t in rcv['time'].split(':')])
                data['song'] = int(rcv['song'])
                data['songid'] = int(rcv['songid'])
                yield data
            else:
                return 'stopped'

    def ParseSongData(self, songID):
        """raw = [{'file': 'Hard_Love.mp3', 'last-modified': '2017-11-08T00:32:13Z', 'artist': 'NEEDTOBREATHE', 'albumartist': 'NEEDTOBREATHE', 'title': 'HARD LOVE', 'album': 'H A R D L O V E', 'track': '2/12', 'genre': 'Rock', 'composer': 'Composer Information Unavailable', 'time': '215', 'pos': '0', 'id': '1'}]"""
        raw = self.playlistid(songID)[0]
        # print(raw)
        sReturn = 'Now playing ' + raw['title'] + ' from ' + raw['album'] + ' by ' + raw['artist']
        return sReturn


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
    #MusicPlayer.rm('testing2')

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
    print('\n<' + MusicPlayer.PlaylistPlay(picked) + '>')

    # MusicPlayer.clear()
    # MusicPlayer.load(picked)
    # MusicPlayer.play()

    # stream now playing data while playlist is playing
    dataStream = MusicPlayer.GetNowPlaying()
    song = None
    for data in dataStream:
        if data['song'] != song:
            song = data['song']
            #print(song, data['songid'])
            print(MusicPlayer.ParseSongData(data['songid']))

        print(data['time'])
        sleep(1)

    # close
    print('closing connection')
    MusicPlayer.close()
