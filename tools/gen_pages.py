import re, io, os, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from gen_youth import *          # reuse helpers (palette, T/TR/TD, btn, card, rounded, section ...)
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
def sec(content, **kw): return section(TR(TD(content)), **kw)
def c(s): return f"<!-- {s} -->\n"

# ---------- embed placeholders ----------
def embed(kind, height, label, note, radius=16):
    r = f"border-radius:{radius}px;"
    if kind == "yt":
        bg, fg, sub = DEEP, WHITE, CREAM
        play = T(TR(f'<td align="center" valign="middle" width="72" height="72" bgcolor="{GOLD}" style="width:72px;height:72px;background-color:{GOLD};border-radius:50%;font-size:28px;line-height:72px;color:{DARK};text-align:center;padding-left:4px;">&#9654;</td>'),
                 width="72", style="border-radius:50%;", extra=' align="center"')
        body = play + sp(14) + txt(f"[YOUTUBE EMBED: {label}]", 16, fg, "600", extra="text-align:center;") + txt(note, 13, sub, extra="text-align:center;padding-top:4px;")
    else:
        bg, fg, sub = LGRAY, MAROON, TGRAY
        body = txt("&#9638;", 40, GOLD, extra="text-align:center;line-height:1;") + sp(10) + txt(f"[ADOBE LIGHTROOM EMBED: {label}]", 16, fg, "600", extra="text-align:center;") + txt(note, 13, sub, extra="text-align:center;padding-top:4px;")
    td = f'<td align="center" valign="middle" height="{height}" bgcolor="{bg}" style="height:{height}px;background-color:{bg};border:2px dashed {GOLD};{r}padding:16px;">{body}</td>'
    return T(TR(td), width="100%", bg=bg, style=f"background-color:{bg};{r}")

def photo(label, height, radius=12):
    r = f"border-radius:{radius}px;"
    td = f'<td align="center" valign="middle" height="{height}" bgcolor="{LGRAY}" style="height:{height}px;background-color:{LGRAY};border:2px dashed {GOLD};{r}font-family:{B};font-size:15px;color:{TGRAY};text-align:center;">[CMS MEDIA: {label}]</td>'
    return T(TR(td), width="100%", style=r)

def chips(items, active=0, ident=None):
    """Filter chips. Items are 'Label' (plain link to #) or ('Label', 'key') for script-driven filtering:
    the anchor gets data-filter="key" and href="#albums" (so it still jumps to the grid if scripts are blocked)."""
    cells = []
    for i, t in enumerate(items):
        key = None
        if isinstance(t, tuple):
            t, key = t
        on = i == active
        bg, col, bd = (MAROON, WHITE, MAROON) if on else (CREAM, MAROON, GOLD)
        attrs = f' data-filter="{key}"' if key else ""
        href = "#albums" if key else "#"
        a = (f'<a href="{href}"{attrs} style="text-decoration:none;display:block;white-space:nowrap;padding:10px 22px;'
             f'font-family:{B};font-size:16px;font-weight:bold;color:{col};">{t}</a>')
        cells.append(f'<td bgcolor="{bg}" style="background-color:{bg};border:1px solid {bd};border-radius:999px;">{a}</td>')
        cells.append(gap_col(12))
    return T(TR(*cells[:-1]), width="auto", extra=f' id="{ident}"' if ident else "")

def grid3(cards, gap=24):
    rows = []
    for i in range(0, len(cards), 3):
        rows.append(TR(cards[i], gap_col(gap), cards[i+1], gap_col(gap), cards[i+2]))
    return T(gap_row(gap, 5).join(rows))

def title_block(inner_html):
    """Reserve room for a two-line card title (22px x 1.2 line-height x 2 = 53px) so every card in a row is the same height.
    A table cell with a height attribute is used because it survives CMS sanitizers."""
    return T(TR(TD(inner_html, valign="top", height="54", style="height:54px;")), width="100%")

