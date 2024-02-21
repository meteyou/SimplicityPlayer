import logging

from mpd import MPDClient, CommandError


class MPDModule:
    def __init__(self, config):
        self._config = config

        host = self._config.get('MPDModule', 'host', fallback='localhost')
        port = self._config.getint('MPDModule', 'port', fallback=6600)
        timeout = self._config.getint('MPDModule', 'timeout', fallback=10)
        self._defaultVolume = self._config.getint('MPDModule', 'defaultVolume',
                                                  fallback=100)

        self._client = MPDClient()
        self._client.connect(host, port)
        self._client.timeout = timeout
        self._client.idle_timeout = None

    def get_state(self):
        try:
            return self._client.status()["state"]
        except KeyError:
            return None

    def get_song(self):
        try:
            name = self._client.currentsong()["file"]
            elapsed = int(float(self._client.status()["elapsed"]))
            duration = int(float(self._client.status()["duration"]))

            return {"name": name, "elapsed": elapsed, "duration": duration}
        except KeyError:
            return None

    def play(self, name, elapsed=0):
        try:
            self._client.setvol(0)

            self._client.clear()
            self._client.add(name)
            self._client.play()

            currentSong = self._client.currentsong()
            if elapsed + 20 > int(currentSong['time']):
                # play from start, if trying to play too close from the end
                elapsed = 0

            logging.getLogger('sp').info('Playing %s from %s' % (name, elapsed))

            self._client.seekcur(elapsed)
            self._client.setvol(self._defaultVolume)

        except CommandError as e:
            logging.getLogger('sp').error('MPD Command error')
            logging.getLogger('sp').exception(e)

    def pause(self):
        self._client.pause()
