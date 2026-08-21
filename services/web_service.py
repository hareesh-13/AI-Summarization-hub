"""
services/web_service.py
Extract and clean text content from web pages using a multi-strategy pipeline:
  1. trafilatura  – best-in-class boilerplate removal (most websites)
  2. newspaper3k  – good for news/article sites
  3. BeautifulSoup fallback – raw paragraph extraction
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Tags to strip — navigation, ads, scripts, etc.
NOISE_TAGS = [
    "script", "style", "nav", "header", "footer",
    "aside", "form", "iframe", "noscript", "button",
    "input", "select", "textarea",
]

MIN_CONTENT_LENGTH = 100  # minimum chars to be considered usable content


def _fetch_raw(url: str) -> tuple[str, str]:
    """Fetch URL and return (html_text, final_url). Raises ValueError on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return resp.text, resp.url
    except requests.exceptions.ConnectionError:
        raise ValueError(
            f"❌ Could not connect to **{url}**.\n\n"
            "Check the URL and your internet connection."
        )
    except requests.exceptions.Timeout:
        raise ValueError(
            f"⏳ Request timed out for **{url}**. The site may be slow — try again."
        )
    except requests.exceptions.HTTPError as exc:
        raise ValueError(
            f"❌ HTTP {exc.response.status_code} error from **{url}**."
        )
    except Exception as exc:
        raise ValueError(f"❌ Failed to fetch page: {exc}")


def _extract_with_trafilatura(html: str, url: str) -> str | None:
    """Try trafilatura extraction. Returns text or None if insufficient."""
    try:
        import trafilatura
        text = trafilatura.extract(
            html,
            url=url,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            favor_precision=False,
            favor_recall=True,
        )
        if text and len(text.strip()) >= MIN_CONTENT_LENGTH:
            return text.strip()
    except Exception:
        pass
    return None


def _extract_with_newspaper(url: str) -> str | None:
    """Try newspaper3k extraction. Returns text or None if insufficient."""
    try:
        from newspaper import Article
        article = Article(url)
        article.download()
        article.parse()
        text = article.text.strip()
        if text and len(text) >= MIN_CONTENT_LENGTH:
            return text
    except Exception:
        pass
    return None


def _extract_with_bs4(html: str) -> str:
    """BeautifulSoup fallback: aggressive extraction across many tag types."""
    soup = BeautifulSoup(html, "lxml")

    # Remove noise tags
    for tag in NOISE_TAGS:
        for element in soup.find_all(tag):
            element.decompose()

    # Try article/main/body in order
    container = soup.find("article") or soup.find("main") or soup.find("body")
    if container:
        # Cast a wide net over content tags
        tags = container.find_all(
            ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "th", "blockquote", "pre", "span", "div"]
        )
        lines = []
        seen = set()
        for t in tags:
            # Only include leaf-ish nodes (skip divs that contain other block elements)
            if t.name in ("div", "span") and t.find(["p", "h1", "h2", "h3", "li"]):
                continue
            line = t.get_text(separator=" ", strip=True)
            if line and len(line) > 20 and line not in seen:
                seen.add(line)
                lines.append(line)
        text = "\n".join(lines)
    else:
        text = soup.get_text(separator="\n", strip=True)

    # Deduplicate and clean up short lines
    cleaned = [ln.strip() for ln in text.splitlines() if len(ln.strip()) > 20]
    return "\n".join(dict.fromkeys(cleaned))  # preserve order, remove duplicates


def _get_title(html: str, url: str) -> str:
    """Extract page title from HTML."""
    try:
        soup = BeautifulSoup(html, "lxml")
        # Try og:title first (more descriptive)
        og = soup.find("meta", property="og:title")
        if og and og.get("content"):
            return og["content"].strip()
        tag = soup.find("title")
        if tag:
            return tag.get_text(strip=True)
    except Exception:
        pass
    return url


def scrape_url(url: str) -> dict:
    """
    Fetches a webpage and returns cleaned text using a 3-strategy pipeline.

    Returns:
        {
            "url": str,
            "title": str,
            "text": str,
            "word_count": int,
            "char_count": int,
            "strategy_used": str,
        }
    Raises:
        ValueError: If the page cannot be fetched or contains no readable content.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    html, final_url = _fetch_raw(url)
    title = _get_title(html, final_url)

    # --- Strategy 1: trafilatura (best for most content sites) ---
    text = _extract_with_trafilatura(html, final_url)
    strategy_used = "trafilatura"

    # --- Strategy 2: newspaper3k (great for news/article sites) ---
    if not text:
        text = _extract_with_newspaper(final_url)
        strategy_used = "newspaper3k"

    # --- Strategy 3: BeautifulSoup fallback ---
    if not text:
        text = _extract_with_bs4(html)
        strategy_used = "beautifulsoup"

    if not text or len(text) < MIN_CONTENT_LENGTH:
        raise ValueError(
            "⚠️ **Very little readable content was found on this page.**\n\n"
            "**Possible reasons:**\n"
            "- The site requires JavaScript to render (e.g. React/Next.js SPAs)\n"
            "- The content is behind a login or paywall\n"
            "- The URL points to a PDF, image, or non-HTML resource\n\n"
            "**Suggestions:**\n"
            "- Try copying the page text manually into the **Text/Document** tab\n"
            "- Look for a 'reader mode' or 'print' version of the page (e.g. `?print=1`)\n"
            "- Try a cached version: `https://webcache.googleusercontent.com/search?q=cache:YOUR_URL`"
        )

    return {
        "url": final_url,
        "title": title,
        "text": text,
        "word_count": len(text.split()),
        "char_count": len(text),
        "strategy_used": strategy_used,
    }
