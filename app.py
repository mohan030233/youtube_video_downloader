from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


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
        print("INFO ERROR:", e)
        return jsonify({"error": "Video not available"}), 500


@app.route("/download", methods=["POST"])
def download():
    try:
        data = request.get_json()
        url = data["url"]
        mode = data["mode"]
        quality = data["quality"]

        output_template = os.path.join(DOWNLOADS_DIR, "%(title)s.%(ext)s")

        if mode == "video":
            if quality == "Best":
                fmt = "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                fmt = f"bv*[ext=mp4][height<={quality}]+ba[ext=m4a]/b[ext=mp4]"

            ydl_opts = {
                "format": fmt,
                "merge_output_format": "mp4",
                "outtmpl": output_template
            }

        else:
            ydl_opts = {
                "format": "bestaudio[ext=m4a]/bestaudio",
                "outtmpl": output_template
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if not os.path.exists(filename):
            possible_extensions = [".m4a", ".webm", ".mp4"]
            for ext in possible_extensions:
                test_file = os.path.splitext(filename)[0] + ext
                if os.path.exists(test_file):
                    filename = test_file
                    break

        return send_file(filename, as_attachment=True)

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        return jsonify({"error": "Download failed"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
