import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json
import sys
from playwright.sync_api import sync_playwright


HEADERS = {
    "User-Agent": "Mozilla/5.0 (BrochureGPT/1.0)"
}

MAX_CHARS_PER_PAGE = 2000
MAX_PAGES = 15



def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"


def same_domain(a: str, b: str) -> bool:
    return urlparse(a).netloc == urlparse(b).netloc



def fetch_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text


def fetch_html_js(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        html = page.content()
        browser.close()
        return html


def needs_js(html: str) -> bool:
    soup = BeautifulSoup(html, "html.parser")
    body_text = soup.body.get_text(strip=True) if soup.body else ""
    return len(body_text) < 150


def extract_text(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "img", "input", "svg", "iframe"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title else ""

    body_text = ""
    if soup.body:
        body_text = soup.body.get_text(separator="\n", strip=True)

    return {
        "title": title,
        "text": clean_text(body_text)[:MAX_CHARS_PER_PAGE]
    }


def extract_links(html: str, base_url: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#") or href.startswith("javascript:"):
            continue
        abs_url = normalize_url(urljoin(base_url, href))
        links.append(abs_url)

    return links


def scrape_site(start_url: str) -> dict:
    visited = set()
    to_visit = [normalize_url(start_url)]
    pages = []

    while to_visit and len(pages) < MAX_PAGES:
        url = to_visit.pop(0)
        if url in visited:
            continue

        visited.add(url)

        try:
            html = fetch_html(url)

            if needs_js(html):
                try:
                    html = fetch_html_js(url)
                except Exception:
                    pass

            content = extract_text(html)
            content["url"] = url
            pages.append(content)

            links = extract_links(html, url)
            for link in links:
                if (
                    same_domain(start_url, link)
                    and link not in visited
                    and link not in to_visit
                ):
                    to_visit.append(link)

        except Exception as e:
            pages.append({"url": url, "error": str(e)})

    return {
        "start_url": start_url,
        "pages_scraped": len(pages),
        "pages": pages
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    result = scrape_site(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
