import pytest
from pathlib import Path

SAMPLE_MARKDOWN = """
# ► Torrenting

## ▷ Torrent Clients

* [qBittorrent](https://www.qbittorrent.org/) - Open-source BitTorrent client
* [Deluge](https://deluge-torrent.org/) - Lightweight cross-platform client

## ▷ Torrent Sites

* [1337x](https://1337x.to/) - General torrent site

# ► Streaming

* ⭐ **[Stremio](https://www.stremio.com/)** - Media center app
* [Plex](https://www.plex.tv/) - Personal media server

# ► AI Tools

## ▷ Coding

* [GitHub Copilot](https://github.com/features/copilot) - AI pair programmer

# ► Anime / French / Français

* [KiboanimeVF](https://www.kiboanime.org/) - French anime streaming
"""

SAMPLE_ENTRIES = [
    {
        "title": "qBittorrent",
        "url": "https://www.qbittorrent.org/",
        "category": "Torrenting",
        "subcategory": "Torrent Clients",
        "description": "Open-source BitTorrent client",
        "search_text": "qBittorrent Torrenting Torrent Clients Open-source BitTorrent client",
        "starred": False,
    },
    {
        "title": "Stremio",
        "url": "https://www.stremio.com/",
        "category": "Streaming",
        "subcategory": "",
        "description": "Media center app",
        "search_text": "Stremio Streaming  Media center app",
        "starred": True,
    },
    {
        "title": "GitHub Copilot",
        "url": "https://github.com/features/copilot",
        "category": "AI Tools",
        "subcategory": "Coding",
        "description": "AI pair programmer",
        "search_text": "GitHub Copilot AI Tools Coding AI pair programmer",
        "starred": False,
    },
    {
        "title": "KiboanimeVF",
        "url": "https://www.kiboanime.org/",
        "category": "Anime / French / Français",
        "subcategory": "",
        "description": "French anime streaming",
        "search_text": "KiboanimeVF Anime / French / Français  French anime streaming",
        "starred": False,
    },
]