def flow_card(inner, pad=20, height=400, gap=24, cats=None):
    """Self-wrapping card using the legacy HTML attribute align="left" (survives CMS sanitizers that strip
    display / float / margin CSS). Three per row: width 33%; fixed height keeps the rows from snagging.
    gap = vertical space under each card row."""
    dc = f' data-cats="{cats}"' if cats else ""
    return (f'<table role="presentation" align="left" width="33%" cellpadding="0" cellspacing="0" border="0"{dc} style="width:33.333%;border-collapse:separate;">'
            f'<tr><td valign="top" height="{height + gap}" style="height:{height + gap}px;padding:0 12px {gap}px 12px;">'
            + rounded(inner, CREAM, 16, pad, f"border:1px solid {GOLD};") + "</td></tr></table>")
def flow(cards, what):
    """Cards wrap into rows on their own: newest goes first, so adding one never means moving the others."""
    body = "".join(f"<!-- {what.upper()} CARD START: copy from here -->\n{cd}\n<!-- {what.upper()} CARD END -->\n" for cd in cards)
    return (f"<!-- NEWEST {what.upper()} FIRST: paste the new card on the line below this one -->\n"
            f"{body}"
            f"<!-- To keep the list short, delete the last card above (the oldest) -->\n"
            '<div style="font-size:0;line-height:0;"><br clear="all" style="clear:both;"></div>\n')

def head_row(title, right_html=""):
    return T(TR(TD(h("h2", title, 36, MAROON), valign="middle"), TD(right_html, valign="middle", align="right", style="white-space:nowrap;")))

def page(rows, header_comment, font_link=False):
    doc = header_comment + (FONT if font_link else "") + T(rows, width="100%", bg=WHITE, style=f"background-color:{WHITE};font-family:{B};color:{DARK};")
    return doc
FONT = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&amp;family=Source+Sans+3:wght@400;600;700&amp;display=swap">\n'

def write(name, doc):
    open(R + f"fbc-{name}-embed.html", "w").write(doc + "\n")
    clean = re.sub(r'<!--.*?-->\s*', '', doc, flags=re.S).strip() + "\n"
    open(R + f"fbc-{name}-embed-clean.html", "w").write(clean)
    print(name, len(re.findall(r'<!--.*?-->', doc, flags=re.S)), doc.count("<table"), doc.count("</table>"))

PALETTE = """  FBC COLOR CODES USED
    #6B1735 Maroon (headings, primary buttons)   #4B1026 Deep Maroon (CTA band, video boxes)
    #C9A55C Gold (accents, secondary buttons)    #F7F3EC Cream (cards)
    #F2F2F2 Light Gray (featured sections)       #666666 Text Gray   #ffffff White   #171717 Dark Gray (body text)"""

# =====================================================================
# SERMONS
# =====================================================================
hero = section(TR(TD(
    eyebrow("Watch &amp; Listen", MAROON, 15, "0.16em") + sp(20) + h("h1", "Sermons", 64, MAROON, lh="1.04") + sp(20)
    + txt("Watch live on Sundays at 9:00 AM, or catch up on any message from our pulpit, anytime and on any device.", 21, TGRAY, extra="line-height:1.5;max-width:760px;") + sp(28)
    + T(TR(TD(btn("Watch live Sunday 9:00 AM", "#", MAROON, WHITE, 18, "10px 32px"), valign="top"), gap_col(16), TD(btn("Subscribe on YouTube", "#", GOLD, DARK, 18, "10px 32px"), valign="top")), width="auto"),
    valign="middle")), pad="16px 0")

