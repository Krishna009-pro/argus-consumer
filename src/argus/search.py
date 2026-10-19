"""Optional search-provider adapter for source discovery only.

Search results are leads; they are never ingested as verified evidence.
"""
from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from .config import load_local_env


class SearchConfigurationError(RuntimeError):
    pass


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
