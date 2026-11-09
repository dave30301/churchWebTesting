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

def chips(items, active=0, ident=None, wrap=False, scroll=False, target="#albums"):
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
        href = target if key else "#"
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

def flow_card(inner, pad=20, height=400, gap=24, cats=None, eq=False, item=""):
    """Self-wrapping card using the legacy HTML attribute align="left" (survives CMS sanitizers that strip
    display / float / margin CSS). Three per row: width 33%; fixed height keeps the rows from snagging.
    gap = vertical space under each card row."""
    dc = (f' data-cats="{cats}"' if cats else "") + (' data-eq="1"' if eq else "") + item
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

def fl_col(inner, width, min_w, pad="0", td_id=None, tbl_id=None, align="left"):
    """Left-floating table (HTML align attribute). Two of them sit side by side when there is room; the second drops
    underneath when the container is narrower than their min-widths. No media queries (this CMS strips style blocks)."""
    ti = f' id="{td_id}"' if td_id else ""
    bi = f' id="{tbl_id}"' if tbl_id else ""
    return (f'<table role="presentation" align="{align}" width="{width}" cellpadding="0" cellspacing="0" border="0"{bi} '
            f'style="width:{width};min-width:{min_w}px;max-width:100%;border-collapse:separate;"><tr><td valign="top"{ti} style="padding:{pad};">{inner}</td></tr></table>')
def fluid_btn(label, href, bg, color, new_tab=False, fbl=None, fbh=None):
    """Pill button whose text and padding shrink on narrow screens (first value of each pair = fallback if clamp() is unsupported)."""
    tgt = (' target="_blank" rel="noopener noreferrer"' if new_tab else "") + (F(fbl) if fbl else "") + (FH(fbh) if fbh else "")
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
  // Header layout: text on the left, logo on the right, with the text centered beside the logo (floats cannot do this alone).
  // When the screen is too narrow for them to sit side by side (phones), the logo is moved ABOVE the text and stretched
  // to the full width. Both are plain left floats; no right float and no media queries.
  var l = document.getElementById('fbcHeroLogo');
  var t = document.getElementById('fbcHeroText');
  if (!l) { return; }
  if (!t) { return; }
  var tt = t;
  while (tt) {
    if (tt.tagName === 'TABLE') { break; }
    tt = tt.parentNode;
  }
  if (!tt) { return; }
  var c = l.getElementsByTagName('td')[0];
  var w0 = l.style.width;
  var p0 = c.style.padding;
  function center() {
    var par = tt.parentNode;
    par.insertBefore(tt, l);
    l.style.width = w0;
    c.style.padding = p0;
    t.style.paddingTop = '0px';
    var tr = tt.getBoundingClientRect();
    var lr = l.getBoundingClientRect();
    var gap = lr.top - (tr.top + tr.height - 5);
    if (Math.max(gap, 0) === gap) {
      par.insertBefore(l, tt);
      l.style.width = '100%';
      c.style.padding = '0px';
      return;
    }
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

MAIL_JS = """<script>
(function () {
  // Email links: instead of opening a mail app, a click copies the address and shows it in place of the link text.
  // Without this script the links still work as normal mailto links. Written without angle brackets or ampersands.
  function copy(text, done) {
    var ok = false;
    try {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.top = '0px';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      ok = document.execCommand('copy');
      document.body.removeChild(ta);
    } catch (e) { ok = false; }
    if (ok) { done(true); return; }
    try {
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(false); });
        return;
      }
    } catch (e2) { }
    done(false);
  }
  document.addEventListener('click', function (ev) {
    var a = ev.target;
    while (a) {
      if (a.tagName === 'A') { break; }
      a = a.parentNode;
    }
    if (!a) { return; }
    var href = a.getAttribute('href') || '';
    if (href.toLowerCase().indexOf('mailto:') !== 0) { return; }
    ev.preventDefault();
    ev.stopPropagation();
    var addr = href.slice(7).split('?')[0];
    if (a.getAttribute('data-orig') === null) { a.setAttribute('data-orig', a.innerHTML); }
    var orig = a.getAttribute('data-orig');
    copy(addr, function (ok) {
      a.style.whiteSpace = 'normal';
      if (Math.min(window.innerWidth, 559) === window.innerWidth) { a.style.maxWidth = '150px'; a.style.wordBreak = 'break-all'; a.style.fontSize = '13px'; }
      a.textContent = (ok ? 'Copied: ' : 'Email us at ') + addr;
      clearTimeout(a.fbcTimer);
      a.fbcTimer = setTimeout(function () { a.innerHTML = orig; a.style.whiteSpace = ''; a.style.maxWidth = ''; a.style.wordBreak = ''; a.style.fontSize = ''; }, 8000);
    });
  }, true);
})();
</script>"""

_FILTER_TEMPLATE = """<script>
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
    var empty = document.getElementById('@EMPTY@');
    if (empty) {
      empty.textContent = shown ? '' : '@MESSAGE@';
      empty.style.cssText = shown ? '' : 'padding:24px 12px 36px 12px;font-family:Arial,Helvetica,sans-serif;font-size:18px;color:#666666;';
    }
  }
  // One click listener on the whole page, so it works wherever the CMS places this script. It runs in the capture
  // phase and stops the event, so a theme script that handles links starting with # cannot jump the page to the top.
  document.addEventListener('click', function (e) {
    var chip = e.target.closest ? e.target.closest('a[data-filter]') : null;
    if (!chip) { return; }
    e.preventDefault();
    e.stopPropagation();
    apply(chip.getAttribute('data-filter'));
    var target = document.getElementById('@TARGET@');
    if (target) { if (target.scrollIntoView) { target.scrollIntoView({ behavior: 'smooth', block: 'start' }); } }
  }, true);
})();
</script>"""
def filter_js(empty_id, target_id, message):
    """Chip filter script. Cards carry data-cats, chips carry data-filter; the empty-state message is created by the script
    (this CMS strips display:none, so it is not hidden in the markup)."""
    return _FILTER_TEMPLATE.replace("@EMPTY@", empty_id).replace("@TARGET@", target_id).replace("@MESSAGE@", message)
FILTER_JS = filter_js("fbcNoAlbums", "albums", "No albums in this category yet.")
SERMON_FILTER_JS = filter_js("fbcNoSermons", "fbcSermonFilters", "No messages in this category yet.")

def head_row(title, right_html="", pad_top=0):
    hd = (h("h2", title, 36, MAROON) if not pad_top else
          f'<h2 style="margin:0;padding:{pad_top}px 0 4px 0;font-family:{H};font-size:36px;font-weight:normal;line-height:1.15;color:{MAROON};">{title}</h2>')
    # right cell: explicit width + three redundant right-alignments (attribute, cell style, inner block) so it holds in any CMS
    right = f'<div style="margin:0;padding:0;text-align:right;">{right_html}</div>' if right_html else ""
    return T(TR(TD(hd, valign="middle", width="55%", style="width:55%;"),
                TD(right, valign="middle", align="right", width="45%", style="width:45%;text-align:right;padding-left:12px;")))

def page(rows, header_comment, font_link=False, key=""):
    doc = header_comment + (FONT if font_link else "") + T(rows, width="100%", bg=WHITE, style=f"background-color:{WHITE};font-family:{B};color:{DARK};table-layout:fixed;", extra=f' data-fbc-page="{key}"')
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
sermons_cover = (f'<img src="{SERMONS_LOGO}"{FI("hero.logo")} alt="First Baptist Church of Manassas Sermons, Media and Archives" width="700" height="700" '
                 f'style="display:block;margin:0 auto;width:100%;max-width:700px;height:auto;aspect-ratio:1/1;object-fit:cover;object-position:center;transform:scale(1.1);transform-origin:center;border:0;">')
hero_s_text = (eyebrow("Watch & Listen", MAROON, 15, "0.16em") + sp(12) + h("h1", "Sermons", 64, MAROON, lh="1.04") + sp(12)
               + txt("Watch live on Sundays at 9:00 AM, or catch up on any message from our pulpit, anytime and on any device.", 21, TGRAY, extra="line-height:1.5;", fb=F("hero.intro", long=True)) + sp(20)
               + fluid_btn("Watch Live", YT_STREAMS, MAROON, WHITE, new_tab=True, fbl="hero.watch", fbh="hero.watch_url"))
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
feat_embed = (f'<iframe width="979" height="551" src="https://www.youtube.com/embed/{LATEST["video_id"]}" title="{LATEST["video_title"]}"{FV("latest.video")} frameborder="0" '
              'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
              'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen '
              'style="display:block;width:100%;height:auto;aspect-ratio:16/9;border:0;border-radius:16px;"></iframe>')
def link_row(t, attrs=""): return link(t, "#", f"font-family:{B};font-size:17px;font-weight:600;color:{MAROON};", attrs)
feat_side = (eyebrow("Latest message") + sp(10) + h("h2", LATEST["title"], 32, MAROON, "600", "1.15", fb=F("latest.title")) + sp(8)
    + txt(SPANS([("latest.pastor", LATEST["pastor"]), ("latest.date", LATEST["date"])]), 17, TGRAY) + sp(12)
    + T(TR(TD(txt("SERIES", 12, MAROON, "bold", extra="letter-spacing:0.14em;"), width="110", valign="top") , TD(txt(LATEST["series"], 17, DARK, "600", fb=F("latest.series")), valign="top")) + gap_row(6, 2)
        + TR(TD(txt("SCRIPTURE", 12, MAROON, "bold", extra="letter-spacing:0.14em;"), width="110", valign="top"), TD(txt(LATEST["scripture"], 17, DARK, "600", fb=F("latest.scripture")), valign="top")))
    + sp(14) + txt(LATEST["summary"], 17, TGRAY, extra="line-height:1.5;", fb=F("latest.summary", long=True)) + sp(14)
    + link_row("Sermon notes (PDF) &rarr;", F("latest.notes") + FH("latest.notes_url")))
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
    return (f'<iframe width="{w}" height="{h_}" src="https://www.youtube.com/embed/{video_id}{qs}" title="{title_attr}"{FV("video")} frameborder="0" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen '
            'style="display:block;width:100%;height:auto;aspect-ratio:16/9;border:0;border-radius:12px;"></iframe>')
def vid(series, title, pastor, date, player=None, cats=None):
    inner = ((player or yt_placeholder()) + sp(12) + eyebrow(series, MAROON, 13, fb=F("tag", upper=True)) + sp(6)
             + title_block(link(txt(title, 22, MAROON, "600", H, "line-height:1.2;", fb=F("title")), "#", "")) + sp(4)
             + txt(SPANS([("pastor", pastor), ("date", date)]), 15, TGRAY, extra="line-height:1.4;"))
    return flow_card(inner, pad=16, height=346, gap=8, cats=cats, eq=True, item=FITEM("sermons"))
# Recent messages, newest first. Each tuple: (category tag, card title, pastor, date, YouTube id, iframe title).
# Titles and dates come from each video's own YouTube title; pastor is a placeholder until you fill it in.
SERMONS = [
    ("Special Service", "Women's Day",       "October 4, 2026",   "kWJuPjSuThk", "Women&#39;s Day, October 4, 2026"),
    ("Sunday Worship",  "4th Sunday",        "September 27, 2026", "tU35vDOLQPg", "4th Sunday, September 27, 2026"),
    ("Sunday Worship",  "3rd Sunday",        "September 20, 2026", "o8ufjlde2J0", "3rd Sunday, September 20, 2026"),
    ("Sunday Worship",  "2nd Sunday",        "September 13, 2026", "FyupYxk9vFs", "2nd Sunday, September 13, 2026"),
    ("Sunday Worship",  "1st Sunday",        "September 6, 2026",  "J1bDxhWXn7w", "1st Sunday, September 6, 2026"),
    ("Sunday Worship",  "5th Sunday",        "August 30, 2026",    "FeZDPJYwOHw", "5th Sunday, August 30, 2026"),
    ("Sunday Worship",  "4th Sunday",        "August 23, 2026",    "ciLDidOW6IY", "4th Sunday, August 23, 2026"),
    ("Special Service", "57th Annual Ushers Day Celebration", "August 16, 2026", "bzloOxNOQmU", "57th Annual Ushers Day Celebration - Sunday, August 16, 2026"),
    ("Sunday Worship",  "3rd Sunday",        "August 16, 2026",    "vA_zMAKdSHQ", "3rd Sunday, August 16, 2026"),
]
# Category keys match the chips: sunday = Sunday Worship, special = Special Services. A card can list several, e.g. "sunday special".
def sermon_cats(tag): return "special" if "special" in tag.lower() else "sunday"
vids = [vid(tag, title, "[Pastor name]", date, player=yt_card_embed(vid_id, title_attr), cats=sermon_cats(tag)) for tag, title, date, vid_id, title_attr in SERMONS]

recent = sec(
    c("Filter chips: each has data-filter=KEY; a card shows when its data-cats contains KEY (script at the end of this section); one row, swipes sideways on narrow screens")
    + chips([("All", "all"), ("Sunday Worship", "sunday"), ("Special Services", "special")], ident="fbcSermonFilters", scroll=True, target="#fbcSermonFilters")
    + head_row("Recent messages", link("View all on YouTube &rarr;", YT_STREAMS, f"font-family:{B};font-size:17px;font-weight:bold;color:{MAROON};", ' target="_blank" rel="noopener noreferrer"' + FH("recent.view_all_url")), pad_top=2) + sp(8)
    + c("Video grid: one YouTube embed per card, newest first; cards re-flow automatically") + flow(vids, "sermon")
    + '<div id="fbcNoSermons"></div>'
    + c("Script: equalizes the video card heights (optional; the fixed heights are the fallback)") + EQ_JS
    + c("Filter script: needs a CMS that keeps <script> tags (no style block or inline handlers needed)") + SERMON_FILTER_JS, pad="0")

cta_s_text = (h("h2", "Join us this Sunday", 40, WHITE, fb=F("cta.heading")) + sp(8)
              + txt("Worship starts at 9:00 AM at 9258 Center Street, Manassas. We would love to worship with you in person.", 19, CREAM, extra="line-height:1.5;", fb=F("cta.text", long=True)))
cta_s_inner = (fl_col(cta_s_text, "66%", 240, "0 24px 0 0") + fl_col(btn("Plan a Visit", PLAN_A_VISIT, GOLD, DARK, 18, "14px 32px", fbl="cta.button", fbh="cta.button_url"), "34%", 220, "14px 0 0 0") + CLEAR)
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
               + c("SECTION 4: Call to action - Join us this Sunday") + cta, hdr, key="sermons")
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



