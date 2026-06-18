import pytest
from tests.conftest import SAMPLE_MARKDOWN


def test_parse_entry_count():
    from src.indexer import parse_markdown
    entries = parse_markdown(SAMPLE_MARKDOWN)
    assert len(entries) == 7


def test_parse_category_and_subcategory():
    from src.indexer import parse_markdown
    entries = parse_markdown(SAMPLE_MARKDOWN)
    qbt = next(e for e in entries if e["title"] == "qBittorrent")
    assert qbt["category"] == "Torrenting"
    assert qbt["subcategory"] == "Torrent Clients"


def test_parse_title_and_url():
    from src.indexer import parse_markdown
    entries = parse_markdown(SAMPLE_MARKDOWN)
    qbt = next(e for e in entries if e["title"] == "qBittorrent")
    assert qbt["url"] == "https://www.qbittorrent.org/"


def test_parse_description():
    from src.indexer import parse_markdown
    entries = parse_markdown(SAMPLE_MARKDOWN)
    qbt = next(e for e in entries if e["title"] == "qBittorrent")
    assert "Open-source" in qbt["description"]


def test_search_text_contains_all_fields():
    from src.indexer import parse_markdown
    entries = parse_markdown(SAMPLE_MARKDOWN)
    qbt = next(e for e in entries if e["title"] == "qBittorrent")
    assert "qBittorrent" in qbt["search_text"]
    assert "Torrenting" in qbt["search_text"]
    assert "Torrent Clients" in qbt["search_text"]


def test_category_resets_on_new_main_heading():
    from src.indexer import parse_markdown
    entries = parse_markdown(SAMPLE_MARKDOWN)
    stremio = next(e for e in entries if e["title"] == "Stremio")
    assert stremio["category"] == "Streaming"
    assert stremio["subcategory"] == ""


def test_subcategory_resets_on_new_main_heading():
    from src.indexer import parse_markdown
    entries = parse_markdown(SAMPLE_MARKDOWN)
    copilot = next(e for e in entries if e["title"] == "GitHub Copilot")
    assert copilot["category"] == "AI Tools"
    assert copilot["subcategory"] == "Coding"


def test_skip_non_http_urls():
    from src.indexer import parse_markdown
    md = "# ► Test\n* [Bad](ftp://example.com/) - Skipped\n* [Good](https://good.com/) - Kept"
    entries = parse_markdown(md)
    assert len(entries) == 1
    assert entries[0]["title"] == "Good"


def test_empty_markdown_returns_empty_list():
    from src.indexer import parse_markdown
    assert parse_markdown("") == []


def test_description_is_empty_string_when_missing():
    from src.indexer import parse_markdown
    md = "# ► Test\n* [Tool](https://tool.com/)"
    entries = parse_markdown(md)
    assert entries[0]["description"] == ""


def test_parse_starred_entry():
    from src.indexer import parse_markdown
    entries = parse_markdown(SAMPLE_MARKDOWN)
    stremio = next(e for e in entries if e["title"] == "Stremio")
    assert stremio["starred"] is True


def test_parse_unstarred_entry_has_starred_false():
    from src.indexer import parse_markdown
    entries = parse_markdown(SAMPLE_MARKDOWN)
    qbt = next(e for e in entries if e["title"] == "qBittorrent")
    assert qbt["starred"] is False


def test_starred_entry_title_and_url():
    from src.indexer import parse_markdown
    entries = parse_markdown(SAMPLE_MARKDOWN)
    stremio = next(e for e in entries if e["title"] == "Stremio")
    assert stremio["url"] == "https://www.stremio.com/"
    assert stremio["description"] == "Media center app"


def test_all_entries_have_starred_field():
    from src.indexer import parse_markdown
    entries = parse_markdown(SAMPLE_MARKDOWN)
    assert all("starred" in e for e in entries)


def test_multi_link_line_creates_entry_per_link():
    from src.indexer import parse_markdown
    md = "# ► System Tools\n* [Wox](https://wox.com/), [FlowLauncher](https://flowlauncher.com/), [Raycast](https://raycast.com/) - Keystroke launchers"
    entries = parse_markdown(md)
    titles = [e["title"] for e in entries]
    assert titles == ["Wox", "FlowLauncher", "Raycast"]
    assert all(e["description"] == "Keystroke launchers" for e in entries)
    assert all(e["category"] == "System Tools" for e in entries)
