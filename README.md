# Prophet Watch

A filtered feed of Harry Potter news, covering the HBO series, the films, the books, the games, the stage productions and the parks.

Live at [betstg.github.io/prophet-watch](https://betstg.github.io/prophet-watch/)

Every story carries a sourcing mark so you can tell at a glance how well stood up it is.

| Mark | What it means |
| --- | --- |
| Official | Announced by Warner Bros, HBO, Bloomsbury or the Wizarding World channels themselves |
| Confirmed | Not an official announcement, but reported and stood up by the trade press |
| Rumor | Circulating without a named, reliable source. Unproven |
| Leak | Material that escaped before release, such as set images or unlisted footage |
| Paparazzi | Photos taken off set or in public by press photographers |

Every story also links back to where it came from, so nothing has to be taken on trust.

## How it works

`index.html` is the whole site. No build step, no framework, no external images. Thumbnails are drawn in code as heraldic shields, one glyph per desk.

The stories live in a single JSON block inside that file, in a `script` tag with the id `news-data`.

```html
<script type="application/json" id="news-data">
{
  "updated": "2026-09-02",
  "stories": [
    {
      "id": "short-slug-2026-09-02",
      "date": "2026-09-02",
      "status": "official",
      "category": "HBO series",
      "headline": "...",
      "summary": "...",
      "source": "Variety",
      "url": "https://..."
    }
  ]
}
</script>
```

The page reads that block on load and builds everything else from it, including the filter chips, the counts and the day groupings.

`status` must be one of `official`, `confirmed`, `rumor`, `leak`, `paparazzi`.

`category` is free text. A new category creates its own filter chip automatically and picks up a matching shield glyph if one is defined in the `GLYPHS` map near the bottom of the file. Anything unrecognised falls back to a star.

## Updating

Two small scripts keep the edits mechanical.

```bash
# the normal path, add only what is new to the top of the feed
python3 add-news.py index.html new-stories.json

# replace the whole story list instead
python3 set-news.py index.html news.json

# regenerate the version published as a Claude Artifact
python3 build-artifact.py index.html artifact.html
```

`new-stories.json` is a plain array of story objects. `add-news.py` checks every required field, rejects an unknown status or a malformed date, skips any id already filed and trims the list to the newest 120. Running it twice on the same input changes nothing, which is what stops a story being filed twice.

`build-artifact.py` exists because the Artifact host supplies its own doctype, head and body. `index.html` marks the two sections that both versions share, `SHARED-HEAD` and `SHARED-BODY`, and the script lifts just those out. Edit `index.html` only. The artifact file is generated, never edited by hand.

## Running it locally

Open `index.html` in a browser. That is the whole thing.

To serve it instead, run `python3 -m http.server` in this folder and open `http://localhost:8000`.

## Notes

The layout is responsive and reflows at phone width. Light and dark both ship, following the browser setting, with a manual switch in the masthead.

The only external request the page makes is to Google Fonts for Grenze Gotisch, IM Fell English SC, EB Garamond and IBM Plex Sans. Each has a real fallback, so the page still reads if the fonts do not load.
