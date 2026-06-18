import re
import sys
import subprocess
import webbrowser
from pathlib import Path

_plugin_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_plugin_root / "lib"))

from flowlauncher import FlowLauncher
from flowlauncher import FlowLauncherAPI

from src.cache import load_json, INDEX_FILE, get_logger
from src.search import search, keyword_search, parse_cat_query, _is_non_english
from src.updater import build_index, should_check_rss, check_and_update_background
from src.commands import (
    get_random_entry, get_latest_entries,
    get_history, add_history,
    get_favorites, toggle_favorite, is_favorite,
)
from src.favicon import get_favicon_path

ICON = "icons\\fmhy.png"

# Maps FMHY index category names → fmhy.net page slug
_CATEGORY_PAGE = {
    # Privacy & Security
    "Adblocking": "privacy", "Antivirus / Anti-Malware": "privacy",
    "Privacy / Security": "privacy", "Web Privacy": "privacy",
    "VPN": "privacy", "Proxy": "privacy",
    "Cybersecurity Tools": "privacy", "Open Source Intelligence": "privacy",
    # AI
    "AI Chatbots": "ai", "AI Writing Tools": "ai", "Video Generation": "ai",
    "Image Generation": "ai", "Audio Generation": "ai", "AI Tools": "ai",
    "AI Indexes": "ai", "AI Benchmarks": "ai", "Machine Learning": "ai",
    # Mobile / Android / iOS
    "Android APKs": "mobile", "Android Device": "mobile", "Android Camera": "mobile",
    "Android Tools": "mobile", "Android Torrenting": "mobile", "Android Reading": "mobile",
    "Android Audio": "mobile", "Android Streaming": "mobile", "Emulators": "mobile",
    "iOS Tools": "mobile", "iOS iPAs": "mobile", "iOS Audio": "mobile",
    "iOS Streaming": "mobile", "iOS Reading": "mobile",
    # Audio
    "Audio Streaming": "audio", "Radio Streaming": "audio", "Spotify Tools": "audio",
    "Audio Ripping": "audio", "Audio Torrenting": "audio", "Royalty Free Music": "audio",
    "Media Soundtracks": "audio", "Audio Tools": "audio", "Audio Editing": "audio",
    "Genre specific": "audio",
    # Developer Tools
    "Dev Communities": "developer-tools", "Dev News": "developer-tools",
    "Developer Tools": "developer-tools", "Game Dev Tools": "developer-tools",
    "IDEs / Code Editors": "developer-tools", "Programming Languages": "developer-tools",
    "Web Development": "developer-tools", "Web Dev Tools": "developer-tools",
    "Hosting Tools": "developer-tools",
    # Downloading
    "Download Directories": "downloading", "Download Sites": "downloading",
    "Software Sites": "downloading", "Usenet": "downloading", "Debrid / Leeches": "downloading",
    # Educational
    "Documentaries": "educational", "Courses": "educational", "Learning Sites": "educational",
    "Science / Math": "educational", "Space": "educational", "History": "educational",
    "Humanities": "educational", "Skills / Hobbies / DIY": "educational",
    "Language Learning": "educational", "Developer Learning": "educational",
    "Exam Prep": "educational", "Educational Tools": "educational", "Coding Tutorials": "educational",
    # File Tools
    "File Tools": "file-tools", "PDF Tools": "file-tools",
    "File Transfer": "file-tools", "File Hosts": "file-tools",
    # Gaming
    "Gaming Tools": "gaming", "Steam / Epic": "gaming", "Multiplayer Tools": "gaming",
    "Homebrew": "gaming", "Minecraft Tools": "gaming", "Game Specific": "gaming",
    "Download Games": "gaming", "Emulation / ROMs": "gaming", "Special Interest": "gaming",
    "Puzzle Games": "gaming", "Tabletop Games": "gaming", "Browser Games": "gaming",
    # Image Tools
    "Image Editing": "image-tools", "Image Creation": "image-tools",
    "Design Resources / Ideas": "image-tools", "Download Images": "image-tools",
    "3D Models": "image-tools", "Image Tools": "image-tools", "Photography / Cameras": "image-tools",
    # Internet Tools
    "Internet Tools": "internet-tools", "RSS Tools": "internet-tools",
    "Search Tools": "internet-tools", "URL Tools": "internet-tools",
    "Email Tools": "internet-tools", "Browser Bookmarks": "internet-tools",
    "Browser Startpages": "internet-tools", "Browser Tools": "internet-tools",
    "Archiving": "internet-tools",
    # Linux / macOS
    "Linux Guides": "linux-macos", "Linux Communities": "linux-macos",
    "Linux Distros": "linux-macos", "Linux Apps": "linux-macos", "Linux Tools": "linux-macos",
    "Mac Apps": "linux-macos", "Mac Tools": "linux-macos", "Unix-Like": "linux-macos",
    # Misc
    "Indexes": "misc", "Free Stuff": "misc", "Food": "misc", "Fashion / Clothing": "misc",
    "Household": "misc", "Gardening": "misc", "Vehicle": "misc", "Sports": "misc",
    "Travel": "misc", "Maps": "misc", "News": "misc", "Health": "misc",
    "Career": "misc", "Shopping": "misc", "Useful Sites": "misc", "Fun Sites": "misc",
    "Helpful Sites / Apps": "misc", "Helpful Sites / Tools": "misc",
    # Reading
    "Ebooks": "reading", "Audiobooks": "reading", "Visual Media": "reading",
    "Educational Books": "reading", "Documents / Articles": "reading",
    "Esoteric / Cultural": "reading", "Tracking / Database": "reading",
    # Social Media
    "Social Media Tools": "social-media-tools", "Discord Tools": "social-media-tools",
    "Reddit Tools": "social-media-tools", "Telegram Tools": "social-media-tools",
    "YouTube Tools": "social-media-tools", "Bilibili Tools": "social-media-tools",
    "Twitch Tools": "social-media-tools", "Twitter/X Tools": "social-media-tools",
    "Facebook Tools": "social-media-tools", "Instagram Tools": "social-media-tools",
    "Blogging Tools": "social-media-tools", "Tumblr Tools": "social-media-tools",
    "Fediverse Tools": "social-media-tools", "4chan Tools": "social-media-tools",
    # System Tools
    "System Tools": "system-tools", "Hardware Tools": "system-tools",
    "Windows ISOs": "system-tools", "Customization": "system-tools",
    # Text Tools
    "Text Tools": "text-tools", "Text Editors": "text-tools",
    "Markup Tools": "text-tools", "Fonts": "text-tools", "Font Tools": "text-tools",
    # Torrenting
    "Torrent Sites": "torrenting", "Torrent Clients": "torrenting",
    "Private Trackers": "torrenting", "Torrent Apps": "torrenting",
    # Video Tools
    "Video Tools": "video-tools", "Video Players": "video-tools",
    "Media Servers": "video-tools", "Video Download": "video-tools", "Video Editing": "video-tools",
    # Video / Streaming
    "Streaming Sites": "video", "Specialty Streaming": "video",
    "Live TV / Sports": "video", "Smart TV": "video",
    "Subtitle Tools": "video", "Tracking / Databases": "video",
}

