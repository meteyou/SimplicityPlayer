from mpd import MPDClient

class MPDModule:
    def __init__(self, config):
        self._config = config

        host = self._config.get('MPDModule', 'host', fallback='localhost')
        port = self._config.getint('MPDModule', 'port', fallback=6600)
        timeout = self._config.getint('MPDModule', 'timeout', fallback=10)

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
