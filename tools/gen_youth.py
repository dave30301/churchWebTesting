import re
H = "Fraunces,Georgia,'Times New Roman',serif"
B = "'Source Sans 3','Source Sans Pro',Arial,Helvetica,sans-serif"
MAROON, DEEP, GOLD, CREAM, LGRAY, TGRAY, WHITE, DARK = "#6B1735","#4B1026","#C9A55C","#F7F3EC","#F2F2F2","#666666","#ffffff","#171717"
SEP = "border-collapse:separate;"

def T(inner, width="100%", style="", bg=None, extra=""):
    b = f' bgcolor="{bg}"' if bg else ""
    w = width if width.endswith("%") or width == "auto" else width + "px"
    return f'<table role="presentation" width="{width}" cellpadding="0" cellspacing="0" border="0"{b} style="width:{w};{SEP}{style}"{extra}>{inner}</table>'
def TR(*c): return "<tr>" + "".join(c) + "</tr>"
def TD(inner, style="", **a):
    at = "".join(f' {k}="{v}"' for k, v in a.items())
    return f'<td{at} style="{style}">{inner}</td>'
def gap_col(w): return f'<td width="{w}" style="width:{w}px;font-size:0;line-height:0;">&nbsp;</td>'
def gap_row(h, cols=1): return f'<tr><td colspan="{cols}" height="{h}" style="height:{h}px;font-size:0;line-height:0;">&nbsp;</td></tr>'
def sp(h): return f'<div style="height:{h}px;line-height:{h}px;font-size:0;">&nbsp;</div>'
def txt(s, size, color, weight="normal", font=B, extra=""):
    return f'<div style="margin:0;font-family:{font};font-size:{size}px;font-weight:{weight};color:{color};{extra}">{s}</div>'
def eyebrow(s, color=MAROON, size=14, ls="0.14em"):
    return txt(s.upper(), size, color, "bold", extra=f"letter-spacing:{ls};line-height:1.3;")
def h(tag, s, size, color=MAROON, weight="normal", lh="1.15"):
    return f'<{tag} style="margin:0;padding:0;font-family:{H};font-size:{size}px;font-weight:{weight};line-height:{lh};color:{color};">{s}</{tag}>'
def link(s, href, style): return f'<a href="{href}" style="text-decoration:none;{style}">{s}</a>'

def btn(s, href, bg=GOLD, color=DARK, size=18, pad="16px 32px", full=False):
    a = link(s, href, f"display:block;white-space:nowrap;padding:{pad};font-family:{B};font-size:{size}px;font-weight:bold;color:{color};text-align:center;")
    return T(TR(f'<td align="center" bgcolor="{bg}" style="background-color:{bg};border-radius:999px;">{a}</td>'),
             width="100%" if full else "auto", style="border-radius:999px;")

def rounded(inner, bg, radius, pad, border=""):
    """Card/band: radius on BOTH the table and its cell so corners hold in any CMS."""
    r = f"border-radius:{radius}px;"
    pd = pad if isinstance(pad, str) else f"{pad}px"
    td = f'<td valign="top" bgcolor="{bg}" style="background-color:{bg};{r}{border}padding:{pd};">{inner}</td>'
    return T(TR(td), width="100%", bg=bg, style=f"background-color:{bg};{r}{border}", extra=' height="100%"')
def card(inner, bg=CREAM, pad=28, radius=16, border=True, width=None):
    b = f"border:1px solid {GOLD};" if border else ""
    w = f' width="{width}" style="width:{width};"' if width else ""
    return f'<td valign="top"{w}>{rounded(inner, bg, radius, pad, b)}</td>'

_n = [0]
def media(label, w, h_, instr, alt, radius=12, size=15, circle=False, spec=""):
    _n[0] += 1
    r = "50%" if circle else f"{radius}px"
    comment = (f"<!-- ============ CMS MEDIA PLACEHOLDER {_n[0]}: {label.upper()} ============\n"
               f"     HOW TO REPLACE: {instr}\n"
               f"     Recommended file: {spec}\n"
               f"     Alt text to use: \"{alt}\"\n"
               f"     Then delete this gray box (the <td> below) or paste the snippet in its place:\n"
               f"       <img src=\"[PASTE CMS MEDIA URL]\" alt=\"{alt}\" width=\"{w}\" style=\"display:block;width:100%;height:auto;border:0;border-radius:{r};\">\n"
               f"     ============================================================== -->\n")
    lab = "[CMS MEDIA]" if circle else f"[CMS MEDIA: {label}]"
    td = (f'<td align="center" valign="middle" height="{h_}" bgcolor="{LGRAY}" style="height:{h_}px;background-color:{LGRAY};'
          f'border:2px dashed {GOLD};border-radius:{r};font-family:{B};font-size:{size}px;color:{TGRAY};text-align:center;">{lab}</td>')
    return comment + T(TR(td), width=str(w) if circle else "100%", style=f"border-radius:{r};")

