from bs4 import BeautifulSoup
import requests
from playwright.sync_api import sync_playwright

url = "https://feelthemusi.com/playlist/pem5gu"  # This is the link that contain my playlist


def run(playwright):
    browser = playwright.chromium.launch(
        headless=True, slow_mo=1000
    )  # headless=True runs without UI
    page = browser.new_page()
    page.goto(url)
    # html = page.inner_html("#container").
    html = page.content()
    browser.close()
    return html


def test_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        print("Success")
    return response


def main():
    # Check that URL is working by sending a request
    try:
        test_url(url)
    except Exception as e:
        print(f"Something went Wrong : the output code is: {e}")
    # Deploying Playwright to scrape
    with sync_playwright() as playwright:
        html = run(playwright)
        soup = BeautifulSoup(html, "html.parser")
    # Scraping and saving song name + artist in csv file
    links = soup.find_all(class_="video_title")
    print(len(links))
    with open("songs.csv", mode="w", encoding="utf-8") as b:
        for link in links[:-1]:
            song = link.get_text(strip=True) + ","
            b.write(song)
        b.write(links[-1].get_text(strip=True))
        b.close()


if __name__ == "__main__":
    main()