feat_embed = embed("yt", 500, "Latest sermon", "16:9 player - paste the iframe from YouTube > Share > Embed", 20)
def link_row(t): return link(t, "#", f"font-family:{B};font-size:17px;font-weight:600;color:{MAROON};")
feat_side = (eyebrow("Latest message") + sp(14) + h("h2", "[Sermon title]", 32, MAROON, "600", "1.15") + sp(10)
    + txt("[Pastor name] &middot; [Month 00, 2026]", 17, TGRAY) + sp(18)
    + T(TR(TD(txt("SERIES", 12, MAROON, "bold", extra="letter-spacing:0.14em;"), width="110", valign="top") , TD(txt("[Series name]", 17, DARK, "600"), valign="top")) + gap_row(8, 2)
        + TR(TD(txt("SCRIPTURE", 12, MAROON, "bold", extra="letter-spacing:0.14em;"), width="110", valign="top"), TD(txt("[Book 0:00-00]", 17, DARK, "600"), valign="top")))
    + sp(22) + txt("[Two or three sentence summary of the message goes here.]", 17, TGRAY, extra="line-height:1.55;") + sp(24)
    + link_row("Sermon notes (PDF) &rarr;") + sp(10) + link_row("Listen as a podcast &rarr;") + sp(10) + link_row("Share this message &rarr;"))
featured = section(TR(TD(c("YouTube embed: latest sermon (use the full-size iframe)") + feat_embed, valign="top", width="64%", style="width:64%;"), gap_col(40),
                       TD(rounded(feat_side, CREAM, 16, 32, f"border:1px solid {GOLD};"), valign="top")), pad="0 0 0")

def vid(series, title, who):
    inner = (embed("yt", 200, "Sermon video", "16:9", 12) + sp(16) + eyebrow(series, MAROON, 13) + sp(8)
             + title_block(link(txt(title, 22, MAROON, "600", H, "line-height:1.2;"), "#", "")) + sp(8) + txt(who, 15, TGRAY, extra="line-height:1.4;"))
    return flow_card(inner, height=397)
vids = [vid("[Series name]", "[Sermon title one]", "[Pastor name] &middot; [Month 00, 2026]"),
        vid("Sunday Worship", "[Sermon title two]", "[Pastor name] &middot; [Month 00, 2026]"),
        vid("Sunday Worship", "[Sermon title three]", "[Pastor name] &middot; [Month 00, 2026]"),
        vid("Bible Study", "[Sermon title four]", "[Teacher name] &middot; [Month 00, 2026]"),
        vid("[Series name]", "[Sermon title five]", "[Pastor name] &middot; [Month 00, 2026]"),
        vid("Special Service", "[Sermon title six]", "[Pastor name] &middot; [Month 00, 2026]")]
recent = sec(
    c("Filter chips: link each to your CMS category/tag page") + chips(["All", "Sunday Worship", "Bible Study", "Special Services", "Series"]) + sp(40)
    + head_row("Recent messages", link("View all on YouTube &rarr;", "#", f"font-family:{B};font-size:17px;font-weight:bold;color:{MAROON};")) + sp(28)
    + c("Video grid: one YouTube embed per card, newest first; cards re-flow automatically") + flow(vids, "sermon"), pad="72px 0 72px")

def series_card(name, count):
    return card(txt(name, 24, MAROON, "600", H, "line-height:1.2;") + sp(6) + txt(count, 16, TGRAY) + sp(14)
                + link("Watch the series &rarr;", "#", f"font-family:{B};font-size:16px;font-weight:bold;color:{MAROON};"), pad=28, width="32%")
series = sec(h("h2", "Browse by series", 36, MAROON) + sp(28)
                 + grid3([series_card("[Series name one]", "[00] messages"), series_card("[Series name two]", "[00] messages"), series_card("[Series name three]", "[00] messages")]),
                 bg=LGRAY, pad="72px 0 72px")

cta_inner = TR(TD(h("h2", "Join us this Sunday", 44, WHITE) + sp(10)
                  + txt("Worship starts at 9:00 AM at 9258 Center Street, Manassas. We would love to worship with you in person.", 19, CREAM, extra="line-height:1.5;"), valign="middle"),
               gap_col(48), TD(btn("Plan a Visit", "#", GOLD, DARK, 19, "18px 36px"), valign="middle", align="right", style="white-space:nowrap;"))
cta = section(TR(TD(rounded(T(cta_inner), DEEP, 20, "20px"))), pad="72px 0 20px")