def lr(share, fb=""):
    return f'<iframe src="https://lightroom.adobe.com/embed/shares/{share}/slideshow?background_color=%232D2D2D&amp;color=%23999999"{fb} style="max-width:100%;"></iframe>'



cover = (f'<img src="{GALLERY_COVER}"{FI("hero.cover")} alt="Photography ministry logo" width="1500" height="1500" '
         f'style="display:block;margin:0 auto;width:auto;height:auto;max-width:100%;max-height:510px;border:0;">')
hero_text = (eyebrow("Our Church Family", MAROON, 15, "0.16em") + sp(20) + h("h1", "Photo Gallery", 64, MAROON, lh="1.04") + sp(20)
             + txt("Moments from worship, ministry, and community life at First Baptist Church of Manassas.", 21, TGRAY, extra="line-height:1.5;", fb=F("hero.intro", long=True)) + sp(28)
             + button_row(fluid_btn("View Full Portfolio", PORTFOLIO_URL, MAROON, WHITE, new_tab=True, fbl="hero.portfolio", fbh="hero.portfolio_url"),
                          fluid_btn("Contact Us", "mailto:" + PHOTO_EMAIL, GOLD, DARK, fbl="hero.contact", fbh="hero.contact_url")))
g_hero = section(TR(TD(
    fl_col(hero_text, "48%", 320, "0", td_id="fbcHeroText")
    + c("IMAGE: cover photo - replace the src with the CMS media URL")
    + fl_col(f'<div style="text-align:center;">{cover}</div>', "52%", 260, "0 0 0 24px", tbl_id="fbcHeroLogo")
    + CLEAR + c("Script: centers the header text beside the logo on wide screens (optional; harmless if blocked)") + HERO_JS)), pad="16px 0 0")

feat_head = T(TR(TD(f'<h2 style="margin:0;padding:8px 0 4px 0;font-family:{H};font-size:36px;font-weight:normal;line-height:1.15;color:{MAROON};">Featured Album</h2>', valign="middle"),
                 TD(link("Open full album &rarr;", FEATURED["link"], f"margin:0;padding:0;font-family:{B};font-size:17px;font-weight:bold;color:{MAROON};", FH("featured.link")),
                    valign="middle", align="right", style="text-align:right;")))
