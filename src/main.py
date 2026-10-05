# My orchestration layer


from urllib.parse import urljoin
from bs4 import BeautifulSoup
from fetcher import fetch_page



BASE_URL = "https://books.toscrape.com/catalogue/"
START_PAGE = "page-1.html"


def discover_catalogue_pages():
    catalogue_pages = 0
    unique_url = set()

    current_url = urljoin(BASE_URL, START_PAGE)
    page_count = 0

    while current_url and page_count < 3:
        page_count += 1
        filename = f"catalogue-page-{page_count}.html"

        html_content, was_cached = fetch_page(current_url, filename)
        if not html_content:
            break

        catalogue_pages += 1
        soup = BeautifulSoup(html_content, 'html.parser')

        # extract book links from the current catalogue page
        book_item = soup.select("article.product_pod h3 a")

        for item in book_item:
            href = item.get("href")

            absolute_url = urljoin(current_url, href)
            unique_urls.add(absolute_url)

        next_btn = soup.select_one("li.next > a")

        if next_btn:
            next_href = next_btn.get("href")
            current_url = urljoin(current_url, next_href)
        else:
            current_url = None

    print(f"catalogue_pages={catalogue_pages}, discovered={len(unique_urls)}, unique_urls={len(unique_urls)}")
    return unique_urls


if __name__ == "__main__":
    discover_catalogue_pages()