# Subcategory overrides for ambiguous categories (e.g. "Specialty Streaming" in both audio and video)
_SUBCATEGORY_PAGE = {
    "Concerts / Live Shows": "audio", "Podcast Streaming": "audio",
    "Ambient / Relaxation": "audio", "Genre Specific Streaming": "audio",
    "YouTube Music Tools": "audio",
}


def _build_fmhy_url(category: str, subcategory: str) -> str:
    if _is_non_english({"category": category}):
        page = "non-english"
    elif subcategory in _SUBCATEGORY_PAGE:
        page = _SUBCATEGORY_PAGE[subcategory]
    else:
        page = _CATEGORY_PAGE.get(category, "single-page")
    heading = subcategory if subcategory else category
    slug = heading.lower()
    slug = re.sub(r'\s', '-', slug)     # each space → hyphen (VitePress style)
    slug = re.sub(r'[^\w-]', '', slug)  # remove non-word, non-hyphen chars
    slug = slug.strip('-')
    return f"https://fmhy.net/{page}#{slug}"


def _build_cat_results(partial: str, entries: list, icon: str) -> list:
    seen = set()
    cats = []
    for e in entries:
        for name in (e["category"], e.get("subcategory", "")):
            if name and name not in seen:
                if not partial or partial.lower() in name.lower():
                    seen.add(name)
                    cats.append(name)
    cats.sort()
    if not cats:
        return [{"Title": f"No categories matching '{partial}'",
                 "SubTitle": "Try a different term",
                 "IcoPath": icon}]
    return [
        {
            "Title": name,
            "SubTitle": f"Press Enter to search within {name}",
            "IcoPath": icon,
            "JsonRPCAction": {"method": "select_category", "parameters": [name]},
        }
        for name in cats[:20]
    ]


