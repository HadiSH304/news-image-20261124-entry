#!/usr/bin/env python3
"""compose.py — builds image.jpg for news-image-20261124.

A 38-story newspaper front page for Tuesday 24 November 2026, drawn fresh
with PIL (local build only; main.py is stdlib-only and only copies the
committed image). Flat vector illustration only: no photos, no recognisable
faces, no hands. Every word is renderer-typeset.

v3 (slot 3, Wed 2026-11-25 19:56 WIB): re-rendered at JPEG quality 55
(JPEG_QUALITY) — the only change vs v1/v2, whose image was q45. Content,
layout, text and main.py are untouched.

Typography (per ~/workspace/makefun/typography-study.md): Playfair Display
Black/Bold for the date and lead headlines; Archivo Narrow 600/700 for
cards, labels and ALL figure strips (tabular digits, x-height 0.526);
Newsreader SemiBold for decks and the DATE CHECK. Barlow SC is retired.
Size floors honoured where the 1024 canvas allows: lead headlines 44px,
card headlines 27px, figure strips 34px figures / 26px labels, DATE CHECK
and sources 22px. Two documented deviations: (1) the date is set at the
largest size that fits full-width in Playfair Black (76px — 110px would
need 1384px; measured); it is still the largest text on the page, as in
the winning entries. (2) Region-bar labels and UTC times are secondary
labels below the strip floor — the winners' grammar puts them there, and
a 26px region label cannot fit a 142px segment.

Layout (1024x1024): navy masthead band -> huge serif date -> count strip
-> numbers strip -> region bar -> UTC strip -> 3 large lead panels ->
2 rows of 6 cards -> dotted world map + 23 briefs (3 columns) -> boxed
DATE CHECK -> sources line.

Story selection (research: news24-analysis/research.md, >=2 sources each;
field: news24-analysis/field-analysis.md):
- Leads: the Tue-night drone war (699 claimed downed, Zaporizhzhia 2/44),
  the Russian drone's ~8 minutes in Polish airspace + NATO AWACS, and the
  Shanghai Politburo purge (Chen Jining) — the day's biggest political story,
  carried in the field's #4 title but led by no top-3 page.
- Cards: Baghdad oilfields, Gaza Hamas chief, Malaysia-Rohingya, Sanofi $41bn,
  Korea ADIZ, Hasina 16 Dec, Solomons pact, Bougainville, UN AI debate,
  Geneva chess, CAS/Senegal, Nepal quake — the verified consensus set.
- Briefs: the full Tuesday evening package the early (Tuesday-built) field
  lacks — Champions League results, US close (Dow 50,019), Huawei verdict,
  Nvidia -5.9%, plus Libya, femicide report, UK heat deaths, Cikande toll,
  Hormuz follow-up, Sparta II, Riyadh drone, quasar, Giuliani, Sarkozy,
  Kim Yo Jong, CIA breach, turkeys, Putin, Germany/Delta, EU LNG,
  Ukraine EUR115bn, Kushner, Sooryavanshi 204.
- Field figures corrected where research proved otherwise: Hormuz has NO new
  Tue IRGC claim (claims were Fri 20 + Mon 23 Nov; UKMTO unconfirmed) —
  carried as a follow-up, not a strike; Sputnik-S first reported MON 23 Nov
  (not Tue); Nvidia +31.5% is Monday's close (Tue: -5.9%); chess is in
  GENEVA (Berlin is the opening); Nepal M5.3 (M5.6 in Nepal); Cikande toll
  26 (missing disputed 8 vs 28 — toll only); Gaza "48 wounded" -> 44;
  Poland drone "~9 min" -> ~8; Korea alert "3 minutes" -> "minutes later";
  Shenzhou-24 crew unveiled Tue, launch Wed; Solomons-Australia signing Wed.
"""
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

W, H = 1024, 1024
JPEG_QUALITY = 55  # v3 re-render: q55 (v1/v2 image was q45); higher quality,
# still well under the 1,048,576-byte cap.
CREAM = (247, 243, 232)
PAPER = (250, 247, 238)
NAVY = (14, 30, 58)
NAVY2 = (20, 42, 78)
RED = (168, 32, 26)
RED2 = (196, 48, 36)
INK = (22, 22, 22)
GREY = (90, 88, 80)
LGREY = (120, 118, 108)
RULE = (180, 172, 150)
TAN = (188, 166, 122)
MAPSEA = (214, 206, 182)
MAPLAND = (232, 222, 196)

REGION_COLORS = {
    "EUROPE": (31, 122, 109),
    "ASIA": (165, 95, 18),
    "MIDDLE EAST": (169, 50, 38),
    "AMERICAS": (46, 95, 163),
    "AFRICA": (138, 109, 59),
    "OCEANIA": (108, 74, 138),
    "GLOBAL": (70, 70, 70),
}

TAG_COLORS = {
    "CONFIRMED": (31, 122, 60),
    "OFFICIAL": (46, 95, 163),
    "REPORTED": (46, 95, 163),
    "CLAIM": (150, 95, 5),
}


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


F_DATE = lambda s: font("PlayfairDisplay-Black.ttf", s)
F_HEAD = lambda s: font("PlayfairDisplay-Bold.ttf", s)
F_DECK = lambda s: font("Newsreader-Regular.ttf", s)
F_DECKB = lambda s: font("Newsreader-SemiBold.ttf", s)
F_AN = lambda s: font("archivo-narrow-v35-latin-700.ttf", s)
F_ANM = lambda s: font("archivo-narrow-v35-latin-600.ttf", s)

