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

def chips(items, active=0, ident=None, wrap=False, scroll=False):
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
        if scroll:   # compact, fluid sizing; the first value in each pair is the fallback if clamp() is not supported
            a = (f'<a href="{href}"{attrs} style="text-decoration:none;display:block;white-space:nowrap;padding:10px 16px;padding:10px clamp(12px,2.8vw,22px);'
                 f'font-family:{B};font-size:15px;font-size:clamp(14px,3.6vw,16px);font-weight:bold;color:{col};">{t}</a>')
        else:
            a = (f'<a href="{href}"{attrs} style="text-decoration:none;display:block;white-space:nowrap;padding:10px 22px;'
                 f'font-family:{B};font-size:16px;font-weight:bold;color:{col};">{t}</a>')
        cell = f'<td bgcolor="{bg}" style="background-color:{bg};border:1px solid {bd};border-radius:999px;">{a}</td>'
        if wrap:   # each chip floats, so the row wraps onto more lines on narrow screens
            cells.append(float_item(T(TR(cell), width="auto"), "0 12px 12px 0"))
        else:
            cells.append(cell)
            cells.append(gap_col(8 if scroll else 12))
    if scroll:   # one unbroken row; swipes sideways on phones instead of wrapping
        idattr = f' id="{ident}"' if ident else ""
        return (f'<div{idattr} style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;padding-bottom:12px;">'
                + T(TR(*cells[:-1]), width="auto", style="white-space:nowrap;") + "</div>")
    if wrap:
        return f'<div{(" id=" + chr(34) + ident + chr(34)) if ident else ""}>' + "".join(cells) + CLEAR + "</div>"
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

def flow_card(inner, pad=20, height=400, gap=24, cats=None, eq=False):
    """Self-wrapping card using the legacy HTML attribute align="left" (survives CMS sanitizers that strip
    display / float / margin CSS). Three per row: width 33%; fixed height keeps the rows from snagging.
    gap = vertical space under each card row."""
    dc = (f' data-cats="{cats}"' if cats else "") + (' data-eq="1"' if eq else "")
    return (f'<table role="presentation" align="left" width="33%" cellpadding="0" cellspacing="0" border="0"{dc} style="width:33.333%;min-width:300px;max-width:100%;border-collapse:separate;">'
            f'<tr><td valign="top" height="{height + gap}" style="height:{height + gap}px;padding:0 12px {gap}px 12px;">'
            + rounded(inner, CREAM, 16, pad, f"border:1px solid {GOLD};") + "</td></tr></table>")
def flow(cards, what):
    """Cards wrap into rows on their own: newest goes first, so adding one never means moving the others."""
    body = "".join(f"<!-- {what.upper()} CARD START: copy from here -->\n{cd}\n<!-- {what.upper()} CARD END -->\n" for cd in cards)
    return (f"<!-- NEWEST {what.upper()} FIRST: paste the new card on the line below this one -->\n"
            f"{body}"
            f"<!-- To keep the list short, delete the last card above (the oldest) -->\n"
            '<div style="font-size:0;line-height:0;"><br clear="all" style="clear:both;"></div>\n')

def fl_col(inner, width, min_w, pad="0", td_id=None, tbl_id=None):
    """Left-floating table (HTML align attribute). Two of them sit side by side when there is room; the second drops
    underneath when the container is narrower than their min-widths. No media queries (this CMS strips style blocks)."""
    ti = f' id="{td_id}"' if td_id else ""
    bi = f' id="{tbl_id}"' if tbl_id else ""
    return (f'<table role="presentation" align="left" width="{width}" cellpadding="0" cellspacing="0" border="0"{bi} '
            f'style="width:{width};min-width:{min_w}px;max-width:100%;border-collapse:separate;"><tr><td valign="top"{ti} style="padding:{pad};">{inner}</td></tr></table>')