class FMHYSearch(FlowLauncher):

    def query(self, query: str) -> list:
        query = query.strip()

        if query == "update":
            return self._cmd_update()
        if query == "random":
            return self._cmd_random()
        if query == "latest":
            return self._cmd_latest()
        if query == "history":
            return self._cmd_history()
        if query in ("fav", "favorites"):
            return self._cmd_favorites()

        entries = self._load_entries()
        if entries is None:
            return self._no_index_result()

        if should_check_rss():
            check_and_update_background(
                lambda msg: FlowLauncherAPI.show_msg("FMHY Search", msg, ICON)
            )

        cat_filter, search_query, fuzzy = parse_cat_query(query)

        if not search_query:
            if query.startswith("cat:") and " " not in query[4:]:
                return self._cmd_cat_picker(query[4:].rstrip("?"), entries)
            pool = entries
            if cat_filter:
                cat_lower = cat_filter.lower()
                pool = [
                    e for e in entries
                    if cat_lower in e["category"].lower()
                    or cat_lower in e["subcategory"].lower()
                ]
            return [self._make_result(e) for e in pool[:20]]

        if fuzzy:
            results = search(search_query, entries, category_filter=cat_filter)
        else:
            results = keyword_search(search_query, entries, category_filter=cat_filter)
        if results:
            add_history(query)

        if not results:
            if fuzzy:
                return [{"Title": f"No results for '{search_query}'",
                         "SubTitle": "Try different keywords or run 'fmhy update'",
                         "IcoPath": ICON}]
            return [{
                "Title": f"No results for '{search_query}' — press Enter to try fuzzy search",
                "SubTitle": "Searches with typo tolerance",
                "IcoPath": ICON,
                "JsonRPCAction": {"method": "fuzzy_rewrite", "parameters": [query]},
            }]
        return [self._make_result(e) for e in results]

    def context_menu(self, data: list) -> list:
        url, title, category, description, subcategory = data
        fav_label = "Remove from Favorites" if is_favorite(url) else "Add to Favorites"
        fmhy_url = self._fmhy_section_url(category, subcategory)
        return [
            {
                "Title": "Copy URL",
                "SubTitle": url,
                "IcoPath": ICON,
                "JsonRPCAction": {"method": "copy_to_clipboard", "parameters": [url]},
            },
            {
                "Title": fav_label,
                "SubTitle": f"Toggle favorite for '{title}'",
                "IcoPath": ICON,
                "JsonRPCAction": {
                    "method": "toggle_fav",
                    "parameters": [url, title, category, subcategory, description],
                },
            },
            {
                "Title": "View section on FMHY.net",
                "SubTitle": fmhy_url,
                "IcoPath": ICON,
                "JsonRPCAction": {"method": "open_url", "parameters": [fmhy_url]},
            },
        ]

    def open_url(self, url: str):
        webbrowser.open(url)

    def copy_to_clipboard(self, text: str):
        try:
            subprocess.run(["clip"], input=text.encode("utf-16-le"), check=False)
        except Exception as e:
            get_logger().warning(f"Clipboard copy failed: {e}")

    def toggle_fav(self, url: str, title: str, category: str, subcategory: str, description: str):
        toggle_favorite(url, title, category, subcategory, description)

    def trigger_build(self):
        success, msg = build_index()
        FlowLauncherAPI.show_msg("FMHY Search", msg, ICON)

    def _make_result(self, entry: dict) -> dict:
        subtitle = entry["category"]
        if entry.get("subcategory"):
            subtitle += f" › {entry['subcategory']}"
        desc = entry.get("description", "")
        if len(desc) > 80:
            desc = desc[:77] + "..."
        if desc:
            subtitle += f" — {desc}"
        return {
            "Title": entry["title"],
            "SubTitle": subtitle,
            "IcoPath": get_favicon_path(entry["url"]),
            "ContextData": [
                entry["url"], entry["title"],
                entry["category"], entry.get("description", ""),
                entry.get("subcategory", ""),
            ],
            "JsonRPCAction": {"method": "open_url", "parameters": [entry["url"]]},
        }

    def _fmhy_section_url(self, category: str, subcategory: str) -> str:
        return _build_fmhy_url(category, subcategory)

    def _load_entries(self):
        if not INDEX_FILE.exists():
            return None
        entries = load_json(INDEX_FILE, None)
        if not entries:
            INDEX_FILE.unlink(missing_ok=True)
            return None
        return entries

    def _no_index_result(self):
        return [{
            "Title": "Index not built — press Enter to download and build",
            "SubTitle": "Fetches the FMHY database (~2 MB) from api.fmhy.net",
            "IcoPath": ICON,
            "JsonRPCAction": {"method": "trigger_build", "parameters": []},
        }]

    def _cmd_update(self):
        return [{
            "Title": "Update FMHY Index",
            "SubTitle": "Press Enter to fetch latest FMHY data and rebuild the index",
            "IcoPath": ICON,
            "JsonRPCAction": {"method": "trigger_build", "parameters": []},
        }]

    def _cmd_random(self):
        entries = self._load_entries()
        if not entries:
            return self._no_index_result()
        entry = get_random_entry(entries)
        return [self._make_result(entry)]

    def _cmd_latest(self):
        entries = get_latest_entries()
        if not entries:
            return [{"Title": "Could not fetch latest entries",
                     "SubTitle": "Check your internet connection",
                     "IcoPath": ICON}]
        return [self._make_result(e) for e in entries]

    def _cmd_history(self):
        history = get_history()
        if not history:
            return [{"Title": "No search history yet",
                     "SubTitle": "Your recent searches will appear here",
                     "IcoPath": ICON}]
        return [
            {"Title": term, "SubTitle": "Press Enter to search again",
             "IcoPath": ICON,
             "JsonRPCAction": {"method": "rerun_history", "parameters": [term]}}
            for term in history
        ]

    def rerun_history(self, term: str):
        FlowLauncherAPI.change_query(term, requery=True)

    def fuzzy_rewrite(self, raw_query: str):
        FlowLauncherAPI.change_query(raw_query.rstrip("?") + "?", requery=True)

    def select_category(self, name: str):
        FlowLauncherAPI.change_query(f"cat:{name} ", requery=True)

    def _cmd_favorites(self):
        favs = get_favorites()
        if not favs:
            return [{"Title": "No favorites yet",
                     "SubTitle": "Open context menu on any result to add a favorite",
                     "IcoPath": ICON}]
        return [self._make_result(e) for e in favs]

    def _cmd_cat_picker(self, partial: str, entries: list) -> list:
        return _build_cat_results(partial, entries, ICON)
