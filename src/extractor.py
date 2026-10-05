from bs4 import BeautifulSoup
from datetime import datetime, timezone


def extract_book_details(html_content, product_url, source_page):
    """Responsible solely for parsing a book detail page and extracting raw fields."""
    soup = BeautifulSoup(html_content, "html.parser")

    # extract title
    title_el = soup.select_one("div.product_main h1")
    title = title_el.get_text(strip=True) if title_el else None

    # extract price
    price_el = soup.select_one("div.product_main p.price_color")
    price_text = price_el.get_text(strip=True) if price_el else None

    # extract stock availability
    stock_el = soup.select_one("div.product_main p.instock.availability")
    availability_text = stock_el.get_text(strip=True) if stock_el else None

    rating_el = soup.select_one("div.product_main p.star-rating")
    rating_text = None
    if rating_el and rating_el.get("class"):
        classes = rating_el.get("class")
        if len(classes) > 1:
            rating_text = classes[1]

    # extract Description
    desc_header = soup.select_one("#product_description")
    desc_el = desc_header.find_next_sibling("p") if desc_header else None
    description = desc_el.get_text(strip=True) if desc_el else None

    # auditing
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    


    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text":  availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page":  source_page,
        "fetched_at": fetched_at
    }



