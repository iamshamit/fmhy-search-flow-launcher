import json
import logging
from pathlib import Path

PLUGIN_DIR = Path(__file__).parent.parent
_DATA_DIR = PLUGIN_DIR / "data"

RSS_URL = "https://fmhy.net/feed.rss"

INDEX_FILE = _DATA_DIR / "search_index.json"
META_FILE = _DATA_DIR / "meta.json"
HISTORY_FILE = _DATA_DIR / "history.json"
FAVORITES_FILE = _DATA_DIR / "favorites.json"
FAVICON_DIR = _DATA_DIR / "favicons"
LOG_FILE = _DATA_DIR / "fmhy_plugin.log"


def _ensure_data_dir():
    _DATA_DIR.mkdir(exist_ok=True)
    FAVICON_DIR.mkdir(exist_ok=True)


def load_json(path: Path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


def get_logger() -> logging.Logger:
    logger = logging.getLogger("fmhy")
    if not logger.handlers:
        _ensure_data_dir()
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
