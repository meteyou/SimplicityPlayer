import configparser
import logging
import time

import RPi.GPIO as GPIO
from modules.RFIDModule import RFIDModule
from modules.LCDModule import LCDModule
from modules.MPDModule import MPDModule
from modules.StateManagerModule import StateManagerModule
from modules.TagManagerModule import TagManagerModule
from modules.WebServerModule import WebServerModule
from threading import Thread


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    logfile = config.get('DEFAULT', 'logfile', fallback='SimplicityPlayer.log')

    logging.basicConfig(filename=logfile,
                        format="%(asctime)s [%(module)s.%(funcName)s] %("
                               "levelname)s: %(message)s")
    logging.getLogger('sp').setLevel(logging.DEBUG)
    logging.getLogger('sp').info('Starting...')

    rfid_read_delay = config.getint('DEFAULT', 'rfid_read_delay', fallback=2)

    mpd = MPDModule(config)
    rfid = RFIDModule(config)
    lcd = LCDModule(config, mpd)
    tag_manager = TagManagerModule(config)
    state_manager = StateManagerModule(config)

    # start the web server in a separate thread
    web_server = WebServerModule(config, lcd, rfid, tag_manager, state_manager)
    web_server_thread = Thread(target=web_server.run)
    web_server_thread.start()

    last_state_store = time.time()

    try:
        while True:
            if not rfid.is_locked():
                lcd.clear_message()

                id = rfid.wait_for_tag(rfid_read_delay)
                if id:
                    lcd.set_message("RFID gelesen:", f"{id}")
            else:
                logging.getLogger('sp').info('RFID is locked. Waiting...')
                time.sleep(rfid_read_delay)

            state_time_diff = time.time() - last_state_store
            if state_time_diff > 60:
                state_manager.set_current(mpd.get_song())
                last_state_store = time.time()

            # do normal stuff here per tick
            lcd.do_tick()
    except KeyboardInterrupt:
        logging.getLogger('sp').info('Received KeyboardInterrupt.')

    logging.getLogger('sp').info('Stopping...')
    GPIO.cleanup()


if __name__ == "__main__":
    main()
