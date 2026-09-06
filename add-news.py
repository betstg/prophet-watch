#!/usr/bin/env python3
"""Add new stories to the top of the feed in index.html.

Usage
    python3 add-news.py index.html new-stories.json [YYYY-MM-DD]

new-stories.json is a JSON array of story objects, newest first. Anything whose
id is already filed is skipped and reported, so running twice is harmless.
The third argument sets the "updated" stamp and defaults to today.

Existing stories are never touched. Only the JSON block changes.
"""

import datetime
import json
import re
import sys

OPEN = '<script type="application/json" id="news-data">'
CLOSE = '</script>'
FIELDS = ('id', 'date', 'status', 'category', 'headline', 'summary', 'source', 'url')
# these are optional, but when they come in they must survive. Leaving them out
# of the copy is what silently stripped the pictures off every filed story.
OPCIONAIS = ('image', 'video', 'imagemIlustrativa')
STATUSES = ('official', 'confirmed', 'analysis', 'rumor', 'leak', 'paparazzi')
MAX_STORIES = 120
# the castle used to be the fallback picture, and it ended up on eight stories
# at once. A story with no picture of its own gets none, and the page draws its
# own engraved plate instead.
PROIBIDA = 'hogwarts-night'


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)

    page_path, new_path = sys.argv[1], sys.argv[2]
    stamp = sys.argv[3] if len(sys.argv) == 4 else datetime.date.today().isoformat()

    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', stamp):
        sys.exit('the date stamp must look like 2026-09-02')

    with open(new_path, encoding='utf-8') as fh:
        incoming = json.load(fh)
    if not isinstance(incoming, list):
        sys.exit('new-stories.json must be a JSON array')

    with open(page_path, encoding='utf-8') as fh:
        page = fh.read()

    start = page.find(OPEN)
    end = page.find(CLOSE, start)
    if start == -1 or end == -1:
        sys.exit('could not find the news-data block in ' + page_path)

    data = json.loads(page[start + len(OPEN):end])
    known = {s['id'] for s in data['stories']}

    added, skipped = [], []
    for s in incoming:
        missing = [f for f in FIELDS if f not in s or not str(s[f]).strip()]
        if missing:
            sys.exit('story is missing {}: {}'.format(', '.join(missing), s.get('id', '?')))
        if s['status'] not in STATUSES:
            sys.exit('unknown status "{}" on {}, expected one of {}'.format(
                s['status'], s['id'], ', '.join(STATUSES)))
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', s['date']):
            sys.exit('bad date on {}, expected YYYY-MM-DD'.format(s['id']))
        if not s['url'].startswith('https://'):
            sys.exit('source url on {} must start with https://'.format(s['id']))
        if s['id'] in known:
            skipped.append(s['id'])
            continue
        if s.get('image') and PROIBIDA in s['image']:
            sys.exit('{} points at the castle photo. A story with no picture of '
                     'its own must be filed with no image field at all.'.format(s['id']))
        known.add(s['id'])
        nova = {f: s[f] for f in FIELDS}
        for f in OPCIONAIS:
            if s.get(f):
                nova[f] = s[f]
        added.append(nova)

    data['stories'] = added + data['stories']
    dropped = 0
    if len(data['stories']) > MAX_STORIES:
        dropped = len(data['stories']) - MAX_STORIES
        data['stories'] = data['stories'][:MAX_STORIES]
    data['updated'] = stamp

    block = OPEN + '\n' + json.dumps(data, indent=2, ensure_ascii=False) + '\n'
    with open(page_path, 'w', encoding='utf-8') as fh:
        fh.write(page[:start] + block + page[end:])

    print('added {}, skipped {} already filed, now {} stories, updated {}'.format(
        len(added), len(skipped), len(data['stories']), stamp))
    if skipped:
        print('skipped ids: ' + ', '.join(skipped))
    if dropped:
        print('dropped {} of the oldest to stay under {}'.format(dropped, MAX_STORIES))
    if not added:
        print('NOTHING ADDED')

    sem = [s['id'] for s in added if not s.get('image')]
    if sem:
        print('')
        print('WITHOUT A PICTURE, {} of the {} just filed:'.format(len(sem), len(added)))
        for i in sem:
            print('  ' + i)
        print('Before you finish the run, go back to each of those articles and look '
              'for a photograph INSIDE the body of the piece. A site with no og:image '
              'usually still illustrates the article. Only leave a story with no '
              'picture once you have actually looked and found nothing.')


if __name__ == '__main__':
    main()
