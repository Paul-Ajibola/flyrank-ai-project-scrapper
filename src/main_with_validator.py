from urllib.parse import urljoin
from bs4 import BeautifulSoup
from fetcher import fetch_page
from extractor import extract_book_details
from validator import validate_raw_record

BASE_URL = "https://books.toscrape.com/catalogue/"
START_PAGE = "page-1.html"

def run_pipeline():
    print("--- Discovering Catalogue Pages and Book URLs ---")
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
            url_to_source[absolute_url] = current_url
            
        next_btn = soup.select_one("li.next > a")
        next_href = next_btn.get("href") if next_btn else None
        current_url = urljoin(current_url, next_href) if next_href else None

    print(f"catalogue_pages={catalogue_pages}, discovered={len(unique_urls)}")

    print("\n--- Extracting and Validating Records ---")
    normalized_records = []
    
    for idx, book_url in enumerate(unique_urls, start=1):
        book_filename = f"book-{idx}.html"
        book_html, _ = fetch_page(book_url, book_filename)
        if not book_html:
            continue
            
        source_page = url_to_source.get(book_url)
        
        # Stage 3: Extract raw record
        raw_record = extract_book_details(book_html, book_url, source_page)
        
        # Stage 4: Validate and normalize record
        validated_record = validate_raw_record(raw_record)
        if validated_record:
            normalized_records.append(validated_record.model_dump())

    # Required Checkpoint Output for Stage 4
    print(f"\n --- Successfully validated records: {len(normalized_records)}")
    if normalized_records:
        import json
        print("\nSample Normalized Record:")
        print(json.dumps(normalized_records[0], indent=2))
        
    return normalized_records

if __name__ == "__main__":
    run_pipeline()