hdr = f"""<!-- =====================================================================
  FBC SERMONS PAGE - CMS EMBED MOCKUP
  HOW TO USE: switch the CMS block to Source/HTML view and paste everything below.
  Inline CSS + tables only (no <style> tags). Fonts are Fraunces + Source Sans 3 (falls back to
  Georgia/Arial). If your theme does not already load them, add this to the site <head>:
  https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Source+Sans+3:wght@400;600;700&display=swap
  Site header, breadcrumb and footer come from your CMS template (not included).

  YOUTUBE EMBEDS: on the video choose Share > Embed and copy the iframe. Replace each
  "[YOUTUBE EMBED]" box (the whole <table> inside its cell) with:
    <iframe width="100%" height="500" src="https://www.youtube.com/embed/VIDEO_ID"
      title="Sermon title" frameborder="0" allow="accelerometer; autoplay; clipboard-write;
      encrypted-media; gyroscope; picture-in-picture" allowfullscreen
      style="display:block;border:0;border-radius:16px;"></iframe>
  Use height 500 for the featured player and 200 for the small cards (16:9 only holds
  if width is fixed, so set height to match the column width).
  ADDING A NEW SERMON: copy one whole card (from "SERMON CARD START" to "SERMON CARD END"),
  paste it right under the "NEWEST SERMON FIRST" comment, then change its title, date and video.
  The other cards re-flow on their own. Delete the last card now and then to keep the list short.
  To embed a whole playlist use https://www.youtube.com/embed/videoseries?list=PLAYLIST_ID

{PALETTE}
====================================================================== -->
"""
sermons = page(c("SECTION 1: Header - title, intro, watch/subscribe buttons") + hero
               + c("SECTION 2: Latest sermon - big YouTube player (left) + message details card (right)") + featured
               + c("SECTION 3: Filter chips + recent messages grid (6 YouTube embeds)") + recent
               + c("SECTION 4: Browse by series - 3 cards") + series
               + c("SECTION 5: Call to action - Join us this Sunday") + cta, hdr)
write("sermons", sermons)

# =====================================================================
# PHOTO GALLERY  (matches v3, the version verified in the CMS)
# Edit the data below, then run:  python3 tools/gen_pages.py
# =====================================================================
GALLERY_COVER = "https://fbcmanassas.org/files/PhotographyLogo2-1.jpg"
# Featured album (big Lightroom slideshow). share = the id in the Lightroom embed URL.
FEATURED = dict(title="FBC Day Cruise", date="September 5, 2026", photos=173,
                share="0c3cfd1047b241a8ac602f75972b7bf9", link="https://adobe.ly/4cX63Rn")
