import os
import time
import requests 


CACHE_DIR = "cache"

def fetch_page(url, filename):
    """Responsible solely for fetching a page and managing the local cache."""
    cache_path = os.path.join(CACHE_DIR, filename)
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # Check local cache first
    if os.path.exists(cache_path):
        print("CACHE HIT!")
        with open(cache_path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"Response size: {len(content)} bytes")
        return content, True


    # Fetch from the web if not cached
    print("FETCH")
    headers = {
        "User-Agent": "FlyRankInternship-A9/1.0 (https://github.com/Paul-Ajibola/flyrank-ai-project-scrapper)"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching {url}: {e}")
        return None, False

    if response.status_code != 200:
        print(f"Failed fetch {url}. Status code: {response.status_code}")
        return None, False

    content = response.text
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(content)

    # delay on live network requests
    time.sleep(0.2)
    return content, False

