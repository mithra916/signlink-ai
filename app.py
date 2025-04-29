from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import requests
from grammar_convert import convert_to_asl_grammar
from play_signs import download_media

app = Flask(__name__)
MEDIA_FOLDER = "media"
UPLOAD_FOLDER = "uploads"

os.makedirs(MEDIA_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["MEDIA_FOLDER"] = MEDIA_FOLDER
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert_text():
    text = request.form.get("text")
    if not text:
        return jsonify({"error": "No input provided."})

    asl_text = convert_to_asl_grammar(text)
    words = asl_text.split()
    video_urls = []

    try:
        with open("word_to_media.json", "r") as f:
            word_map = json.load(f)
    except:
        word_map = {}

    for word in words:
        media_file = word_map.get(word, f"{word}.mp4")
        media_path = os.path.join(MEDIA_FOLDER, media_file)

        if not os.path.exists(media_path):
            downloaded = download_media(word)
            if downloaded:
                media_file = os.path.basename(downloaded)
                media_path = os.path.join(MEDIA_FOLDER, media_file)
            else:
                continue

        video_urls.append(f"/media/{media_file}")

    return jsonify({
        "asl_gloss": asl_text,
        "media": video_urls
    })

@app.route("/search_convert", methods=["POST"])
def search_convert():
    data = request.get_json()
    query = data.get("query")
    summary = query

    try:
        wiki = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}")
        if wiki.status_code == 200:
            summary = wiki.json().get("extract", summary)
    except Exception as e:
        print("Wikipedia lookup failed:", e)

    asl_text = convert_to_asl_grammar(summary)
    words = asl_text.split()

    media_paths = []
    try:
        with open("word_to_media.json", "r") as f:
            word_map = json.load(f)
    except:
        word_map = {}

    for word in words:
        media_file = word_map.get(word, f"{word}.mp4")
        media_path = os.path.join(MEDIA_FOLDER, media_file)
        if os.path.exists(media_path):
            media_paths.append(f"/media/{media_file}")

    return jsonify({
        "asl_gloss": asl_text,
        "media": media_paths
    })

@app.route("/media/<filename>")
def media(filename):
    return send_from_directory(MEDIA_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
