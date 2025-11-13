from playwright.sync_api import sync_playwright


def run(playwright):
    browser = playwright.chromium.launch(
        headless=False
    )  # headless=True runs without UI
    page = browser.new_page()
    page.goto("https://feelthemusi.com/playlist/pem5gu")
    print(page.title())
    # browser.close()


with sync_playwright() as playwright:
    run(playwright)
