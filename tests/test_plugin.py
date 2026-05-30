import pytest
from src.plugin import _build_fmhy_url, _CATEGORY_PAGE


@pytest.mark.parametrize("category,subcategory,expected", [
    # Confirmed by live testing
    ("Specialty Streaming", "Anime Streaming",   "https://fmhy.net/video#anime-streaming"),
    # Subcategory override: audio beats video for these
    ("Specialty Streaming", "Podcast Streaming", "https://fmhy.net/audio#podcast-streaming"),
    ("Specialty Streaming", "Concerts / Live Shows", "https://fmhy.net/audio#concerts--live-shows"),
    # Category-only (no subcategory)
    ("Torrent Clients",     "",                  "https://fmhy.net/torrenting#torrent-clients"),
    ("AI Chatbots",         "",                  "https://fmhy.net/ai#ai-chatbots"),
    ("Adblocking",          "",                  "https://fmhy.net/privacy#adblocking"),
    ("Ebooks",              "",                  "https://fmhy.net/reading#ebooks"),
    ("Discord Tools",       "",                  "https://fmhy.net/social-media-tools#discord-tools"),
    ("System Tools",        "",                  "https://fmhy.net/system-tools#system-tools"),
    ("Download Games",      "",                  "https://fmhy.net/gaming#download-games"),
    ("Image Editing",       "",                  "https://fmhy.net/image-tools#image-editing"),
    # Non-English (non-ASCII) → /non-english
    ("French / Français",   "Streaming",         "https://fmhy.net/non-english#streaming"),
    # Non-English (ASCII language name) → /non-english
    ("Polish / Polski",     "Streaming",         "https://fmhy.net/non-english#streaming"),
    ("German / Deutsch",    "",                  "https://fmhy.net/non-english#german--deutsch"),
    # Unknown category → single-page fallback
    ("Unknown Category",    "Some Sub",          "https://fmhy.net/single-page#some-sub"),
])
def test_build_fmhy_url(category, subcategory, expected):
    assert _build_fmhy_url(category, subcategory) == expected


def test_all_index_categories_have_mapping():
    """Every category in _CATEGORY_PAGE must map to a non-empty page slug."""
    for cat, page in _CATEGORY_PAGE.items():
        assert page, f"Empty page slug for category '{cat}'"
        assert "/" not in page or page == "single-page", (
            f"Page slug '{page}' for '{cat}' looks like a URL path, not a slug"
        )


def test_slug_spaces_become_hyphens():
    url = _build_fmhy_url("Torrent Clients", "Torrent Clients")
    assert " " not in url


def test_slug_slash_removed():
    url = _build_fmhy_url("Adblocking", "DNS Adblocking")
    assert "/" not in url.split("#")[1]
