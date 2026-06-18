import re
from typing import List, Dict

_MAIN_CAT = re.compile(r'^#{1,2}\s+[►◄▶◀]\s+(.*)')
_SUB_CAT = re.compile(r'^#{2,4}\s+[▷◁▸◂]\s+(.*)')
# Starred entries: * ⭐ **[Title](url)** - description
_STARRED_ENTRY = re.compile(r'^\*\s+⭐\s+\*\*\[([^\]]+)\]\((https?://[^)]+)\)\*\*\s*(.*)')
# Plain entries: * [Title](url) - description
_ENTRY = re.compile(r'^\*\s+\[([^\]]+)\]\((https?://[^)]+)\)\s*(.*)')
# Strips leading extra links like ", [2](url), [3](url)" that follow the primary link
_EXTRA_LINKS = re.compile(r'^[,\s]*(?:\[[^\]]*\]\([^)]*\)[,\s]*)+')
# Strips remaining inline markdown links: [text](url) → text
_MD_LINK = re.compile(r'\[([^\]]+)\]\([^)]+\)')
# Matches a single comma-separated co-listed resource link at the start of a tail string
_EXTRA_LINK_ITEM = re.compile(r'^[,\s]+\[([^\]]+)\]\((https?://[^)]+)\)')
# Numbered mirror links like [2], [3] — not real tool names
_NUMERIC_TITLE = re.compile(r'^\d+$')


def _clean_description(raw: str) -> str:
    raw = _EXTRA_LINKS.sub('', raw)
    raw = _MD_LINK.sub(r'\1', raw)
    return re.sub(r'^[-–\s]+', '', raw).strip()


def parse_markdown(markdown: str) -> List[Dict]:
    entries = []
    current_category = ""
    current_subcategory = ""

    for line in markdown.splitlines():
        line = line.strip()

        m = _MAIN_CAT.match(line)
        if m:
            current_category = m.group(1).strip()
            current_subcategory = ""
            continue

        m = _SUB_CAT.match(line)
        if m:
            current_subcategory = m.group(1).strip()
            continue

        starred = False
        m = _STARRED_ENTRY.match(line)
        if m:
            starred = True
        else:
            m = _ENTRY.match(line)

        if m:
            title = m.group(1).strip()
            url = m.group(2).strip()
            raw_tail = m.group(3)
            description = _clean_description(raw_tail)

            def _make_entry(t, u):
                return {
                    "title": t,
                    "url": u,
                    "category": current_category,
                    "subcategory": current_subcategory,
                    "description": description,
                    "search_text": f"{t} {current_category} {current_subcategory} {description}",
                    "starred": starred,
                }

            entries.append(_make_entry(title, url))

            # Extract additional co-listed resource links (e.g. ", [Raycast](url), [FlowLauncher](url)")
            # Skip numbered mirror links like [2], [3] which are alternate URLs, not separate tools
            tail = raw_tail
            while True:
                extra = _EXTRA_LINK_ITEM.match(tail)
                if not extra:
                    break
                extra_title = extra.group(1).strip()
                if not _NUMERIC_TITLE.match(extra_title):
                    entries.append(_make_entry(extra_title, extra.group(2).strip()))
                tail = tail[extra.end():]

    return entries