g_feat = sec(c("Filter chips: each has data-filter=KEY; a card shows when its data-cats contains KEY (script at the end of the albums section)") + chips([("All", "all"), ("Worship", "worship"), ("Youth", "youth"), ("Events", "events"), ("Missions", "missions"), ("Baptisms", "baptisms")], ident="fbcFilters", scroll=True)
             + feat_head
             + txt(SPANS([("featured.title", FEATURED["title"]), ("featured.date", FEATURED["date"]), f'<span{F("featured.photos")}>{FEATURED["photos"]}</span> Photos']), 17, TGRAY)
             + c("Lightroom embed: featured album (Lightroom > Share > Embed > copy the share id into the src)") + lr(FEATURED["share"], FL("featured.embed")), pad="0")

def album(a):
    inner = (lr(a["share"], FL("embed")) + sp(16)
             + title_block(txt(a["title"], 22, MAROON, "600", H, "line-height:1.2;", fb=F("title"))) + sp(8)
             + txt(SPANS([("date", a["date"]), f'<span{F("photos")}>{a["photos"]}</span> photos']), 15, TGRAY) + sp(12)
             + link("View album &rarr;", a["link"], f"font-family:{B};font-size:16px;font-weight:bold;color:{MAROON};", FH("link")))
    return flow_card(inner, height=347, gap=12, cats=a["cats"], item=FITEM("albums"))
g_albums = sec(T(TR(TD(h("h2", '<a id="albums" name="albums"></a>Browse Recent Albums', 36, MAROON), valign="middle"), TD("&nbsp;", valign="middle", align="right"))) + sp(12)
               + c("Album grid: newest first; cards re-flow automatically") + flow([album(a) for a in ALBUMS], "album")
               + '<div id="fbcNoAlbums"></div>'
               + c("Email script: clicking an email link copies the address and shows it (optional; without it the links open the mail app)") + MAIL_JS
    + c("Filter script: needs a CMS that keeps <script> tags (no style block or inline handlers needed)") + FILTER_JS, bg=LGRAY, pad="12px 0 0")

cta_col = fl_col
cta_text = (h("h2", "Were you at an event?", 40, WHITE, fb=F("cta.heading")) + sp(12)
            + txt("Share your photos with the church family. Email them to the media team and we&rsquo;ll add them to the albums.", 19, CREAM, extra="line-height:1.5;", fb=F("cta.text", long=True)))
cta_removal = (f'<div style="margin:0;font-family:{B};font-size:14px;color:{CREAM};line-height:1.5;">Want a photo of you or your child removed? Please '
               + link("reach out to the media team", "mailto:" + PHOTO_EMAIL + "?subject=Photo%20removal%20request", f"color:{GOLD};font-weight:bold;text-decoration:underline;", FH("cta.removal_url"))
               + " and we will take it down right away.</div>")
g_cta_inner = (cta_col(cta_text, "66%", 240, "0 24px 0 0")
               + cta_col(btn("Send us your photos", "mailto:" + PHOTO_EMAIL + "?subject=Photos%20for%20the%20FBC%20gallery", GOLD, DARK, 18, "14px 32px", fbl="cta.button", fbh="cta.button_url"), "34%", 220, "20px 0 0 0")
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
               + c("SECTION 4: Call to action - send us your photos") + g_cta, ghdr, key="gallery")
write("photo-gallery", gallery)

# =====================================================================
# FORMS
# Edit FORM_SECTIONS below, then run:  python3 tools/gen_pages.py
# Every link is a "#" PLACEHOLDER until you set the real PDF / online form address.
# =====================================================================
OFFICE_EMAIL = "[office@fbcmanassas.org]"
# (section heading, [ (icon entity, title, description, keywords for search, button text, link) ... ])
FORM_SECTIONS = [
    ("Facility &amp; Event Planning", [
        ("&#127963;&#65039;", "Facility Use Application", "Required for reserving any room or space at FBC Manassas for ministry or private events.", "facility building room application event", "Download PDF", "#"),
        ("&#128141;", "Wedding Guidelines &amp; Request", "Policies, scheduling details, and request paperwork for holding weddings at the church.", "wedding marriage ceremony guidelines", "Download PDF", "#"),
        ("&#128197;", "Ministry Planning Form", "Submission form for scheduling ministry events and activities for the upcoming calendar year.", "ministry planning calendar year events", "Download Form", "#"),
    ]),
    ("Administrative &amp; Operations", [
        ("&#128179;", "Procurement Request Form", "Submit this form for ministry purchases, expense approvals, and financial reimbursements.", "procurement finance purchase request money", "Download Form", "#"),
        ("&#128226;", "Ministry Marketing Request", "Request graphics, social media posts, bulletin announcements, or slide displays for your ministry.", "marketing communications graphics flyer social media", "Submit Request", "#"),
        ("&#129309;", "Ministry Support Request", "General administrative or logistical support paperwork for ministry leaders and volunteers.", "support assistance help ministry", "Download Form", "#"),
    ]),
]
FORMS_FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"   # same system font stack as the supplied layout
def form_card(icon, title, desc, kw, btext, href):
    """Icon tile on the left, text on the right (a two-cell table, since flex is not safe in this CMS). White card, gold border."""
    tile = (f'<td valign="top" width="60" style="width:60px;padding:0 16px 0 0;"><table role="presentation" width="52" cellpadding="0" cellspacing="0" border="0" style="width:52px;border-collapse:separate;border-radius:8px;"><tr>'
            f'<td align="center" valign="middle" width="52" height="52" bgcolor="{CREAM}" style="width:52px;height:52px;background-color:{CREAM};border-radius:8px;font-size:28px;line-height:52px;text-align:center;"{F("icon")}>{icon}</td></tr></table></td>')
    a = (f'<a href="{href}" target="_blank" rel="noopener noreferrer"{F("button")}{FH("button_url")} style="text-decoration:none;display:block;white-space:nowrap;padding:7px 14px;'
         f'font-family:{FORMS_FONT};font-size:14px;font-weight:600;color:{WHITE};text-align:center;">{btext}</a>')
    button = T(TR(f'<td align="center" bgcolor="{MAROON}" style="background-color:{MAROON};border-radius:6px;">{a}</td>'), width="auto", style="border-radius:6px;")
    text = (f'<div style="margin:0 0 6px 0;font-family:{FORMS_FONT};font-size:18px;font-weight:600;line-height:1.25;color:{MAROON};"{F("title")}>{title}</div>'
            f'<div style="margin:0 0 14px 0;font-family:{FORMS_FONT};font-size:15px;line-height:1.45;color:{TGRAY};"{F("desc", long=True)}>{desc}</div>' + button)
    box = (f'<table role="presentation" width="100%" height="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{WHITE}" style="width:100%;height:100%;border-collapse:separate;background-color:{WHITE};border:1px solid {GOLD};border-radius:10px;">'
           f'<tr><td valign="top" height="100%" style="height:100%;padding:20px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:separate;"><tr>{tile}<td valign="top">{text}</td></tr></table></td></tr></table>')
    return (f'<table role="presentation" align="left" width="33%" cellpadding="0" cellspacing="0" border="0" data-eq="1"{FITEM("forms")} data-keywords="{kw}" '
            f'style="width:33.333%;min-width:320px;max-width:100%;border-collapse:separate;"><tr><td valign="top" height="270" style="height:270px;padding:0 10px 20px 10px;">{box}</td></tr></table>')

def form_section(n, heading, items):
    head = T(TR(f'<td style="border-bottom:2px solid {GOLD};padding:0 0 8px 0;"><h2{F(f"forms.s{n}")} style="margin:0;font-family:{FORMS_FONT};font-size:22px;font-weight:700;line-height:1.25;color:{MAROON};">{heading}</h2></td>'), width="100%")
    return (f'<div data-fbc-section="{n}">' + head + sp(20) + c("Forms in this section: copy one whole card to add another; the other cards re-flow on their own")
            + flow([form_card(*it) for it in items], "form") + sp(20) + "</div>")

forms_head = (f'<div style="text-align:center;padding:0 0 8px 0;">'
              f'<h1{F("hero.title")} style="margin:0 0 10px 0;font-family:{FORMS_FONT};font-size:35px;font-weight:700;line-height:1.2;color:{MAROON};">Church Forms &amp; Resources</h1>'
              f'<p{F("hero.intro", long=True)} style="margin:0 auto;max-width:700px;font-family:{FORMS_FONT};font-size:17px;line-height:1.5;color:{TGRAY};">Find facility requests, ministry planning tools, administrative documents, and spiritual growth guides below. Click any card to download or view the document.</p></div>')
