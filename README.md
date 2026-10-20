# Musync

Rescue your playlists from [Musi](https://feelthemusi.com), the music app that streamed
from YouTube and no longer works, and move them to Spotify.

Musi playlists can still be opened through their share link
(`https://feelthemusi.com/playlist/<id>`). Musync scrapes the song titles from that page with
Playwright (they are the original YouTube video titles), cleans them
(removes `[Official Video]`, `#tags`, `@channels`, ...), searches each one on Spotify and
adds the matches to a new playlist.

## Setup

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run playwright install chromium
```

Create a Spotify app on the [Spotify developer dashboard](https://developer.spotify.com/dashboard)
and add `https://127.0.0.1:9090` as a redirect URI. Then copy the example env file and fill in
your credentials:

```bash
cp .env.example .env
```

## Usage

```bash
uv run main.py https://feelthemusi.com/playlist/<id> --name "My playlist"
```

The first run opens a browser to log in to Spotify; the token is then cached in `.cache`.

- The scraped titles are saved to `songs.csv`. To retry the Spotify part without scraping
  again, run `uv run main.py --from-csv`.
- Titles that could not be found on Spotify are written to `errors.csv`.
