# FMHY Search — Flow Launcher Plugin

Search the [Free Media Heck Yeah](https://fmhy.net) database directly from Flow Launcher. Results are ranked by relevance, with curated (⭐) picks and English results always shown first.

---

## Requirements

- [Flow Launcher](https://www.flowlauncher.com/) 2.12 or later
- Python 3.10+ (bundled with Flow Launcher — no separate install needed)

---

## Installation

### Option 1 — Manual install from release zip

1. Download the latest `FMHY-Search-x.x.x.zip` from the [Releases](../../releases) page
2. Extract the folder into:
   ```
   %APPDATA%\FlowLauncher\Plugins\
   ```
   so the structure is `…\Plugins\FMHY Search-1.0.0\main.py`
3. Restart Flow Launcher

### Option 2 — Build from source

```bat
git clone https://github.com/iamshamit/fmhy-search-flow-launcher
cd fmhy-search-flow-launcher

:: Install runtime dependencies into lib\
pip install -r requirements.txt -t lib\

:: Copy the folder to Flow Launcher plugins directory
xcopy /E /I . "%APPDATA%\FlowLauncher\Plugins\FMHY Search-1.0.0"

:: Restart Flow Launcher
```

> **First run:** type `fmhy` and press Enter on the prompt to download and build the index (~2 MB, ~5 seconds). All subsequent searches are instant and fully local.

---

## Features

### Search

| What you type | What happens |
|---|---|
| `fmhy torrent client` | Fuzzy search across all 14,000+ FMHY entries |
| `fmhy anime streaming` | Find anime streaming sites |
| `fmhy qbittorrent` | Match by title, even with typos |
| `fmhy flac music download` | Match by description and keywords |

- **Fuzzy matching** — finds results even with typos or partial words (powered by [rapidfuzz](https://github.com/maxbachmann/RapidFuzz))
- **Smart ranking** — ⭐ curated picks appear first, then regular English results, then non-English results
- **15,000+ entries** indexed locally — no internet connection needed to search

### Category Filter

Narrow results to a specific topic before searching:

```
fmhy cat:anime streaming
fmhy cat:audio flac
fmhy cat:privacy vpn
fmhy cat:ai coding
fmhy cat:torrenting clients
```

Matches against both the category and subcategory of each entry. Partial matches work (`cat:torrent` matches "Torrenting", "Torrent Clients", etc.).

### Commands

| Command | Description |
|---|---|
| `fmhy update` | Force re-download and rebuild the index |
| `fmhy random` | Open a random FMHY resource in your browser |
| `fmhy latest` | Show recently starred entries from the latest monthly FMHY update |
| `fmhy history` | List your last 20 searches — select one to re-run it |
| `fmhy fav` | List your saved favorites — select one to open it |

### Context Menu Actions

Open the context menu with **Shift+Enter** or right-click on any result:

| Action | Description |
|---|---|
| **Copy URL** | Copy the resource link to clipboard |
| **Add / Remove Favorite** | Toggle the entry in your favorites list |
| **View section on FMHY.net** | Open the exact section of fmhy.net where this entry lives (e.g. `fmhy.net/video#anime-streaming`) |

### Result Icons

Each result shows the favicon of the linked site. Favicons are fetched asynchronously on first display and cached permanently — there is no delay to search results.

### Auto-Update

The plugin silently checks the FMHY RSS feed in the background on the 1st of each month. If a new update is published, the index rebuilds automatically and you get a notification when it's done. You never have to run `fmhy update` manually unless you want to force a refresh.

---

## How It Works

1. **Index** — on first run (or `fmhy update`), the plugin fetches the full FMHY database from `api.fmhy.net/single-page` (~2 MB of markdown) and parses it into a local JSON index stored in `data\search_index.json`
2. **Search** — every query runs entirely against the local index using rapidfuzz's `WRatio` scorer with a score cutoff of 60. No network request is made during search
3. **Ranking** — results are re-ranked after fuzzy scoring: ⭐ starred English entries → unstarred English entries → non-English entries
4. **Auto-update** — on the first query on the 1st of each month, the plugin fetches the RSS feed in a background thread. If the latest post's month/year differs from what was last indexed, a full rebuild is triggered

---

## Data Files

All plugin data is stored under the plugin folder in `data\`:

| File | Purpose |
|---|---|
| `search_index.json` | Full parsed FMHY entry list (~15,000 entries) |
| `meta.json` | Last RSS check timestamp and last-indexed month/year |
| `history.json` | Your last 20 search terms |
| `favorites.json` | Your bookmarked entries (keyed by URL) |
| `favicons\` | Per-domain favicon PNGs cached to disk |
| `fmhy_plugin.log` | Plugin log file for debugging |

---

## Development

```bat
:: Install dev dependencies (pytest etc.)
pip install -r requirements-dev.txt

:: Run tests
python -m pytest tests/ -v
```

69 tests cover the indexer, search ranking, updater, commands, cache, and URL generation.

### Project Structure

```
FMHY Search/
├── main.py              # Entry point called by Flow Launcher
├── plugin.json          # Plugin manifest
├── requirements.txt     # Runtime deps (requests, rapidfuzz)
├── requirements-dev.txt # Dev deps (pytest)
├── src/
│   ├── plugin.py        # Main plugin class — routes queries and commands
│   ├── search.py        # Fuzzy search + result ranking
│   ├── indexer.py       # Parses FMHY markdown into entry dicts
│   ├── updater.py       # Index builder + RSS-gated auto-update
│   ├── commands.py      # random, latest, history, favorites logic
│   ├── cache.py         # JSON I/O, path constants, logger
│   └── favicon.py       # Async per-domain favicon fetching and caching
├── icons/
│   └── fmhy.png         # Plugin icon
├── lib/                 # Bundled runtime dependencies
└── tests/               # pytest test suite
```

---

## Building a Release Zip

```bat
pip install -r requirements.txt -t lib\
```

Zip the plugin folder excluding `.git\`, `tests\`, `docs\`, and `requirements-dev.txt`. Submit the zip to the Flow Launcher plugin store.
