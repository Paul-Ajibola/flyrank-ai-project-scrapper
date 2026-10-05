# My orchestration layer


from urllib.parse import urljoin
from bs4 import BeautifulSoup
from fetcher import fetch_page



BASE_URL = "https://books.toscrape.com/catalogue/"
START_PAGE = "page-1.html"


def discover_catalogue_pages():
    """Start at catalogue page 1, follow the site's 'next' links, stop after 3
    catalogue pages, and collect the book URLs found those pages.
    """
    # start the counter
    catalogue_pages = 0
    # create empty python set; to prevent duplicates
    unique_urls = set()

    # build the first url
    current_url = urljoin(BASE_URL, START_PAGE)

    # begin the page counter
    page_count = 0

    while current_url and page_count < 3:
        page_count += 1
        filename = f"catalogue-page-{page_count}.html"

        html_content, was_cached = fetch_page(current_url, filename)
        # returns html content and was_cached returns a boolean
        if not html_content:
            break

        catalogue_pages += 1
        # use BeautifulSoup to parse the html content and make it accessible and readable
        soup = BeautifulSoup(html_content, 'html.parser')
        # soup: BeautifulSoup representation of the HTML page

        # extract book links from the current catalogue page
        # CSS selector; look for all <a> elements inside an <h3> inside an <article>
        # whose class is 'product_pod'. This targets the links of matching elements
        # returns: {a book link}. [remember a typical html structure]

        # selector 1
        book_item = soup.select("article.product_pod h3 a")

        for item in book_item:
            href = item.get("href")
            # use 'href' to generate the absolute url from the relative url
            absolute_url = urljoin(current_url, href)
            # add the absolute url to the set of unique urls
            unique_urls.add(absolute_url)

        # look for the 'next' button on the HTML page to the next page
        # CSS selector

        # selector 2
        next_btn = soup.select_one("li.next > a")
        print(f"DEBUG: Page {page_count} next button found? -> {next_btn}")

        # if next_btn is found, then we update current_url to the next page url
        # if not found, then we set current_url to None, which will end the while loop
        if next_btn:
            next_href = next_btn.get("href")
            current_url = urljoin(current_url, next_href)
        else:
            current_url = None

    print(f"catalogue_pages={catalogue_pages}, discovered={len(unique_urls)}, unique_urls={len(unique_urls)}")
    return unique_urls


if __name__ == "__main__":
    discover_catalogue_pages()

