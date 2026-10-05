from datetime import datetime, timezone
from bs4 import BeautifulSoup

def extract_book_details(html_content, product_url, source_page):
    """Extracts raw fields and provenance metadata from a book detail page safely."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 1. Title
    title_el = soup.select_one("div.product_main h1")
    title = title_el.get_text(strip=True) if title_el else "Unknown Title"

    # 2. Price Text
    price_el = soup.select_one("div.product_main p.price_color")
    price_text = price_el.get_text(strip=True) if price_el else "£0.00"

    # 3. Availability Text
    stock_el = soup.select_one("div.product_main p.instock.availability")
    availability_text = stock_el.get_text(strip=True) if stock_el else "In stock (0 available)"

    # 4. Rating Text
    rating_el = soup.select_one("div.product_main p.star-rating")
    rating_text = "One"
    if rating_el and rating_el.get("class"):
        classes = rating_el.get("class")
        if len(classes) > 1:
            rating_text = classes[1]

    # 5. Description
    desc_header = soup.select_one("#product_description")
    desc_el = desc_header.find_next_sibling("p") if desc_header else None
    description = desc_el.get_text(strip=True) if desc_el else None

    # 6. Provenance
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }