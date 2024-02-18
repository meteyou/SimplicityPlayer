from flask import Flask, render_template, request, redirect, url_for
from DatabaseModule import DatabaseModule
from RFIDModule import RFIDModule
from LCDModule import LCDModule

app = Flask(__name__)
db = DatabaseModule(db_path='path_to_your_database.db')
rfid = RFIDModule()

@app.route('/')
def index():
    songs = db.get_all_songs()
    return render_template('index.html', songs=songs)

@app.route('/add', methods=['POST'])
def add_song():
    tag_id = request.form.get('tag_id')
    song_name = request.form.get('song_name')
    db.add_song(tag_id, song_name)
    return redirect(url_for('index'))

@app.route('/read_and_add', methods=['POST'])
def read_and_add():
    song_name = request.form.get('song_name')
    lcd.display_text("Bitte RFID-Tag vorhalten...")
    tag_id, _ = rfid.wait_for_card(timeout=30)
    if tag_id:
        db.add_song(tag_id, song_name)
        lcd.show_message("RFID erkannt und gespeichert!")
    else:
        lcd.show_message("Zeit abgelaufen, kein RFID erkannt.")
    return redirect(url_for('index'))

def run_server():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    run_server()
