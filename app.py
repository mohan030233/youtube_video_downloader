from flask import Flask, render_template, request, jsonify
import yt_dlp
import os
import requests
import time
from flask import send_file


app = Flask(__name__)

DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
THUMB_DIR = os.path.join(BASE_DIR, "static", "thumbnails")
os.makedirs(THUMB_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/info", methods=["POST"])
def info():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "No URL"}), 400

        ydl_opts = {
            "quiet": True,
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        # Get only real video resolutions (ignore trash formats)
        resolutions = sorted(
            list({
                f.get("height")
                for f in info.get("formats", [])
                if f.get("height")
                and f.get("vcodec") != "none"
                and f.get("height") >= 144
            }),
            reverse=True
        )

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "resolutions": resolutions
        })

    except Exception as e:
        print("🔥 INFO ERROR:", e)
        return jsonify({"error": "Video not available"}), 500






@app.route("/download", methods=["POST"])
def download():
    url = request.json["url"]
    mode = request.json["mode"]
    quality = request.json["quality"]

    temp_dir = os.path.join(BASE_DIR, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    output_template = os.path.join(temp_dir, "%(title)s.%(ext)s")

    if mode == "video":
        if quality == "Best":
            fmt = "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
        else:
            fmt = f"bv*[ext=mp4][height<={quality}]+ba[ext=m4a]/b[ext=mp4]"

        opts = {
            "format": fmt,
            "merge_output_format": "mp4",
            "outtmpl": output_template
        }

    else:
        opts = {
            "format": "bestaudio[ext=m4a]/bestaudio",
            "outtmpl": output_template,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }]
        }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return send_file(filename, as_attachment=True)



if __name__ == "__main__":
    app.run(debug=True)
