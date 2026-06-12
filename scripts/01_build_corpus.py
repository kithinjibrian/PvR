"""
scripts/01_build_corpus.py

Builds data/filler/corpus.txt from Wikipedia article text included in this repo,
or downloads articles via the Wikipedia plain-text API if the file does not exist.

The target size is ~150k tokens (600k characters at 4 chars/token). Topics chosen
to have zero overlap with any fact in data/facts/facts.json: astronomy,
mycology, medieval history, marine biology, and classical music.

Usage:
  uv run python scripts/01_build_corpus.py

Depends on: urllib.request (stdlib only — no extra dependencies)
Used by: scripts/03_run_experiment.py (reads data/filler/corpus.txt)
"""

import logging
import os
import urllib.request

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

OUTPUT_PATH = "data/filler/corpus.txt"

# Wikipedia article titles chosen for topic diversity and zero factual overlap
# with any fact in facts.json.
WIKIPEDIA_ARTICLES = [
    "Stellar_evolution",
    "Andromeda_Galaxy",
    "Nebula",
    "Black_hole",
    "Neutron_star",
    "Mycorrhiza",
    "Amanita",
    "Penicillium",
    "Truffle",
    "Lichens",
    "Medieval_warfare",
    "Feudalism",
    "Crusades",
    "Byzantine_Empire",
    "Viking_Age",
    "Coral_reef",
    "Deep_sea",
    "Whale",
    "Cephalopod",
    "Tidal_zone",
    "Johann_Sebastian_Bach",
    "Wolfgang_Amadeus_Mozart",
    "Ludwig_van_Beethoven",
    "Baroque_music",
    "Symphony",
]

_WIKI_API = "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&titles={title}&format=json"
TARGET_CHARS = 600_000


def fetch_article(title: str) -> str:
    """Fetches plain text of a Wikipedia article via the MediaWiki API.

    Args:
        title: Wikipedia article title (URL-encoded underscores are fine).

    Returns:
        Plain-text content of the article, or empty string on failure.

    Example:
        text = fetch_article("Nebula")
    """
    url = _WIKI_API.format(title=title)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "pvr-experiment/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            import json
            data = json.load(resp)
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            return page.get("extract", "")
    except Exception as exc:  # noqa: BLE001
        log.warning("Failed to fetch %s: %s", title, exc)
    return ""


def main() -> None:
    """Entry point for the corpus builder."""
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    if os.path.exists(OUTPUT_PATH):
        size = os.path.getsize(OUTPUT_PATH)
        log.info("Corpus already exists (%d bytes). Delete to rebuild.", size)
        return

    log.info("Building corpus from %d Wikipedia articles…", len(WIKIPEDIA_ARTICLES))
    parts: list[str] = []
    total_chars = 0

    for title in WIKIPEDIA_ARTICLES:
        if total_chars >= TARGET_CHARS:
            break
        log.info("  Fetching %s…", title)
        text = fetch_article(title)
        if text:
            parts.append(text)
            total_chars += len(text)
            log.info("    Got %d chars (total: %d)", len(text), total_chars)

    corpus = "\n\n".join(parts)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(corpus)

    log.info(
        "Corpus written to %s (%d chars, ~%d tokens)",
        OUTPUT_PATH, len(corpus), len(corpus) // 4,
    )


if __name__ == "__main__":
    main()
