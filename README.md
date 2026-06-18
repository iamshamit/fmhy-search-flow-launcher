# FMHY Search — Flow Launcher Plugin

Search the [Free Media Heck Yeah](https://fmhy.net) database directly from Flow Launcher. 15,000+ entries indexed locally — no internet needed to search.

---

## Requirements

- [Flow Launcher](https://www.flowlauncher.com/) 2.12 or later
- Python 3.10+ (bundled with Flow Launcher — no separate install needed)

---

## Installation

### Recommended — Flow Launcher Plugin Manager

Open Flow Launcher and run:

```
pm install FMHY Search by iamshamit
```

Flow Launcher will download, install, and activate the plugin automatically.

### Manual — Release zip

1. Download the latest `FMHY-Search-x.x.x.zip` from the [Releases](../../releases) page
2. Extract into:
   ```
   %APPDATA%\FlowLauncher\Plugins\
   ```
   so the path is `…\Plugins\FMHY Search-1.0.0\main.py`
3. Restart Flow Launcher

### Build from source

```bat
git clone https://github.com/iamshamit/fmhy-search-flow-launcher
cd fmhy-search-flow-launcher
pip install -r requirements.txt -t lib\
xcopy /E /I . "%APPDATA%\FlowLauncher\Plugins\FMHY Search-1.0.0"
```

Restart Flow Launcher after copying.

> **First run:** type `fmhy` and press Enter on the prompt to download and build the index (~2 MB, ~5 seconds). All subsequent searches are instant and fully local.

---

## Usage

### Search

Type `fmhy` followed by your query. Search is **keyword-based by default** — all words must match — giving precise, noise-free results.

| What you type | What happens |
|---|---|
| `fmhy torrent client` | Keyword search — both words must appear in the result |
| `fmhy cat:audio flac` | Keyword search within the Audio category |
| `fmhy qbittorrent?` | **Fuzzy search** — finds results even with typos |
| `fmhy anime streaming?` | Fuzzy search for broader coverage |

**Ranking** within keyword results:

1. ⭐ Starred entries where query appears in the **title**
2. Unstarred entries where query appears in the **title**
3. ⭐ Starred entries where query appears in description or category
4. Unstarred entries where query appears in description or category
5. Non-English results last

If a keyword search returns no results, a prompt appears — press **Enter** to retry as a fuzzy search automatically.

### Fuzzy Search

Append `?` to your query for typo-tolerant, approximate matching:

```
fmhy qbittorent?       → finds qBittorrent despite the typo
fmhy free moovies?     → broader match when exact keywords miss
```

Works with category filters too: `fmhy cat:gaming emulater?`

### Category Filter

Narrow results to a specific topic:

```
fmhy cat:              → browse all categories
fmhy cat:audio         → browse Audio entries (or pick from the list)
fmhy cat:audio flac    → search "flac" within Audio
fmhy cat:privacy vpn?  → fuzzy search "vpn" within Privacy
```

Typing `fmhy cat:` shows a live category picker — select one and press **Enter** to filter, then type your search term.

### Commands

| Command | Description |
|---|---|
| `fmhy update` | Re-download and rebuild the index |
| `fmhy random` | Open a random FMHY resource in your browser |
| `fmhy latest` | Show recently starred entries from the latest monthly update |
| `fmhy history` | List your last 20 searches — select one to re-run it |
| `fmhy fav` | List your saved favorites — select one to open it |

### Context Menu

Open with **Shift+Enter** or right-click on any result:

| Action | Description |
|---|---|
| **Copy URL** | Copy the resource link to clipboard |
| **Add / Remove Favorite** | Toggle the entry in your favorites list |
| **View section on FMHY.net** | Open the exact section on fmhy.net (e.g. `fmhy.net/video#anime-streaming`) |

### Result Icons

Each result shows the favicon of the linked site, fetched asynchronously on first display and cached permanently — no delay to search results.

### Auto-Update

The plugin silently checks the FMHY RSS feed in the background on the 1st of each month. If a new update is available, the index rebuilds automatically. You never need to run `fmhy update` manually unless you want to force a refresh.

---

## How It Works

1. **Index** — on first run, the plugin fetches the full FMHY database from `api.fmhy.net/single-page` (~2 MB of Markdown) and parses it into a local JSON index at `data\search_index.json`
2. **Keyword search** — queries run entirely against the local index using substring matching; all query tokens must appear in an entry's title, description, or category. No network request during search.
3. **Fuzzy search** — append `?` to your query to use rapidfuzz's `WRatio` scorer (cutoff 60) for typo-tolerant matching
4. **Ranking** — keyword results are sorted by title relevance and starred status; non-English entries are always last
5. **Auto-update** — on the first query on the 1st of each month, the plugin checks the RSS feed in a background thread and rebuilds if there's a new release

---

## Data Files

All plugin data is stored in `data\` under the plugin folder:

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
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

84 tests cover the indexer, search ranking, updater, commands, cache, and URL generation.

### Project Structure

```
FMHY Search/
├── main.py              # Entry point called by Flow Launcher
├── plugin.json          # Plugin manifest
├── requirements.txt     # Runtime deps (requests, rapidfuzz)
├── requirements-dev.txt # Dev deps (pytest)
├── src/
│   ├── plugin.py        # Query routing, commands, and RPC handlers
│   ├── search.py        # Keyword search, fuzzy search, and result ranking
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

## Release

CI (`.github/workflows/Publish Release.yml`) triggers on every push to `master`. It installs runtime deps into `lib\`, zips the plugin, and publishes a GitHub Release. Bump `Version` in `plugin.json` to cut a new release.