search_box = T(TR(TD(f'<input type="text" id="fbcFormSearch" placeholder="Search forms (e.g., wedding, facility, marketing)..." '
                     f'style="width:100%;box-sizing:border-box;padding:12px 16px;border:1px solid {GOLD};border-radius:8px;background-color:{WHITE};font-family:{FORMS_FONT};font-size:16px;color:{DARK};outline:none;">')),
               width="500", style="max-width:100%;", extra=' align="center"')
FORM_SEARCH_JS = r"""<script>
(function () {
  // Search box: a card shows when every word typed appears in its keywords or text. A section with no visible
  // cards is hidden. Written without angle brackets or ampersands so CMS editors cannot break it.
  var box = document.getElementById('fbcFormSearch');
  if (!box) { return; }
  function each(list, fn) { Array.prototype.forEach.call(list, fn); }
  function run() {
    var q = (box.value || '').toLowerCase().replace(/^\s+|\s+$/g, '');
    var words = q ? q.split(/\s+/) : [];
    var shown = 0;
    each(document.querySelectorAll('table[data-keywords]'), function (card) {
      var hay = ((card.getAttribute('data-keywords') || '') + ' ' + (card.textContent || '')).toLowerCase();
      var ok = true;
      each(words, function (w) { if (hay.indexOf(w) === -1) { ok = false; } });
      card.style.display = ok ? '' : 'none';
      if (ok) { shown += 1; }
    });
    each(document.querySelectorAll('div[data-fbc-section]'), function (sec) {
      var any = false;
      each(sec.querySelectorAll('table[data-keywords]'), function (card) { if (card.style.display !== 'none') { any = true; } });
      sec.style.display = any ? '' : 'none';
    });
    var empty = document.getElementById('fbcNoForms');
    if (empty) {
      empty.textContent = shown ? '' : 'No forms match your search.';
      empty.style.cssText = shown ? '' : 'text-align:center;padding:24px 12px 36px 12px;font-family:Arial,Helvetica,sans-serif;font-size:18px;color:#666666;';
    }
  }
  box.addEventListener('input', run);
  box.addEventListener('keyup', run);
})();
</script>"""

forms_body = sec(
    c("Page header: centered title and intro")
    + forms_head + sp(22)
    + c("Search box: filters the cards below as you type (script at the end of this section)")
    + search_box + sp(34)
    + "".join(form_section(i + 1, hd, its) for i, (hd, its) in enumerate(FORM_SECTIONS))
    + '<div id="fbcNoForms"></div>'
    + c("Script: equalizes the card heights (optional; the fixed heights are the fallback)") + EQ_JS
    + c("Search script: needs a CMS that keeps <script> tags (no inline handlers needed)") + FORM_SEARCH_JS, pad="20px 0")

fhdr = f"""<!-- =====================================================================
  FBC FORMS PAGE - CMS EMBED
  HOW TO USE: switch the CMS block to Source/HTML view and paste everything below.
  Inline CSS + tables only (no <style> tags). Same layout as the supplied forms page (centered header, search box,
  sections with an underlined heading, icon cards with a small button) in the FBC colors.
  Site header, breadcrumb and footer come from your CMS template (not included).

  PLACEHOLDERS: every card's button link is "#" until you set the real PDF or online-form address (use the FBC Page
  Editor, or edit the href). PDF forms: upload the PDF to the CMS media library and paste its address as the link.
  ADDING A FORM: copy one whole card (from "FORM CARD START" to "FORM CARD END"), paste it into the section it belongs to,
  then change its icon, title, description, button and link. Put extra words people might search for in its data-keywords.
  The other cards re-flow on their own. To add a section, copy one whole <div data-fbc-section="..."> block.

{PALETTE}
====================================================================== -->
"""
forms = page(c("SECTION 1: Header, search box and forms grouped by section") + forms_body, fhdr, key="forms")
write("forms", forms)

# =====================================================================
# PASTOR'S PEN  (library page, built from the roadmap's live sample site)
# Edit PENS below, then run:  python3 tools/gen_pages.py
# Newest first. Picture names are date stamped (Pen_YYYY-MM-DD_img) so no week overwrites another;
# upload each picture to the CMS media library and the page finds it at PEN_IMG_BASE + name + ".jpg".
# =====================================================================
PEN_IMG_BASE = "https://fbcmanassas.org/wp-content/uploads/"
PEN_IMG_EXT = ".jpg"
PENS = [
    # Each entry is one week's actual Pastor's Pen HTML (saved in pens_html/). For now the library is five copies of the
    # November 1 Pen, so the library can be tried out. Real weeks are added with the FBC Page Editor (Pastor's Pen files),
    # which names each library card from the Pen's own header.
    dict(embed="pens_html/Pastors_Pen_2026-11-01_READY.html") for _ in range(5)
]
PEN_NOTE = "The full Pen continues here: Sunday Recap, Life Applicable Gems, and Sit With This This Week."

def pen_embed_html(path):
    """The body of a saved Pen file: its top-level table. (Fixes a stray width="100%%" some exports contain.)"""
    raw = open(R + path, encoding="utf-8").read()
    m = re.search(r"<body[^>]*>(.*)</body>", raw, re.S | re.I)
    return (m.group(1) if m else raw).strip().replace('width="100%%"', 'width="100%"')

def pen_embed_card(p):
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" data-pen="1"{FITEM("pens")} style="width:100%;border-collapse:separate;">'
            f'<tr><td valign="top" style="padding:0;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:separate;">'
            f'<tr><td style="background-color:{WHITE};padding:0;">{pen_embed_html(p["embed"])}</td></tr></table></td></tr></table>')

def pen_card(p):
    if p.get("embed"):
        return pen_embed_card(p)
    def pic(name, field, alt):
        return (f'<img src="{PEN_IMG_BASE}{name}{PEN_IMG_EXT}"{FI(field)} alt="{alt}" width="1280" height="720" '
                'style="display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;border:0;border-radius:12px;">')
    if p["img"]:
        top = pic(p["img"], "img1", p["title"].replace('"', "&quot;"))
    else:   # no picture that week: a maroon title banner stands in
        top = (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:separate;border-radius:12px;"><tr>'
               f'<td align="center" valign="middle" height="150" bgcolor="{MAROON}" style="height:150px;background-color:{MAROON};border-radius:12px;padding:16px 20px;font-family:{H};font-size:28px;line-height:1.2;color:{WHITE};text-align:center;"{F("banner")}>{p["title"]}</td></tr></table>')
    inner = (top + sp(16)
             + txt(SPANS([("date", p["date"]), ("occ", p["occ"])]), 13, MAROON, "bold", extra="letter-spacing:0.1em;text-transform:uppercase;line-height:1.35;") + sp(8)
             + h("h3", p["title"], 30, MAROON, "600", "1.15", fb=F("title")) + sp(8)
             + txt(SPANS([("preacher", p["preacher"])], sep="") , 16, TGRAY, "600", extra="line-height:1.4;") 
             + txt(f'<span{F("scripture")}>{p["scripture"]}</span>', 16, TGRAY, extra="line-height:1.4;") + sp(12)
             + txt(p["summary"], 18, DARK, extra="line-height:1.55;", fb=F("summary", long=True)))
    if p["img2"]:
        inner += sp(16) + pic(p["img2"], "img2", "")
    inner += sp(14) + txt(PEN_NOTE, 14, TGRAY, extra="line-height:1.5;", fb=F("note", long=True))
    card_html = rounded(inner, CREAM, 16, 20, f"border:1px solid {GOLD};")
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" data-pen="1"{FITEM("pens")} style="width:100%;border-collapse:separate;">'
            f'<tr><td valign="top" style="padding:0 0 20px 0;">{card_html}</td></tr></table>')

pen_cards = "".join(f"<!-- PEN CARD START: copy from here -->\n{pen_card(p)}\n<!-- PEN CARD END -->\n" for p in PENS)
pens_block = ("<!-- NEWEST SUNDAY FIRST: paste the new Pen card on the line below this one. The library list on the right builds itself from these cards. -->\n"
              + pen_cards + "<!-- To keep a rolling 12 months, delete the last card above (the oldest) -->\n")

# Header: page name and purpose on the left, logo on the right (same layout and script as Photo Gallery and Forms)
PEN_LOGO = "https://fbcmanassas.org/wp-content/uploads/PastorsPenLogo.png"
pen_logo_img = (f'<img src="{PEN_LOGO}"{FI("hero.logo")} alt="The Pastor&rsquo;s Pen" width="1000" height="1000" '
                'style="display:block;margin:0 auto;width:auto;height:auto;max-width:100%;max-height:340px;border:0;">')