def fluid_btn(label, href, bg, color, new_tab=False):
    """Pill button whose text and padding shrink on narrow screens (first value of each pair = fallback if clamp() is unsupported)."""
    tgt = ' target="_blank" rel="noopener noreferrer"' if new_tab else ""
    a = (f'<a href="{href}"{tgt} style="text-decoration:none;display:block;white-space:nowrap;padding:10px 16px;padding:10px clamp(16px,1vw + 8px,32px);'
         f'font-family:{B};font-size:15px;font-size:clamp(15px,0.9vw + 6px,18px);font-weight:bold;color:{color};text-align:center;">{label}</a>')
    return T(TR(f'<td align="center" bgcolor="{bg}" style="background-color:{bg};border-radius:999px;">{a}</td>'), width="auto", style="border-radius:999px;")
def button_row(left_btn, right_btn):
    """Two buttons that always stay on one line (a single table row, not floats)."""
    return T(TR(TD(left_btn, valign="top"), gap_col(12), TD(right_btn, valign="top")), width="auto", style="max-width:100%;")
def float_item(inner, pad="0 16px 12px 0"):
    """Shrink-to-fit floating wrapper so buttons wrap onto a new line instead of overflowing."""
    return f'<table role="presentation" align="left" cellpadding="0" cellspacing="0" border="0" style="border-collapse:separate;"><tr><td style="padding:{pad};">{inner}</td></tr></table>'
CLEAR = '<div style="font-size:0;line-height:0;"><br clear="all" style="clear:both;"></div>'
HERO_JS = """<script>
(function () {
  // Vertically centers the header text beside the logo when they sit side by side (floats cannot do this on their own).
  // On narrow screens the logo drops below the text and no extra padding is added.
  function center() {
    var t = document.getElementById('fbcHeroText');
    var l = document.getElementById('fbcHeroLogo');
    if (!t) { return; }
    if (!l) { return; }
    t.style.paddingTop = '0px';
    var tr = t.getBoundingClientRect();
    var lr = l.getBoundingClientRect();
    if (Math.round((lr.top - tr.top) / 5) !== 0) { return; }
    t.style.paddingTop = Math.max(0, Math.round((lr.height - tr.height) / 2)) + 'px';
  }
  center();
  window.addEventListener('load', center);
  window.addEventListener('resize', center);
})();
</script>"""

EQ_JS = """<script>
(function () {
  // Makes every video card exactly as tall as the tallest one, so the float grid never snags when a real
  // YouTube player is a little taller than a placeholder. The fixed heights in the HTML are the fallback.
  function each(list, fn) { Array.prototype.forEach.call(list, fn); }
  function equalize() {
    var cards = document.querySelectorAll('table[data-eq]');
    var best = 0;
    each(cards, function (card) {
      var td = card.getElementsByTagName('td')[0];
      td.style.height = 'auto';
    });
    each(cards, function (card) {
      var td = card.getElementsByTagName('td')[0];
      var inner = td.getElementsByTagName('table')[0];
      best = Math.max(best, Math.ceil(inner.getBoundingClientRect().height));
    });
    each(cards, function (card) {
      var td = card.getElementsByTagName('td')[0];
      var gap = parseFloat(window.getComputedStyle(td).paddingBottom) || 0;
      td.style.height = (best + gap) + 'px';
    });
  }
  equalize();
  window.addEventListener('load', equalize);
  window.addEventListener('resize', equalize);
})();
</script>"""

def head_row(title, right_html="", pad_top=0):
    hd = (h("h2", title, 36, MAROON) if not pad_top else
          f'<h2 style="margin:0;padding:{pad_top}px 0 4px 0;font-family:{H};font-size:36px;font-weight:normal;line-height:1.15;color:{MAROON};">{title}</h2>')
    # right cell: explicit width + three redundant right-alignments (attribute, cell style, inner block) so it holds in any CMS
    right = f'<div style="margin:0;padding:0;text-align:right;">{right_html}</div>' if right_html else ""
    return T(TR(TD(hd, valign="middle", width="55%", style="width:55%;"),
                TD(right, valign="middle", align="right", width="45%", style="width:45%;text-align:right;padding-left:12px;")))

