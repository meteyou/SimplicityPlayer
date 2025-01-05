from RPLCD.i2c import CharLCD
from modules.MPDModule import MPDModule
import logging

class LCDModule:
    def __init__(self, config, mpd):
        self._config = config

        self._enabled = self._config.getboolean('LCDModule', 'enabled', fallback=True)
        self._mpd = mpd

        if self._enabled:
            self._lcd = CharLCD(i2c_expander='PCF8574', address=0x27,
                                auto_linebreaks=False)
            self.clear()

        self._message_1 = None
        self._message_2 = None
        self._textPosition = 0

    def do_tick(self):
        if not self._enabled:
            return

        # if there is a message, display it
        if self._message_1 is not None or self._message_2 is not None:
            self._lcd.clear()
            if self._message_1 is not None:
                self._lcd.cursor_pos = (0, 0)
                self._lcd.write_string(self._message_1)
            if self._message_2 is not None:
                self._lcd.cursor_pos = (1, 0)
                self._lcd.write_string(self._message_2)
            return

        state = self._mpd.get_state()
        song = self._mpd.get_song()

        if state is not None or song is not None:
            self._lcd.clear()

        if state is not None:
            self._lcd.cursor_pos = (0, 0)
            self._lcd.write_string(state.capitalize())

        if state == 'play' or state == 'pause':
            duration = int(song['duration'] / 60)
            elapsed = int(song['elapsed'] / 60)
            text = '%s/%s' % (elapsed, duration)
            textLength = len(text)
            self._lcd.cursor_pos = (0, 16 - textLength)
            self._lcd.write_string(text)

        if song is not None:
            self._textPosition += 1
            name = song['name'].replace('.mp3', '')

            namesplits = [name[i:i + 16] for i in
                          range(0, len(name), 16)]
            if self._textPosition >= len(namesplits):
                self._textPosition = 0

            self._lcd.cursor_pos = (1, 0)
            self._lcd.write_string(namesplits[self._textPosition])

    def clear(self):
        if self._enabled:
            self._lcd.clear()

    def set_message(self, message_1, message_2=None):
        self._message_1 = message_1
        self._message_2 = message_2

        if not self._enabled:
            logging.getLogger('sp').info(f'LCD: {message_1}, {message_2}')

    def clear_message(self):
        self._message_1 = None
        self._message_2 = None