pen_head_text = (eyebrow("Weekly Word", MAROON, 15, "0.16em", fb=F("hero.eyebrow", upper=True)) + sp(20)
                 + h("h1", "The Pastor&rsquo;s Pen", 64, MAROON, lh="1.04", fb=F("hero.title")) + sp(20)
                 + txt("A weekly word from your pastor. Every Sunday, written down, so the Word goes home with you.", 21, TGRAY, extra="line-height:1.5;", fb=F("hero.intro", long=True)))
pen_hero = section(TR(TD(
    fl_col(pen_head_text, "48%", 320, "0", td_id="fbcHeroText")
    + c("IMAGE: Pastor's Pen logo - replace the src with the CMS media URL")
    + fl_col(f'<div style="text-align:center;font-size:0;line-height:0;">{pen_logo_img}</div>', "52%", 260, "0 0 0 24px", tbl_id="fbcHeroLogo")
    + CLEAR + c("Script: centers the text beside the logo on wide screens and puts the logo above the text on phones") + HERO_JS)), pad="0 0 24px")

# Footer: call to action (text left, buttons right; stacks on phones like the other pages' bands)
pen_foot_text = (txt("Worship With Us", 14, GOLD, "bold", extra="letter-spacing:0.18em;text-transform:uppercase;line-height:1.3;", fb=F("cta.eyebrow")) + sp(10)
                 + h("h2", "Hear the Word in person this Sunday", 40, WHITE, lh="1.12", fb=F("cta.heading")) + sp(10)
                 + txt("Join us for worship at 9:00 AM at 9258 Center Street, Manassas, with Sunday School at 11:00 AM. Bring a friend, and let someone know they are seen. Can&rsquo;t be here? Worship with us live online.", 19, CREAM, extra="line-height:1.5;", fb=F("cta.text", long=True)))
pen_foot_btns = (btn("Plan a Visit", PLAN_A_VISIT, GOLD, DARK, 18, "14px 32px", fbl="cta.button", fbh="cta.button_url") + sp(12)
                 + btn("Watch Live", YT_STREAMS, CREAM, DARK, 18, "14px 32px", fbl="cta.button2", fbh="cta.button2_url"))
pen_foot_inner = fl_col(pen_foot_text, "66%", 240, "0 24px 0 0") + fl_col(pen_foot_btns, "34%", 220, "14px 0 0 0") + CLEAR
pen_foot = sec(sp(8) + c("Call to action: text and buttons sit side by side on wide screens and stack on phones") + rounded(pen_foot_inner, MAROON, 20, "28px 24px"), pad="24px 0 0")

PEN_LIB_FALLBACK = "Scroll down to read earlier Sundays."
pen_lib_col = (txt("The Library &nbsp;&middot;&nbsp; Rolling 12 Months", 13, GOLD, "bold", extra="letter-spacing:0.14em;text-transform:uppercase;", fb=F("lib.label")) + sp(10)
               + f'<div id="fbcPenLib" style="max-height:640px;overflow-y:auto;font-family:{B};font-size:15px;color:{TGRAY};">{PEN_LIB_FALLBACK}</div>' + sp(10)
               + txt("Archive: 2026 &nbsp;&middot;&nbsp; Older years move here each year.", 14, TGRAY, extra="line-height:1.5;", fb=F("lib.archive")))
PEN_JS = r"""<script>
(function () {
  // Pastor's Pen library. Each Sunday is one card in the left column; the list on the right is built from those cards,
  // and clicking a Sunday shows only that card. With scripts blocked every card simply stays stacked, newest first.
  // Written without angle brackets or ampersands so CMS editors cannot HTML-escape it and break the script.
  var pens = document.querySelectorAll('table[data-pen]');
  var lib = document.getElementById('fbcPenLib');
  if (!lib) { return; }
  if (!pens.length) { return; }
  var entries = [];
  var box = document.getElementById('fbcPenBox');
  function each(list, fn) { Array.prototype.forEach.call(list, fn); }
  // The Pen's header is the row with three lines: "1st Sunday . Sunday, November 1, 2026", the title, and the verses.
  function words(n) { return (n.textContent || '').replace(/\s+/g, ' ').replace(/^\s+|\s+$/g, ''); }
  function header(card) {
    var cells = card.getElementsByTagName('td');
    for (var k = 0; k !== cells.length; k++) {
      var kids = cells[k].children;
      if (kids.length !== 0) {
        if (Math.max(kids.length, 3) === kids.length) {
          var first = words(kids[0]);
          if (/Sunday/.test(first)) {
            if (/[0-9][0-9][0-9][0-9]/.test(first)) { return [first, words(kids[1]), words(kids[2])]; }
          }
        }
      }
    }
    return ['', '', ''];
  }
  function paint(e, on) {
    e.a.style.backgroundColor = on ? '#6B1735' : '#ffffff';
    e.a.style.borderColor = on ? '#6B1735' : '#C9A55C';
    e.d.style.color = on ? '#E3C78F' : '#666666';
    e.t.style.color = on ? '#ffffff' : '#6B1735';
    e.p.style.color = on ? '#F7F3EC' : '#666666';
  }
  function show(i) {
    each(pens, function (p, j) { p.style.display = (j === i) ? '' : 'none'; });
    each(entries, function (e, j) { paint(e, j === i); });
  }
  function line(text, css) {
    var d = document.createElement('div');
    d.style.cssText = css;
    d.textContent = text;
    return d;
  }
  lib.textContent = '';
  each(pens, function (card, j) {
    var a = document.createElement('a');
    a.setAttribute('href', '#');
    a.setAttribute('data-pen-idx', String(j));
    a.style.cssText = 'display:block;text-decoration:none;margin:0 0 10px 0;padding:12px 14px;border:1px solid #C9A55C;border-radius:12px;background-color:#ffffff;';
    var h3 = header(card);
    var keep = ['data-pen-line1', 'data-pen-title', 'data-pen-verses'];
    for (var q = 0; q !== 3; q++) { if (card.hasAttribute(keep[q])) { h3[q] = card.getAttribute(keep[q]); } }
    var d = line(h3[0], 'font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:1.4;');
    var t = line(h3[1], 'font-family:Arial,Helvetica,sans-serif;font-size:17px;font-weight:bold;line-height:1.3;');
    var p = line(h3[2], 'font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:1.4;');
    a.appendChild(d); a.appendChild(t); a.appendChild(p);
    lib.appendChild(a);
    entries.push({ a: a, d: d, t: t, p: p });
  });
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest ? ev.target.closest('a[data-pen-idx]') : null;
    if (!a) { return; }
    ev.preventDefault();
    ev.stopPropagation();
    var i = parseInt(a.getAttribute('data-pen-idx'), 10);
    show(i);
    var holder = box ? box : pens[i];
    if (box) { box.scrollTop = 0; }
    var r = holder.getBoundingClientRect();
    if (Math.max(r.top, 0) !== r.top) { holder.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  }, true);
  function fit() {
    // The library list scrolls on its own. This is set here (not only in the markup) because some CMS editors drop
    // overflow from inline styles but keep what a script sets.
    lib.style.maxHeight = '640px';
    lib.style.overflowY = 'auto';
    lib.style.overflow = 'auto';
    lib.style.webkitOverflowScrolling = 'touch';
    if (!box) { return; }
    box.style.maxHeight = '';
    box.style.overflowY = '';
    var pr = box.getBoundingClientRect();
    var lr = lib.getBoundingClientRect();
    if (Math.max(pr.right - lr.left - 2, 0) === 0) {
      box.style.maxHeight = '700px';
      box.style.overflowY = 'auto';
    }
  }
  show(0);
  fit();
  window.addEventListener('load', fit);
  window.addEventListener('resize', fit);
})();
</script>"""
pen_body = sec(
    c("Two columns: the Pen on the left (the selected Sunday shows), the library list on the right (built by the script below). Side by side, each column scrolls on its own; on phones they stack and the page scrolls normally.")
    + fl_col(f'<div id="fbcPenBox" style="border:1px solid {GOLD};background-color:{WHITE};">{pens_block}</div>', "62%", 340, "0 12px 0 0")
    + fl_col(pen_lib_col, "38%", 280, "0 0 0 12px")
    + CLEAR + c("Library script: builds the list from the cards and shows the Sunday you click (optional; without it every card stays stacked)") + PEN_JS, pad="0")

