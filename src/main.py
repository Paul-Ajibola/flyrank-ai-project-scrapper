import os
import requests


CACHE_DIR = "cache"
PAGE_URL="https://books.toscrape.com/catalogue/page-1.html"
CACHE_FILE = os.path.join(CACHE_DIR, "catalogue-page-1.html")


def fetch_first_page():
    os.makedirs(CACHE_DIR, exist_ok=True)

    # check if cache exists
    if os.path.exists(CACHE_FILE):
        print("CACHE HIT")
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"Response size: {len(content)} bytes")
        return content

    print("FETCH")

    # set up the User-Agent for 'id' as part of being polite
    headers = {
        "User-Agent": "FlyRankInternship-A9/1.0 (https://github.com/Paul-Ajibola/flyrank-ai-project-scrapper)"
    }

    try:
        response = requests.get(PAGE_URL, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None

    # check status code strictly
    if response.status_code != 200:
        print(f"Failed fetch: Status code: {response.status_code}")
        return None

    content = response.text
    print(f"Response size: {len(content)} bytes")

    # save to cache
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    return content


if __name__ == "__main__":
    fetch_first_page()


