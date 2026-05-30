import threading
import requests
from urllib.parse import urlparse
from pathlib import Path

from src.cache import FAVICON_DIR, get_logger

PLUGIN_ICON = "icons\\fmhy.png"
GOOGLE_FAVICON = "https://www.google.com/s2/favicons?domain={domain}&sz=32"

_in_flight: set = set()
_in_flight_lock = threading.Lock()


def get_favicon_path(url: str) -> str:
    domain = _domain(url)
    if not domain:
        return PLUGIN_ICON

    favicon_path = FAVICON_DIR / f"{domain}.png"
    if favicon_path.exists() and favicon_path.stat().st_size > 0:
        return str(favicon_path)

    with _in_flight_lock:
        if domain in _in_flight:
            return PLUGIN_ICON
        _in_flight.add(domain)

    threading.Thread(target=_fetch, args=(domain, favicon_path), daemon=True).start()
    return PLUGIN_ICON


def _domain(url: str) -> str:
    try:
        netloc = urlparse(url).netloc
        return netloc.replace("www.", "") if netloc else ""
    except Exception:
        return ""


def _fetch(domain: str, dest: Path):
    try:
        favicon_url = GOOGLE_FAVICON.format(domain=domain)
        resp = requests.get(favicon_url, timeout=5)
        resp.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(resp.content)
    except Exception as e:
        get_logger().debug(f"Favicon fetch failed for {domain}: {e}")
    finally:
        with _in_flight_lock:
            _in_flight.discard(domain)