phdr = f"""<!-- =====================================================================
  FBC PASTOR'S PEN PAGE - CMS EMBED
  HOW TO USE: switch the CMS block to Source/HTML view and paste everything below.
  Inline CSS + tables only (no <style> tags). Pictures are loaded from the CMS media library.
  LOGO: the header logo is PEN_LOGO in tools/gen_pages.py; upload it to the CMS and set that address.

  EACH SUNDAY: the left column shows that Sunday's actual Pastor's Pen. Easiest: open tools/dashboard.html (FBC Page Editor),
  load this page, and use "Add Pen files" to pick one or many Pen HTML files. By hand: copy everything inside <body> ... </body>
  of the Pen file (the one big table) and paste it inside a new "PEN CARD START" ... "PEN CARD END" wrapper (copy a wrapper from below).
  The library list on the right names each card from the Pen's own maroon header: line 1 "1st Sunday . Sunday, November 1, 2026",
  line 2 the sermon title, line 3 the verses. Nothing else to fill in. If a Pen has no such header, give its wrapper the
  attributes data-pen-line1, data-pen-title and data-pen-verses (the FBC Page Editor fills them in for you); they win over the header.
  Put the newest Sunday first, and delete the oldest at the bottom to keep a rolling 12 months.
  The Pen's own pictures keep loading from their addresses in the Pen file (the CMS media library).

{PALETTE}
====================================================================== -->
"""
pen_page = page(c("SECTION 1: Header - page name and purpose on the left, logo on the right") + pen_hero + c("SECTION 2: This Sunday's Pen + the library") + pen_body + c("SECTION 3: Call to action") + pen_foot, phdr, key="pen")
# No theme padding or margin at the top of the page or under the footer: every bare cell and table gets explicit zeros
pen_page = pen_page.replace('<td style="">', '<td style="padding:0;margin:0;">').replace("border-collapse:separate;", "border-collapse:separate;margin:0;")
write("pastors-pen", pen_page)


# =====================================================================================================
# PASTOR'S HIGHLIGHTS: same two-sided header and call-to-action footer as the Pastor's Pen, with five tabs
# (this week on the left, oldest on the right) instead of a library. Each tab shows one week's highlights HTML.
# =====================================================================================================
HL_LOGO = "https://fbcmanassas.org/wp-content/uploads/PastorsHighlightsLogo.png"
hl_logo_img = (f'<img src="{HL_LOGO}"{FI("hero.logo")} alt="Pastor&rsquo;s Highlights" width="1000" height="1000" '
               'style="display:block;margin:0 auto;width:auto;height:auto;max-width:100%;max-height:340px;border:0;">')
hl_head_text = (eyebrow("Week by Week", MAROON, 15, "0.16em", fb=F("hero.eyebrow", upper=True)) + sp(20)
                + h("h1", "Pastor&rsquo;s Highlights", 64, MAROON, lh="1.04", fb=F("hero.title")) + sp(20)
                + txt("The moments, people and ministries your pastor wants you to see. The last five weeks, one tab each, newest first.", 21, TGRAY, extra="line-height:1.5;", fb=F("hero.intro", long=True)))
hl_hero = section(TR(TD(
    fl_col(hl_head_text, "48%", 320, "0", td_id="fbcHeroText")
    + c("IMAGE: Pastor's Highlights logo - replace the src with the CMS media URL")
    + fl_col(f'<div style="text-align:center;font-size:0;line-height:0;">{hl_logo_img}</div>', "52%", 260, "0 0 0 24px", tbl_id="fbcHeroLogo")
    + CLEAR + c("Script: centers the text beside the logo on wide screens and puts the logo above the text on phones") + HERO_JS)), pad="0 0 24px")

# Footer: the same call to action layout as the Pen page
hl_foot_text = (txt("Be Part of It", 14, GOLD, "bold", extra="letter-spacing:0.18em;text-transform:uppercase;line-height:1.3;", fb=F("cta.eyebrow")) + sp(10)
                + h("h2", "See what God is doing, in person", 40, WHITE, lh="1.12", fb=F("cta.heading")) + sp(10)
                + txt("These highlights are only a glimpse. Join us for worship at 9:00 AM at 9258 Center Street, Manassas, with Sunday School at 11:00 AM. Can&rsquo;t be here? Worship with us live online.", 19, CREAM, extra="line-height:1.5;", fb=F("cta.text", long=True)))
hl_foot_btns = (btn("Plan a Visit", PLAN_A_VISIT, GOLD, DARK, 18, "14px 32px", fbl="cta.button", fbh="cta.button_url") + sp(12)
                + btn("Watch Live", YT_STREAMS, CREAM, DARK, 18, "14px 32px", fbl="cta.button2", fbh="cta.button2_url"))
hl_foot_inner = fl_col(hl_foot_text, "66%", 240, "0 24px 0 0") + fl_col(hl_foot_btns, "34%", 220, "14px 0 0 0") + CLEAR
hl_foot = sec(sp(8) + c("Call to action: text and buttons sit side by side on wide screens and stack on phones") + rounded(hl_foot_inner, MAROON, 20, "28px 24px"), pad="24px 0 0")

# One tab = one week. The tab name is the week's "label" field; the week's own HTML goes in the cell marked data-hl-body.
HL_EMPTY = (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:separate;"><tr><td style="padding:20px;">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:separate;"><tr>'
            f'<td align="center" valign="middle" bgcolor="{LGRAY}" style="background-color:{LGRAY};border:2px dashed {GOLD};border-radius:12px;padding:48px 24px;font-family:{B};font-size:17px;line-height:1.5;color:{TGRAY};text-align:center;">'
            f'[PASTOR&rsquo;S HIGHLIGHTS: add this week&rsquo;s highlights here. In the Page Editor, open this week and paste or pick the highlights HTML.]</td></tr></table></td></tr></table>')
HL_WEEKS = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]   # newest first; edit each tab name in the Page Editor
def hl_week(label):
    return ('<!-- WEEK START: copy from here -->\n'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" data-hl="1" data-hl-label="{label}"{FITEM("hl")} style="width:100%;border-collapse:separate;">'
            f'<tr data-hl-title="1"><td style="padding:16px 20px 0 20px;">{txt(label, 22, MAROON, "bold", fb=F("label"))}</td></tr>'
            f'<tr><td data-hl-body="1" data-hl-empty="1" style="padding:0;">{HL_EMPTY}</td></tr></table>\n'
            '<!-- WEEK END -->\n')
hl_weeks_block = ("<!-- NEWEST WEEK FIRST (leftmost tab): paste a new week's wrapper on the line below this one -->\n"
                  + "".join(hl_week(w) for w in HL_WEEKS)
                  + "<!-- Keep five weeks: delete the last wrapper above (the oldest, rightmost tab) when you add a new one -->\n")