def section(inner, bg=WHITE, pad="0 0"):
    return f'<tr><td align="center" bgcolor="{bg}" style="background-color:{bg};padding:{pad};">' + T(inner, style="max-width:none;table-layout:fixed;") + "</td></tr>"

# HERO  (mockup: 2 equal cols, gap 64, padding 16 80 64)
hero_left = (eyebrow("Kids & Youth", MAROON, 15, "0.16em") + sp(20)
    + h("h1", "Youth Ministry", 64, MAROON, lh="1.04") + sp(20)
    + txt("Helping children and teens grow in faith, from the nursery through 12th grade.", 21, TGRAY, extra="line-height:1.5;") + sp(28)
    + T(TR(TD(btn("Plan your child&rsquo;s first visit", "#", MAROON, WHITE), valign="top"), gap_col(16),
           TD(btn("Contact the leader", "#contact"), valign="top")), width="auto"))
hero_right = media("Hero photo - youth group together", 700, 400,
    "In the CMS page editor, open this block in Source/HTML view. Click the image icon or choose Insert Media, pick the hero photo from the media library, and set the width to 100%.",
    "Youth group together", radius=20, size=16, spec="1400 x 800 px JPG or WebP, landscape, under 300 KB")
hero = section(TR(TD(hero_left, valign="middle", width="48%", style="width:48%;"), gap_col(64), TD(hero_right, valign="middle", width="52%")), pad="16px 0 64px")

# INFO STRIP (padding 32 40, 4 cols gap 32, radius 20)
def stat(label, main, sub=None, sublink=False):
    s = eyebrow(label, GOLD, 13) + sp(6) + txt(main, 20, WHITE, "600", extra="line-height:1.3;")
    if sub:
        s += sp(6) + (link(sub, "#", f"font-family:{B};font-size:16px;color:{CREAM};") if sublink else txt(sub, 16, CREAM, extra="line-height:1.4;"))
    return TD(s, valign="top", width="23%", style="width:23%;")
strip_inner = TR(stat("Who", "Ages 1 through 12th grade"), gap_col(32),
                 stat("When", "Groups: 2nd Saturday &middot; 11:30 AM", "YDH: 1st &amp; 3rd Sundays during worship"), gap_col(32),
                 stat("Where", "9258 Center Street", "[Room name]"), gap_col(32),
                 stat("Contact", "[Youth leader name]", "[youth ministry email]", True))
strip = section(TR(TD(rounded(T(strip_inner), MAROON, 20, "32px 40px"))))

# MAIN (mockup: 3-col grid gap 64, left spans 2; padding 96 80 80)
about = h("h2", "About Youth Ministry", 40, MAROON) + sp(16) + txt(
    "Youth Discipleship Hour (YDH) meets during morning worship on the 1st and 3rd Sundays for grades K&ndash;12. Youth Ministry Groups meet the 2nd Saturday of each month at 11:30 AM. Teens in grades 7&ndash;12 can also join a Bible class on Thursdays at 7:00 PM on Zoom.",
    19, DARK, extra="line-height:1.65;")
def grp(name, ages, when):
    return txt(name, 24, MAROON, "600", H, "line-height:1.2;") + sp(8) + txt(ages, 16, MAROON, "bold") + sp(8) + txt(when, 17, TGRAY, extra="line-height:1.4;")
g = [("Nursery","Ages 1&ndash;4","[When nursery care is offered]"),("Angelic Group","Kindergarten&ndash;5th grade","2nd Saturday &middot; 11:30 AM"),
     ("Paradise Group","6th&ndash;8th grade","2nd Saturday &middot; 11:30 AM"),("Torchbearers","9th&ndash;12th grade","2nd Saturday &middot; 11:30 AM")]
groups_grid = T(TR(card(grp(*g[0]), width="48%"), gap_col(20), card(grp(*g[1]), width="48%")) + gap_row(20, 3)
                + TR(card(grp(*g[2]), width="48%"), gap_col(20), card(grp(*g[3]), width="48%")))
groups = h("h2", "Groups by age", 40, MAROON) + sp(24) + groups_grid
def ph(i):
    return TD(media(f"Photo {i}", 300, 200, "Open this cell in Source/HTML view, choose Insert Media, and select a ministry photo from the media library. Keep all three photos the same shape so the row stays even.",
              "Youth ministry activity", radius=12, spec="600 x 400 px JPG or WebP, 3:2 landscape, under 150 KB"), valign="top", width="32%", style="width:32%;")