# Newest first. Each album becomes one card with its own Lightroom slideshow.
ALBUMS = [
    dict(title="Usher's Anniversary", cats="worship events", date="August 16, 2026", photos=107, share="f3d318fb178f467db2b670183518d86b", link="https://adobe.ly/4hVJePE"),
    dict(title="Youth Splash Down", cats="youth events", date="August 8, 2026", photos=22, share="ebc3219e0c854a44bd3e4fbbfef3c834", link="https://adobe.ly/4hUws3M"),
    dict(title="Youth Spring Fest", cats="youth events", date="May 9, 2026", photos=378, share="4d88c8d2efb04b05867a42c430050b3f", link="https://adobe.ly/4wq3oXI"),
    dict(title="Graduation Service", cats="worship events", date="June 15, 2026", photos=43, share="774e53a174c34868bb45082283f59d01", link="https://adobe.ly/4vC7bBd"),
    dict(title="Youth Christmas Play", cats="youth worship", date="December 2025", photos=120, share="1cbef6d2190e4975aa6f5e3315529b37", link="https://adobe.ly/4psSmwH"),
    dict(title="Missions Feed the Children", cats="missions events", date="September 13, 2025", photos=94, share="ea82b57a566f45d49dad4999c053e932", link="https://adobe.ly/4grGpEO"),
]
FILTER_JS = """<script>
(function () {
  // Written without angle brackets or ampersands so CMS editors cannot HTML-escape them and break the script.
  function each(list, fn) { Array.prototype.forEach.call(list, fn); }
  function paint(a, on) {
    var cell = a.parentNode;
    cell.style.backgroundColor = on ? '#6B1735' : '#F7F3EC';
    cell.style.borderColor = on ? '#6B1735' : '#C9A55C';
    a.style.color = on ? '#ffffff' : '#6B1735';
  }
  function apply(key) {
    var shown = 0;
    each(document.querySelectorAll('table[data-cats]'), function (card) {
      var cats = ' ' + (card.getAttribute('data-cats') || '') + ' ';
      var show = (key === 'all') || (cats.indexOf(' ' + key + ' ') !== -1);
      card.style.display = show ? '' : 'none';
      if (show) { shown += 1; }
    });
    each(document.querySelectorAll('a[data-filter]'), function (a) {
      paint(a, a.getAttribute('data-filter') === key);
    });
    var empty = document.getElementById('fbcNoAlbums');
    if (empty) { empty.style.display = shown ? 'none' : 'block'; }
  }
  // One click listener on the whole page, so it works wherever the CMS places this script.
  document.addEventListener('click', function (e) {
    var chip = e.target.closest ? e.target.closest('a[data-filter]') : null;
    if (!chip) { return; }
    e.preventDefault();
    apply(chip.getAttribute('data-filter'));
    var target = document.getElementById('albums');
    if (target) { if (target.scrollIntoView) { target.scrollIntoView({ behavior: 'smooth', block: 'start' }); } }
  });
})();
</script>"""
def lr(share):
    return f'<iframe src="https://lightroom.adobe.com/embed/shares/{share}/slideshow?background_color=%232D2D2D&amp;color=%23999999"></iframe>'

cover = (f'<img src="{GALLERY_COVER}" alt="Photography ministry logo" width="1500" height="1500" '
         f'style="display:block;margin:0 auto;width:auto;height:auto;max-width:100%;max-height:510px;border:0;">')
cover_cell = T(TR(f'<td align="center" valign="middle" height="510" style="height:510px;text-align:center;">{cover}</td>'),
               width="100%")
g_hero = section(TR(TD(
    eyebrow("Our Church Family", MAROON, 15, "0.16em") + sp(20) + h("h1", "Photo Gallery", 64, MAROON, lh="1.04") + sp(20)
    + txt("Moments from worship, ministry, and community life at First Baptist Church of Manassas.", 21, TGRAY, extra="line-height:1.5;") + sp(28)
    + T(TR(TD(btn("View all albums", "#albums", MAROON, WHITE, 18, "10px 32px"), valign="top"), gap_col(16),
           TD(btn("Contact Us", "#", GOLD, DARK, 18, "10px 32px"), valign="top")), width="auto"),
    valign="middle", width="48%", style="width:48%;"),
    TD(c("IMAGE: cover photo - replace the src with the CMS media URL") + cover_cell, valign="middle", width="52%")), pad="16px 0 0")

feat_head = T(TR(TD(f'<h2 style="margin:0;padding:20px 0 4px 0;font-family:{H};font-size:36px;font-weight:normal;line-height:1.15;color:{MAROON};">Featured Album</h2>', valign="middle"),
                 TD(link("Open full album in Lightroom &rarr;", FEATURED["link"], f"margin:0;padding:0;font-family:{B};font-size:17px;font-weight:bold;color:{MAROON};"),
                    valign="middle", align="right", style="text-align:right;")))
g_feat = sec(c("Filter chips: each has data-filter=KEY; a card shows when its data-cats contains KEY (script at the end of the albums section)") + chips([("All", "all"), ("Worship", "worship"), ("Youth", "youth"), ("Events", "events"), ("Missions", "missions"), ("Baptisms", "baptisms")], ident="fbcFilters")
             + feat_head
             + txt(f'{FEATURED["title"]} &middot; {FEATURED["date"]} &middot; {FEATURED["photos"]} Photos', 17, TGRAY)
             + c("Lightroom embed: featured album (Lightroom > Share > Embed > copy the share id into the src)") + lr(FEATURED["share"]), pad="0")

