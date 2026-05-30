import json
import pytest
from datetime import date
from unittest.mock import MagicMock, patch


RSS_XML_MAY = b"""<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Monthly Updates [May]</title>
      <pubDate>Thu, 01 May 2026 00:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""


def _mock_get(content=RSS_XML_MAY, text="", raise_for=None):
    resp = MagicMock()
    resp.content = content
    resp.text = text
    if raise_for:
        resp.raise_for_status.side_effect = raise_for
    else:
        resp.raise_for_status = MagicMock()
    return resp


def test_fetch_rss_month_year_success():
    from src.updater import fetch_rss_month_year
    with patch("src.updater.requests.get", return_value=_mock_get()):
        result = fetch_rss_month_year()
    assert result == (5, 2026)


def test_fetch_rss_month_year_returns_none_on_network_error():
    from src.updater import fetch_rss_month_year
    with patch("src.updater.requests.get", side_effect=Exception("timeout")):
        result = fetch_rss_month_year()
    assert result is None


FIRST = date(2026, 6, 1)
NOT_FIRST = date(2026, 6, 15)


def test_should_check_rss_true_on_first_no_meta(tmp_path, monkeypatch):
    from src import updater, cache
    monkeypatch.setattr(cache, "META_FILE", tmp_path / "meta.json")
    monkeypatch.setattr(updater, "META_FILE", tmp_path / "meta.json")
    with patch("src.updater.date") as mock_date:
        mock_date.today.return_value = FIRST
        from src.updater import should_check_rss
        assert should_check_rss() is True


def test_should_check_rss_false_when_not_first_of_month(tmp_path, monkeypatch):
    from src import updater, cache
    monkeypatch.setattr(cache, "META_FILE", tmp_path / "meta.json")
    monkeypatch.setattr(updater, "META_FILE", tmp_path / "meta.json")
    with patch("src.updater.date") as mock_date:
        mock_date.today.return_value = NOT_FIRST
        from src.updater import should_check_rss
        assert should_check_rss() is False


def test_should_check_rss_false_on_first_already_checked(tmp_path, monkeypatch):
    from src import updater, cache
    meta_path = tmp_path / "meta.json"
    monkeypatch.setattr(cache, "META_FILE", meta_path)
    monkeypatch.setattr(updater, "META_FILE", meta_path)
    from src.cache import save_json
    save_json(meta_path, {"last_rss_check_date": FIRST.isoformat()})
    with patch("src.updater.date") as mock_date:
        mock_date.today.return_value = FIRST
        from src.updater import should_check_rss
        assert should_check_rss() is False


def test_build_index_success(tmp_path, monkeypatch):
    from src import updater, cache
    index_path = tmp_path / "index.json"
    meta_path = tmp_path / "meta.json"
    monkeypatch.setattr(updater, "INDEX_FILE", index_path)
    monkeypatch.setattr(updater, "META_FILE", meta_path)
    monkeypatch.setattr(cache, "INDEX_FILE", index_path)
    monkeypatch.setattr(cache, "META_FILE", meta_path)

    sample_md = "# ► Test\n## ▷ Sub\n* [Tool](https://example.com/) - A tool"
    mock_resp = _mock_get(text=sample_md)

    with patch("src.updater.requests.get", return_value=mock_resp):
        with patch("src.updater.fetch_rss_month_year", return_value=(5, 2026)):
            from src.updater import build_index
            success, msg = build_index()

    assert success
    assert "1 entries" in msg
    assert index_path.exists()
    data = json.loads(index_path.read_text())
    assert data[0]["title"] == "Tool"


def test_build_index_fails_on_network_error(tmp_path, monkeypatch):
    from src import updater, cache
    monkeypatch.setattr(updater, "INDEX_FILE", tmp_path / "index.json")
    monkeypatch.setattr(updater, "META_FILE", tmp_path / "meta.json")

    with patch("src.updater.requests.get", side_effect=Exception("network error")):
        from src.updater import build_index
        success, msg = build_index()

    assert not success
    assert "failed" in msg.lower() or "error" in msg.lower()


def test_build_index_returns_false_when_zero_entries(tmp_path, monkeypatch):
    from src import updater, cache
    monkeypatch.setattr(updater, "INDEX_FILE", tmp_path / "index.json")
    monkeypatch.setattr(updater, "META_FILE", tmp_path / "meta.json")
    empty_md = "# ► Empty section with no links"
    mock_resp = _mock_get(text=empty_md)
    with patch("src.updater.requests.get", return_value=mock_resp):
        from src.updater import build_index
        success, msg = build_index()
    assert not success
