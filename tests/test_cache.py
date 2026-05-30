import json
import pytest
from pathlib import Path


def test_load_json_returns_default_when_missing(tmp_path, monkeypatch):
    from src import cache
    monkeypatch.setattr(cache, "INDEX_FILE", tmp_path / "missing.json")
    result = cache.load_json(tmp_path / "missing.json", {"default": True})
    assert result == {"default": True}


def test_load_json_returns_default_on_corrupt(tmp_path):
    from src.cache import load_json
    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text("not valid json")
    result = load_json(corrupt, [])
    assert result == []


def test_save_and_load_json_roundtrip(tmp_path):
    from src.cache import load_json, save_json
    path = tmp_path / "test.json"
    data = [{"title": "test", "url": "https://example.com"}]
    save_json(path, data)
    assert load_json(path, []) == data


def test_save_json_creates_parent_dir(tmp_path):
    from src.cache import save_json, load_json
    nested = tmp_path / "subdir" / "file.json"
    save_json(nested, {"key": "val"})
    assert nested.exists()


def test_get_logger_returns_logger():
    from src.cache import get_logger
    import logging
    log = get_logger()
    assert isinstance(log, logging.Logger)
    assert log.name == "fmhy"