def page(rows, header_comment, font_link=False):
    doc = header_comment + (FONT if font_link else "") + T(rows, width="100%", bg=WHITE, style=f"background-color:{WHITE};font-family:{B};color:{DARK};table-layout:fixed;")
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
import os as _os
SERMONS_LOGO = "https://fbcmanassas.org/wp-content/uploads/SermonsLogo-Background-Removed.png"
YT_STREAMS = "https://www.youtube.com/@fbcmanassas5180/streams"   # live and past streams
PLAN_A_VISIT = "https://fbcmanassas.org/about/times/"
sermons_cover = (f'<img src="{SERMONS_LOGO}" alt="First Baptist Church of Manassas Sermons, Media and Archives" width="700" height="700" '
                 f'style="display:block;margin:0 auto;width:100%;max-width:700px;height:auto;aspect-ratio:1/1;object-fit:cover;object-position:center;transform:scale(1.1);transform-origin:center;border:0;">')
hero_s_text = (eyebrow("Watch & Listen", MAROON, 15, "0.16em") + sp(12) + h("h1", "Sermons", 64, MAROON, lh="1.04") + sp(12)
               + txt("Watch live on Sundays at 9:00 AM, or catch up on any message from our pulpit, anytime and on any device.", 21, TGRAY, extra="line-height:1.5;") + sp(20)
               + fluid_btn("Watch Live", YT_STREAMS, MAROON, WHITE, new_tab=True))
hero = section(TR(TD(
    fl_col(hero_s_text, "42%", 320, "0", td_id="fbcHeroText")
    + c("IMAGE: Sermons logo - replace the src with the CMS media URL")
    + fl_col(f'<div style="text-align:center;overflow:hidden;">{sermons_cover}</div>', "58%", 260, "0 0 0 24px", tbl_id="fbcHeroLogo")
    + CLEAR + c("Script: centers the header text beside the logo on wide screens (optional; harmless if blocked)") + HERO_JS)), pad="0")

# Latest sermon. Edit this block each week. Anything still in [brackets] is a placeholder for you to fill in.
LATEST = dict(video_id="sjCGtIPS8AU", video_title="154th Church Anniversary, October 11, 2026",
              title="154th Church Anniversary", pastor="[Pastor name]", date="October 11, 2026",
              series="[Series name]", scripture="[Book 0:00-00]",
              summary="[Two or three sentence summary of the message goes here.]")
feat_embed = (f'<iframe width="979" height="551" src="https://www.youtube.com/embed/{LATEST["video_id"]}" title="{LATEST["video_title"]}" frameborder="0" '
              'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
              'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen '
              'style="display:block;width:100%;height:auto;aspect-ratio:16/9;border:0;border-radius:16px;"></iframe>')
def link_row(t): return link(t, "#", f"font-family:{B};font-size:17px;font-weight:600;color:{MAROON};")
feat_side = (eyebrow("Latest message") + sp(10) + h("h2", LATEST["title"], 32, MAROON, "600", "1.15") + sp(8)
    + txt(LATEST["pastor"] + " &middot; " + LATEST["date"], 17, TGRAY) + sp(12)
    + T(TR(TD(txt("SERIES", 12, MAROON, "bold", extra="letter-spacing:0.14em;"), width="110", valign="top") , TD(txt(LATEST["series"], 17, DARK, "600"), valign="top")) + gap_row(6, 2)
        + TR(TD(txt("SCRIPTURE", 12, MAROON, "bold", extra="letter-spacing:0.14em;"), width="110", valign="top"), TD(txt(LATEST["scripture"], 17, DARK, "600"), valign="top")))
    + sp(14) + txt(LATEST["summary"], 17, TGRAY, extra="line-height:1.5;") + sp(14)
    + link_row("Sermon notes (PDF) &rarr;"))
featured = section(TR(TD(
    c("YouTube embed: latest sermon. To change it, replace the video id in the iframe src and the title") + fl_col(feat_embed, "62%", 340, "0 12px 4px 0")
    + fl_col(rounded(feat_side, CREAM, 16, 24, f"border:1px solid {GOLD};"), "38%", 300, "0 0 4px 12px")
    + CLEAR)), pad="0")

