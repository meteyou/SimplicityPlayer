import logging

from mpd import MPDClient, CommandError


class MPDModule:
    def __init__(self, config):
        self._config = config
        self._host = self._config.get('MPDModule', 'host', fallback='localhost')
        self._port = self._config.getint('MPDModule', 'port', fallback=6600)
        self._timeout = self._config.getint('MPDModule', 'timeout', fallback=10)
        self._defaultVolume = self._config.getint('MPDModule', 'defaultVolume', fallback=100)

    def get_state(self):
        self._connect()

        try:
            status = self._client.status()
            if "state" not in status:
                return None

            self._disconnect()
            return status["state"]
        except KeyError:
            self._disconnect()
            return None

    def get_song(self):
        self._connect()
        try:
            song = self._client.currentsong()
            if "file" not in song:
                return None

            status = self._client.status()
            if "elapsed" not in status or "duration" not in status:
                return None

            name = song["file"]
            elapsed = round(float(status["elapsed"]))
            duration = round(float(status["duration"]))

            self._disconnect()

            return {"name": name, "elapsed": elapsed, "duration": duration}
        except KeyError:
            self._disconnect()
            return None


    def play(self, name, elapsed=0):
        self._connect()

        try:
            self._client.setvol(0)

            self._client.clear()
            self._client.add(name)
            self._client.play()

            currentSong = self._client.currentsong()
            if elapsed + 20 > int(currentSong['time']):
                # play from start, if trying to play too close from the end
                elapsed = 0

            if elapsed < 0:
                elapsed = 0

            logging.getLogger('sp').info('Playing %s from %s' % (name, elapsed))

            self._client.seekcur(elapsed)
            self._client.setvol(self._defaultVolume)

        except CommandError as e:
            logging.getLogger('sp').error('MPD Command error')
            logging.getLogger('sp').exception(e)

        self._disconnect()


    def _connect(self):
        self._client = MPDClient()
        self._client.connect(self._host, self._port)
        self._client.timeout = self._timeout
        self._client.idle_timeout = None

    def _disconnect(self):
        self._client.disconnect()

    def _reconnect(self):
        logging.getLogger('sp').info('Reconnecting to MPD server')
        self._client.disconnect()
        self._connect()

    def pause(self):
        self._connect()
        self._client.pause()
        self._disconnect()

    def toggle_playback(self):
        self._connect()
        state = self.get_state()
        if state == 'play':
            self.pause()
        else:
            self.play(self.get_song()['name'], self.get_song()['elapsed'])
        self._disconnect()

    def update(self):
        self._connect()
        self._client.update()
        self._disconnect()
