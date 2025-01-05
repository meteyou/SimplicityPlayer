import configparser
import logging
import time

import RPi.GPIO as GPIO
from modules.RFIDModule import RFIDModule
from modules.LCDModule import LCDModule
from modules.MPDModule import MPDModule
from modules.StateManagerModule import StateManagerModule
from modules.TagManagerModule import TagManagerModule
from modules.USBModule import USBModule
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
    usb = USBModule(config, lcd, mpd)
    tag_manager = TagManagerModule(config)
    state_manager = StateManagerModule(config)

    def button_callback(_):
        mpd.toggle_playback()

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    try:
        GPIO.add_event_detect(16, GPIO.FALLING, callback=button_callback,
                              bouncetime=800)
    except RuntimeError as e:
        logging.getLogger('sp').error('Failed to add edge detection')
        logging.getLogger('sp').error(e)
        return

    # start the web server in a separate thread
    web_server = WebServerModule(config, lcd, rfid, tag_manager, state_manager)
    web_server_thread = Thread(target=web_server.run)
    web_server_thread.start()

    last_state_store = time.time()
    last_read_tag = None

    try:
        while True:
            if not rfid.is_locked() and not usb.is_working():
                lcd.clear_message()

                # read tag from RFID reader
                tag = rfid.wait_for_tag(rfid_read_delay)

                # if tag is not None and not the same as the last tag read
                if tag and tag != last_read_tag:
                    last_read_tag = tag

                    # get the file name from the tag
                    file_name = tag_manager.get_tag(tag)
                    if file_name is not None:
                        # get the elapsed time from the state manager
                        elapsed = state_manager.get_elapsed(file_name)
                        mpd.play(file_name, elapsed)
                    else:
                        lcd.set_message('Unbekannter Tag')

                # if tag is the same as the last tag read
                elif tag and tag == last_read_tag:
                    time.sleep(rfid_read_delay)

                # if tag is None, reset the last read tag
                elif tag is None and last_read_tag is not None:
                    last_read_tag = None

            # if the RFID reader is locked
            else:
                time.sleep(rfid_read_delay)

            # store the current state every 60 seconds
            state_time_diff = time.time() - last_state_store
            if state_time_diff > 60:
                state_manager.set_current(mpd.get_song())
                last_state_store = time.time()

            # check if a USB stick is inserted
            if not usb.is_working() and usb.exists():
                usb.copy_files()

            # do normal stuff here per tick
            lcd.do_tick()
    except KeyboardInterrupt:
        logging.getLogger('sp').info('Received KeyboardInterrupt.')

    logging.getLogger('sp').info('Stopping...')
    GPIO.cleanup()


if __name__ == "__main__":
    main()
