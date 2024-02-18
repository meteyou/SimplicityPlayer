import configparser
import logging

import RPi.GPIO as GPIO
from modules.RFIDModule import RFIDModule
from modules.LCDModule import LCDModule
from modules.MPDModule import MPDModule
#from modules.DatabaseModule import DatabaseModule
#from modules.WebServerModule import run_server
#from threading import Thread

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

    rfid = RFIDModule(config)
    lcd = LCDModule(config)
    #db = DatabaseModule(db_path='path_to_your_database.db')

    # start the web server in a separate thread
    #server_thread = Thread(target=run_server)
    #server_thread.start()

    try:
        while True:
            lcd.clear_message()

            id = rfid.wait_for_tag(rfid_read_delay)
            if id:
                lcd.set_message("RFID gelesen:", f"{id}")

            # do normal stuff here per tick
            lcd.do_tick()
    except KeyboardInterrupt:
        logging.getLogger('sp').info('Received KeyboardInterrupt.')

    logging.getLogger('sp').info('Stopping...')
    GPIO.cleanup()

if __name__ == "__main__":
    main()