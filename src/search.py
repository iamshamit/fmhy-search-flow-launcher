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

    search_texts = [e["search_text"] for e in pool]
    # Fetch 3× the limit so re-ranking has enough English candidates to fill the final list
    matches = process.extract(
        query, search_texts, scorer=fuzz.WRatio, limit=limit * 3, score_cutoff=60,
        processor=utils.default_process,
    )
    results = [pool[idx] for _, _, idx in matches]
    # Re-rank: starred English → unstarred English → non-English (stable sort preserves score order within groups)
    results.sort(key=lambda e: (_is_non_english(e), not e.get("starred", False)))
    return results[:limit]


def parse_cat_query(query: str) -> Tuple[Optional[str], str]:
    if query.startswith("cat:"):
        parts = query[4:].split(None, 1)
        cat = parts[0] if parts else ""
        rest = parts[1] if len(parts) > 1 else ""
        return cat, rest
    return None, query
