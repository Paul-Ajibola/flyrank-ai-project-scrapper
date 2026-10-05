
# FlyRank-AI Book-Scraper

A modular Python web-scraping pipeline built to demonstrate reliable data collection, caching, extraction, validation, normalization, provenance tracking, and structured data export.

The project scrapes book information from [Books to Scrape](https://books.toscrape.com/), processes the raw HTML through several stages, validates and normalizes the extracted data with Pydantic, and exports the final records to JSON and CSV.

---

## Project Overview

This project was developed as a practical exercise in building a reliable data ingestion pipeline rather than simply writing a web scraper.

The pipeline follows this general flow:

```text
Website
   │
   ▼
Fetch Web Pages
   │
   ├── Cache locally
   │
   ▼
Discover Catalogue Pages
   │
   ▼
Discover Book URLs
   │
   ▼
Extract Raw Book Data
   │
   ▼
Validate & Normalize Data
   │
   ▼
Export Structured Data
   │
   ├── JSON
   └── CSV
````

The project separates each responsibility into its own module so that each stage can be developed, tested, and maintained independently.

---

## Key Features

* Web scraping with `requests`
* HTML parsing with `BeautifulSoup`
* Local HTML caching
* Catalogue pagination
* Unique book URL discovery
* URL provenance tracking
* Structured field extraction
* Data validation with Pydantic
* Data normalization
* Flexible handling of alternative field names
* Currency parsing
* Stock availability parsing
* Rating normalization
* JSON export
* CSV export
* Modular pipeline architecture

---

## Technologies Used

| Technology     | Purpose                                               |
| -------------- | ----------------------------------------------------- |
| Python 3.11+   | Main programming language                             |
| Requests       | HTTP requests                                         |
| BeautifulSoup4 | HTML parsing                                          |
| Pydantic       | Data validation and normalization                     |
| FastAPI        | Included as a project dependency for API-related work |
| JSON           | Structured data export                                |
| CSV            | Tabular data export                                   |

The project requires Python `>=3.11`.

---

# Project Structure

```text
flyrank-ai-project-scrapper/
│
├── .env
├── .env.example
├── .gitignore
├── .python-version
├── README.md
├── pyproject.toml
├── requirements.txt
│
├── cache/
│   ├── catalogue-page-1.html
│   ├── catalogue-page-2.html
│   ├── catalogue-page-3.html
│   │
│   ├── book-1.html
│   ├── book-2.html
│   ├── book-3.html
│   ├── ...
│   └── book-60.html
│
└── src/
    │
    ├── fetcher.py
    ├── extractor.py
    ├── validator.py
    ├── exporter.py
    │
    ├── main_with_fetcher.py
    ├── main_with_extractor.py
    ├── main_with_validator.py
    └── main_with_exporter.py
```

The repository currently contains the four main processing modules and four pipeline-stage entry points under `src/`.

---

# Pipeline Architecture

The scraper is intentionally divided into separate stages.

## Stage 1 — Fetching and Caching

**File:**

```text
src/fetcher.py
```

The fetcher is responsible for retrieving webpages and managing the local cache.

Before making a network request, it checks whether the requested page already exists in the `cache/` directory.

If the page exists:

```text
CACHE HIT
```

the cached HTML is returned.

If the page does not exist, the scraper sends a request to the website, saves the response locally, and returns the downloaded HTML.

This provides two major benefits:

1. Reduces unnecessary network requests.
2. Allows previously downloaded pages to be reused during development.

---

# Stage 2 — Discovering Catalogue and Book URLs

The main pipeline starts from:

```text
https://books.toscrape.com/catalogue/page-1.html
```

The scraper identifies book links on catalogue pages and converts relative URLs into absolute URLs.

For example:

```text
../book/example_123/index.html
```

becomes a complete URL.

The pipeline also maintains:

```python
unique_urls = set()
```

to prevent duplicate book URLs.

It additionally maintains:

```python
url_to_source = {}
```

to preserve provenance.

The mapping is conceptually:

```text
book URL → catalogue page where it was discovered
```

For example:

```text
https://books.toscrape.com/catalogue/book-1/index.html
    →
https://books.toscrape.com/catalogue/page-1.html
```

This allows the final record to retain information about where the book was originally discovered.

---

# Stage 3 — Extracting Book Information

**File:**

```text
src/extractor.py
```

The extractor takes the downloaded HTML and extracts individual fields from the book page.

The extracted fields include:

```text
title
product_url
price_text
availability_text
rating_text
description
source_page
fetched_at
```

The extractor uses CSS selectors with BeautifulSoup to locate elements inside the HTML.

For example:

```python
soup.select_one("div.product_main h1")
```

is used to locate the book title.

The extractor deliberately produces **raw values**.

For example:

```text
price_text = "£20.66"
rating_text = "Four"
availability_text = "In stock (5 available)"
```

These values have not yet been converted into their final data types.

---

# Stage 4 — Validation and Normalization

**File:**

```text
src/validator.py
```

This stage converts the raw extracted dictionary into a structured Pydantic model.

The central model is:

```python
NormalizedBook
```

It defines the expected structure of a valid book record.

The normalized record contains fields such as:

```text
title
product_url
price
stock_count
rating
description
source_page
fetched_at
```

For example, raw data such as:

```text
"£20.66"
```

can become:

```text
20.66
```

Likewise:

```text
"Four"
```

can become:

```text
4
```

And:

```text
"In stock (5 available)"
```

can become:

```text
5
```

This makes the final dataset easier to analyze and use programmatically.

---

# Pydantic Validators

The validation stage uses Pydantic decorators such as:

```python
@model_validator(mode="before")
```

and:

```python
@field_validator("price", mode="before")
```

These validators allow the pipeline to clean and transform raw values before Pydantic performs its normal validation.

### Model-level validation

The model validator handles alternative field names.

For example:

```text
price_text
```

can be mapped to:

```text
price
```

Similarly:

```text
availability_text
availablity_text
stock_raw
```

can be mapped to:

```text
stock_count
```

This makes the validator more tolerant of differences in extractor output.

### Price normalization

A value such as:

```text
£20.66
```

is converted to:

```text
20.66
```

### Stock normalization

A value such as:

```text
In stock (5 available)
```

is converted to:

```text
5
```

### Rating normalization

A rating such as:

```text
Four
```

is converted to:

```text
4
```

---

# Stage 5 — Exporting Data

**File:**

```text
src/exporter.py
```

The exporter converts the validated records into persistent files.

Two output formats are supported:

### JSON

```text
books.json
```

### CSV

```text
books.csv
```

The exporter creates an `output/` directory when required.

The JSON exporter writes structured records using:

```python
json.dump()
```

The CSV exporter uses:

```python
csv.DictWriter
```

to write the records as rows and columns.

---

# Pipeline Entry Points

The project contains several `main_with_*` files.

These represent the progressive development of the pipeline.

## `main_with_fetcher.py`

Demonstrates the pipeline after adding the fetching and caching layer.

```text
Website
   ↓
Fetcher
   ↓
Cached HTML
```

---

## `main_with_extractor.py`

Adds HTML extraction.

```text
Website
   ↓
Fetcher
   ↓
HTML
   ↓
Extractor
   ↓
Raw book record
```

---

## `main_with_validator.py`

Adds Pydantic validation and normalization.

```text
Website
   ↓
Fetcher
   ↓
Extractor
   ↓
Raw record
   ↓
Validator
   ↓
Normalized record
```

The validator pipeline also prints a sample normalized record after successful validation.

---

## `main_with_exporter.py`

Represents the more complete pipeline.

```text
Website
   ↓
Fetcher + Cache
   ↓
Catalogue Discovery
   ↓
Book URL Discovery
   ↓
Extractor
   ↓
Validator / Normalizer
   ↓
JSON + CSV Export
```

The exporter-enabled pipeline calls both the JSON and CSV exporters after validation.

---

# Data Flow Example

A raw scraped record might look like:

```json
{
  "title": "A Book Title",
  "product_url": "https://books.toscrape.com/catalogue/example/index.html",
  "price_text": "£20.66",
  "availability_text": "In stock (5 available)",
  "rating_text": "Four",
  "description": "A description of the book.",
  "source_page": "https://books.toscrape.com/catalogue/page-1.html",
  "fetched_at": "2026-10-05T12:00:00Z"
}
```

After validation and normalization, it becomes:

```json
{
  "title": "A Book Title",
  "product_url": "https://books.toscrape.com/catalogue/example/index.html",
  "price": 20.66,
  "stock_count": 5,
  "rating": 4,
  "description": "A description of the book.",
  "source_page": "https://books.toscrape.com/catalogue/page-1.html",
  "fetched_at": "2026-10-05T12:00:00Z"
}
```

The important distinction is:

```text
RAW DATA
    ↓
CLEANING
    ↓
VALIDATION
    ↓
NORMALIZED DATA
```

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/Paul-Ajibola/flyrank-ai-project-scrapper.git
```

Move into the project directory:

```bash
cd flyrank-ai-project-scrapper
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

The current requirements file includes:

```text
fastapi
requests
beautifulsoup4
pydantic
```

---

# Running the Scraper

From the project root:

```bash
python src/main_with_exporter.py
```

The pipeline will:

1. Discover catalogue pages.
2. Fetch pages from the website.
3. Cache downloaded HTML.
4. Discover book URLs.
5. Fetch individual book pages.
6. Extract book information.
7. Validate and normalize records.
8. Export the records to JSON.
9. Export the records to CSV.

---

# Output

After a successful run, the exporter creates:

```text
output/
├── books.json
└── books.csv
```

The JSON file contains structured records.

The CSV file contains the same information in tabular form.

---

# Caching

Downloaded webpages are stored in:

```text
cache/
```

Examples include:

```text
cache/catalogue-page-1.html
cache/catalogue-page-2.html
cache/catalogue-page-3.html

cache/book-1.html
cache/book-2.html
cache/book-3.html
...
```

On subsequent executions, the scraper can reuse these cached pages instead of downloading them again.

This is particularly useful during development because the extraction and validation logic can be modified without repeatedly requesting the website.

---

# Provenance Tracking

An important part of this project is maintaining the relationship between a book and the catalogue page from which it was discovered.

The pipeline maintains:

```python
url_to_source
```

This is a Python dictionary.

The structure is:

```text
KEY
↓
Book URL

VALUE
↓
Catalogue page URL
```

For example:

```python
url_to_source[
    "https://books.toscrape.com/catalogue/example/index.html"
] = "https://books.toscrape.com/catalogue/page-1.html"
```

Later, the pipeline retrieves the source page using:

```python
source_page = url_to_source.get(book_url)
```

That provenance information is then included in the extracted record.

This makes the data more traceable.

---

# Error Handling

The fetcher handles network-related exceptions using `requests` exception handling.

If a network request fails, the scraper does not simply crash. Instead, it reports the error and returns a failure status.

HTTP responses are also checked for successful status codes.

The validator similarly catches validation errors and reports which product URL caused the problem.

This makes failures easier to identify during pipeline execution.

---

# Design Principles

The project follows several important software engineering principles.

## Separation of Concerns

Each component has one primary responsibility:

```text
fetcher.py
    → fetching and caching

extractor.py
    → extracting information

validator.py
    → validation and normalization

exporter.py
    → exporting data
```

This makes the code easier to understand and modify.

---

## Modularity

Individual pipeline stages can be changed without rewriting the entire application.

For example, the extraction logic can be changed while keeping the caching and validation layers intact.

---

## Data Quality

Raw web data is not assumed to be clean.

Instead, the pipeline explicitly performs:

```text
Extraction
    ↓
Normalization
    ↓
Validation
    ↓
Export
```

This helps prevent malformed or inconsistent data from reaching the final dataset.

---

## Reproducibility

The local cache allows previously downloaded HTML pages to be reused.

This makes development and debugging more reproducible because the same input HTML can be processed repeatedly.

---

# Future Improvements

Potential improvements include:

* Add automated tests
* Add retry logic for temporary network failures
* Add structured logging
* Add configurable crawl limits
* Add command-line arguments
* Add database storage
* Add Docker support
* Add scheduled scraping
* Add API endpoints for accessing scraped data
* Add automated data-quality reports
* Add monitoring and metrics
* Add concurrent fetching where appropriate
* Add stronger URL validation
* Add more robust handling of missing fields

---

# Learning Objectives

This project demonstrates practical concepts in:

* Python
* Web scraping
* HTTP requests
* HTML parsing
* CSS selectors
* File caching
* Dictionaries and sets
* Data provenance
* Data validation
* Data normalization
* Pydantic models
* Python decorators
* JSON serialization
* CSV serialization
* Modular software architecture
* Data pipeline design

---

# Project Architecture

At a high level:

```text
                 ┌──────────────────┐
                 │  Books to Scrape │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │     Fetcher      │
                 │  requests +      │
                 │     cache        │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │    Discovery     │
                 │ Catalogue + URLs │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │    Extractor     │
                 │   BeautifulSoup  │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │    Validator     │
                 │     Pydantic     │
                 │                  │
                 │ Normalize +      │
                 │ Validate         │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │     Exporter     │
                 └────────┬─────────┘
                          │
                  ┌───────┴────────┐
                  ▼                ▼
              books.json       books.csv
```

---

GitHub:

[https://github.com/Paul-Ajibola](https://github.com/Paul-Ajibola)

---

