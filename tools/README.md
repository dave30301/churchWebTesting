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

## Pastor's Highlights page (`fbc-pastors-highlights-embed-clean.html`)

Same two-sided header (page name left, logo right) and call-to-action footer as the Pastor's Pen, with five tabs in place of the
library: this week on the left, the oldest on the right. Each tab shows one week's highlights HTML, which sits in a block marked
`data-hl` (its HTML goes in the cell marked `data-hl-body`; the tab name is the block's `label` field). The tab row is built by a
script; without scripts the five weeks simply stack. The header logo is `HL_LOGO` in `gen_pages.py` (placeholder address until the
logo is uploaded). The page starts with five empty weeks (grey placeholder, "Week 1" to "Week 5").

In the Page Editor (`tools/dashboard.html`) load the page, then under "Weeks, newest on the left":
- **+ Add highlight files**: pick one HTML file per week. Each becomes a tab, named from the first date found in it ("Nov 8") and
  placed newest-first; it replaces an empty week so there are five. A file with no date is added at the left for you to name.
- Or open a week and paste its HTML ("Use this HTML for this week"), edit its **Tab name**, move it, clear it or remove it.
- If you end up with more than five weeks, the editor says so; remove the oldest.

## Church Calendar page (`fbc-calendar-embed-clean.html`)

Same header and footer as the Pastor's Pen and Highlights pages, with small trapezoid (folder-style) tabs, left-justified. The page
starts with **no tabs**: every calendar you add becomes its own tab, most recent month on the left. Each calendar sits in a block
marked `data-cal`, its HTML in the cell marked `data-cal-body`. A tab shows its name exactly as typed (new ones start as "Nov",
or "Jan 2027" for another year; rename them in the **Tab name** field). Which month a calendar is for is kept apart, in
`data-cal-key="2026-11"`, so renaming a tab never breaks the ordering or the "current month opens first" rule. The header logo is `CAL_LOGO` in `gen_pages.py` (placeholder address).

In the Page Editor load the page, then under "Months, January to December":
- **+ Add calendar files**: pick one HTML file per month. The month comes from the file name, title, picture names or text
  (`Church_Calendar_2026-11.html`, `november.html`, a file that is all about April), the year from the same places (else this
  year). Each becomes a tab such as "November 2026", placed most recent first. Adding a month again replaces it. A file with no
  month in it is skipped with a note.
- **Or paste one month's HTML**: pick the month and year, paste, add. Open any month to replace its HTML, edit its **Tab name**,
  clear it, or remove it.

Like the Highlights page, if a CMS removes the invisible marks the page still finds each tab name from the visible title line, and
the editor puts the marks back and updates an older tabs script when you load the page.

## Call-to-action spacing (Pen, Highlights and Calendar pages)

The Page Editor shows three number fields (pixels) for the call-to-action band: space above, space below, and space inside (top and
bottom). They appear in the "Call-to-action band" section of any of those three pages, even one generated before the fields
existed. Use these to tune the spacing on a page you keep editing in the dashboard. Changing `pad=` in `gen_pages.py` only affects
pages you re-generate and paste in fresh; HTML you load from the CMS into the dashboard keeps whatever spacing it already has.

On the Calendar page only, the call-to-action buttons ("Plan a Visit", "Watch Live") are vertically centred beside the text by code
inside the calendar's one tabs script (`CTA_JS` in `gen_pages.py`, marker `fbcCtaCenter`). That script sits above the footer, so the
centring waits until the page has loaded. On phones, where the buttons stack under the text, it leaves their normal gap. It finds the
two columns from the heading and the first button (not from the `align` attribute). Loading a calendar page into the Page Editor
replaces its tabs script with the current one, and removes the separate centring script an earlier version added. The Pen and
Highlights pages do not use it.
The calendar band also wraps the two columns in a `display:flex` row with `align-items:center`, so the buttons are centred even where a
CMS does not run scripts (the script then leaves them alone). Where a CMS drops `display:flex`, the columns float as before and the
script does the centring.

