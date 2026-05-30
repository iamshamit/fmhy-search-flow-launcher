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
            description = _clean_description(m.group(3))
            search_text = f"{title} {current_category} {current_subcategory} {description}"
            entries.append({
                "title": title,
                "url": url,
                "category": current_category,
                "subcategory": current_subcategory,
                "description": description,
                "search_text": search_text,
                "starred": starred,
            })

    return entries
