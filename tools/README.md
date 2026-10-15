# Embed generators

Python scripts that produce the CMS-ready HTML embeds in the repo root. No dependencies.

    python3 tools/gen_pages.py   # Sermons + Photo Gallery (also re-runs the Youth page)
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
