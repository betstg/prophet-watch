#!/usr/bin/env python3
"""Produce the Artifact version of the page from index.html.

Usage
    python3 build-artifact.py index.html artifact.html

index.html is a complete standalone document, which is what GitHub Pages serves.
The Artifact host wraps the file it publishes in its own doctype, head and body,
so the published file must carry none of those. This script lifts out the two
shared sections marked in index.html and writes just those, in order.
"""

import base64
import mimetypes
import os
import re
import sys

HEAD = ('<!-- SHARED-HEAD-START -->', '<!-- SHARED-HEAD-END -->')
BODY = ('<!-- SHARED-BODY-START -->', '<!-- SHARED-BODY-END -->')


def section(page, markers, path):
    start = page.find(markers[0])
    end = page.find(markers[1])
    if start == -1 or end == -1 or end < start:
        sys.exit('could not find {} in {}'.format(markers[0], path))
    return page[start + len(markers[0]):end].strip()


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)

    src_path, out_path = sys.argv[1], sys.argv[2]

    with open(src_path, encoding='utf-8') as fh:
        page = fh.read()

    out = section(page, HEAD, src_path) + '\n\n' + section(page, BODY, src_path) + '\n'

    # The Artifact host blocks images from anywhere else, so bake them in.
    base = os.path.dirname(os.path.abspath(src_path))

    def inline(match):
        rel = match.group(2)
        path = os.path.join(base, rel)
        if not os.path.isfile(path):
            sys.exit('referenced asset is missing, ' + rel)
        kind = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        with open(path, 'rb') as fh:
            blob = base64.b64encode(fh.read()).decode('ascii')
        print('inlined {} ({} KB)'.format(rel, len(blob) // 1024))
        return match.group(1) + 'data:' + kind + ';base64,' + blob + match.group(3)

    out = re.sub(r'(src=")((?:assets/)?[\w./-]+\.(?:jpg|jpeg|png|svg|webp))(")', inline, out)

    for bad in ('<!doctype', '<html', '<head>', '<body>'):
        if bad in out.lower():
            sys.exit('the artifact file must not contain ' + bad)

    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write(out)

    print('wrote {} ({} bytes)'.format(out_path, len(out)))


if __name__ == '__main__':
    main()
