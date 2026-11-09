# Embed generators

Python scripts that produce the CMS-ready HTML embeds in the repo root. No dependencies.

    python3 tools/gen_pages.py   # Sermons + Photo Gallery + Forms (also re-runs the Youth page)
    python3 tools/gen_youth.py   # Youth Ministry page only

Outputs per page: `fbc-<page>-embed.html` (full instructions in comments) and
`fbc-<page>-embed-clean.html` (no comments). The Youth page also has an `-annotated` copy.

**Photo Gallery** follows `fbc-photo-gallery-embed-clean-v3.html`, the version verified in the CMS.
To change albums, edit the `FEATURED` and `ALBUMS` lists near the bottom of `gen_pages.py`
(title, date, photo count, Lightroom share id, adobe.ly link; newest first) and re-run.

**Gallery filters** are script-driven (verified with `cms-script-test.html`: this CMS keeps `<script>` and `data-`
attributes but strips `<style>` blocks and inline `onclick`). Each album in `ALBUMS` has `cats="worship events"`
(space-separated keys); chip keys live in the `chips([...])` call. A card shows when its `cats` contains the chip key.

## Page editor (`tools/dashboard.html`)

A single-file web tool for updating the pages without touching code. Open it in a browser (or use the published copy),
paste the current page HTML from the CMS, fill in the fields, press **Copy updated HTML**, and paste the result back
into the CMS block. Nothing is uploaded; everything runs in the browser tab.

What it does:
- Finds every editable value by the invisible `data-fbc-*` labels the generators add (see below) and shows them as a form.
- YouTube fields accept a link, an embed code or a bare video ID (a `t=234s` start time is kept).
  Lightroom fields accept the embed code, a share link or the 32-character share ID. Email addresses become `mailto:` links.
- Message / album lists: add a new card at the top, duplicate, move, remove, and pick which filters it appears under.
- Live preview (desktop / tablet / phone) that runs the page's own scripts, plus a list of what changed.
- "Find & replace" works on any HTML, even a copy made before the labels existed.

The page HTML must come from a version generated **after** the labels were added (re-run `python3 tools/gen_pages.py`
and paste the new files into the CMS once; after that, edit through the dashboard).

### Edit labels
Plain `data-` attributes, invisible on the page:

| Attribute | Meaning |
|---|---|
| `data-fbc="group.name"` | text of this element is an editable field (`data-fbc-upper`, `data-fbc-long` tune it) |
| `data-fbc-href="group.name"` | this link's address is a field |
| `data-fbc-video="name"` / `data-fbc-lr="name"` | YouTube / Lightroom iframe |
| `data-fbc-img="name"` | image address and alt text |
| `data-fbc-item="list"` | one repeating card (`data-fbc-fixed` = no add/remove) |
| `data-fbc-page="sermons"` | which page this is |

Helpers for adding labels in the generators: `F()`, `FH()`, `FV()`, `FL()`, `FI()`, `FITEM()`, `SPANS()` in `gen_youth.py`.
Field names get their friendly labels from the `LABELS` table at the top of the script in `dashboard.html`.

The Forms page is generated from the `FORMS` list at the bottom of `gen_pages.py` (all links are "#" placeholders until you set the real ones).

The table-based Forms page (`fbc-forms-tables-recolored.html`) carries edit labels too: section headings, cards (`data-fbc-item="fs1"`..) and the footer. In the Page Editor, "Add a new form" puts a card first in its section and the cards re-flow into rows of three (a new row appears when the last is full). Search finds new cards by their title and description.

The Pastor's Pen page (`fbc-pastors-pen-embed-clean.html`) is generated from the `PENS` list in `gen_pages.py`. Each entry is one week's real Pen HTML saved in `pens_html/` (for now the library is five copies of the November 1 "3 A.M. Bench" Pen so the library can be tried out). The library list on the right builds itself from the Pens: each card is named from the Pen's own header, which has three lines: "1st Sunday · Sunday, November 1, 2026", the sermon title, and the verses. `images/pen/` holds the 400px preview pictures from the roadmap file.

Adding weeks: open `tools/dashboard.html` (FBC Page Editor), load the Pen page, and under "Sundays, newest first" use **+ Add Pen files** to pick one or many Pen HTML files (or paste one). Each Pen is placed by the date in its header, newest first, and its library card is named automatically. A Pen with no readable header is still added, with its three card lines left to fill in (the date is guessed from the file name or title). Move / Duplicate / Remove work on every Sunday. Open any Sunday to edit the three lines of its library card (they override the header; the Pen itself is not changed).