HL_JS = r"""<script>
(function () {
  // Pastor's Highlights tabs. Each week is one block in the box below; the tab row is built from those blocks
  // (newest on the left). With scripts blocked every week simply stays stacked, newest first.
  // Written without angle brackets or ampersands so CMS editors cannot HTML-escape it and break the script.
  var bar = document.getElementById('fbcHlTabs');
  var box = document.getElementById('fbcHlBox');
  if (!bar) { return; }
  var tabs = [];
  function each(list, fn) { Array.prototype.forEach.call(list, fn); }
  function words(n) { return (n.textContent || '').replace(/\s+/g, ' ').replace(/^\s+|\s+$/g, ''); }
  // The weeks are the blocks marked data-hl. If a CMS dropped that mark, the weeks are the tables directly inside the box.
  var panels = [];
  each(document.querySelectorAll('table[data-hl]'), function (n) { panels.push(n); });
  if (panels.length === 0) {
    if (box) { each(box.children, function (n) { if (n.tagName === 'TABLE') { panels.push(n); } }); }
  }
  if (panels.length === 0) { return; }
  // A week's tab name is its title line. Looked up three ways, so it survives a CMS that drops some of the invisible marks:
  // the marked line, the first short cell of the block, then the block's data-hl-label.
  function titleCell(p) {
    var td = p.querySelector('td');
    if (!td) { return null; }
    if (td.hasAttribute('data-hl-body')) { return null; }
    if (Math.max(words(td).length, 40) !== 40) { return null; }
    return td;
  }
  function labelOf(p, i) {
    var el = p.querySelector('[data-fbc="label"]');
    var t = el ? words(el) : '';
    if (t === '') { var td = titleCell(p); if (td) { t = words(td); } }
    if (t === '') { t = p.getAttribute('data-hl-label') || ''; }
    if (t === '') { return 'Week ' + (i + 1); }
    return t;
  }
  function paint(a, on) {
    a.style.backgroundColor = on ? '#6B1735' : '#ffffff';
    a.style.borderColor = on ? '#6B1735' : '#C9A55C';
    a.style.color = on ? '#ffffff' : '#6B1735';
  }
  function show(i) {
    each(panels, function (p, j) { p.style.display = (j === i) ? '' : 'none'; });
    each(tabs, function (a, j) { paint(a, j === i); });
  }
  bar.textContent = '';
  each(panels, function (p, i) {
    var row = p.querySelector('[data-hl-title]');
    if (!row) { var tc = titleCell(p); if (tc) { row = tc.parentNode; } }
    if (row) { row.style.display = 'none'; }
    var a = document.createElement('a');
    a.setAttribute('href', '#');
    a.setAttribute('data-hl-idx', String(i));
    a.style.cssText = 'display:block;float:left;box-sizing:border-box;width:19%;min-width:110px;margin:0 1% 10px 0;padding:14px 8px;text-align:center;text-decoration:none;font-family:Arial,Helvetica,sans-serif;font-size:17px;font-weight:bold;line-height:1.25;border:1px solid #C9A55C;border-radius:12px;background-color:#ffffff;color:#6B1735;';
    a.textContent = labelOf(p, i);
    bar.appendChild(a);
    tabs.push(a);
  });
  var clr = document.createElement('div');
  clr.style.cssText = 'clear:both;height:0;font-size:0;line-height:0;';
  bar.appendChild(clr);
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest ? ev.target.closest('a[data-hl-idx]') : null;
    if (!a) { return; }
    ev.preventDefault();
    ev.stopPropagation();
    show(parseInt(a.getAttribute('data-hl-idx'), 10));
  }, true);
  show(0);
})();
</script>"""
hl_body = sec(
    c("Five tabs, one per week: this week on the left, the oldest on the right (the tabs are built by the script below from the weekly blocks)")
    + f'<div id="fbcHlTabs" style="font-family:{B};font-size:15px;color:{TGRAY};">Scroll down to read the earlier weeks.</div>'
    + c("Weekly highlights: one block per week, newest first")
    + f'<div id="fbcHlBox" style="border:1px solid {GOLD};background-color:{WHITE};">{hl_weeks_block}</div>'
    + c("Tabs script (optional; without it every week stays stacked)") + HL_JS, pad="0")

hl_hdr = f"""<!-- =====================================================================
  FBC PASTOR'S HIGHLIGHTS PAGE - CMS EMBED
  HOW TO USE: switch the CMS block to Source/HTML view and paste everything below.
  Inline CSS + tables only (no <style> tags). Pictures are loaded from the CMS media library.
  LOGO: the header logo is HL_LOGO in tools/gen_pages.py; upload it to the CMS and set that address.

  EACH WEEK: five tabs, newest on the left. Easiest: open tools/dashboard.html (FBC Page Editor), load this page, open a week
  and paste (or pick) that week's highlights HTML, or use "Add highlight files" to add several at once. Each week's tab name
  is its "Tab name" field. By hand: put the week's HTML inside the cell marked data-hl-body (delete data-hl-empty and the grey
  placeholder), and set the week's name in the field marked data-fbc="label".
  When a new week comes: add it at the top and delete the oldest (rightmost) so there are five.

{PALETTE}
====================================================================== -->
"""
hl_page = page(c("SECTION 1: Header - page name and purpose on the left, logo on the right") + hl_hero + c("SECTION 2: Five weekly tabs") + hl_body + c("SECTION 3: Call to action") + hl_foot, hl_hdr, key="hl")
hl_page = hl_page.replace('<td style="">', '<td style="padding:0;margin:0;">').replace("border-collapse:separate;", "border-collapse:separate;margin:0;")
write("pastors-highlights", hl_page)

# =====================================================================================================
# CHURCH CALENDAR: same two-sided header and call-to-action footer; twelve small folder-style tabs (January to December,
# left-justified) instead of the Highlights tabs. Each tab shows one month's calendar HTML.
# =====================================================================================================
CAL_LOGO = "https://fbcmanassas.org/wp-content/uploads/CalendarLogo.png"
cal_logo_img = (f'<img src="{CAL_LOGO}"{FI("hero.logo")} alt="Church Calendar" width="1000" height="1000" '
                'style="display:block;margin:0 auto;width:auto;height:auto;max-width:100%;max-height:340px;border:0;">')
cal_head_text = (txt("What&rsquo;s Happening", 15, MAROON, "bold", extra="letter-spacing:0.16em;text-transform:uppercase;line-height:1.3;", fb=F("hero.eyebrow", upper=True)) + sp(20)
                 + h("h1", "Church Calendar", 64, MAROON, lh="1.04", fb=F("hero.title")) + sp(20)
                 + txt("Every service, study, ministry meeting and special event at First Baptist, month by month. Pick a month to see what is ahead.", 21, TGRAY, extra="line-height:1.5;", fb=F("hero.intro", long=True)))
cal_hero = section(TR(TD(
    fl_col(cal_head_text, "48%", 320, "0", td_id="fbcHeroText")
    + c("IMAGE: Church Calendar logo - replace the src with the CMS media URL")
    + fl_col(f'<div style="text-align:center;font-size:0;line-height:0;">{cal_logo_img}</div>', "52%", 260, "0 0 0 24px", tbl_id="fbcHeroLogo")
    + CLEAR + c("Script: centers the text beside the logo on wide screens and puts the logo above the text on phones") + HERO_JS)), pad="0 0 24px")

cal_foot_text = (txt("Join Us", 14, GOLD, "bold", extra="letter-spacing:0.18em;text-transform:uppercase;line-height:1.3;", fb=F("cta.eyebrow")) + sp(10)
                 + h("h2", "Mark your calendar and come as you are", 40, WHITE, lh="1.12", fb=F("cta.heading")) + sp(10)
                 + txt("Worship is Sundays at 9:00 AM at 9258 Center Street, Manassas, with Sunday School at 11:00 AM, Bible Study on Wednesdays at 7:00 PM and IGNITE on Thursdays at 7:30 PM. Can&rsquo;t be here? Worship with us live online.", 19, CREAM, extra="line-height:1.5;", fb=F("cta.text", long=True)))
cal_foot_btns = (btn("Plan a Visit", PLAN_A_VISIT, GOLD, DARK, 18, "14px 32px", fbl="cta.button", fbh="cta.button_url") + sp(12)
                 + btn("Watch Live", YT_STREAMS, CREAM, DARK, 18, "14px 32px", fbl="cta.button2", fbh="cta.button2_url"))
cal_foot_inner = fl_col(cal_foot_text, "66%", 240, "0 24px 0 0") + fl_col(cal_foot_btns, "34%", 220, "14px 0 0 0") + CLEAR
cal_foot = sec(sp(8) + c("Call to action: text and buttons sit side by side on wide screens and stack on phones") + rounded(cal_foot_inner, MAROON, 20, "28px 24px"), pad="24px 0 0")

CAL_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
CAL_EMPTY = (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:separate;"><tr><td style="padding:20px;">'
             f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:separate;"><tr>'
             f'<td align="center" valign="middle" bgcolor="{LGRAY}" style="background-color:{LGRAY};border:2px dashed {GOLD};border-radius:12px;padding:48px 24px;font-family:{B};font-size:17px;line-height:1.5;color:{TGRAY};text-align:center;">'
             f'[CHURCH CALENDAR: add this month&rsquo;s calendar here. In the Page Editor, open this month and paste or pick the calendar HTML.]</td></tr></table></td></tr></table>')
def cal_month(label):
    return ('<!-- MONTH START: copy from here -->\n'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" data-cal="1" data-cal-label="{label}"{FITEM("cal")} style="width:100%;border-collapse:separate;">'
            f'<tr data-cal-title="1"><td style="padding:16px 20px 0 20px;">{txt(label, 22, MAROON, "bold", fb=F("label"))}</td></tr>'
            f'<tr><td data-cal-body="1" data-cal-empty="1" style="padding:0;">{CAL_EMPTY}</td></tr></table>\n'
            '<!-- MONTH END -->\n')
CAL_NOTE = (f'<div data-cal-note="1" style="padding:40px 24px;font-family:{B};font-size:17px;line-height:1.5;color:{TGRAY};text-align:center;">'
            '[CHURCH CALENDAR: no months yet. In the Page Editor, use &ldquo;Add calendar files&rdquo;; every calendar you add gets its own tab, most recent first.]</div>')
