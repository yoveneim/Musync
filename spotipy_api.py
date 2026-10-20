import os
import re

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from tqdm import tqdm

ERRORS_FILE = "errors.csv"
SCOPE = "playlist-modify-public"
BATCH_SIZE = 100  # Spotify accepts at most 100 tracks per request

# Noise found in YouTube titles that hurts the Spotify search
NOISE_PATTERNS = [
    r"\[.*?\]",  # [Official Music Video], [S1.E12]
    r"\(.*?\)",  # (Prod. X), (FULL QUALITY)
    r"#\w+",  # #OFB
    r"@\w+",  # @MixtapeMadness
    r"\b(official|music|lyric|lyrics|video|audio|visualizer|hd|4k)\b",
    r"\bw/",
]


def authenticate():
    """Log in with the credentials found in .env (SPOTIPY_CLIENT_ID, ...)."""
    load_dotenv()
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
            scope=SCOPE,
        )
    )


def clean_title(title):
    cleaned = title
    for pattern in NOISE_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s(?:[|:\-]|x|X)\s", " ", cleaned)  # "A | B", "A x B"
    cleaned = " ".join(cleaned.split())
    return cleaned or title


def find_track(sp, title):
    """Return the Spotify URI of the best match for a title, or None."""
    result = sp.search(q=clean_title(title), limit=1, type="track")
    items = result["tracks"]["items"]
    return items[0]["uri"] if items else None


def build_playlist(songs, name):
    sp = authenticate()
    user_id = sp.current_user()["id"]

    song_uris = []
    errors = []
    for title in tqdm(songs, desc="Searching on Spotify"):
        uri = find_track(sp, title)
        if uri:
            song_uris.append(uri)
        else:
            errors.append(title)

    playlist = sp.user_playlist_create(user_id, name, public=True)
    for i in range(0, len(song_uris), BATCH_SIZE):
        sp.playlist_add_items(playlist["id"], song_uris[i : i + BATCH_SIZE])

    with open(ERRORS_FILE, "w", encoding="utf-8") as f:
        f.writelines(f"{title}\n" for title in errors)

    print(f"Added {len(song_uris)}/{len(songs)} songs to '{name}'")
    print(playlist["external_urls"]["spotify"])
    if errors:
        print(f"{len(errors)} songs not found, see {ERRORS_FILE}")
