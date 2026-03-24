from flask import Flask, render_template, request
import os
import requests
import base64
import random
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

mood_queries = {
    "happy": "happy upbeat",
    "sad": "sad mellow",
    "calm": "calm chill",
    "energetic": "energetic workout",
    "focus": "focus concentration",
    "party": "party dance",
    "romantic": "romantic love"
}

activity_queries = {
    "studying": "study instrumental",
    "working-out": "gym workout",
    "relaxing": "relax ambient",
    "commuting": "commute travel",
    "sleeping": "sleep soft",
    "partying": "party club"
}

def get_spotify_token():
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        raise Exception("Missing Spotify credentials in .env file")

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

    random_offset = random.randint(0, 20)

    params = {
        "q": query,
        "type": "track",
        "limit": 10,
        "offset": random_offset,
        "market": "GB"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    items = response.json()["tracks"]["items"]
    random.shuffle(items)

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

        if len(tracks) == limit:
            break

    return tracks

@app.route("/", methods=["GET", "POST"])
def home():
    mood = None
    activity = None
    songs = []
    error = None

    if request.method == "POST":
        mood = request.form.get("mood")
        activity = request.form.get("activity")

        mood_text = mood_queries.get(mood, "")
        activity_text = activity_queries.get(activity, "")
        combined_query = f"{mood_text} {activity_text}".strip()

        if combined_query:
            try:
                songs = search_tracks(combined_query)
            except Exception as e:
                error = f"Spotify error: {e}"

    return render_template(
        "index.html",
        mood=mood,
        activity=activity,
        songs=songs,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)