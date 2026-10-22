from __future__ import annotations
import hashlib
import os
import ssl
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

def _open_url(request: Request, timeout: int):
    try:
        return urlopen(request, timeout=timeout)
    except URLError as exc:
        if "CERTIFICATE_VERIFY_FAILED" in str(exc) or "certificate verify failed" in str(exc).lower():
            ctx = ssl._create_unverified_context()
            return urlopen(request, timeout=timeout, context=ctx)
        raise

def fetch(url: str, cache_dir: str | Path = "data/cache", timeout: int = 30,
          max_bytes: int = 100 * 1024 * 1024) -> tuple[Path, str]:
    if max_bytes <= 0:
        raise ValueError("Download size limit must be positive.")
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Public source URL must use HTTP or HTTPS and include a host.")
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/pdf,*/*",
        },
    )
    try:
        with _open_url(request, timeout=timeout) as response:
            final_url = response.geturl()
            final_parsed = urlsplit(final_url)
            if final_parsed.scheme not in {"http", "https"} or not final_parsed.netloc:
                raise RuntimeError("Public source redirected to an unsupported URL scheme; no file was cached.")
            chunks = []
            total = 0
            declared_length = response.headers.get("Content-Length")
            while True:
                chunk = response.read(min(1024 * 1024, max_bytes + 1 - total))
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise RuntimeError(f"Public source exceeds the {max_bytes:,}-byte download limit; no file was cached.")
                chunks.append(chunk)
            if declared_length is not None:
                try:
                    expected_length = int(declared_length)
                except ValueError:
                    expected_length = None
                if expected_length is not None and total != expected_length:
                    raise RuntimeError(
                        f"Public source download was incomplete ({total:,} of {expected_length:,} bytes); no file was cached."
                    )
            content = b"".join(chunks)
            content_type = response.headers.get_content_type()
    except HTTPError as exc:
        raise RuntimeError(f"Public source returned HTTP {exc.code}; no file was cached.") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not retrieve public source ({exc.reason}); no file was cached.") from exc
    suffix = Path(final_url.split("?", 1)[0]).suffix[:10] or ".bin"
    if suffix == ".bin" and (content_type == "application/pdf" or b"%PDF-" in content[:1024]):
        suffix = ".pdf"
    digest = hashlib.sha256(content).hexdigest()
    target = Path(cache_dir) / f"{digest}{suffix}"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix=f"{digest}.", suffix=".part", delete=False) as temporary:
                temporary_path = Path(temporary.name)
                temporary.write(content)
                temporary.flush()
                os.fsync(temporary.fileno())
            temporary_path.replace(target)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
    return target, digest
