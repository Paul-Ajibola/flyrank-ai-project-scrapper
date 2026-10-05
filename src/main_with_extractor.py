from urllib.parse import urljoin
from bs4 import BeautifulSoup
from fetcher import fetch_page
from extractor import extract_book_details


BASE_URL = "https://books.toscrape.com/catalogue/"
START_PAGE = "page-1.html"


def run_pipeline():
    print("---- Discovering Catalogues Pages and Book URLs ----")
    catalogue_pages = 0
    unique_urls = set()
    url_to_source = {}


    current_url = urljoin(BASE_URL, START_PAGE)
    page_count = 0

    while current_url and page_count < 3:
        page_count += 1
        filename = f"catalogue-page-{page_count}.html"

        html_content, _ = fetch_page(current_url, filename)
        if not html_content:
            break

        catalogue_pages += 1
        soup = BeautifulSoup(html_content, "html.parser")

        for item in soup.select("article.product_pod h3 a"):
            absolute_url = urljoin(current_url, item.get("href"))
            unique_urls.add(absolute_url)
            # 'absolute_url' is the key and 'current_url' is the value
            url_to_source[absolute_url] = current_url

        next_btn = soup.select_one("li.next > a")
        print(f"DEBUG: Page {page_count} next button found? -> {next_btn}")

        if next_btn:
            current_url = urljoin(current_url, next_btn.get("href"))
        else:
            current_url = None

        print(f"catalogue_pages={catalogue_pages}, discovered={len(unique_urls)}, unique_urls={len(unique_urls)}")

        print("\n --- Extracting Raw Records from Detail Pgaes ----")

        raw_records = []

        for idx, book_url in enumerate(unique_urls, start=1):
            book_filename = f"book-{idx}.html"

            book_html, _ = fetch_page(book_url, book_filename)

            if not book_html:
                continue

            source_page = url_to_source.get(book_url)
            record = extract_book_details(book_html, book_url, source_page)
            raw_records.append(record)

        print(f"-- Extracted raw records: {len(raw_records)}")

        if raw_records:
            print("\Sample Complete Record")
            import json
            print(json.dumps(raw_records[0], indent=2))

        return raw_records


if __name__ == "__main__":
    run_pipeline()

