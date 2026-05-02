#!/usr/bin/env python3
"""
Scrape https://www.enchantedlearning.com/wordlist/ for thematic word lists and
write themes.json — an array of {"name": "...", "words": [...]} entries.

Each theme's word list IS the dictionary for that level: the game will only
recognise words from the same theme. We don't cross-check against any global
dictionary — the themes themselves provide the universe of valid words.

Usage:
    python3 build_themes.py             # scrape up to MAX_THEMES themes
    python3 build_themes.py --max 80    # override theme cap

Be a good neighbour: a small sleep between fetches, modest UA, and we cap the
number of themes pulled per run.
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_FILE = ROOT / 'themes.json'
INDEX_URL = 'https://www.enchantedlearning.com/wordlist/'
SITE = 'https://www.enchantedlearning.com'
UA = 'Mozilla/5.0 (10000monkeys-themes-builder; +contact: local-script)'

MIN_WORD_LEN = 4
DEFAULT_MAX_THEMES = 40
MIN_WORDS_PER_THEME = 12
PER_REQUEST_SLEEP = 0.4

WORDLIST_ITEM_RE = re.compile(
    r'<div class="wordlist-item[^"]*">([^<]+)</div>', re.IGNORECASE
)
THEME_LINK_RE = re.compile(r'href="(/wordlist/[^"#?]+\.shtml)"')
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z']{2,}")


def fetch(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', errors='replace')


def name_from_url(path: str) -> str:
    base = path.rsplit('/', 1)[-1].removesuffix('.shtml')
    return base.replace('-', ' ').replace('_', ' ').title()


def discover_theme_links(index_html: str) -> list[str]:
    seen, out = set(), []
    for m in THEME_LINK_RE.finditer(index_html):
        path = m.group(1)
        if path.endswith('/index.shtml'):
            continue
        # Skip generic / non-theme pages
        if any(s in path for s in ('/index', 'commoncore')):
            continue
        if path in seen:
            continue
        seen.add(path)
        out.append(path)
    return out


def words_from_page(html: str) -> list[str]:
    out, seen = [], set()
    for raw in WORDLIST_ITEM_RE.findall(html):
        # Each item may be a phrase. Pull every letter-run >= MIN_WORD_LEN.
        for tok in TOKEN_RE.findall(raw):
            w = tok.lower().replace("'", '')
            if len(w) < MIN_WORD_LEN or w in seen:
                continue
            seen.add(w)
            out.append(w)
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--max', type=int, default=DEFAULT_MAX_THEMES,
                   help=f'maximum themes to fetch (default {DEFAULT_MAX_THEMES})')
    args = p.parse_args()

    print(f'fetching index: {INDEX_URL}')
    try:
        index_html = fetch(INDEX_URL)
    except urllib.error.URLError as e:
        print(f'ERROR fetching index: {e}', file=sys.stderr)
        return 1

    links = discover_theme_links(index_html)
    print(f'found {len(links)} theme links; will fetch up to {args.max}')

    themes: list[dict] = []
    skipped_thin = skipped_err = 0
    for i, link in enumerate(links):
        if len(themes) >= args.max:
            break
        url = SITE + link
        try:
            html = fetch(url)
        except Exception as e:
            print(f'  [err]  {link}: {e}')
            skipped_err += 1
            continue

        words = words_from_page(html)
        if len(words) < MIN_WORDS_PER_THEME:
            skipped_thin += 1
            print(f'  [thin] {name_from_url(link):30s} ({len(words)} words)')
        else:
            themes.append({'name': name_from_url(link), 'words': words})
            print(f'  [{len(themes):3d}]  {name_from_url(link):30s} {len(words):4d} words')
        time.sleep(PER_REQUEST_SLEEP)

    OUT_FILE.write_text(
        json.dumps(themes, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    total_words = sum(len(t['words']) for t in themes)
    print(f'\nwrote {OUT_FILE}: {len(themes)} themes, {total_words:,} total words '
          f'({skipped_thin} thin, {skipped_err} errors)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