photos = h("h2", "Photos", 40, MAROON) + sp(24) + T(TR(ph(1), gap_col(16), ph(2), gap_col(16), ph(3)))
left = about + sp(56) + groups + sp(56) + photos

def event(mon, day, title, sub):
    badge = TD(txt(mon, 12, GOLD, "bold", extra="line-height:1.3;text-align:center;") + txt(day, 22, WHITE, "normal", H, "line-height:1.2;text-align:center;"),
               align="center", valign="middle", width="60", height="60", bgcolor=MAROON,
               style=f"width:60px;height:60px;background-color:{MAROON};border-radius:10px;text-align:center;")
    body = TD(link(txt(title, 18, DARK, "bold", extra="line-height:1.3;"), "#", "") + txt(sub, 15, TGRAY, extra="line-height:1.4;padding-top:2px;"), valign="middle")
    return T(TR(badge, gap_col(16), body))
coming = eyebrow("Coming up") + sp(18) + event("DEC","4","FBC Youth Christmas Parade","[Time &middot; place]") + sp(18) \
    + event("[MON]","[00]","[Next youth event]","[Time &middot; place]") + sp(18) \
    + link("Full calendar &rarr;", "#", f"font-family:{B};font-size:16px;font-weight:bold;color:{MAROON};")
leader_photo = media("Leader headshot", 72, 72, "Open this cell in Source/HTML view, choose Insert Media, and select the youth leader's headshot. The image will display as a circle.",
    "Youth leader headshot", size=12, circle=True, spec="300 x 300 px square JPG or WebP, face centered, under 60 KB")
leader = ('<a id="contact" name="contact"></a>' + eyebrow("Meet the leader") + sp(16)
    + T(TR(TD(leader_photo, valign="middle", width="72", style="width:72px;"), gap_col(16),
           TD(txt("[Youth leader name]", 22, MAROON, "600", H, "line-height:1.2;") + txt("[Role]", 15, TGRAY, extra="padding-top:2px;"), valign="middle"))) + sp(16)
    + btn("Send a message", "#", GOLD, DARK, 17, "13px 20px", full=True))
parents = eyebrow("For parents") + sp(12) + link("[Permission slip] (PDF)", "#", f"font-family:{B};font-size:17px;font-weight:600;color:{MAROON};") + sp(12) \
    + link("[Youth schedule] (PDF)", "#", f"font-family:{B};font-size:17px;font-weight:600;color:{MAROON};")
sidebar = T(TR(card(coming, pad=32)) + gap_row(24) + TR(card(leader, pad=32)) + gap_row(24) + TR(card(parents, bg=LGRAY, pad=32, border=False)))
main = section(TR(TD(left, valign="top", width="65%", style="width:65%;"), gap_col(64), TD(sidebar, valign="top")), pad="96px 0 80px")

# CTA (padding 56 64, gap 48, radius 20)
cta_inner = TR(TD(h("h2", "Bring your kids this Sunday", 44, WHITE) + sp(10)
                  + txt("Worship starts at 9:00 AM. We&rsquo;ll help you find the right group when you arrive.", 19, CREAM, extra="line-height:1.5;"), valign="middle"),
               gap_col(48), TD(btn("Plan a Visit", "#", GOLD, DARK, 19, "18px 36px"), valign="middle", align="right", style="white-space:nowrap;"))
cta = section(TR(TD(rounded(T(cta_inner), DEEP, 20, "56px 64px"))), pad="0 0")

# MORE (padding 96 80, cards gap 24)
def more(t, s):
    return card(link(txt(t, 24, MAROON, "600", H, "line-height:1.2;"), "#", "") + sp(6) + txt(s, 16, TGRAY, extra="line-height:1.4;"), pad=28, width="32%")
more_inner = (TR(TD(h("h2", "More for young people", 36, MAROON), colspan=5)) + gap_row(32, 5)
    + TR(more("Hand &amp; Step Team","Ages 5&ndash;12 and 13+ &middot; Mondays 6:30 PM"), gap_col(24),
         more("Youth Praise Dance","Ages 5&ndash;18 &middot; Wednesdays 6:30 PM"), gap_col(24),
         more("Youth Choir","Ages 5&ndash;12 &middot; sings 2nd Sundays")))
more_s = section(more_inner, bg=LGRAY, pad="96px 0 96px")
gapwhite = f'<tr><td height="96" bgcolor="{WHITE}" style="height:96px;font-size:0;line-height:0;background-color:{WHITE};">&nbsp;</td></tr>'

