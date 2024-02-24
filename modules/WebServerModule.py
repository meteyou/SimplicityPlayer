import logging
import shutil
import time
from os import listdir, stat
from os.path import join

from flask import Flask, render_template, redirect, url_for, send_from_directory

from modules.MPDModule import MPDModule


# size formatting from https://stackoverflow.com/a/1094933/1166086
def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


class WebServerModule:
    def __init__(self, config, lcd, rfid, tag_manager, state_manager):
        self._config = config
        self._host = config.get('WebServerModule', 'host', fallback='0.0.0.0')
        self._port = config.get('WebServerModule', 'port', fallback=5000)
        self._fileDirPath = config.get('DEFAULT', 'audiobooksPath',
                                       fallback='/var/lib/mpd/music/')

        self._lcd = lcd
        self._rfid = rfid
        self._tagManager = tag_manager
        self._stateManager = state_manager
        self._mpd = MPDModule(config)

        self.app = Flask(__name__, template_folder='../templates')
        # declare routes
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/assets/<path:filepath>', 'assets',
                              self.assets)
        self.app.add_url_rule('/add_tag/<name>', 'add_tag', self.add_tag)
        self.app.add_url_rule('/remove_tag/<tag>', 'remove_tag',
                              self.remove_tag)
        self.app.add_url_rule('/play/<name>', 'play', self.play)
        self.app.add_url_rule('/play_from_start/<name>', 'play_from_start',
                              self.play)

    def run(self):
        self.app.run(host=self._host, port=self._port)

    def index(self):
        total, used, free = shutil.disk_usage(self._fileDirPath)
        usedPercent = round(used / total * 100, 0)
        freePercent = round(free / total * 100, 0)
        return render_template('index.html',
                               items=self._get_items(),
                               freePercent=freePercent,
                               usedPercent=usedPercent,
                               totalSpace=sizeof_fmt(total),
                               freeSpace=sizeof_fmt(free),
                               usedSpace=sizeof_fmt(used),
                               sizeof_fmt=sizeof_fmt)

    def _get_items(self, **k):
        currentFiles = sorted(listdir(self._fileDirPath))
        tags = self._tagManager.get_tags()
        states = self._stateManager.get_states()

        filesTagArray = []
        for fileName in currentFiles:
            file_stats = stat(join(self._fileDirPath, fileName))

            tag = None
            for key, value in tags.items():
                if value == fileName:
                    tag = key

            state = None
            if fileName in states:
                state = states[fileName]

            filesTagArray.append({"name": fileName,
                                  "size": file_stats.st_size,
                                  "tag": tag,
                                  "state": state})

        return filesTagArray

    def assets(self, filepath):
        return send_from_directory('../assets', filepath)

    def add_tag(self, name):
        self._rfid.lock()
        self._lcd.set_message("Bitte RFID-Tag", "vorhalten...")
        tag_id = self._rfid.wait_for_tag(timeout=30)
        if tag_id:
            self._tagManager.add_tag(tag_id, name)
            self._lcd.set_message("RFID erkannt", "und gespeichert!")
            time.sleep(10)
        else:
            self._lcd.set_message("Zeit abgelaufen,", "kein RFID erkannt.")
            time.sleep(5)

        self._rfid.unlock()
        return redirect(url_for('index'))

    def remove_tag(self, tag):
        self._tagManager.remove_tag(tag)
        return redirect(url_for('index'))

    def play(self, name):
        elapsed = 0

        state = self._stateManager.get_state(name)
        if state is not None:
            elapsed = state['elapsed']

        self._mpd.play(name, elapsed)
        return redirect(url_for('index'))

    def play_from_start(self, name):
        self._mpd.play(name, 0)
        return redirect(url_for('index'))
