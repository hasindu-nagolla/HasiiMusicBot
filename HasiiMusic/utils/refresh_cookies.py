import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()  # Load credentials from .env

YOUTUBE_EMAIL = os.getenv("YOUTUBE_EMAIL")
YOUTUBE_PASS = os.getenv("YOUTUBE_PASS")
COOKIES_PATH = os.path.join(os.path.dirname(__file__), '../assets/cookies.txt')

def fetch_new_cookies():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto('https://accounts.google.com/signin/v2/identifier?service=youtube')
        page.fill('input[type="email"]', YOUTUBE_EMAIL)
        page.click('button:has-text("Next")')
        page.wait_for_selector('input[type="password"]', timeout=20000)
        page.fill('input[type="password"]', YOUTUBE_PASS)
        page.click('button:has-text("Next")')
        page.wait_for_timeout(5000)
        page.goto('https://youtube.com')

        cookies = context.cookies()
        with open(COOKIES_PATH, 'w') as f:
            for cookie in cookies:
                f.write(f"{cookie['name']}={cookie['value']}; domain={cookie['domain']}; path={cookie['path']};\n")
        browser.close()

if __name__ == "__main__":
    fetch_new_cookies()