def yt_placeholder(radius=12):
    """Stand-in for a YouTube player: always 16:9 like the real iframe, so placeholder and real cards are the same size at any width."""
    play = (f'<div style="width:56px;height:56px;margin:0 auto 10px auto;border-radius:50%;background-color:{GOLD};color:{DARK};'
            f'font-size:22px;line-height:56px;text-align:center;">&#9654;</div>')
    label = (f'<div style="font-family:{B};font-size:14px;font-weight:600;color:{WHITE};line-height:1.3;">[YOUTUBE EMBED]</div>'
             f'<div style="font-family:{B};font-size:12px;color:{CREAM};line-height:1.4;padding-top:2px;">paste the iframe here</div>')
    return (f'<div style="position:relative;width:100%;aspect-ratio:16/9;box-sizing:border-box;background-color:{DEEP};border:2px dashed {GOLD};border-radius:{radius}px;">'
            f'<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:90%;text-align:center;">{play}{label}</div></div>')
def yt_card_embed(video_id, title_attr, w=971, h_=546, start=None):
    """Real YouTube player for a video card: fluid, always 16:9 (attributes are the fallback if the style is stripped)."""
    qs = f"?start={start}" if start else ""
    return (f'<iframe width="{w}" height="{h_}" src="https://www.youtube.com/embed/{video_id}{qs}" title="{title_attr}" frameborder="0" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen '
            'style="display:block;width:100%;height:auto;aspect-ratio:16/9;border:0;border-radius:12px;"></iframe>')
def vid(series, title, who, player=None):
    inner = ((player or yt_placeholder()) + sp(12) + eyebrow(series, MAROON, 13) + sp(6)
             + title_block(link(txt(title, 22, MAROON, "600", H, "line-height:1.2;"), "#", "")) + sp(4) + txt(who, 15, TGRAY, extra="line-height:1.4;"))
    return flow_card(inner, pad=16, height=346, gap=8, eq=True)
# Recent messages, newest first. Each tuple: (category tag, card title, pastor, date, YouTube id, iframe title).
# Titles and dates come from each video's own YouTube title; pastor is a placeholder until you fill it in.
SERMONS = [
    ("[Series name]",   "Women's Day",       "October 4, 2026",   "kWJuPjSuThk", "Women&#39;s Day, October 4, 2026"),
    ("Sunday Worship",  "4th Sunday",        "September 27, 2026", "tU35vDOLQPg", "4th Sunday, September 27, 2026"),
    ("Sunday Worship",  "3rd Sunday",        "September 20, 2026", "o8ufjlde2J0", "3rd Sunday, September 20, 2026"),
    ("Sunday Worship",  "2nd Sunday",        "September 13, 2026", "FyupYxk9vFs", "2nd Sunday, September 13, 2026"),
    ("Sunday Worship",  "1st Sunday",        "September 6, 2026",  "J1bDxhWXn7w", "1st Sunday, September 6, 2026"),
    ("Sunday Worship",  "5th Sunday",        "August 30, 2026",    "FeZDPJYwOHw", "5th Sunday, August 30, 2026"),
    ("Sunday Worship",  "4th Sunday",        "August 23, 2026",    "ciLDidOW6IY", "4th Sunday, August 23, 2026"),
    ("Special Service", "57th Annual Ushers Day Celebration", "August 16, 2026", "bzloOxNOQmU", "57th Annual Ushers Day Celebration - Sunday, August 16, 2026"),
]
vids = [vid(tag, title, "[Pastor name] &middot; " + date, player=yt_card_embed(vid_id, title_attr)) for tag, title, date, vid_id, title_attr in SERMONS]
# Remaining slot(s) stay as placeholders until there is another video to add.
vids += [vid("Sunday Worship", "[Sermon title nine]", "[Pastor name] &middot; [Month 00, 2026]")]

recent = sec(
    c("Filter chips: link each to your CMS category/tag page; one row, swipes sideways on narrow screens")
    + chips(["All", "Sunday Worship", "Special Services"], scroll=True)
    + head_row("Recent messages", link("View all on YouTube &rarr;", YT_STREAMS, f"font-family:{B};font-size:17px;font-weight:bold;color:{MAROON};", ' target="_blank" rel="noopener noreferrer"'), pad_top=2) + sp(8)
    + c("Video grid: one YouTube embed per card, newest first; cards re-flow automatically") + flow(vids, "sermon") + c("Script: equalizes the video card heights (optional; the fixed heights are the fallback)") + EQ_JS, pad="0")

