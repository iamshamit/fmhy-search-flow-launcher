from typing import List, Dict, Optional, Tuple

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "lib"))

from rapidfuzz import process, fuzz, utils


# Language names that appear as the first word of non-English FMHY category headings
_LANGUAGE_NAMES = frozenset({
    "Arabic", "Bangla", "Bengali", "Bulgarian", "Chinese", "Czech", "Dutch",
    "Filipino", "Finnish", "French", "German", "Greek", "Hebrew", "Hindi",
    "Hungarian", "Indian", "Indonesian", "Italian", "Japanese", "Korean",
    "Malay", "Norwegian", "Persian", "Polish", "Portuguese", "Romanian",
    "Russian", "Slovak", "Spanish", "Swedish", "Tamil", "Thai", "Turkish",
    "Ukrainian", "Uzbek", "Vietnamese",
})


def _is_non_english(entry: Dict) -> bool:
    cat = entry.get("category", "")
    if any(ord(c) > 127 for c in cat):
        return True
    first_word = cat.split()[0] if cat else ""
    return first_word in _LANGUAGE_NAMES


def keyword_search(
    query: str,
    entries: List[Dict],
    category_filter: Optional[str] = None,
    limit: int = 20,
) -> List[Dict]:
    pool = entries
    if category_filter:
        cat_lower = category_filter.lower()
        pool = [
            e for e in entries
            if cat_lower in e["category"].lower()
            or cat_lower in e["subcategory"].lower()
        ]
    tokens = [t for t in query.lower().split() if len(t) > 1]
    if not tokens:
        return []

    def _rank_key(entry: Dict) -> tuple:
        non_en = _is_non_english(entry)
        title_match = all(t in entry["title"].lower() for t in tokens)
        starred = entry.get("starred", False)
        return (non_en, not title_match, not starred)

    results = [e for e in pool if all(t in e["search_text"].lower() for t in tokens)]
    results.sort(key=_rank_key)
    return results[:limit]


def search(
    query: str,
    entries: List[Dict],
    category_filter: Optional[str] = None,
    limit: int = 20,
) -> List[Dict]:
    pool = entries
    if category_filter:
        cat_lower = category_filter.lower()
        pool = [
            e for e in entries
            if cat_lower in e["category"].lower()
            or cat_lower in e["subcategory"].lower()
        ]

    if not pool:
        return []

    # Two-pass fuzzy: title first (catches typo'd tool names), then search_text for
    # anything the title pass missed (catches category/description matches).
    titles = [e["title"] for e in pool]
    title_matches = process.extract(
        query, titles, scorer=fuzz.WRatio, limit=limit * 3, score_cutoff=60,
        processor=utils.default_process,
    )
    seen = {idx for _, _, idx in title_matches}

    search_texts = [e["search_text"] for e in pool]
    text_matches = process.extract(
        query, search_texts, scorer=fuzz.WRatio, limit=limit * 3, score_cutoff=60,
        processor=utils.default_process,
    )

    # Title hits first, then search_text hits not already found
    ordered = [pool[idx] for _, _, idx in title_matches]
    ordered += [pool[idx] for _, _, idx in text_matches if idx not in seen]

    # Re-rank: starred English → unstarred English → non-English (stable sort preserves score order within groups)
    ordered.sort(key=lambda e: (_is_non_english(e), not e.get("starred", False)))
    return ordered[:limit]


def parse_cat_query(query: str) -> Tuple[Optional[str], str, bool]:
    fuzzy = query.endswith("?")
    q = query.rstrip("?")
    if q.startswith("cat:"):
        rest = q[4:]
        # Quoted multi-word category: cat:"Anime Streaming" search term
        if rest.startswith('"'):
            end = rest.find('"', 1)
            if end != -1:
                return rest[1:end], rest[end + 1:].strip(), fuzzy
        parts = rest.split(None, 1)
        cat = parts[0] if parts else ""
        search = parts[1] if len(parts) > 1 else ""
        return cat, search, fuzzy
    return None, q, fuzzy
