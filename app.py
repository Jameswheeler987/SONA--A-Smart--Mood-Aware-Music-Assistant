from flask import Flask, render_template, request
import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

mood_queries = {
    "happy": "happy upbeat pop",
    "sad": "sad acoustic mellow",
    "calm": "calm ambient chill",
    "energetic": "energetic workout dance",
    "focus": "deep focus instrumental",
    "party": "party dance hits",
    "romantic": "romantic love songs"
}

def get_spotify_token():
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()

    return response.json()["access_token"]

def search_tracks(query, limit=5):
    token = get_spotify_token()

    url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": query,
        "type": "track",
        "limit": limit
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    items = response.json()["tracks"]["items"]

    tracks = []
    for item in items:
        track_name = item["name"]
        artists = ", ".join(artist["name"] for artist in item["artists"])
        spotify_url = item["external_urls"]["spotify"]

        image_url = ""
        if item["album"]["images"]:
            image_url = item["album"]["images"][-1]["url"]

        tracks.append({
            "name": track_name,
            "artists": artists,
            "url": spotify_url,
            "image": image_url
        })

    return tracks

@app.route("/", methods=["GET", "POST"])
def home():
    mood = None
    songs = []
    error = None

    if request.method == "POST":
        mood = request.form.get("mood")
        query = mood_queries.get(mood)

        if query:
            try:
                songs = search_tracks(query)
            except Exception as e:
                error = f"Spotify error: {e}"

    return render_template("index.html", mood=mood, songs=songs, error=error)

if __name__ == "__main__":
    app.run(debug=True)