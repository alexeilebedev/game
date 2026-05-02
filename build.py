#!/usr/bin/env python3
"""
Read source.txt and produce:
  syllable.txt — every 2- and 3-letter substring of the most frequent words
                 in source.txt, weighted by source-word frequency.
                 Format: '<syllable>\\t<count>' per line, sorted desc by count.

dict.txt is NOT written here — it is provided separately.

source.txt may be plain text or HTML; HTML tags and entities are stripped.
"""
import html as _html
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'source.txt'
SYL_OUT = ROOT / 'syllable.txt'

# Use this many top-frequency source words to weight the syllable counts.
TOP_WORDS = 10_000
MIN_WORD_LEN = 4
SYL_LENS = (2, 3)

# Cyrillic + Latin letter runs
WORD_RE = re.compile(r'[А-Яа-яЁёA-Za-z]+')


def strip_html(s: str) -> str:
    s = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    return _html.unescape(s)


def main() -> int:
    if not SRC.exists():
        print(f'ERROR: {SRC} not found', file=sys.stderr)
        return 1

    raw = SRC.read_text(encoding='utf-8', errors='replace')
    head = raw[:1024].lstrip()
    if head.startswith('<') or '<html' in head.lower():
        raw = strip_html(raw)

    words = [w.lower() for w in WORD_RE.findall(raw)]
    word_counts = Counter(w for w in words if len(w) >= MIN_WORD_LEN)
    top = word_counts.most_common(TOP_WORDS)

    syl_counts: Counter = Counter()
    for word, cnt in top:
        for n in SYL_LENS:
            if len(word) < n:
                continue
            for i in range(len(word) - n + 1):
                syl_counts[word[i:i + n]] += cnt

    with SYL_OUT.open('w', encoding='utf-8') as f:
        for syl, cnt in syl_counts.most_common():
            f.write(f'{syl}\t{cnt}\n')

    total_tokens = len(words)
    print(f'source tokens (any letter run):   {total_tokens:,}')
    print(f'words used for weighting:         {len(top):,} (>= {MIN_WORD_LEN} letters)')
    print(f'syllable.txt: {len(syl_counts):,} unique 2/3-letter syllables')
    if syl_counts:
        top_sy = syl_counts.most_common(5)
        print(f'              top 5: {", ".join(f"{s}({c})" for s, c in top_sy)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
