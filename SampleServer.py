from flask import Flask, send_file

from CalenderInterface import SharedCalendar
from BitmapGenerator import make_countdown_screen

app = Flask(__name__)

@app.route("/image")
def image():
    cal = SharedCalendar()
    event = cal.next_event()
    make_countdown_screen(event).save(f"./screen.bmp")

    return send_file("./screen.bmp", mimetype="application/octet-stream")

@app.route("/cover_image")
def cover_image():
    return send_file("./cover_image.bmp", mimetype="application/octet-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
