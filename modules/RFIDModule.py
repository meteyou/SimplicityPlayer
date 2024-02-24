import logging
import time

from mfrc522 import SimpleMFRC522

class RFIDModule:
    def __init__(self, config):
        self._config = config
        self._reader = SimpleMFRC522()

        self._polling_sleep = config.getfloat('RFIDModule', 'polling_sleep',
                                              fallback=0.5)

        self._lock = False

    def get_tag(self):
        try:
            return self._reader.read_id_no_block()
        except Exception as e:
            logging.getLogger('sp').error('Error reading RFID tag.')
            logging.getLogger('sp').exception(e)
            return None

    def wait_for_tag(self, timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            id = self.get_tag()
            if id:
                return str(id)
            time.sleep(self._polling_sleep)
        return None

    def is_locked(self):
        return self._lock

    def lock(self):
        self._lock = True

    def unlock(self):
        self._lock = False