cal_months_block = ("<!-- No months yet. Each calendar you add (Page Editor: Add calendar files) becomes one block below with its own tab, most recent first. -->\n" + CAL_NOTE + "\n")
CAL_JS = r"""<script>
(function () {
  // Church Calendar tabs: one small folder-style tab per calendar you have added, most recent first (on the left). Each calendar
  // is one block in the box below; the tab row is built from those blocks, and the current month opens first.
  // With scripts blocked every calendar simply stays stacked. Written without angle brackets or ampersands so CMS editors
  // cannot HTML-escape it and break the script.
  var bar = document.getElementById('fbcCalTabs');
  var box = document.getElementById('fbcCalBox');
  if (!bar) { return; }
  var FULL = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'];
  var tabs = [];
  function each(list, fn) { Array.prototype.forEach.call(list, fn); }
  function words(n) { return (n.textContent || '').replace(/\s+/g, ' ').replace(/^\s+|\s+$/g, ''); }
  // The months are the blocks marked data-cal. If a CMS dropped that mark, they are the tables directly inside the box.
  var panels = [];
  each(document.querySelectorAll('table[data-cal]'), function (n) { panels.push(n); });
  if (panels.length === 0) {
    if (box) { each(box.children, function (n) { if (n.tagName === 'TABLE') { panels.push(n); } }); }
  }
  if (panels.length === 0) { bar.textContent = ''; return; }
  var note = box ? box.querySelector('[data-cal-note]') : null;
  if (note) { note.style.display = 'none'; }
  // A tab's name is its title line. Looked up three ways, so it survives a CMS that drops some of the invisible marks:
  // the marked line, the first short cell of the block, then the block's data-cal-label.
  function titleCell(p) {
    var td = p.querySelector('td');
    if (!td) { return null; }
    if (td.hasAttribute('data-cal-body')) { return null; }
    if (Math.max(words(td).length, 40) !== 40) { return null; }
    return td;
  }
  function labelOf(p, i) {
    var el = p.querySelector('[data-fbc="label"]');
    var t = el ? words(el) : '';
    if (t === '') { var td = titleCell(p); if (td) { t = words(td); } }
    if (t === '') { t = p.getAttribute('data-cal-label') || ''; }
    if (t === '') { return 'Calendar ' + (i + 1); }
    return t;
  }
  // "November 2026" gives month 10 and year 2026 (month -1 if the name is not a month)
  function parse(t) {
    var r = /^([A-Za-z]+)[.]?\s*([0-9][0-9][0-9][0-9])?$/.exec(t);
    if (!r) { return { m: -1, y: 0 }; }
    var w = r[1].toLowerCase();
    for (var k = 0; k !== 12; k++) {
      if (FULL[k] === w) { return { m: k, y: r[2] ? parseInt(r[2], 10) : 0 }; }
      if (FULL[k].slice(0, 3) === w) { return { m: k, y: r[2] ? parseInt(r[2], 10) : 0 }; }
    }
    return { m: -1, y: 0 };
  }
  var labels = [];
  var years = {};
  var yearCount = 0;
  each(panels, function (p, i) {
    var l = labelOf(p, i);
    labels.push(l);
    var y = parse(l).y;
    if (y !== 0) { if (!years[y]) { years[y] = 1; yearCount++; } }
  });
  // Month names show as "Nov"; when the tabs cover more than one year they show as "Nov 2026".
  function shortOf(t) {
    var p = parse(t);
    if (p.m === -1) { return t; }
    var s = FULL[p.m].charAt(0).toUpperCase() + FULL[p.m].slice(1, 3);
    if (Math.max(yearCount, 2) === yearCount) { if (p.y !== 0) { s = s + ' ' + p.y; } }
    return s;
  }
  function paint(a, on) {
    a.style.backgroundColor = on ? '#6B1735' : '#F2F2F2';
    a.style.color = on ? '#ffffff' : '#6B1735';
    a.style.zIndex = on ? '3' : '1';
  }
  function show(i) {
    each(panels, function (p, j) { p.style.display = (j === i) ? '' : 'none'; });
    each(tabs, function (a, j) { paint(a, j === i); });
  }
  var nowD = new Date();
  var start = 0;
  var found = false;
  bar.textContent = '';
  each(panels, function (p, i) {
    var row = p.querySelector('[data-cal-title]');
    if (!row) { var tc = titleCell(p); if (tc) { row = tc.parentNode; } }
    if (row) { row.style.display = 'none'; }
    var pr = parse(labels[i]);
    if (!found) {
      if (pr.m === nowD.getMonth()) {
        if (pr.y === 0 || pr.y === nowD.getFullYear()) { start = i; found = true; }
      }
    }
    var a = document.createElement('a');
    var slant = 'polygon(0 100%, 14px 0, calc(100% - 14px) 0, 100% 100%)';
    a.setAttribute('href', '#');
    a.setAttribute('data-cal-idx', String(i));
    a.style.cssText = 'display:block;float:left;position:relative;z-index:1;box-sizing:border-box;min-width:66px;margin:0 -9px 0 0;padding:9px 24px 8px 24px;text-align:center;text-decoration:none;font-family:Arial,Helvetica,sans-serif;font-size:14px;font-weight:bold;line-height:1.2;background-color:#F2F2F2;color:#6B1735;';
    a.style.clipPath = slant;
    a.style.webkitClipPath = slant;
    a.textContent = shortOf(labels[i]);
    a.setAttribute('title', labels[i]);
    bar.appendChild(a);
    tabs.push(a);
  });
  var clr = document.createElement('div');
  clr.style.cssText = 'clear:both;height:0;font-size:0;line-height:0;';
  bar.appendChild(clr);
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest ? ev.target.closest('a[data-cal-idx]') : null;
    if (!a) { return; }
    ev.preventDefault();
    ev.stopPropagation();
    show(parseInt(a.getAttribute('data-cal-idx'), 10));
  }, true);
  show(start);
})();
</script>"""
cal_body = sec(
    c("Small folder tabs, one per calendar you add, most recent on the left (built by the script below from the blocks in the box)")
    + f'<div id="fbcCalTabs" style="font-family:{B};font-size:15px;color:{TGRAY};">Scroll down to read every calendar.</div>'
    + c("The calendars: one block per month, most recent first")
    + f'<div id="fbcCalBox" style="border:1px solid {GOLD};border-top:3px solid {MAROON};background-color:{WHITE};">{cal_months_block}</div>'
    + c("Tabs script (optional; without it every month stays stacked)") + CAL_JS, pad="0")

cal_hdr = f"""<!-- =====================================================================
  FBC CHURCH CALENDAR PAGE - CMS EMBED
  HOW TO USE: switch the CMS block to Source/HTML view and paste everything below.
  Inline CSS + tables only (no <style> tags). Pictures are loaded from the CMS media library.
  LOGO: the header logo is CAL_LOGO in tools/gen_pages.py; upload it to the CMS and set that address.

  EACH MONTH: the page starts with no tabs. Easiest: open tools/dashboard.html (FBC Page Editor), load this page, and use
  "Add calendar files" to pick one HTML file per month. Each file becomes a tab named from its month ("November 2026"), placed
  most recent first (leftmost); or paste one month's HTML under "Or paste one month". By hand: add a block like the ones the editor
  makes (a table marked data-cal with data-cal-label, a title row, and a cell marked data-cal-body holding the month's HTML).
  The current month opens first.

{PALETTE}
====================================================================== -->
"""
cal_page = page(c("SECTION 1: Header - page name and purpose on the left, logo on the right") + cal_hero + c("SECTION 2: Month tabs") + cal_body + c("SECTION 3: Call to action") + cal_foot, cal_hdr, key="cal")
cal_page = cal_page.replace('<td style="">', '<td style="padding:0;margin:0;">').replace("border-collapse:separate;", "border-collapse:separate;margin:0;")
write("calendar", cal_page)

# keep the Page Editor's copy of the Highlights tabs script identical to the page's (it replaces older copies on load)
import json
_d = open(R + "tools/dashboard.html").read()
_body = HL_JS[len("<script>"):-len("</script>")].strip("\n")
_d = re.sub(r"/\*HL_JS_START\*/.*?/\*HL_JS_END\*/", lambda m: "/*HL_JS_START*/var HL_SCRIPT = " + json.dumps(_body) + ";/*HL_JS_END*/", _d, count=1, flags=re.S)
_cb = CAL_JS[len("<script>"):-len("</script>")].strip("\n")
_d = re.sub(r"/\*CAL_JS_START\*/.*?/\*CAL_JS_END\*/", lambda m: "/*CAL_JS_START*/var CAL_SCRIPT = " + json.dumps(_cb) + ";/*CAL_JS_END*/", _d, count=1, flags=re.S)
open(R + "tools/dashboard.html", "w").write(_d)
