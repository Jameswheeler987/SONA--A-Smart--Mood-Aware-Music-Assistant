from flask import Flask, render_template, request

app = Flask(__name__)

# Dummy music data
music_data = {
    "happy": ["Happy - Pharrell Williams", "Good Time - Owl City", "Can't Stop the Feeling - Justin Timberlake"],
    "sad": ["Someone Like You - Adele", "Fix You - Coldplay", "Let Her Go - Passenger"],
    "calm": ["Weightless - Marconi Union", "Sunset Lover - Petit Biscuit", "Bloom - ODESZA"],
    "energetic": ["Titanium - David Guetta", "Stronger - Kanye West", "Eye of the Tiger - Survivor"]
}

@app.route("/", methods=["GET", "POST"])
def home():
    mood = None
    songs = []

    if request.method == "POST":
        mood = request.form.get("mood")
        songs = music_data.get(mood, [])

    return render_template("index.html", mood=mood, songs=songs)

if __name__ == "__main__":
    app.run(debug=True)