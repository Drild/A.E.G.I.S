import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import random
import subprocess
import time

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8888/callback"
CACHE_PATH = os.path.join(os.path.expanduser("~"), ".spotify_cache")

auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-read-playback-state user-modify-playback-state user-read-currently-playing",
    cache_path=CACHE_PATH,
    open_browser=True
)

token_info = {
    "access_token": "BQAfAAlYP9EvcU_vx6h1Ykm1NnMeoqu-75MQWLu4SPFmsPQNoOh3kABYEUWscy6QNWylENMIIslUzq764tpr7R4zb74UJ-H1GL28m9IQNLnxacekL4aFVsBLnWhT5W8pwqV8hSO9Uan_plZMCK-iRxGpbXswqgvKcr_SKrV1NHE-P0We13bj_-P9mVR-0TsZfy4-l_cVocNsmrmRk8EyfhaHfJG330JvPog03rIxUJ3Vc4XyBIzXEKPC116_",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "AQCcSOFNDz9l7uuqrOvVANGLRqr0YYEKUfRpLNccYwEvdPOnGDz6WyS9qEL1EMoaSNBz4e3m8teW54WNwOPSbFZWR5KLnPlyTN3gfMmdex9nCK6kFRJxb2N_sT_Wi-eQg9s",
    "scope": "user-read-playback-state user-modify-playback-state user-read-currently-playing",
    "expires_at": 1780370378
}

try:
    auth_manager.cache_handler.save_token_to_cache(token_info)
except Exception:
    pass

sp = spotipy.Spotify(auth_manager=auth_manager)

MOOD_PARAMS = {
    "happy":    {"valence": 0.8, "energy": 0.7, "tempo": 120},
    "sad":      {"valence": 0.2, "energy": 0.3, "tempo": 70},
    "chill":    {"valence": 0.5, "energy": 0.3, "tempo": 90},
    "focus":    {"valence": 0.5, "energy": 0.4, "tempo": 100},
    "hype":     {"valence": 0.7, "energy": 0.95, "tempo": 140},
    "angry":    {"valence": 0.1, "energy": 0.9, "tempo": 150},
    "romantic": {"valence": 0.6, "energy": 0.3, "tempo": 80},
    "workout":  {"valence": 0.6, "energy": 0.9, "tempo": 140},
    "study":    {"valence": 0.4, "energy": 0.2, "tempo": 80},
    "party":    {"valence": 0.8, "energy": 0.9, "tempo": 130},
}

def clean_query(query: str) -> str:
    remove = ["put on ", "i want to hear ", "can you play ",
              "please play ", "jarvis play ", "start playing ", "on spotify"]
    q = query.lower()
    for r in remove:
        q = q.replace(r, "")
    return q.strip()

def ensure_device() -> str | None:
    devices = sp.devices()["devices"]
    if devices:
        for d in devices:
            if d["is_active"]:
                return d["id"]
        return devices[0]["id"]
    subprocess.Popen("spotify", shell=True)
    time.sleep(4)
    devices = sp.devices()["devices"]
    return devices[0]["id"] if devices else None

def play_song(query: str) -> str:
    try:
        query = clean_query(query)
        device_id = ensure_device()
        if not device_id:
            return "Couldn't find or launch Spotify. Please open it manually."

        query_lower = query.lower()

        # Mood detection
        for mood, params in MOOD_PARAMS.items():
            if mood in query_lower:
                return play_mood(mood, params, device_id)

        # Artist detection
        artist_triggers = ["something by ", "a song by ", "random ", "by "]
        for trigger in artist_triggers:
            if trigger in query_lower:
                artist = query_lower.replace(trigger, "").strip()
                for word in ["song", "music", "track", "something", "random"]:
                    artist = artist.replace(word, "").strip()
                return play_by_artist(artist, device_id)

        # Specific song
        results = sp.search(q=query, limit=10, type="track")
        tracks = results["tracks"]["items"]
        if not tracks:
            return f"Couldn't find '{query}' on Spotify."
        track = max(tracks, key=lambda t: t.get("popularity", 0))
        sp.start_playback(device_id=device_id, uris=[track["uri"]])
        return f"Playing {track['name']} by {track['artists'][0]['name']}."

    except Exception as e:
        return f"Spotify error: {str(e)}"

def play_by_artist(artist: str, device_id: str) -> str:
    try:
        results = sp.search(q=f"artist:{artist}", limit=20, type="track")
        tracks = results["tracks"]["items"]
        if not tracks:
            return f"Couldn't find tracks by '{artist}'."
        track = random.choice(tracks)
        sp.start_playback(device_id=device_id, uris=[track["uri"]])
        return f"Playing {track['name']} by {track['artists'][0]['name']}."
    except Exception as e:
        return f"Spotify error: {str(e)}"

def play_mood(mood: str, params: dict, device_id: str) -> str:
    try:
        # Search for a mood playlist instead of using recommendations
        results = sp.search(q=f"{mood} mood playlist", limit=10, type="playlist")
        playlists = results["playlists"]["items"]
        if not playlists:
            results = sp.search(q=f"{mood} music", limit=10, type="track")
            tracks = results["tracks"]["items"]
            if not tracks:
                return f"Couldn't find {mood} songs."
            track = random.choice(tracks)
            sp.start_playback(device_id=device_id, uris=[track["uri"]])
            return f"Playing {track['name']} by {track['artists'][0]['name']} for a {mood} vibe."

        # Pick a random playlist and play it
        playlist = random.choice([p for p in playlists if p])
        sp.start_playback(device_id=device_id, context_uri=playlist["uri"])
        return f"Playing '{playlist['name']}' playlist for a {mood} vibe."
    except Exception as e:
        return f"Mood play error: {str(e)}"

def pause_music() -> str:
    try:
        sp.pause_playback()
        return "Paused."
    except Exception as e:
        return f"Spotify error: {str(e)}"

def next_track() -> str:
    try:
        sp.next_track()
        return "Skipped to next track."
    except Exception as e:
        return f"Spotify error: {str(e)}"

def previous_track() -> str:
    try:
        sp.previous_track()
        return "Going back to previous track."
    except Exception as e:
        return f"Spotify error: {str(e)}"

def current_track() -> str:
    try:
        current = sp.current_playback()
        if not current or not current["is_playing"]:
            return "Nothing is playing right now."
        track = current["item"]
        return f"Currently playing {track['name']} by {track['artists'][0]['name']}."
    except Exception as e:
        return f"Spotify error: {str(e)}"