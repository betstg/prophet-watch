#!/usr/bin/env python3
"""Replace the news data block inside index.html.

Usage
    python3 set-news.py index.html news.json

news.json must be the whole data object, meaning {"updated": "...", "stories": [...]}.
The script rewrites index.html in place and prints how many stories it wrote.
It never touches the markup, the CSS or the script around the block.
"""

import json
import re
import sys

OPEN = '<script type="application/json" id="news-data">'
CLOSE = '</script>'


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)

    page_path, data_path = sys.argv[1], sys.argv[2]

    with open(data_path, encoding='utf-8') as fh:
        data = json.load(fh)

    if 'updated' not in data or 'stories' not in data:
        sys.exit('news.json needs both an "updated" field and a "stories" array')

    ids = [s['id'] for s in data['stories']]
    if len(ids) != len(set(ids)):
        sys.exit('duplicate story ids found, refusing to write')

    with open(page_path, encoding='utf-8') as fh:
        page = fh.read()

    start = page.find(OPEN)
    if start == -1:
        sys.exit('could not find the news-data block in ' + page_path)
    end = page.find(CLOSE, start)
    if end == -1:
        sys.exit('the news-data block is not closed in ' + page_path)

    block = OPEN + '\n' + json.dumps(data, indent=2, ensure_ascii=False) + '\n'
    page = page[:start] + block + page[end:]

    with open(page_path, 'w', encoding='utf-8') as fh:
        fh.write(page)

    print('wrote {} stories, updated {}'.format(len(data['stories']), data['updated']))


if __name__ == '__main__':
    main()
