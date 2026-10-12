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
