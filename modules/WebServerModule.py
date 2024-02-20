import shutil
from os import listdir, stat
from os.path import join

from flask import Flask, render_template, request, redirect, url_for, \
    send_from_directory


#from DatabaseModule import DatabaseModule
#from RFIDModule import RFIDModule
#from LCDModule import LCDModule

# size formatting from https://stackoverflow.com/a/1094933/1166086
def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

class WebServerModule:
    def __init__(self, config):
        self._config = config
        self._host = config.get('WebServerModule', 'host', fallback='0.0.0.0')
        self._port = config.get('WebServerModule', 'port', fallback=5000)
        self._fileDirPath = config.get('WebServerModule', 'fileDirPath',
                                       fallback='/var/lib/mpd/music/')

        self.app = Flask(__name__, template_folder='../templates')
        # declare routes
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/assets/<path:filepath>', 'assets', self.assets)
        self.app.add_url_rule('/addTag/<name>', 'addTag', self.addTag)

        #self.app.add_url_rule('/add', 'add_song', self.add_song, methods=['POST'])
        #self.app.add_url_rule('/read_and_add', 'read_and_add', self.read_and_add, methods=['POST'])

    def run(self):
        self.app.run(host=self._host, port=self._port)

    def index(self):
        #songs = db.get_all_songs()
        items = []
        total, used, free = shutil.disk_usage(self._fileDirPath)
        usedPercent = round(used / total * 100, 0)
        freePercent = round(free / total * 100, 0)
        return render_template('index.html',
                               items=self._getItems(),
                               freePercent=freePercent,
                               usedPercent=usedPercent,
                               totalSpace=sizeof_fmt(total),
                               freeSpace=sizeof_fmt(free),
                               usedSpace=sizeof_fmt(used),
                               sizeof_fmt=sizeof_fmt)

    def _getItems(self, **k):
        currentFiles = sorted(listdir(self._fileDirPath))
        tags = []

        filesTagArray = []
        for fileName in currentFiles:
            file_stats = stat(join(self._fileDirPath, fileName))

            filesTagArray.append({"name": fileName,
                                  "size": file_stats.st_size,
                                  "tag": None})


        return filesTagArray

    def assets(self, filepath):
        return send_from_directory('../assets', filepath)

    def addTag(self, name):
        #tagActor.addTag(name)
        return redirect(url_for('index'))


#db = DatabaseModule(db_path='path_to_your_database.db')
#rfid = RFIDModule()

# @app.route('/add', methods=['POST'])
# def add_song():
#     tag_id = request.form.get('tag_id')
#     song_name = request.form.get('song_name')
#     db.add_song(tag_id, song_name)
#     return redirect(url_for('index'))

# @app.route('/read_and_add', methods=['POST'])
# def read_and_add():
#     song_name = request.form.get('song_name')
#     lcd.display_text("Bitte RFID-Tag vorhalten...")
#     tag_id, _ = rfid.wait_for_card(timeout=30)
#     if tag_id:
#         db.add_song(tag_id, song_name)
#         lcd.show_message("RFID erkannt und gespeichert!")
#     else:
#         lcd.show_message("Zeit abgelaufen, kein RFID erkannt.")
#     return redirect(url_for('index'))