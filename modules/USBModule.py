import logging
import os
import shutil


class USBModule:
    def __init__(self, config, lcd, mpd):
        self._config = config
        self._path = self._config.get('USBModule', 'path',
                                      fallback='/media/pi/audiobooks')
        self._store_path = self._config.get('DEFAULT', 'audiobooksPath',
                                            fallback='/var/lib/mpd/music')
        self._lcd = lcd
        self._mpd = mpd

        self._is_working = False

    def is_working(self):
        return self._is_working

    def exists(self):
        if not os.path.exists(self._path):
            return False
        if not os.path.exists(self._store_path):
            return False

        return len(self._file_to_copy()) > 0

    def _file_to_copy(self):
        output = []
        _files_in_store = os.listdir(self._store_path)
        for file in os.listdir(self._path):
            if file.endswith(".mp3") and file not in _files_in_store:
                output.append(file)

        return output

    def copy_files(self):
        logging.getLogger('sp').info('Copying files from USB stick to store'
                                     'path')
        self._is_working = True
        self._lcd.set_message('Kopieren von USB')

        for file in self._file_to_copy():
            try:
                logging.getLogger('sp').info('Copying %s' % file)
                shutil.copy2(self._path + '/' + file,
                             self._store_path + '/' + file)
            except Exception as e:
                logging.getLogger('sp').error('Error while copying file')
                logging.getLogger('sp').exception(e)

        self._mpd.update()
        self._is_working = False
