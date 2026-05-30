import pytest
from unittest.mock import patch, MagicMock
from tests.conftest import SAMPLE_ENTRIES

RSS_HTML_WITH_STARS = """
<h2>Stars Added ⭐</h2>
<ul>
<li><a href="https://example.com">Example Tool</a> - great tool</li>
<li><a href="https://another.org">Another Site</a></li>
</ul>
<h2>Things Removed</h2>
<ul><li><a href="https://removed.com">Old Site</a></li></ul>
"""


def test_get_random_entry_is_from_entries():
    from src.commands import get_random_entry
    for _ in range(10):
        entry = get_random_entry(SAMPLE_ENTRIES)
        assert entry in SAMPLE_ENTRIES


def test_add_and_get_history(tmp_path, monkeypatch):
    import src.commands as cmds
    monkeypatch.setattr(cmds, "HISTORY_FILE", tmp_path / "history.json")
    cmds.add_history("anime")
    cmds.add_history("music")
    history = cmds.get_history()
    assert history[0] == "music"
    assert "anime" in history


def test_history_deduplicates_and_bumps_to_top(tmp_path, monkeypatch):
    import src.commands as cmds
    monkeypatch.setattr(cmds, "HISTORY_FILE", tmp_path / "history.json")
    cmds.add_history("torrent")
    cmds.add_history("anime")
    cmds.add_history("torrent")
    history = cmds.get_history()
    assert history.count("torrent") == 1
    assert history[0] == "torrent"


def test_history_capped_at_20(tmp_path, monkeypatch):
    import src.commands as cmds
    monkeypatch.setattr(cmds, "HISTORY_FILE", tmp_path / "history.json")
    for i in range(25):
        cmds.add_history(f"query{i}")
    assert len(cmds.get_history()) == 20


def test_toggle_favorite_adds_entry(tmp_path, monkeypatch):
    import src.commands as cmds
    monkeypatch.setattr(cmds, "FAVORITES_FILE", tmp_path / "favs.json")
    cmds.toggle_favorite("https://example.com", "Example", "Test", "Sub", "desc")
    assert cmds.is_favorite("https://example.com")
    favs = cmds.get_favorites()
    assert favs[0]["subcategory"] == "Sub"


def test_toggle_favorite_removes_on_second_call(tmp_path, monkeypatch):
    import src.commands as cmds
    monkeypatch.setattr(cmds, "FAVORITES_FILE", tmp_path / "favs.json")
    cmds.toggle_favorite("https://example.com", "Example", "Test", "Sub", "desc")
    cmds.toggle_favorite("https://example.com", "Example", "Test", "Sub", "desc")
    assert not cmds.is_favorite("https://example.com")


def test_get_favorites_returns_list(tmp_path, monkeypatch):
    import src.commands as cmds
    monkeypatch.setattr(cmds, "FAVORITES_FILE", tmp_path / "favs.json")
    cmds.toggle_favorite("https://a.com", "A", "Cat", "Sub", "desc")
    cmds.toggle_favorite("https://b.com", "B", "Cat", "Sub", "desc")
    favs = cmds.get_favorites()
    assert len(favs) == 2
    urls = [f["url"] for f in favs]
    assert "https://a.com" in urls


def test_parse_stars_added_extracts_links():
    from src.commands import _parse_stars_added
    entries = _parse_stars_added(RSS_HTML_WITH_STARS)
    assert len(entries) == 2
    assert entries[0]["title"] == "Example Tool"
    assert entries[0]["url"] == "https://example.com"
    assert entries[1]["title"] == "Another Site"


def test_parse_stars_added_stops_at_things_removed():
    from src.commands import _parse_stars_added
    entries = _parse_stars_added(RSS_HTML_WITH_STARS)
    urls = [e["url"] for e in entries]
    assert "https://removed.com" not in urls


def test_parse_stars_added_empty_when_section_missing():
    from src.commands import _parse_stars_added
    assert _parse_stars_added("<p>No relevant sections here</p>") == []
