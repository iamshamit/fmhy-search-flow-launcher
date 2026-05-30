import html
import re
import random as _random
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict
from pathlib import Path

from src.cache import load_json, save_json, HISTORY_FILE, FAVORITES_FILE, RSS_URL, get_logger
HISTORY_LIMIT = 20


def get_random_entry(entries: List[Dict]) -> Dict:
    return _random.choice(entries)


def get_latest_entries() -> List[Dict]:
    log = get_logger()
    try:
        resp = requests.get(RSS_URL, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        ns = {"content": "http://purl.org/rss/1.0/modules/content/"}
        encoded = root.findtext(".//item/content:encoded", namespaces=ns) or ""
        content = html.unescape(encoded)
        return _parse_stars_added(content)
    except Exception as e:
        log.warning(f"Latest fetch failed: {e}")
        return []


def _parse_stars_added(html_content: str) -> List[Dict]:
    entries = []
    stars_match = re.search(
        r'Stars Added.*?(?=Things Removed|$)', html_content, re.DOTALL | re.IGNORECASE
    )
    if not stars_match:
        return entries
    section = stars_match.group(0)
    link_re = re.compile(r'<a[^>]+href="(https?://[^"]+)"[^>]*>([^<]+)</a>', re.IGNORECASE)
    for m in link_re.finditer(section):
        url, title = m.group(1), m.group(2).strip()
        if title and url:
            entries.append({
                "title": title,
                "url": url,
                "category": "Latest",
                "subcategory": "Stars Added ⭐",
                "description": "",
                "search_text": title,
            })
    return entries


def add_history(term: str):
    history = load_json(HISTORY_FILE, [])
    if term in history:
        history.remove(term)
    history.insert(0, term)
    save_json(HISTORY_FILE, history[:HISTORY_LIMIT])


def get_history() -> List[str]:
    return load_json(HISTORY_FILE, [])


def get_favorites() -> List[Dict]:
    favs = load_json(FAVORITES_FILE, {})
    return list(favs.values())


def toggle_favorite(url: str, title: str, category: str, subcategory: str, description: str):
    favs = load_json(FAVORITES_FILE, {})
    if url in favs:
        del favs[url]
    else:
        favs[url] = {"title": title, "url": url, "category": category,
                     "subcategory": subcategory, "description": description, "search_text": title}
    save_json(FAVORITES_FILE, favs)


def is_favorite(url: str) -> bool:
    favs = load_json(FAVORITES_FILE, {})
    return url in favs
