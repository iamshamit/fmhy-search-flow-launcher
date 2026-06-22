import sys
import socket
import threading
import warnings
import requests
import urllib3
import xml.etree.ElementTree as ET
from datetime import date
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Optional, Tuple, Callable

from src.cache import load_json, save_json, INDEX_FILE, META_FILE, RSS_URL, get_logger
from src.indexer import parse_markdown

SINGLE_PAGE_URL = "https://api.fmhy.net/single-page"
SINGLE_PAGE_URL_HTTP = "http://api.fmhy.net/single-page"

# Suppress urllib3 warnings that leak to stderr and crash Flow Launcher's JSON-RPC parser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Keep module-level references so monkeypatching updater.INDEX_FILE /
# updater.META_FILE works in tests. Functions must read these via the
# module object, not the names bound at import time.
_mod = sys.modules[__name__]


def fetch_rss_month_year() -> Optional[Tuple[int, int]]:
    try:
        resp = requests.get(RSS_URL, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        pub_date = root.findtext(".//item/pubDate")
        if pub_date:
            dt = parsedate_to_datetime(pub_date)
            return (dt.month, dt.year)
    except Exception as e:
        get_logger().warning(f"RSS fetch failed: {e}")
    return None


def should_check_rss() -> bool:
    today = date.today()
    if today.day != 1:
        return False
    meta = load_json(_mod.META_FILE, {})
    return meta.get("last_rss_check_date") != today.isoformat()


def _try_urllib(url: str, timeout: int = 30) -> Optional[str]:
    import urllib.request
    try:
        resp = urllib.request.urlopen(url, timeout=timeout)
        return resp.read().decode("utf-8")
    except Exception:
        return None


def _try_fetch(url: str, timeout: int = 30, verify: bool = True) -> Optional[str]:
    try:
        resp = requests.get(url, timeout=timeout, verify=verify)
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.SSLError:
        return None
    except requests.exceptions.RequestException:
        return None


_BLOCK_KEYWORDS = [
    "block.charter-prod.hosted.cujo.io",
    "blocked", "blockpage", "content not available",
    "this site has been blocked",
]


def _is_block_page(text: str) -> Optional[str]:
    lower = text.lower()
    for kw in _BLOCK_KEYWORDS:
        if kw in lower:
            return kw
    return None


def build_index() -> Tuple[bool, str]:
    log = get_logger()
    try:
        log.info("Fetching FMHY single-page API")
        text = _try_fetch(SINGLE_PAGE_URL, verify=True)
        if text is None:
            log.info("HTTPS failed, retrying without SSL verification")
            text = _try_fetch(SINGLE_PAGE_URL, verify=False)
        if text is None:
            log.info("HTTPS unavailable, retrying via plain HTTP")
            text = _try_fetch(SINGLE_PAGE_URL_HTTP, timeout=30, verify=False)
        if text is None:
            log.info("All requests methods failed, trying urllib as fallback")
            text = _try_urllib(SINGLE_PAGE_URL, timeout=30)
        if text is not None:
            blocked = _is_block_page(text)
            if blocked:
                log.info(f"Request was blocked (detected: {blocked})")
                return False, f"Update blocked by your ISP or firewall — {SINGLE_PAGE_URL} is not accessible on this network"
        if text is None:
            log.info("All fetch attempts failed — api.fmhy.net unreachable")
            try:
                ip = socket.gethostbyname("api.fmhy.net")
                log.info(f"api.fmhy.net resolves to {ip}")
            except Exception as e:
                log.info(f"DNS resolution failed: {e}")
            return False, "Update failed: could not reach api.fmhy.net — try disabling your VPN, antivirus, or proxy"
        entries = parse_markdown(text)
        if not entries:
            return False, "Parsed 0 entries — index not updated"
        save_json(_mod.INDEX_FILE, entries)

        rss_result = fetch_rss_month_year()
        meta = load_json(_mod.META_FILE, {})
        meta["last_rss_check_date"] = date.today().isoformat()
        if rss_result:
            meta["month"], meta["year"] = rss_result
        save_json(_mod.META_FILE, meta)

        log.info(f"Index built: {len(entries)} entries")
        return True, f"Index updated: {len(entries)} entries"
    except Exception as e:
        log.error(f"Build index failed: {e}")
        return False, f"Update failed: {e}"


def check_and_update_background(notify_fn: Callable[[str], None]):
    def _run():
        meta = load_json(_mod.META_FILE, {})
        meta["last_rss_check_date"] = date.today().isoformat()
        save_json(_mod.META_FILE, meta)

        rss_result = fetch_rss_month_year()
        if rss_result is None:
            return
        month, year = rss_result
        if meta.get("month") != month or meta.get("year") != year:
            success, msg = build_index()
            notify_fn(msg)

    threading.Thread(target=_run, daemon=True).start()