cta_s_text = (h("h2", "Join us this Sunday", 40, WHITE) + sp(8)
              + txt("Worship starts at 9:00 AM at 9258 Center Street, Manassas. We would love to worship with you in person.", 19, CREAM, extra="line-height:1.5;"))
cta_s_inner = (fl_col(cta_s_text, "66%", 240, "0 24px 0 0") + fl_col(btn("Plan a Visit", PLAN_A_VISIT, GOLD, DARK, 18, "14px 32px"), "34%", 220, "14px 0 0 0") + CLEAR)
cta = section(TR(TD(c("Call to action: text and button sit side by side on wide screens and stack on phones")
                    + rounded(cta_s_inner, DEEP, 20, "22px 24px"))), pad="0")

hdr = f"""<!-- =====================================================================
  FBC SERMONS PAGE - CMS EMBED MOCKUP
  HOW TO USE: switch the CMS block to Source/HTML view and paste everything below.
  Inline CSS + tables only (no <style> tags). Fonts are Fraunces + Source Sans 3 (falls back to
  Georgia/Arial). If your theme does not already load them, add this to the site <head>:
  https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Source+Sans+3:wght@400;600;700&display=swap
  Site header, breadcrumb and footer come from your CMS template (not included).

  LOGO: loaded from the CMS (SERMONS_LOGO in tools/gen_pages.py). The src is the full-size PNG; it scales down to fit.
  LINKS: "Watch Live" and "View all on YouTube" open the YouTube streams page in a new tab (YT_STREAMS in
  tools/gen_pages.py). "Plan a Visit" goes to PLAN_A_VISIT.

  YOUTUBE EMBEDS: on the video choose Share > Embed and copy the iframe. Replace each
  "[YOUTUBE EMBED]" box (the whole <table> inside its cell) with:
    <iframe width="100%" height="420" src="https://www.youtube.com/embed/VIDEO_ID"
      title="Sermon title" frameborder="0" allow="accelerometer; autoplay; clipboard-write;
      encrypted-media; gyroscope; picture-in-picture" allowfullscreen
      style="display:block;width:100%;height:auto;aspect-ratio:16/9;border:0;border-radius:16px;"></iframe>
  The aspect-ratio style keeps the player 16:9 at any width (phone or desktop). If your CMS strips it,
  the height attribute (420 for the featured player, 200 for the small cards) is used instead.
  ADDING A NEW SERMON: copy one whole card (from "SERMON CARD START" to "SERMON CARD END"),
  paste it right under the "NEWEST SERMON FIRST" comment, then change its title, date and video.
  The other cards re-flow on their own. Delete the last card now and then to keep the list short.
  To embed a whole playlist use https://www.youtube.com/embed/videoseries?list=PLAYLIST_ID

{PALETTE}
====================================================================== -->
"""
sermons = page(c("SECTION 1: Header - title, intro, watch/subscribe buttons") + hero
               + c("SECTION 2: Latest sermon - big YouTube player (left) + message details card (right)") + featured
               + c("SECTION 3: Filter chips + recent messages grid (9 YouTube embeds)") + recent
               + c("SECTION 4: Call to action - Join us this Sunday") + cta, hdr)
write("sermons", sermons)

# =====================================================================
# PHOTO GALLERY  (matches v3, the version verified in the CMS)
# Edit the data below, then run:  python3 tools/gen_pages.py
# =====================================================================
GALLERY_COVER = "https://fbcmanassas.org/files/PhotographyLogo2-1.jpg"
PORTFOLIO_URL = "https://fbcphotography.myportfolio.com/home"
PHOTO_EMAIL = "fbcphotodirectory@gmail.com"
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
    // The message is an empty element in the page and is only filled in (and styled) here when nothing matches.
    var empty = document.getElementById('fbcNoAlbums');
    if (empty) {
      empty.textContent = shown ? '' : 'No albums in this category yet.';
      empty.style.cssText = shown ? '' : 'padding:24px 12px 36px 12px;font-family:Arial,Helvetica,sans-serif;font-size:18px;color:#666666;';
    }
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
    return f'<iframe src="https://lightroom.adobe.com/embed/shares/{share}/slideshow?background_color=%232D2D2D&amp;color=%23999999" style="max-width:100%;"></iframe>'



