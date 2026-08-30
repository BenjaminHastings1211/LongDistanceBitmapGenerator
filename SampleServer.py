from flask import Flask, send_from_directory

app = Flask(__name__)

SCREEN_DIR = "./screens"


@app.route("/<path:filename>")
def serve_screen(filename):
    return send_from_directory(SCREEN_DIR, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)