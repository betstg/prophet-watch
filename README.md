# Prophet Watch

A filtered feed of Harry Potter news, covering the HBO series, the films, the books, the games, the stage productions and the parks.

Every story carries a status tag so you can tell at a glance how well sourced it is.

| Tag | What it means |
| --- | --- |
| Official | Announced by Warner Bros, HBO, Bloomsbury or the Wizarding World channels themselves |
| Confirmed | Not an official announcement, but reported and stood up by the trade press |
| Rumor | Circulating without a named, reliable source. Unproven |
| Leak | Material that escaped before release, such as set images or unlisted footage |
| Paparazzi | Photos taken off set or in public by press photographers |

Every story also links back to where it came from, so nothing has to be taken on trust.

## How it works

The whole site is one file, `index.html`. There is no build step and no framework.

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

To add a story, drop a new object at the top of the `stories` array and change `updated`. The page reads that block on load and builds everything else from it, including the filter chips, the counts and the day groupings.

`status` must be one of `official`, `confirmed`, `rumor`, `leak`, `paparazzi`.

`category` is free text. A new category creates its own filter chip automatically, and picks up a matching thumbnail if one is defined in the `GLYPHS` map near the bottom of the file. Anything unrecognised falls back to a star.

## Running it

Open `index.html` in a browser. That is the whole thing.

To serve it locally instead, run `python3 -m http.server` in this folder and open `http://localhost:8000`.

## Notes

Thumbnails are drawn in code as inline SVG, so the page loads no external images and stays fast.

The layout is responsive and reflows at phone width. Light and dark themes both ship, following the browser setting, with a manual switch in the corner.

The only external request the page makes is to Google Fonts for Gloock, Newsreader and IBM Plex Sans. Every one of those has a real fallback, so the page still reads if the fonts do not load.
