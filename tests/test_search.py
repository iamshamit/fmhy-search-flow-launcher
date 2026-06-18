import pytest
from tests.conftest import SAMPLE_ENTRIES


def test_search_exact_title_match():
    from src.search import search
    results = search("qBittorrent", SAMPLE_ENTRIES)
    assert len(results) >= 1
    assert results[0]["title"] == "qBittorrent"


def test_search_fuzzy_typo():
    from src.search import search
    results = search("qbittorent", SAMPLE_ENTRIES)  # missing 't'
    assert any(r["title"] == "qBittorrent" for r in results)


def test_search_by_description_keyword():
    from src.search import search
    results = search("BitTorrent client", SAMPLE_ENTRIES)
    assert any(r["title"] == "qBittorrent" for r in results)


def test_search_with_category_filter_matching():
    from src.search import search
    results = search("copilot", SAMPLE_ENTRIES, category_filter="ai tools")
    assert all("AI" in r["category"] for r in results)


def test_search_with_category_filter_excludes_others():
    from src.search import search
    results = search("qbittorrent", SAMPLE_ENTRIES, category_filter="streaming")
    assert not any(r["title"] == "qBittorrent" for r in results)


def test_search_empty_entries_returns_empty():
    from src.search import search
    assert search("anything", []) == []


def test_search_below_threshold_returns_empty():
    from src.search import search
    results = search("xyzzy_nonexistent_zzz", SAMPLE_ENTRIES)
    assert results == []


def test_search_limit_respected():
    from src.search import search
    large = SAMPLE_ENTRIES * 20
    results = search("torrent", large, limit=5)
    assert len(results) <= 5


def test_parse_cat_query_with_prefix():
    from src.search import parse_cat_query
    cat, q, fuzzy = parse_cat_query("cat:anime naruto streaming")
    assert cat == "anime"
    assert q == "naruto streaming"
    assert fuzzy is False


def test_parse_cat_query_without_prefix():
    from src.search import parse_cat_query
    cat, q, fuzzy = parse_cat_query("torrent client")
    assert cat is None
    assert q == "torrent client"
    assert fuzzy is False


def test_parse_cat_query_cat_only():
    from src.search import parse_cat_query
    cat, q, fuzzy = parse_cat_query("cat:music")
    assert cat == "music"
    assert q == ""
    assert fuzzy is False


def test_parse_cat_query_fuzzy_suffix():
    from src.search import parse_cat_query
    cat, q, fuzzy = parse_cat_query("torrents?")
    assert cat is None
    assert q == "torrents"
    assert fuzzy is True


def test_parse_cat_query_cat_and_fuzzy():
    from src.search import parse_cat_query
    cat, q, fuzzy = parse_cat_query("cat:gaming torrents?")
    assert cat == "gaming"
    assert q == "torrents"
    assert fuzzy is True


def test_parse_cat_query_no_fuzzy():
    from src.search import parse_cat_query
    cat, q, fuzzy = parse_cat_query("torrents")
    assert cat is None
    assert q == "torrents"
    assert fuzzy is False


def test_parse_cat_query_double_question():
    from src.search import parse_cat_query
    cat, q, fuzzy = parse_cat_query("torrents??")
    assert q == "torrents"
    assert fuzzy is True


def test_starred_results_before_unstarred():
    from src.search import search
    results = search("streaming", SAMPLE_ENTRIES)
    starred_idx = next((i for i, r in enumerate(results) if r.get("starred")), None)
    unstarred_idx = next((i for i, r in enumerate(results) if not r.get("starred") and r["category"].isascii()), None)
    if starred_idx is not None and unstarred_idx is not None:
        assert starred_idx < unstarred_idx


def test_non_english_results_after_english():
    from src.search import search
    results = search("anime streaming", SAMPLE_ENTRIES)
    if len(results) < 2:
        return
    non_en_indices = [i for i, r in enumerate(results) if not r["category"].isascii()]
    en_indices = [i for i, r in enumerate(results) if r["category"].isascii()]
    if non_en_indices and en_indices:
        assert min(non_en_indices) > max(en_indices)


def test_is_non_english_detection():
    from src.search import _is_non_english
    assert _is_non_english({"category": "French / Français"}) is True   # non-ASCII
    assert _is_non_english({"category": "Polish / Polski"}) is True     # ASCII language name
    assert _is_non_english({"category": "German / Deutsch"}) is True    # ASCII language name
    assert _is_non_english({"category": "Indian Languages"}) is True    # ASCII language name
    assert _is_non_english({"category": "Torrenting"}) is False
    assert _is_non_english({"category": "Antivirus / Anti-Malware"}) is False
    assert _is_non_english({"category": "Privacy / Security"}) is False