header = f"""<!-- =====================================================================
  FBC YOUTH MINISTRY PAGE - CMS EMBED
  First Baptist Church of Manassas

  HOW TO USE
  1. In your CMS page editor, switch the content block to Source / HTML / Embed view.
  2. Paste everything from the <link> line (or the first <table>) to the last </table>.
  3. Replace each gray "CMS MEDIA" box using the instructions in the comment above it.
  4. Replace [bracketed] text with real content, then swap each href="#" for a real URL.

  FONTS (same as the mockup): Fraunces for headings, Source Sans 3 for body text.
  The <link> line below loads them from Google Fonts. If your CMS strips <link> tags,
  add that same URL to your site's <head> instead. Without it the page falls back to
  Georgia (headings) and Arial (body); nothing breaks.

  ABOUT THE BUILD
  - All styling is inline CSS. No <style> tags, classes, scripts or CSS variables.
  - Side-by-side columns are HTML tables.
  - The site header, top bar, breadcrumb and footer from the mockup are NOT included;
    your CMS template supplies them. This embed is the page content only.
  - Sizes and corner radii match the mockup (cards 16px, bands 20px, photos 12px,
    buttons fully round). Layout is full width: it fills its container edge to edge with no side padding (your CMS supplies that).

  FBC COLOR CODES USED
    #6B1735 Maroon       headings, primary buttons, info strip
    #4B1026 Deep Maroon  call-to-action band
    #C9A55C Gold         accents, secondary buttons, card borders, placeholder outlines
    #F7F3EC Cream        cards
    #F2F2F2 Light Gray   featured sections, parent-resources card, image placeholders
    #666666 Text Gray    secondary text
    #ffffff White        primary-button text, backgrounds
    #171717 Dark Gray    body text, text on gold buttons
====================================================================== -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&amp;family=Source+Sans+3:wght@400;600;700&amp;display=swap">
"""
doc = header + T(hero + strip + main + cta + gapwhite + more_s, width="100%", bg=WHITE, style=f"background-color:{WHITE};font-family:{B};color:{DARK};")
import os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
open(R+"fbc-youth-ministry-embed.html","w").write(doc+"\n")

# clean copy (keep the font <link>, it is not a comment)
clean = re.sub(r'<!--.*?-->\s*','',doc,flags=re.S).strip()+"\n"
open(R+"fbc-youth-ministry-embed-clean.html","w").write(clean)

# annotated copy
s = doc
s = re.sub(r'\A<!--.*?-->\n','<!-- FBC Youth Ministry embed: paste into CMS HTML view; inline CSS + tables only; fonts load via the <link> below (Fraunces + Source Sans 3); replace gray CMS MEDIA boxes and [bracketed] text -->\n',s,flags=re.S)
sizes={"1":"1400x800 JPG","2":"600x400 JPG","3":"600x400 JPG","4":"600x400 JPG","5":"300x300 JPG"}
s = re.sub(r'<!-- =+ CMS MEDIA PLACEHOLDER (\d+): (.*?) =+\n.*?=+ -->\n',
           lambda m: f'<!-- IMAGE {m.group(1)}: {m.group(2).capitalize()} - swap gray box for CMS media ({sizes[m.group(1)]}) -->\n', s, flags=re.S)
names=["SECTION 1: Hero - title, intro, buttons, photo (2 columns)","SECTION 2: Info strip - Who / When / Where / Contact (4 columns)",
       "SECTION 3: Main content - text and cards left, sidebar right (2 columns)","SECTION 4: Call to action - Bring your kids this Sunday",
       "SECTION 5: More for young people - 3 linked cards"]
it = iter(names)
s = re.sub(r'<tr><td align="center" bgcolor="#(?:ffffff|F2F2F2)" style="background-color:[^"]*;padding:(?!96px 0 96px";">)|<tr><td align="center" bgcolor="#F2F2F2"',
           lambda m: f'<!-- {next(it)} -->\n'+m.group(0), s, flags=re.I)
for marker,c in [('>About Youth Ministry<','About text'),('>Groups by age<','Groups by age - 2x2 cards'),('>Photos<','Photos - 3 images'),
                 ('>COMING UP<','Sidebar: Coming up - event list'),('>MEET THE LEADER<','Sidebar: Meet the leader - headshot and message button'),('>FOR PARENTS<','Sidebar: For parents - PDF links')]:
    i=s.find(marker); assert i>=0,marker
    j=max(s.rfind('<h2',0,i), s.rfind('<div',0,i)); s=s[:j]+f'<!-- {c} -->'+s[j:]
open(R+"fbc-youth-ministry-embed-annotated.html","w").write(s)
for f in ("embed","embed-clean","embed-annotated"):
    t=open(R+f"fbc-youth-ministry-{f}.html").read(); print(f,len(re.findall(r'<!--.*?-->',t,flags=re.S)),t.count("<table"),t.count("</table>"))
