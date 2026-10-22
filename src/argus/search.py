"""Optional search-provider adapter for source discovery only.

Search results are leads; they are never ingested as verified evidence.
"""
from __future__ import annotations

import json
import os
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlsplit
from .config import load_local_env


class SearchConfigurationError(RuntimeError):
    pass


class _PdfLinkParser(HTMLParser):
    """Collect PDF links from a company report landing page without caching the HTML."""

    def __init__(self, page_url: str):
        super().__init__(convert_charrefs=True)
        self.page_url = page_url
        self.links: list[dict[str, str]] = []
        self._anchor_text: list[str] = []
        self._anchor_href: str | None = None

    def handle_starttag(self, tag: str, attrs):
        attributes = dict(attrs)
        if tag.casefold() == "a":
            self._anchor_href = attributes.get("href")
            self._anchor_text = []
        for attr in ("href", "src", "data"):
            if tag.casefold() == "a" and attr == "href":
                continue
            value = attributes.get(attr)
            if value:
                self._add(value, "")

    def handle_data(self, data: str):
        if self._anchor_href:
            self._anchor_text.append(data.strip())

    def handle_endtag(self, tag: str):
        if tag.casefold() == "a" and self._anchor_href:
            self._add(self._anchor_href, " ".join(part for part in self._anchor_text if part))
            self._anchor_href = None
            self._anchor_text = []

    def _add(self, raw_url: str, title: str):
        url = urljoin(self.page_url, raw_url.strip())
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or not parsed.path.casefold().endswith(".pdf"):
            return
        if any(item["url"] == url for item in self.links):
            return
        self.links.append({"title": title or parsed.path.rsplit("/", 1)[-1], "url": url})


def is_pdf_url(url: str) -> bool:
    return urlsplit(url).path.casefold().endswith(".pdf")


def extract_pdf_links(page_html: str, page_url: str) -> list[dict[str, str]]:
    parser = _PdfLinkParser(page_url)
    parser.feed(page_html)
    return parser.links[:50]


def discover_pdf_links(page_url: str, *, timeout: int = 20, max_bytes: int = 5_000_000) -> list[dict[str, str]]:
    """Read an HTML landing page and return direct PDF links for reviewer selection."""
    if not 1 <= max_bytes <= 20_000_000:
        raise ValueError("Landing-page size limit must be between 1 byte and 20 MB.")
    parsed_url = urlsplit(page_url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValueError("Report landing page must use a public HTTP or HTTPS URL.")
    request = Request(
        page_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get_content_type()
            if content_type not in {"text/html", "application/xhtml+xml"}:
                return []
            payload = response.read(max_bytes + 1)
            if len(payload) > max_bytes:
                raise RuntimeError("The report landing page exceeded the 5 MB inspection limit.")
            html_text = payload.decode(response.headers.get_content_charset() or "utf-8", errors="replace")
            return extract_pdf_links(html_text, response.geturl())
    except HTTPError as exc:
        raise RuntimeError(f"Report landing page returned HTTP {exc.code}.") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not inspect report landing page ({exc.reason}).") from exc


def search_serper(query: str, *, limit: int = 10) -> list[dict[str, str]]:
    load_local_env()
    if not 1 <= limit <= 20:
        raise ValueError("Search result limit must be between 1 and 20.")
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        raise SearchConfigurationError(
            "Serper is not configured. Set SERPER_API_KEY in the environment, then rerun this command."
        )
    body = json.dumps({"q": query, "num": limit}).encode("utf-8")
    request = Request(
        "https://google.serper.dev/search",
        data=body,
        headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"Serper request failed with HTTP {exc.code}.") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"Serper request could not complete: {exc.reason if isinstance(exc, URLError) else exc}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Serper returned an unreadable response.") from exc

    organic = payload.get("organic", [])
    return [
        {
            "title": str(item.get("title", "")),
            "url": str(item.get("link", "")),
            "snippet": str(item.get("snippet", "")),
        }
        for item in organic[:limit]
        if isinstance(item, dict) and item.get("link")
    ]