def album(a):
    inner = (lr(a["share"]) + sp(16)
             + title_block(txt(a["title"], 22, MAROON, "600", H, "line-height:1.2;")) + sp(8)
             + txt(f'{a["date"]} &middot; {a["photos"]} photos', 15, TGRAY) + sp(12)
             + link("View album &rarr;", a["link"], f"font-family:{B};font-size:16px;font-weight:bold;color:{MAROON};"))
    return flow_card(inner, height=347, gap=12, cats=a["cats"])
g_albums = sec(T(TR(TD(h("h2", '<a id="albums" name="albums"></a>Browse Recent Albums', 36, MAROON), valign="middle"), TD("&nbsp;", valign="middle", align="right"))) + sp(12)
               + c("Album grid: newest first; cards re-flow automatically") + flow([album(a) for a in ALBUMS], "album")
               + f'<div id="fbcNoAlbums" style="display:none;padding:24px 12px 36px 12px;font-family:{B};font-size:18px;color:{TGRAY};">No albums in this category yet.</div>'
               + c("Filter script: needs a CMS that keeps <script> tags (no style block or inline handlers needed)") + FILTER_JS, bg=LGRAY, pad="12px 0 0")

g_cta_inner = TR(TD(h("h2", "Were you at an event?", 44, WHITE) + sp(10)
                    + txt("Share your photos with the church family. Email them to the media team and we will add them to the albums.", 19, CREAM, extra="line-height:1.5;"),
                    valign="middle", width="64%"),
                 gap_col(48), TD(btn("Send us your photos", "#", GOLD, DARK, 15, "10px 10px"), valign="middle", align="right"))
g_cta = section(TR(TD(rounded(T(g_cta_inner), DEEP, 20, "20px"))), pad="0")

ghdr = f"""<!-- =====================================================================
  FBC PHOTO GALLERY PAGE - CMS EMBED (matches the CMS-verified v3)
  HOW TO USE: switch the CMS block to Source/HTML view and paste everything below.
  Inline CSS + tables only (no <style> tags). Fonts are Fraunces + Source Sans 3 (falls back to
  Georgia/Arial). If your theme does not already load them, add this to the site <head>:
  https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Source+Sans+3:wght@400;600;700&display=swap
  Site header, breadcrumb and footer come from your CMS template (not included).

  ADDING A NEW ALBUM: copy one whole card (from "ALBUM CARD START" to "ALBUM CARD END"),
  paste it right under the "NEWEST ALBUM FIRST" comment, then change the Lightroom share id in the
  iframe src, the title, the date/photo count and the "View album" link. The other cards re-flow on
  their own. Delete the last card now and then to keep the list short.
  FILTERS: each card carries data-cats="worship events" (space-separated keys). Each chip carries
  data-filter="key"; clicking it shows only cards whose data-cats contains that key ("all" shows everything)
  and scrolls to the albums. To tag a new album, set its data-cats. To add a chip, copy one in the chip row,
  change its label and data-filter, and use that key in the cards. Needs the <script> at the bottom of the
  albums section (it does not use style blocks or onclick attributes, which this CMS strips).
  LIGHTROOM: open the album in Lightroom web, Share > publish, copy the embed code; the long id
  between /embed/shares/ and /slideshow is the share id. Albums must be shared publicly.

{PALETTE}
====================================================================== -->
"""
gallery = page(c("SECTION 1: Header - title, intro, buttons, cover photo (2 columns)") + g_hero
               + c("SECTION 2: Filter chips + featured album (Lightroom slideshow)") + g_feat
               + c("SECTION 3: Browse recent albums - one Lightroom slideshow per card") + g_albums
               + c("SECTION 4: Call to action - send us your photos") + g_cta, ghdr)
write("photo-gallery", gallery)