cover = (f'<img src="{GALLERY_COVER}" alt="Photography ministry logo" width="1500" height="1500" '
         f'style="display:block;margin:0 auto;width:auto;height:auto;max-width:100%;max-height:510px;border:0;">')
hero_text = (eyebrow("Our Church Family", MAROON, 15, "0.16em") + sp(20) + h("h1", "Photo Gallery", 64, MAROON, lh="1.04") + sp(20)
             + txt("Moments from worship, ministry, and community life at First Baptist Church of Manassas.", 21, TGRAY, extra="line-height:1.5;") + sp(28)
             + button_row(fluid_btn("View Full Portfolio", PORTFOLIO_URL, MAROON, WHITE, new_tab=True),
                          fluid_btn("Contact Us", "mailto:" + PHOTO_EMAIL, GOLD, DARK)))
g_hero = section(TR(TD(
    fl_col(hero_text, "48%", 320, "0", td_id="fbcHeroText")
    + c("IMAGE: cover photo - replace the src with the CMS media URL")
    + fl_col(f'<div style="text-align:center;">{cover}</div>', "52%", 260, "0 0 0 24px", tbl_id="fbcHeroLogo")
    + CLEAR + c("Script: centers the header text beside the logo on wide screens (optional; harmless if blocked)") + HERO_JS)), pad="16px 0 0")

feat_head = T(TR(TD(f'<h2 style="margin:0;padding:8px 0 4px 0;font-family:{H};font-size:36px;font-weight:normal;line-height:1.15;color:{MAROON};">Featured Album</h2>', valign="middle"),
                 TD(link("Open full album &rarr;", FEATURED["link"], f"margin:0;padding:0;font-family:{B};font-size:17px;font-weight:bold;color:{MAROON};"),
                    valign="middle", align="right", style="text-align:right;")))
g_feat = sec(c("Filter chips: each has data-filter=KEY; a card shows when its data-cats contains KEY (script at the end of the albums section)") + chips([("All", "all"), ("Worship", "worship"), ("Youth", "youth"), ("Events", "events"), ("Missions", "missions"), ("Baptisms", "baptisms")], ident="fbcFilters", scroll=True)
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
               + '<div id="fbcNoAlbums"></div>'
               + c("Filter script: needs a CMS that keeps <script> tags (no style block or inline handlers needed)") + FILTER_JS, bg=LGRAY, pad="12px 0 0")

cta_col = fl_col
cta_text = (h("h2", "Were you at an event?", 40, WHITE) + sp(12)
            + txt("Share your photos with the church family. Email them to the media team and we&rsquo;ll add them to the albums.", 19, CREAM, extra="line-height:1.5;"))
cta_removal = (f'<div style="margin:0;font-family:{B};font-size:14px;color:{CREAM};line-height:1.5;">Want a photo of you or your child removed? Please '
               + link("reach out to the media team", "mailto:" + PHOTO_EMAIL + "?subject=Photo%20removal%20request", f"color:{GOLD};font-weight:bold;text-decoration:underline;")
               + " and we will take it down right away.</div>")
g_cta_inner = (cta_col(cta_text, "66%", 240, "0 24px 0 0")
               + cta_col(btn("Send us your photos", "mailto:" + PHOTO_EMAIL + "?subject=Photos%20for%20the%20FBC%20gallery", GOLD, DARK, 18, "14px 32px"), "34%", 220, "20px 0 0 0")
               + '<div style="font-size:0;line-height:0;"><br clear="all" style="clear:both;"></div>'
               + sp(16) + cta_removal)
g_cta = section(TR(TD(c("Call to action: text and button sit side by side on wide screens and stack on phones (floating tables with a minimum width)")
                      + rounded(g_cta_inner, DEEP, 20, "28px 24px"))), pad="0")

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
