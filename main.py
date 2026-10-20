import argparse
import csv

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from spotipy_api import build_playlist

SONGS_FILE = "songs.csv"


def scrape(url):
    """Open the Musi playlist share page and return the list of video titles."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector(".video_title")
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    return [link.get_text(strip=True) for link in soup.find_all(class_="video_title")]


def save_songs(songs, path=SONGS_FILE):
    # One title per row, so titles containing commas stay intact
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for song in songs:
            writer.writerow([song])


def load_songs(path=SONGS_FILE):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return [row[0] for row in csv.reader(f) if row]


def main():
    parser = argparse.ArgumentParser(description="Move a Musi playlist to Spotify.")
    parser.add_argument(
        "url",
        nargs="?",
        help="Musi playlist share link (https://feelthemusi.com/playlist/<id>)",
    )
    parser.add_argument(
        "--name", default="MyMusync", help="name of the Spotify playlist to create"
    )
    parser.add_argument(
        "--from-csv",
        action="store_true",
        help=f"skip scraping and reuse the titles saved in {SONGS_FILE}",
    )
    args = parser.parse_args()

    if args.from_csv:
        songs = load_songs()
    elif args.url:
        songs = scrape(args.url)
        if not songs:
            parser.exit(1, "No songs found on that page.\n")
        save_songs(songs)
        print(f"Scraped {len(songs)} songs into {SONGS_FILE}")
    else:
        parser.error("give a playlist URL or use --from-csv")

    build_playlist(songs, args.name)


if __name__ == "__main__":
    main()