TRUNCATED = []


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def fit_lines(draw, text, f, max_w, max_lines, tag=""):
    """Greedy word-wrap; records a warning (never silently drops text)."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        TRUNCATED.append((tag, text, len(lines), max_lines))
        lines = lines[:max_lines]
    return lines


def draw_lines(draw, lines, x, y, f, fill, leading):
    for i, ln in enumerate(lines):
        draw.text((x, y + i * leading), ln, font=f, fill=fill)
    return y + len(lines) * leading


def center(draw, y, s, f, fill, cx=W // 2):
    w = draw.textlength(s, font=f)
    draw.text((cx - w / 2, y), s, font=f, fill=fill)
    return w


def chip(draw, x, y, s, f, fg, bg=None, pad_x=4, pad_y=2):
    w = draw.textlength(s, font=f) + 2 * pad_x
    h = f.size + 2 * pad_y
    if bg is not None:
        draw.rounded_rectangle([x, y, x + w, y + h], radius=2, fill=bg)
    draw.text((x + pad_x, y + pad_y - 1), s, font=f, fill=fg)
    return w


def tracked(draw, x, y, s, f, fill, tracking=0.06):
    """Draw all-caps text with letter tracking (em fraction per char)."""
    cx = x
    adv = f.size * tracking
    for ch in s:
        draw.text((cx, y), ch, font=f, fill=fill)
        cx += draw.textlength(ch, font=f) + adv
    return cx - x


# --- dotted world map -------------------------------------------------------
# Coarse land bitmap, 64 columns (lon -180..180) x 28 rows (lat 78..-58).
LAND = [
    "................................................................",
    "....XXXXXX......................................................",
    "...XXXXXXXXXX...........XXXXXXX..................................",
    "..XXXXXXXXXXXXXX.......XXXXXXXXX.........XXXXXXXX.................",
    "..XXXXXXXXXXXXXXXX....XXXXXXXXXX.......XXXXXXXXXXXXX.............",
    "...XXXXXXXXXXXXXXX.....XXXXXXXXX.......XXXXXXXXXXXXXXXX..........",
    "....XXXXXXXXXXXXX.......XXXXXXX.........XXXXXXXXXXXXXXXXXX.......",
    ".....XXXXXXXXXXX.........XXXXX..........XXXXXXXXXXXXXXXXX........",
    "......XXXXXXXXX...........XXX...........XXXXXXXXXXXXXXXX.........",
    ".......XXXXXXX.............X.............XXXXXXXXXXXXX...........",
    "........XXXXX.............................XXXXXXXXXX.............",
    ".........XXX...............................XXXXXXXX..............",
    "..........XX................................XXXXXX..............",
    "...........X.................................XXXX...............",
    "..............................................XX................",
    "..............................................XX................",
    ".............................................XXXX...............",
    "............................................XXXXXX..............",
    "...........................................XXXXXXXX.............",
    "............................................XXXXXX..............",
    ".............................................XXXX...............",
    "..............................................XX................",
    "................................................................",
    "................................................................",
    "................................................................",
    "................................................................",
    "................................................................",
    "................................................................",
]


def lonlat_to_xy(lon, lat, box):
    x0, y0, bw, bh = box
    x = x0 + (lon + 180.0) / 360.0 * bw
    y = y0 + (78.0 - lat) / 136.0 * bh
    return x, y


def draw_map(draw, box, pins):
    """pins: list of (num, lon, lat, dx, dy). Dark navy sea, tan land dots."""
    x0, y0, bw, bh = box
    draw.rectangle([x0, y0, x0 + bw, y0 + bh], fill=NAVY)
    cw, ch = bw / 64.0, bh / 28.0
    for r, row in enumerate(LAND):
        for c, ch_ in enumerate(row):
            if ch_ == "X":
                cx = x0 + c * cw + cw / 2
                cy = y0 + r * ch + ch / 2
                draw.ellipse([cx - 2.2, cy - 2.2, cx + 2.2, cy + 2.2],
                             fill=(216, 202, 164))
    ey = lonlat_to_xy(0, 0, box)[1]
    draw.line([x0, ey, x0 + bw, ey], fill=(90, 110, 150), width=1)
    for num, lon, lat, dx, dy in pins:
        px, py = lonlat_to_xy(lon, lat, box)
        px += dx
        py += dy
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                     outline=(255, 255, 255), width=1)
        t = str(num)
        tw = draw.textlength(t, font=F_AN(9))
        draw.text((px - tw / 2, py - 6), t, font=F_AN(9), fill=(255, 255, 255))
    return box


# --- story data -------------------------------------------------------------
# Verified Tue 24 Nov 2026 (research: news24-analysis/research.md, >=2
# sources each). Region counts sum to 38.
NUMBERS = [
    ("699", "DRONES"),
    ("$41bn", "SANOFI"),
    ("6,500", "ROHINGYA"),
    ("47,000", "FEMICIDES"),
    ("204", "53 BALLS"),
    ("50,019", "DOW"),
]
REGIONS = [
    ("EUROPE", 11), ("ASIA", 8), ("MIDDLE EAST", 5),
    ("AMERICAS", 6), ("AFRICA", 3), ("OCEANIA", 2), ("GLOBAL", 3),
]
TIMELINE = [
    ("07:02", "Nepal quake"),
    ("07:52", "Ulleung alert"),
    ("08:00", "Hanoi blast"),
    ("19:30", "Shanghai bulletin"),
    ("21:00", "Dow 50,019"),
]

LEADS = [
    {
        "n": 1, "place": "KYIV / ZAPORIZHZHIA", "beat": "WAR",
        "banner": "699 DOWNED",
        "head": "699 drones downed",
        "deck": ("Russia claims 699 downed; Zaporizhzhia strike kills 2, "
                 "wounds 44."),
        "src": "Reuters \u00b7 AP \u00b7 AFP", "tag": "CLAIM",
    },
    {
        "n": 2, "place": "DOROHUSK, POLAND", "beat": "AIRSPACE",
        "banner": "8 MIN IN POLAND",
        "head": "Russian drone enters Poland",
        "deck": ("Geran-5 flies ~8 minutes over Poland; NATO sends AWACS "
                 "jets."),
        "src": "Reuters \u00b7 AP", "tag": "CONFIRMED",
    },
    {
        "n": 3, "place": "SHANGHAI, CHINA", "beat": "POLITICS",
        "banner": "POLITBURO PURGE",
        "head": "Purge hits Shanghai chief",
        "deck": ("Chen Jining, 62, probed for graft; 4th Politburo member "
                 "in a term."),
        "src": "Xinhua \u00b7 Reuters", "tag": "CONFIRMED",
    },
]

# n, place, beat, banner, head (<=27 chars), deck (<=52 chars), src, tag
CARDS = [
    (4, "BAGHDAD", "OIL", "4 PROVINCES",
     "Baghdad takes oilfields",
     "PM orders Oil Ministry to run 4 provinces' fields.",
     "Reuters \u00b7 Iraq Oil Report", "CONFIRMED"),
    (5, "GAZA CITY", "WAR", "7 KILLED",
     "Hamas chief killed",
     "Abu Nahel killed in Gaza City; 7 dead Tuesday.",
     "Reuters \u00b7 AP", "CONFIRMED"),
    (6, "KUALA LUMPUR", "REFUGEES", "6,500",
     "Rohingya to return",
     "1,500 by ship, 5,303 by air in Dec.",
     "AFP \u00b7 Reuters", "CONFIRMED"),
    (7, "PARIS", "PHARMA", "$41BN",
     "Sanofi buys Insmed",
     "$175 a share; biggest pharma deal of 2026.",
     "Reuters \u00b7 AP", "CONFIRMED"),
    (8, "ULLEUNG", "AIRSPACE", "ADIZ",
     "Jets enter Korea's ADIZ",
     "Ulleung told to shelter; alert lifted minutes later.",
     "Yonhap \u00b7 Reuters", "CONFIRMED"),
    (9, "DHAKA", "POLITICS", "16 DEC",
     "Hasina plans 16 Dec return",
     "Dhaka: only in handcuffs, by extradition.",
     "Reuters \u00b7 AFP", "CONFIRMED"),
    (10, "HONIARA", "PACT", "PACT ENDS",
     "Solomons ends pact",
     "Won't renew 2022 security pact; Australia deal next.",
     "SMH \u00b7 Reuters", "CONFIRMED"),
    (11, "PORT MORESBY", "VOTE", "89 OF 118",
     "Bougainville votes",
     "PNG votes on 2019 result; 89 of 118 MPs needed.",
     "Reuters \u00b7 AP", "CONFIRMED"),
    (12, "NEW YORK", "UN", "AI \u00b7 WAR",
     "UN debates AI and war",
     "Guterres: no place for killer robots.",
     "UN News \u00b7 Reuters", "CONFIRMED"),
    (13, "GENEVA", "CHESS", "GAME 1 DRAW",
     "Chess title match opens",
     "Gukesh\u2013Sindarov Game 1 drawn in 38 moves.",
     "FIDE \u00b7 Reuters", "CONFIRMED"),
    (14, "DAKAR", "FOOTBALL", "AFCON",
     "CAS restores Senegal title",
     "1\u20130 final win reinstated; Morocco to appeal.",
     "Reuters \u00b7 AP", "CONFIRMED"),
    (15, "TAPLEJUNG", "QUAKE", "M5.3",
     "Quake shakes Nepal",
     "M5.3 (M5.6 in Nepal); felt across the region.",
     "USGS \u00b7 Reuters", "CONFIRMED"),
]

# n, region-word, text (kept short; 3-column briefs)
BRIEFS = [
    (16, "LIBYA", "2 sailors die of Benghazi wounds"),
    (17, "FEMICIDE", "47,000 killed by partners"),
    (18, "UK HEAT", "5,258 heat deaths, most since 2016"),
    (19, "CIKANDE", "fire toll rises to 26"),
    (20, "HORMUZ", "no new mine claim; Brent climbs"),
    (21, "SPARTA II", "Zelensky confirms Kyiv strike"),
    (22, "RIYADH", "11 hurt in PIF Tower hit"),
    (23, "QUASAR", "most distant quasar found, z=8.13"),
    (24, "GIULIANI", "gets Medal of Freedom at 82"),
    (25, "SARKOZY", "ordered to trial with Bruni"),
    (26, "PYONGYANG", "threatens Swiss pullout"),
    (27, "CIA", "unclassified network breached"),
    (28, "TURKEYS", "Trump pardons Freedom, Feathers"),
    (29, "CHAMPIONS", "Real Madrid 5\u20131 PSV"),
    (30, "NVIDIA", "falls 5.9% as chips rout"),
    (31, "HUAWEI", "guilty on 10 of 12 counts"),
    (32, "PUTIN", "retaliation \u2018inevitable\u2019 on refineries"),
    (33, "DOW", "first close above 50,000"),
    (34, "GERMANY", "first to get Ukraine\u2019s Delta"),
    (35, "LNG", "EU to end Russian LNG from Jan 1"),
    (36, "UKRAINE", "needs \u20ac115bn for 2027"),
    (37, "KUSHNER", "pushes peace deal by January"),
    (38, "CRICKET", "Sooryavanshi, 15, hits 204 off 53"),
]

# num, lon, lat, dx, dy — pins for leads 1-3 + cards 4-15.
# Europe/ME + East Asia clusters need fan-out offsets (map is 300px wide
# for 360 deg, so 1 deg lon ~ 0.83px); offsets verified numerically below.
PINS = [
    (1, 30.52, 50.45, 0, -10),      # Kyiv
    (2, 23.50, 51.15, -24, -16),    # Chelm, Poland — offset from Kyiv
    (3, 121.47, 31.23, 0, 0),       # Shanghai
    (4, 44.37, 33.31, 14, 8),       # Baghdad
    (5, 34.47, 31.50, -20, 16),     # Gaza City — offset from Baghdad
    (6, 101.69, 3.14, 14, 4),       # Kuala Lumpur — offset from Dhaka
    (7, 2.35, 48.86, -12, 12),      # Paris
    (8, 130.90, 37.50, 14, -8),     # Ulleung — offset from Shanghai
    (9, 90.41, 23.81, 0, 16),       # Dhaka — offset from Taplejung
    (10, 159.97, -9.65, 0, 0),      # Honiara
    (11, 155.00, -6.30, -14, -10),  # Bougainville — offset from Honiara
    (12, -74.01, 40.71, 0, 0),      # New York (UN)
    (13, 6.14, 46.20, 24, 8),       # Geneva — offset from Paris/Kyiv
    (14, -17.47, 14.72, 0, 10),     # Dakar — offset from Paris
    (15, 87.90, 27.60, 6, -6),      # Taplejung — offset from Dhaka
]

DATE_CHECK = (
    "DATE CHECK \u2014 Left out: Huang (Mon) \u00b7 COP31 (Sun) \u00b7 Kh-101s "
    "(Fri) \u00b7 El Chapo (Fri) \u00b7 Cikande fire (Sat) \u00b7 Sputnik-S "
    "(Mon). Not yet: Shenzhou-24 \u00b7 Solomons treaty \u00b7 Shenzhen summit."
)

SOURCES = ("SOURCES: REUTERS \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 AL JAZEERA "
           "\u00b7 YONHAP \u00b7 XINHUA \u00b7 FIDE \u2014 TUESDAY 24 NOVEMBER 2026")


# --- lead art (full scenes, flat vector, no faces) --------------------------
def lead_art(draw, idx, x0, y0, w, h):
    if idx == 0:
        # Drone war: night sky over a Kyiv skyline, interception flashes,
        # small drone silhouettes on dotted paths, moon.
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(16, 22, 44))
        draw.ellipse([x0 + 0.80 * w, y0 + 0.06 * h, x0 + 0.90 * w, y0 + 0.26 * h],
                     fill=(240, 230, 190))
        # skyline: dark blocks with lit windows
        for fx, fw, fh in [(0.02, 0.16, 0.42), (0.20, 0.12, 0.55), (0.34, 0.18, 0.36),
                           (0.54, 0.12, 0.50), (0.68, 0.14, 0.40), (0.84, 0.14, 0.58)]:
            draw.rectangle([x0 + fx * w, y0 + (1 - fh) * h, x0 + (fx + fw) * w, y0 + h],
                           fill=(8, 12, 26))
            for wy in (0.62, 0.74, 0.86):
                for wx in (0.04, 0.09):
                    draw.rectangle([x0 + (fx + wx) * w, y0 + wy * h,
                                    x0 + (fx + wx) * w + 3, y0 + wy * h + 3],
                                   fill=(250, 210, 110))
        # interception flashes: orange starbursts
        for fx, fy, r in [(0.30, 0.30, 9), (0.62, 0.20, 7), (0.78, 0.42, 6)]:
            cx, cy = x0 + fx * w, y0 + fy * h
            draw.polygon([(cx, cy - r), (cx + 2, cy - 2), (cx + r, cy),
                          (cx + 2, cy + 2), (cx, cy + r), (cx - 2, cy + 2),
                          (cx - r, cy), (cx - 2, cy - 2)], fill=(250, 170, 60))
            draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 230, 150))
        # drone silhouettes on dotted paths
        for i in range(5):
            fx = 0.12 + i * 0.05
            fy = 0.18 + i * 0.02
            draw.ellipse([x0 + fx * w - 1.5, y0 + fy * h - 1.5,
                          x0 + fx * w + 1.5, y0 + fy * h + 1.5], fill=(200, 200, 210))
        draw.polygon([(x0 + 0.44 * w, y0 + 0.34 * h), (x0 + 0.50 * w, y0 + 0.32 * h),
                      (x0 + 0.50 * w, y0 + 0.36 * h), (x0 + 0.44 * w, y0 + 0.36 * h)],
                     fill=(180, 185, 195))
        draw.line([x0 + 0.44 * w, y0 + 0.34 * h, x0 + 0.38 * w, y0 + 0.30 * h],
                  fill=(180, 185, 195), width=1)
    elif idx == 1:
        # Poland airspace: dawn sky, radar arcs, a small recon drone,
        # an AWACS-style plane silhouette with radar dome.
        for i, col in enumerate([(250, 214, 170), (244, 190, 150), (232, 160, 130),
                                 (218, 140, 120)]):
            draw.rectangle([x0, y0 + i * h / 4, x0 + w, y0 + (i + 1) * h / 4], fill=col)
        draw.ellipse([x0 + 0.06 * w, y0 + 0.08 * h, x0 + 0.16 * w, y0 + 0.28 * h],
                     fill=(255, 240, 200))
        # radar arcs from lower left
        for r in (18, 32, 46):
            draw.arc([x0 + 0.10 * w - r, y0 + h - r, x0 + 0.10 * w + r, y0 + h + r],
                     start=270, end=360, fill=(120, 60, 60), width=3)
        draw.ellipse([x0 + 0.10 * w - 4, y0 + h - 8, x0 + 0.10 * w + 4, y0 + h],
                     fill=(168, 32, 26))
        # recon drone (larger dark quad silhouette, upper middle)
        dx, dy = x0 + 0.58 * w, y0 + 0.30 * h
        draw.rectangle([dx - 14, dy - 3, dx + 14, dy + 3], fill=(40, 40, 50))
        draw.ellipse([dx - 20, dy - 6, dx - 10, dy + 6], fill=(40, 40, 50))
        draw.ellipse([dx + 10, dy - 6, dx + 20, dy + 6], fill=(40, 40, 50))
        draw.rectangle([dx - 3, dy - 8, dx + 3, dy + 8], fill=(40, 40, 50))
        # dotted flight path behind it
        for i in range(5):
            fx = 0.28 + i * 0.06
            draw.ellipse([x0 + fx * w - 2, y0 + 0.34 * h - 2,
                          x0 + fx * w + 2, y0 + 0.34 * h + 2], fill=(120, 60, 60))
        # AWACS plane with dome, low right (larger, light grey on dusk)
        px, py = x0 + 0.62 * w, y0 + 0.66 * h
        draw.polygon([(px, py), (px + 0.30 * w, py - 5), (px + 0.30 * w, py + 5)],
                     fill=(240, 235, 225))
        draw.polygon([(px + 0.02 * w, py), (px + 0.12 * w, py - 12),
                      (px + 0.20 * w, py)], fill=(240, 235, 225))
        draw.ellipse([px + 0.11 * w, py - 15, px + 0.19 * w, py - 5],
                     fill=(240, 235, 225))
        draw.polygon([(px + 0.04 * w, py), (px + 0.12 * w, py + 10),
                      (px + 0.18 * w, py)], fill=(220, 215, 205))
        # ground line
        draw.rectangle([x0, y0 + 0.88 * h, x0 + w, y0 + h], fill=(90, 70, 70))
    else:
        # Shanghai: dusk skyline with the Oriental Pearl Tower (two spheres
        # on a needle — the city's silhouette), dark towers, red sun disc.
        for i, col in enumerate([(250, 200, 150), (240, 170, 130), (226, 140, 120),
                                 (210, 120, 110)]):
            draw.rectangle([x0, y0 + i * h / 4, x0 + w, y0 + (i + 1) * h / 4], fill=col)
        draw.ellipse([x0 + 0.78 * w, y0 + 0.10 * h, x0 + 0.90 * w, y0 + 0.34 * h],
                     fill=(196, 48, 36))
        # Pearl Tower: needle + two spheres, centre-left
        tx = x0 + 0.30 * w
        draw.rectangle([tx - 2, y0 + 0.18 * h, tx + 2, y0 + 0.92 * h], fill=(70, 55, 60))
        draw.ellipse([tx - 12, y0 + 0.22 * h, tx + 12, y0 + 0.44 * h], fill=(70, 55, 60))
        draw.ellipse([tx - 8, y0 + 0.52 * h, tx + 8, y0 + 0.66 * h], fill=(70, 55, 60))
        # dark towers
        for fx, fw, fh in [(0.02, 0.12, 0.45), (0.44, 0.10, 0.60), (0.56, 0.14, 0.40),
                           (0.72, 0.12, 0.55), (0.86, 0.12, 0.48)]:
            draw.rectangle([x0 + fx * w, y0 + (1 - fh) * h, x0 + (fx + fw) * w, y0 + h],
                           fill=(60, 45, 55))
            for wy in (0.66, 0.78, 0.90):
                draw.rectangle([x0 + (fx + 0.03) * w, y0 + wy * h,
                                x0 + (fx + 0.03) * w + 3, y0 + wy * h + 3],
                               fill=(250, 210, 110))
        # river band
        draw.rectangle([x0, y0 + 0.92 * h, x0 + w, y0 + h], fill=(120, 90, 100))


# --- card art (24px mini-scene strips) --------------------------------------
def card_art(draw, n, x0, y0, w, h):
    if n == 4:  # Baghdad: oil derricks + desert sun
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(200, 170, 110))
        draw.ellipse([x0 + 0.80 * w, y0 + 0.10 * h, x0 + 0.92 * w, y0 + 0.55 * h],
                     fill=(250, 220, 130))
        for fx in (0.12, 0.38, 0.62):
            draw.polygon([(x0 + fx * w, y0 + h), (x0 + (fx + 0.05) * w, y0 + 0.25 * h),
                          (x0 + (fx + 0.10) * w, y0 + h)], fill=(60, 50, 45))
            draw.line([x0 + (fx + 0.05) * w, y0 + 0.25 * h, x0 + (fx + 0.05) * w, y0 + h],
                      fill=(60, 50, 45), width=2)
        draw.rectangle([x0, y0 + 0.85 * h, x0 + w, y0 + h], fill=(150, 120, 80))
    elif n == 5:  # Gaza: night skyline + smoke columns
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(30, 30, 50))
        for fx, fw, fh in [(0.05, 0.18, 0.55), (0.28, 0.14, 0.70), (0.46, 0.16, 0.45),
                           (0.66, 0.14, 0.62), (0.84, 0.14, 0.50)]:
            draw.rectangle([x0 + fx * w, y0 + (1 - fh) * h, x0 + (fx + fw) * w, y0 + h],
                           fill=(12, 12, 22))
        for fx, fy in [(0.30, 0.18), (0.36, 0.08), (0.68, 0.14)]:
            draw.ellipse([x0 + fx * w - 4, y0 + fy * h - 3, x0 + fx * w + 4, y0 + fy * h + 3],
                         fill=(150, 145, 140))
        draw.ellipse([x0 + 0.84 * w, y0 + 0.08 * h, x0 + 0.92 * w, y0 + 0.30 * h],
                     fill=(240, 230, 190))
    elif n == 6:  # Malaysia: navy ship + plane over sea
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(24, 90, 120))
        draw.rectangle([x0, y0 + 0.62 * h, x0 + w, y0 + h], fill=(16, 60, 85))
        draw.rectangle([x0 + 0.10 * w, y0 + 0.42 * h, x0 + 0.55 * w, y0 + 0.60 * h],
                       fill=(150, 155, 165))
        draw.rectangle([x0 + 0.38 * w, y0 + 0.28 * h, x0 + 0.44 * w, y0 + 0.42 * h],
                       fill=(150, 155, 165))
        # plane silhouette top right
        px, py = x0 + 0.72 * w, y0 + 0.22 * h
        draw.polygon([(px, py), (px + 0.20 * w, py - 3), (px + 0.20 * w, py + 3)],
                     fill=(240, 240, 235))
        draw.polygon([(px + 0.04 * w, py), (px + 0.10 * w, py - 7),
                      (px + 0.14 * w, py)], fill=(240, 240, 235))
        # wake dots
        for i in range(4):
            fx = 0.60 + i * 0.08
            draw.ellipse([x0 + fx * w - 1.5, y0 + 0.72 * h - 1.5,
                          x0 + fx * w + 1.5, y0 + 0.72 * h + 1.5], fill=(200, 220, 230))
    elif n == 7:  # Sanofi: capsule pills + flask on teal
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(16, 90, 90))
        # flask
        draw.polygon([(x0 + 0.14 * w, y0 + 0.15 * h), (x0 + 0.20 * w, y0 + 0.15 * h),
                      (x0 + 0.20 * w, y0 + 0.45 * h), (x0 + 0.28 * w, y0 + 0.85 * h),
                      (x0 + 0.06 * w, y0 + 0.85 * h), (x0 + 0.14 * w, y0 + 0.45 * h)],
                     fill=(220, 230, 230))
        draw.rectangle([x0 + 0.09 * w, y0 + 0.62 * h, x0 + 0.25 * w, y0 + 0.85 * h],
                       fill=(46, 180, 130))
        # capsules
        for fx, fy, col in [(0.55, 0.35, (240, 90, 60)), (0.72, 0.55, (250, 210, 90)),
                            (0.85, 0.30, (240, 240, 235))]:
            draw.ellipse([x0 + fx * w - 8, y0 + fy * h - 4, x0 + fx * w + 8, y0 + fy * h + 4],
                         fill=col)
            draw.rectangle([x0 + fx * w - 8, y0 + fy * h - 4, x0 + fx * w, y0 + fy * h + 4],
                           fill=(200, 200, 195))
    elif n == 8:  # Korea ADIZ: radar arcs + jet
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(18, 40, 70))
        for r in (8, 16, 24):
            draw.arc([x0 + 0.18 * w - r, y0 + h - r, x0 + 0.18 * w + r, y0 + h + r],
                     start=270, end=360, fill=(120, 200, 240), width=2)
        draw.ellipse([x0 + 0.18 * w - 3, y0 + h - 6, x0 + 0.18 * w + 3, y0 + h],
                     fill=(240, 210, 120))
        # jet silhouette
        jx, jy = x0 + 0.60 * w, y0 + 0.40 * h
        draw.polygon([(jx, jy), (jx + 0.28 * w, jy - 4), (jx + 0.28 * w, jy + 4)],
                     fill=(220, 220, 215))
        draw.polygon([(jx + 0.06 * w, jy), (jx + 0.12 * w, jy - 9),
                      (jx + 0.18 * w, jy)], fill=(220, 220, 215))
        draw.polygon([(jx + 0.06 * w, jy), (jx + 0.12 * w, jy + 9),
                      (jx + 0.18 * w, jy)], fill=(200, 200, 195))
    elif n == 9:  # Hasina: plane over green field + runway
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(140, 190, 160))
        draw.rectangle([x0, y0 + 0.70 * h, x0 + w, y0 + h], fill=(90, 90, 95))
        for i in range(4):
            fx = 0.10 + i * 0.22
            draw.rectangle([x0 + fx * w, y0 + 0.83 * h, x0 + (fx + 0.10) * w, y0 + 0.87 * h],
                           fill=(250, 240, 200))
        px, py = x0 + 0.55 * w, y0 + 0.32 * h
        draw.polygon([(px, py), (px + 0.30 * w, py - 4), (px + 0.30 * w, py + 4)],
                     fill=(250, 250, 245))
        draw.polygon([(px + 0.06 * w, py), (px + 0.12 * w, py - 9),
                      (px + 0.18 * w, py)], fill=(250, 250, 245))
        draw.ellipse([x0 + 0.10 * w, y0 + 0.12 * h, x0 + 0.18 * w, y0 + 0.32 * h],
                     fill=(255, 240, 200))
    elif n == 10:  # Solomons: island + palm + sun
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(90, 160, 200))
        draw.rectangle([x0, y0 + 0.65 * h, x0 + w, y0 + h], fill=(30, 110, 140))
        draw.ellipse([x0 + 0.10 * w, y0 + 0.55 * h, x0 + 0.55 * w, y0 + 0.95 * h],
                     fill=(220, 200, 140))
        draw.ellipse([x0 + 0.78 * w, y0 + 0.10 * h, x0 + 0.90 * w, y0 + 0.42 * h],
                     fill=(250, 220, 130))
        # palm
        draw.line([x0 + 0.30 * w, y0 + 0.65 * h, x0 + 0.30 * w, y0 + 0.30 * h],
                  fill=(90, 70, 50), width=3)
        for dx, dy in [(-12, -6), (12, -6), (-10, 2), (10, 2)]:
            draw.line([x0 + 0.30 * w, y0 + 0.30 * h,
                       x0 + 0.30 * w + dx, y0 + 0.30 * h + dy], fill=(40, 120, 60), width=2)
    elif n == 11:  # Bougainville: ballot box + green check
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(235, 230, 220))
        draw.rectangle([x0 + 0.30 * w, y0 + 0.45 * h, x0 + 0.62 * w, y0 + 0.90 * h],
                       fill=(46, 95, 163))
        draw.rectangle([x0 + 0.42 * w, y0 + 0.30 * h, x0 + 0.50 * w, y0 + 0.45 * h],
                       fill=(250, 247, 238), outline=(46, 95, 163))
        draw.line([x0 + 0.68 * w, y0 + 0.55 * h, x0 + 0.76 * w, y0 + 0.75 * h,
                   x0 + 0.92 * w, y0 + 0.30 * h], fill=(31, 122, 60), width=4)
        draw.ellipse([x0 + 0.08 * w, y0 + 0.15 * h, x0 + 0.20 * w, y0 + 0.50 * h],
                     fill=(250, 220, 130))
    elif n == 12:  # UN AI: blue globe + circuit dots
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(20, 42, 110))
        draw.ellipse([x0 + 0.38 * w, y0 + 0.12 * h, x0 + 0.62 * w, y0 + 0.88 * h],
                     fill=(90, 140, 200))
        draw.ellipse([x0 + 0.44 * w, y0 + 0.20 * h, x0 + 0.56 * w, y0 + 0.45 * h],
                     fill=(120, 170, 220))
        for fx, fy in [(0.14, 0.25), (0.82, 0.30), (0.10, 0.70), (0.86, 0.68),
                       (0.26, 0.80), (0.74, 0.82)]:
            draw.ellipse([x0 + fx * w - 3, y0 + fy * h - 3, x0 + fx * w + 3, y0 + fy * h + 3],
                         fill=(240, 210, 60))
        draw.line([x0 + 0.14 * w, y0 + 0.25 * h, x0 + 0.38 * w, y0 + 0.30 * h],
                  fill=(240, 210, 60), width=1)
        draw.line([x0 + 0.82 * w, y0 + 0.30 * h, x0 + 0.62 * w, y0 + 0.35 * h],
                  fill=(240, 210, 60), width=1)
    elif n == 13:  # Chess: board + king/queen silhouettes
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(60, 45, 35))
        sq = w / 8.0
        for r in range(2):
            for c in range(8):
                if (r + c) % 2 == 0:
                    draw.rectangle([x0 + c * sq, y0 + r * h / 2,
                                    x0 + (c + 1) * sq, y0 + (r + 1) * h / 2],
                                   fill=(240, 225, 200))
        # king + queen pieces (simple silhouettes)
        draw.polygon([(x0 + 0.30 * w, y0 + 0.55 * h), (x0 + 0.34 * w, y0 + 0.15 * h),
                      (x0 + 0.38 * w, y0 + 0.55 * h)], fill=(250, 247, 238))
        draw.ellipse([x0 + 0.31 * w, y0 + 0.10 * h, x0 + 0.37 * w, y0 + 0.22 * h],
                     fill=(250, 247, 238))
        draw.polygon([(x0 + 0.58 * w, y0 + 0.60 * h), (x0 + 0.62 * w, y0 + 0.20 * h),
                      (x0 + 0.66 * w, y0 + 0.60 * h)], fill=(30, 28, 26))
        draw.ellipse([x0 + 0.59 * w, y0 + 0.14 * h, x0 + 0.65 * w, y0 + 0.26 * h],
                     fill=(30, 28, 26))
    elif n == 14:  # CAS/Senegal: green pitch + ball + trophy
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(40, 130, 70))
        draw.ellipse([x0 + 0.42 * w, y0 + 0.20 * h, x0 + 0.58 * w, y0 + 0.80 * h],
                     outline=(250, 250, 245), width=2)
        draw.line([x0 + 0.50 * w, y0, x0 + 0.50 * w, y0 + h], fill=(250, 250, 245), width=2)
        # ball
        draw.ellipse([x0 + 0.12 * w, y0 + 0.30 * h, x0 + 0.26 * w, y0 + 0.70 * h],
                     fill=(250, 250, 245))
        draw.polygon([(x0 + 0.19 * w, y0 + 0.38 * h), (x0 + 0.23 * w, y0 + 0.48 * h),
                      (x0 + 0.15 * w, y0 + 0.48 * h)], fill=(30, 30, 30))
        # trophy
        draw.polygon([(x0 + 0.76 * w, y0 + 0.25 * h), (x0 + 0.88 * w, y0 + 0.25 * h),
                      (x0 + 0.85 * w, y0 + 0.55 * h), (x0 + 0.79 * w, y0 + 0.55 * h)],
                     fill=(240, 210, 60))
        draw.rectangle([x0 + 0.79 * w, y0 + 0.55 * h, x0 + 0.85 * w, y0 + 0.70 * h],
                       fill=(240, 210, 60))
        draw.rectangle([x0 + 0.74 * w, y0 + 0.70 * h, x0 + 0.90 * w, y0 + 0.78 * h],
                       fill=(240, 210, 60))
    else:  # 15 Nepal: mountains + seismograph line
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(90, 120, 140))
        draw.polygon([(x0 + 0.02 * w, y0 + h), (x0 + 0.28 * w, y0 + 0.12 * h),
                      (x0 + 0.52 * w, y0 + h)], fill=(60, 60, 75))
        draw.polygon([(x0 + 0.24 * w, y0 + 0.12 * h), (x0 + 0.28 * w, y0 + 0.22 * h),
                      (x0 + 0.32 * w, y0 + 0.12 * h)], fill=(250, 250, 245))
        draw.polygon([(x0 + 0.48 * w, y0 + h), (x0 + 0.72 * w, y0 + 0.25 * h),
                      (x0 + 0.98 * w, y0 + h)], fill=(80, 80, 95))
        draw.polygon([(x0 + 0.68 * w, y0 + 0.25 * h), (x0 + 0.72 * w, y0 + 0.35 * h),
                      (x0 + 0.76 * w, y0 + 0.25 * h)], fill=(250, 250, 245))
        # seismograph zigzag
        pts = []
        for i, fy in enumerate([0.55, 0.55, 0.30, 0.75, 0.40, 0.62, 0.55, 0.55]):
            pts.append((x0 + (0.05 + i * 0.12) * w, y0 + fy * h))
        draw.line(pts, fill=(196, 48, 36), width=2)


# --- build ------------------------------------------------------------------
MX = 16
CW = W - 2 * MX


def check_pins(box):
    """Verify every pair of pins is >=17px apart after offsets."""
    pts = []
    for num, lon, lat, dx, dy in PINS:
        px, py = lonlat_to_xy(lon, lat, box)
        pts.append((num, px + dx, py + dy))
    worst = (999, None, None)
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d = ((pts[i][1] - pts[j][1]) ** 2 + (pts[i][2] - pts[j][2]) ** 2) ** 0.5
            if d < worst[0]:
                worst = (d, pts[i][0], pts[j][0])
    return worst


def build(quality=JPEG_QUALITY):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # masthead band
    d.rectangle([0, 0, W, 20], fill=NAVY)
    tracked(d, MX, 4, "THE WORLD IN ONE DAY", F_AN(13), (255, 255, 255), 0.06)
    r = "DAY 328 OF 2026 \u00b7 ALL TIMES UTC"
    d.text((W - MX - d.textlength(r, font=F_AN(11)), 5), r, font=F_AN(11),
           fill=(200, 205, 215))

    # date — largest fitting Playfair Black (76px; 110px needs 1384px)
    center(d, 22, "Tuesday 24 November 2026", F_DATE(76), INK)

    # count strip
    cs = "38 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED TUESDAY 24 NOVEMBER 2026"
    wcs = d.textlength(cs, font=F_AN(26)) + 0.04 * 26 * len(cs)
    tracked(d, (W - wcs) / 2, 98, cs, F_AN(26), RED, 0.04)
    d.line([MX, 128, W - MX, 128], fill=RULE, width=1)

    # numbers strip: figure 34px + label 26px, tabular digits
    ny = 130
    cellw = CW / 6.0
    for i, (fig, lab) in enumerate(NUMBERS):
        cx = MX + cellw * i + cellw / 2
        fw = d.textlength(fig, font=F_AN(34))
        d.text((cx - fw / 2, ny), fig, font=F_AN(34), fill=INK)
        lw = d.textlength(lab, font=F_AN(26))
        d.text((cx - lw / 2, ny + 34), lab, font=F_AN(26), fill=RED)
        if i:
            d.line([MX + cellw * i, ny + 4, MX + cellw * i, ny + 60],
                   fill=RULE, width=1)
    d.line([MX, 194, W - MX, 194], fill=RULE, width=1)

    # region bar: 26px count + 13px name per segment
    ry = 198
    segw = CW / 7.0
    for i, (name, cnt) in enumerate(REGIONS):
        x0 = MX + segw * i
        d.rectangle([x0, ry, x0 + segw - 1, ry + 42], fill=REGION_COLORS[name])
        c = str(cnt)
        cw_ = d.textlength(c, font=F_AN(26))
        d.text((x0 + (segw - 1 - cw_) / 2, ry + 2), c, font=F_AN(26),
               fill=(255, 255, 255))
        nw = d.textlength(name, font=F_ANM(13)) + 0.05 * 13 * len(name)
        tracked(d, x0 + (segw - 1 - nw) / 2, ry + 28, name, F_ANM(13),
                (255, 255, 255), 0.05)

    # UTC strip
    uy = 244
    d.rectangle([MX, uy, W - MX, uy + 16], fill=NAVY2)
    tx = MX + 8
    d.text((tx, uy + 2), "THE DAY IN UTC", font=F_AN(12), fill=(240, 210, 120))
    tx += d.textlength("THE DAY IN UTC", font=F_AN(12)) + 14
    for t, s in TIMELINE:
        seg = f"{t}  {s}"
        wseg = d.textlength(seg, font=F_ANM(12))
        if tx + wseg > W - MX - 4:
            break
        d.text((tx, uy + 2), t, font=F_AN(12), fill=(240, 210, 120))
        d.text((tx + d.textlength(t + "  ", font=F_AN(12)), uy + 2), s,
               font=F_ANM(12), fill=(255, 255, 255))
        tx += wseg + 16

    # leads
    ly = 264
    colw = (CW - 32) / 3.0
    for i, lead in enumerate(LEADS):
        x0 = MX + i * (colw + 16)
        lead_art(d, i, x0, ly, colw, 46)
        chip(d, x0 + 6, ly + 6, lead["banner"], F_AN(9), (255, 255, 255), RED)
        py = ly + 50
        d.text((x0, py), f"{lead['n']}  {lead['place']} \u00b7 {lead['beat']}",
               font=F_AN(13), fill=RED)
        tag = lead["tag"]
        tw = d.textlength(tag, font=F_AN(9)) + 8
        chip(d, x0 + colw - tw, py - 1, tag, F_AN(9),
             (255, 255, 255), TAG_COLORS[tag])
        hy = py + 16
        hl = fit_lines(d, lead["head"], F_HEAD(44), colw, 2, tag=f"lead{i}head")
        draw_lines(d, hl, x0, hy, F_HEAD(44), INK, 50)
        dy = hy + len(hl) * 50 + 2
        dl = fit_lines(d, lead["deck"], F_DECK(15), colw, 2, tag=f"lead{i}deck")
        draw_lines(d, dl, x0, dy, F_DECK(15), INK, 17)
        sy = dy + len(dl) * 17 + 2
        d.text((x0, sy), lead["src"], font=F_ANM(11), fill=GREY)

    # cards: 2 rows x 6
    cy0 = 483
    cardw = (CW - 5 * 8) / 6.0
    cardh = 144
    for r in range(2):
        for c in range(6):
            idx = r * 6 + c
            n, place, beat, banner, head, deck, src, tag = CARDS[idx]
            x0 = MX + c * (cardw + 8)
            y0 = cy0 + r * (cardh + 8)
            d.rectangle([x0, y0, x0 + cardw, y0 + cardh], fill=PAPER,
                        outline=RULE, width=1)
            card_art(d, n, x0 + 1, y0 + 1, cardw - 2, 24)
            chip(d, x0 + 5, y0 + 5, banner, F_AN(8), (255, 255, 255), RED)
            py = y0 + 31
            d.text((x0 + 5, py), f"{n}  {place}", font=F_AN(11), fill=RED)
            tw = d.textlength(tag, font=F_AN(9)) + 8
            chip(d, x0 + cardw - tw - 4, py - 1, tag, F_AN(9),
                 (255, 255, 255), TAG_COLORS[tag])
            hy = py + 14
            hl = fit_lines(d, head, F_AN(27), cardw - 10, 2, tag=f"card{n}head")
            draw_lines(d, hl, x0 + 5, hy, F_AN(27), INK, 29)
            dy = hy + len(hl) * 29 + 2
            dl = fit_lines(d, deck, F_DECK(13), cardw - 10, 2, tag=f"card{n}deck")
            draw_lines(d, dl, x0 + 5, dy, F_DECK(13), INK, 14.5)
            sy = dy + len(dl) * 14.5 + 2
            sl = fit_lines(d, src, F_ANM(10), cardw - 10, 1, tag=f"card{n}src")
            if sl:
                d.text((x0 + 5, sy), sl[0], font=F_ANM(10), fill=GREY)

    # map + briefs
    by = 787
    d.text((MX, by), "WHERE IT HAPPENED", font=F_AN(13), fill=RED)
    d.text((MX, by + 14), "pins match story numbers", font=F_ANM(11), fill=GREY)
    mapbox = (MX, by + 28, 300, 106)
    draw_map(d, mapbox, PINS)
    bx = MX + 312
    bw = W - MX - bx
    d.text((bx, by), "ALSO ON TUESDAY 24 NOVEMBER \u2014 23 MORE STORIES",
           font=F_AN(13), fill=RED)
    colw2 = (bw - 16) / 3.0
    for i, (n, region, text) in enumerate(BRIEFS):
        col = i // 8
        row = i % 8
        x0 = bx + col * (colw2 + 8)
        yy = by + 16 + row * 15
        prefix = f"{n} {region} \u2014 "
        pw = d.textlength(prefix, font=F_DECKB(12))
        d.text((x0, yy), prefix, font=F_DECKB(12), fill=RED)
        avail = colw2 - pw
        if d.textlength(text, font=F_DECK(12)) > avail:
            fsize = 11.5
            while d.textlength(text, font=F_DECK(fsize)) > avail and fsize > 9:
                fsize -= 0.5
            if d.textlength(text, font=F_DECK(fsize)) > avail:
                TRUNCATED.append(("brief", text, "too long even at 9px", avail))
            d.text((x0 + pw, yy + 0.5), text, font=F_DECK(fsize), fill=INK)
        else:
            d.text((x0 + pw, yy), text, font=F_DECK(12), fill=INK)

    # DATE CHECK
    dy = 931
    dc_lines = fit_lines(d, DATE_CHECK, F_DECKB(22), CW - 16, 2, tag="datecheck")
    dc_h = len(dc_lines) * 26 + 10
    d.rectangle([MX, dy, W - MX, dy + dc_h], outline=RED, width=2,
                fill=(255, 250, 240))
    draw_lines(d, dc_lines, MX + 8, dy + 5, F_DECKB(22), INK, 26)

    # sources footer
    sy = dy + dc_h + 6
    d.text((MX, sy), SOURCES, font=F_AN(22), fill=GREY)
    bottom = sy + 22
    assert bottom <= 1022, f"layout overflows: bottom={bottom}"
    assert not TRUNCATED, f"truncated text: {TRUNCATED[:5]}"

    out = os.path.join(HERE, "image.jpg")
    img.save(out, "JPEG", quality=quality, optimize=True)
    data = open(out, "rb").read()
    sha = hashlib.sha256(data).hexdigest()
    worst = check_pins(mapbox)
    print(f"image.jpg: {len(data)} bytes, sha256 {sha}, bottom={bottom}, "
          f"datecheck_lines={len(dc_lines)}, min_pin_sep={worst[0]:.1f}px "
          f"(pins {worst[1]}-{worst[2]})")
    return out, len(data), sha


if __name__ == "__main__":
    q = int(sys.argv[1]) if len(sys.argv) > 1 else JPEG_QUALITY
    build(q)
