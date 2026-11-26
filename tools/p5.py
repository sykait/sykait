"""Tiny toolkit for Persona-flavoured animated SVG panels.

Text is converted to outlines (GitHub won't load fonts inside SVG <img>),
so every panel renders the same everywhere.
"""
import base64
import os
import io
import math
import random

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTCollection, TTFont

# Open-licensed fonts (SIL OFL / Apache) fetched from the official google/fonts repo
# on first use and cached in tools/.fonts (git-ignored), so the same build runs
# locally and inside GitHub Actions.
FONTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".fonts")
GF = "https://raw.githubusercontent.com/google/fonts/main/"
FONTS = {
    "dmserif": "ofl/dmserifdisplay/DMSerifDisplay-Regular.ttf",
    "abril": "ofl/abrilfatface/AbrilFatface-Regular.ttf",
    "archivo": "ofl/archivoblack/ArchivoBlack-Regular.ttf",
    "anton": "ofl/anton/Anton-Regular.ttf",
    "bowlby": "ofl/bowlbyone/BowlbyOne-Regular.ttf",
    "alfaslab": "ofl/alfaslabone/AlfaSlabOne-Regular.ttf",
    "ultra": "apache/ultra/Ultra-Regular.ttf",
    "bungee": "ofl/bungee/Bungee-Regular.ttf",
    "rubikmono": "ofl/rubikmonoone/RubikMonoOne-Regular.ttf",
    "barlow": "ofl/barlow/Barlow-Bold.ttf",
    "barlowx": "ofl/barlowcondensed/BarlowCondensed-ExtraBold.ttf",
    "mono": "ofl/spacemono/SpaceMono-Bold.ttf",
    "jp": "ofl/zenkakugothicnew/ZenKakuGothicNew-Bold.ttf",
    "jpd": "ofl/delagothicone/DelaGothicOne-Regular.ttf",
}
RANSOM_FONTS = ["dmserif", "abril", "archivo", "anton", "bowlby", "alfaslab", "ultra", "bungee"]

RED = "#E60012"
RED_D = "#9E000C"
BLACK = "#0A0A0A"
WHITE = "#FFFFFF"

_cache = {}


def fmt(v):
    s = f"{v:.1f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def font_file(key):
    path = os.path.join(FONTDIR, os.path.basename(FONTS[key]))
    if not os.path.exists(path):
        import urllib.request
        os.makedirs(FONTDIR, exist_ok=True)
        urllib.request.urlretrieve(GF + FONTS[key], path + ".part")
        os.replace(path + ".part", path)
    return path


def _font(key):
    if key not in _cache:
        fn = font_file(key)
        f = TTCollection(fn).fonts[0] if fn.lower().endswith(".ttc") else TTFont(fn)
        _cache[key] = (f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    return _cache[key]


def has(key, ch):
    return ord(ch) in _font(key)[1]


def glyph(key, ch, size, x=0.0, y=0.0):
    """Outline of one character, baseline at y. Returns (d, advance, bounds|None)."""
    if not has(key, ch):
        key = "jp"
    gs, cmap, upm = _font(key)
    name = cmap[ord(ch)]
    s = size / upm
    t = (s, 0, 0, -s, x, y)
    pen = SVGPathPen(gs, ntos=fmt)
    gs[name].draw(TransformPen(pen, t))
    bp = BoundsPen(gs)
    gs[name].draw(TransformPen(bp, t))
    return pen.getCommands(), gs[name].width * s, bp.bounds


def measure(key, text, size, tracking=0.0):
    return sum(glyph(key, c, size)[1] + tracking for c in text) - tracking


def text_d(key, text, size, x=0.0, y=0.0, anchor="start", tracking=0.0):
    """Whole string as one path (baseline y). Returns (d, width)."""
    w = measure(key, text, size, tracking)
    cx = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    parts = []
    for c in text:
        d, adv, _ = glyph(key, c, size, cx, y)
        if d:
            parts.append(d)
        cx += adv + tracking
    return "".join(parts), w


def vtext_d(key, text, size, x, y, gap=1.05):
    """Vertical (top-to-bottom) text, centred on x, first glyph top at y."""
    parts = []
    for i, c in enumerate(text):
        _, adv, bb = glyph(key, c, size)
        if not bb:
            continue
        w = bb[2] - bb[0]
        d, _, _ = glyph(key, c, size, x - bb[0] - w / 2, y + size * 0.88 + i * size * gap)
        parts.append(d)
    return "".join(parts)


def wrap(key, text, size, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if cur and measure(key, t, size) > maxw:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- ransom note

def _quad(rng, hw, hh, j):
    pts = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
    return [(x + rng.uniform(-j, j), y + rng.uniform(-j, j)) for x, y in pts]


def _poly(pts, dx=0, dy=0):
    return " ".join(f"{fmt(x + dx)},{fmt(y + dy)}" for x, y in pts)


def ransom(text, size, seed, styles=None, fonts=None, jitter=1.0, overlap=0.9, shadow=BLACK):
    """Lay out text as mismatched cut-out letters.

    Each letter is centred at (x, y) relative to the word origin; returns
    (items, width). styles cycle: ow / bo / wb / bw / wr / rw / rb.
    """
    rng = random.Random(seed)
    fonts = fonts or RANSOM_FONTS
    styles = styles or ["ow", "wb", "bw", "ow", "wr", "bw", "wb"]
    items, cursor, last_font = [], 0.0, None
    for i, ch in enumerate(text):
        if ch == " ":
            cursor += size * 0.32
            continue
        fk = rng.choice([f for f in fonts if f != last_font] or fonts)
        last_font = fk
        sz = size * rng.uniform(0.86, 1.12)
        _, _, bb = glyph(fk, ch, sz)
        if bb is None:
            cursor += size * 0.3
            continue
        x0, y0, x1, y1 = bb
        gw, gh = x1 - x0, y1 - y0
        d, _, _ = glyph(fk, ch, sz, -(x0 + x1) / 2, -(y0 + y1) / 2)
        style = styles[i % len(styles)] if isinstance(styles, list) else styles
        pad = sz * 0.1
        hw, hh = gw / 2 + pad, max(gh, sz * 0.5) / 2 + pad
        q = _quad(rng, hw, hh, pad * 0.55)
        sw = sz * 0.075
        so = sz * 0.05
        svg = []
        glyph_fill = {"ow": WHITE, "bo": BLACK, "wb": BLACK, "bw": WHITE, "wr": RED, "rw": WHITE, "rb": BLACK}[style]
        box = {"wb": WHITE, "bw": BLACK, "wr": WHITE, "rw": RED, "rb": RED}.get(style)
        if box:
            svg.append(f'<polygon points="{_poly(q, so, so * 1.2)}" fill="{shadow}"/>')
            edge = BLACK if box == WHITE else WHITE
            svg.append(f'<polygon points="{_poly(q)}" fill="{box}" stroke="{edge}" stroke-width="{fmt(sz * 0.03)}" stroke-linejoin="round"/>')
            svg.append(f'<path d="{d}" fill="{glyph_fill}"/>')
        else:
            stroke = BLACK if style == "ow" else WHITE
            svg.append(f'<path d="{d}" transform="translate({fmt(so)} {fmt(so * 1.2)})" fill="{shadow if style == "ow" else BLACK}" stroke="{shadow if style == "ow" else BLACK}" stroke-width="{fmt(sw * 2)}" stroke-linejoin="round"/>')
            svg.append(f'<path d="{d}" fill="{glyph_fill}" stroke="{stroke}" stroke-width="{fmt(sw * 2)}" stroke-linejoin="round" paint-order="stroke"/>')
        bw = hw * 2
        items.append({
            "x": cursor + bw / 2,
            "y": rng.uniform(-0.05, 0.05) * size * jitter,
            "rot": rng.uniform(-9, 9) * jitter,
            "w": bw,
            "svg": "".join(svg),
        })
        cursor += bw * overlap
    width = cursor + (items[-1]["w"] * (1 - overlap) if items else 0)
    return items, width


def place(items, ox, oy, delay=0.0, step=0.07, pop="pop", bob="bob"):
    out = []
    for i, it in enumerate(items):
        inner = it["svg"]
        if bob:
            inner = f'<g class="{bob}" style="animation-delay:{-(i * 0.43) % 3:.2f}s">{inner}</g>'
        if pop:
            inner = f'<g class="{pop}" style="animation-delay:{delay + i * step:.2f}s">{inner}</g>'
        out.append(f'<g transform="translate({fmt(ox + it["x"])} {fmt(oy + it["y"])}) rotate({fmt(it["rot"])})">{inner}</g>')
    return "".join(out)


# ---------------------------------------------------------------- shapes

def starburst(n, r, inner=0.0):
    """Alternating wedge rays (path) centred on the origin."""
    parts = []
    for k in range(n):
        a0 = 2 * math.pi * k / n
        a1 = a0 + math.pi / n
        p = [(inner * math.cos(a0), inner * math.sin(a0)), (r * math.cos(a0), r * math.sin(a0)),
             (r * math.cos(a1), r * math.sin(a1)), (inner * math.cos(a1), inner * math.sin(a1))]
        parts.append("M" + "L".join(f"{fmt(x)},{fmt(y)}" for x, y in p) + "Z")
    return "".join(parts)


def spiky(n, r_out, r_in, seed=1, wobble=0.12):
    rng = random.Random(seed)
    pts = []
    for k in range(n * 2):
        a = math.pi * k / n - math.pi / 2
        r = (r_out if k % 2 == 0 else r_in) * (1 + rng.uniform(-wobble, wobble))
        pts.append((r * math.cos(a), r * math.sin(a)))
    return _poly(pts)


def star5(r, inner=0.45):
    pts = []
    for k in range(10):
        a = math.pi * k / 5 - math.pi / 2
        rr = r if k % 2 == 0 else r * inner
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    return _poly(pts)


def sparkle(r):
    """4-point twinkle star path centred at origin."""
    k = r * 0.22
    return (f"M0,{fmt(-r)}C{fmt(k * .4)},{fmt(-k)} {fmt(k)},{fmt(-k * .4)} {fmt(r)},0"
            f"C{fmt(k)},{fmt(k * .4)} {fmt(k * .4)},{fmt(k)} 0,{fmt(r)}"
            f"C{fmt(-k * .4)},{fmt(k)} {fmt(-k)},{fmt(k * .4)} {fmt(-r)},0"
            f"C{fmt(-k)},{fmt(-k * .4)} {fmt(-k * .4)},{fmt(-k)} 0,{fmt(-r)}Z")


def heart(s):
    return (f"M0,{fmt(s * .35)}C{fmt(-s * .9)},{fmt(-s * .2)} {fmt(-s * .45)},{fmt(-s * .95)} 0,{fmt(-s * .45)}"
            f"C{fmt(s * .45)},{fmt(-s * .95)} {fmt(s * .9)},{fmt(-s * .2)} 0,{fmt(s * .35)}Z")


def image_data_uri(path, size, quality=86, height=None):
    from PIL import Image
    im = Image.open(path).convert("RGBA").resize((size, height or size), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=quality, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


PETAL = "M0,-11C7,-9 10,-1 6,7C3,12 -3,12 -6,7C-10,-1 -7,-9 0,-11Z"
PETAL_CSS = """
.pf{animation:pfA 9s linear infinite}.pf.b{animation-name:pfB}.pf.c{animation-name:pfC}
@keyframes pfA{0%{transform:translate(0,0) rotate(0)}100%{transform:translate(-160px,var(--fall,700px)) rotate(520deg)}}
@keyframes pfB{0%{transform:translate(0,0) rotate(0)}100%{transform:translate(-90px,var(--fall,700px)) rotate(-430deg)}}
@keyframes pfC{0%{transform:translate(0,0) rotate(0)}100%{transform:translate(-230px,var(--fall,700px)) rotate(610deg)}}
.flut{transform-box:fill-box;transform-origin:50% 50%;animation:flut 1.6s ease-in-out infinite alternate}
@keyframes flut{0%{transform:scaleX(1)}100%{transform:scaleX(.25)}}
"""


def petals(n, width, height, seed=9, scale=(1.0, 2.2)):
    """Rose petals drifting down-left across the panel. Needs PETAL_CSS and #petal gradient."""
    rng = random.Random(seed)
    out = []
    for i in range(n):
        x = rng.uniform(80, width + 180)
        s = rng.uniform(*scale)
        dur = rng.uniform(7, 12)
        cls = "pf " + "abc"[i % 3]
        fall = height + 80
        out.append(f'<g transform="translate({fmt(x)} -40)"><g class="{cls}" style="--fall:{fall}px;animation-duration:{dur:.1f}s;'
                   f'animation-delay:-{rng.uniform(0, dur):.1f}s"><g transform="scale({s:.2f})"><g class="flut" style="animation-delay:-{rng.uniform(0, 1.6):.1f}s">'
                   f'<path d="{PETAL}" fill="url(#petal)"/><path d="M-1,-8C2,-5 3,0 1,5" fill="none" stroke="#ff6b7a" stroke-width="1" opacity=".6"/>'
                   f"</g></g></g></g>")
    return "".join(out)


PETAL_DEF = ('<radialGradient id="petal" cx=".35" cy=".3" r=".9"><stop offset="0" stop-color="#ff3346"/>'
             '<stop offset=".6" stop-color="#c8001a"/><stop offset="1" stop-color="#6e000c"/></radialGradient>')


# ---------------------------------------------------------------- shared CSS

BASE_CSS = """
.pop{transform-box:fill-box;transform-origin:50% 50%;animation:pop .75s cubic-bezier(.18,1.5,.4,1) both}
@keyframes pop{0%{opacity:0;transform:scale(.2) rotate(-35deg)}60%{opacity:1}100%{opacity:1;transform:none}}
.bob{transform-box:fill-box;transform-origin:50% 50%;animation:bob 3s ease-in-out infinite}
@keyframes bob{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-3px) rotate(2.5deg)}}
.slideL{animation:slideL .8s cubic-bezier(.2,.9,.2,1) both}
@keyframes slideL{0%{opacity:0;transform:translateX(-120px) skewX(-12deg)}100%{opacity:1;transform:none}}
.slideR{animation:slideR .8s cubic-bezier(.2,.9,.2,1) both}
@keyframes slideR{0%{opacity:0;transform:translateX(120px) skewX(12deg)}100%{opacity:1;transform:none}}
.slideD{animation:slideD .8s cubic-bezier(.2,.9,.2,1) both}
@keyframes slideD{0%{opacity:0;transform:translateY(-80px)}100%{opacity:1;transform:none}}
.fade{animation:fade .9s ease both}
@keyframes fade{0%{opacity:0}100%{opacity:1}}
.spin{transform-box:fill-box;transform-origin:50% 50%;animation:spin 80s linear infinite}
.spinF{transform-box:fill-box;transform-origin:50% 50%;animation:spin 24s linear infinite}
.spinR{transform-box:fill-box;transform-origin:50% 50%;animation:spin 36s linear infinite reverse}
@keyframes spin{to{transform:rotate(360deg)}}
.float{animation:float 4.2s ease-in-out infinite}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
.pulse{transform-box:fill-box;transform-origin:50% 50%;animation:pulse 2.6s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:.55;transform:scale(.94)}50%{opacity:1;transform:scale(1.04)}}
.tw{transform-box:fill-box;transform-origin:50% 50%;animation:tw 2.4s ease-in-out infinite both}
@keyframes tw{0%,100%{opacity:0;transform:scale(.1) rotate(0)}45%,55%{opacity:1;transform:scale(1) rotate(45deg)}}
.wig{transform-box:fill-box;transform-origin:50% 100%;animation:wig 2.2s ease-in-out infinite}
@keyframes wig{0%,100%{transform:rotate(-4deg)}50%{transform:rotate(5deg) scale(1.04)}}
.beat{transform-box:fill-box;transform-origin:50% 50%;animation:beat 1.2s ease-in-out infinite}
@keyframes beat{0%,100%{transform:scale(1)}15%{transform:scale(1.25)}30%{transform:scale(1)}45%{transform:scale(1.15)}}
.shine{animation:shine 5s cubic-bezier(.5,0,.2,1) infinite}
@keyframes shine{0%{transform:translateX(-300px)}22%,100%{transform:translateX(1300px)}}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01s!important;animation-iteration-count:1!important}}
"""


def svg_doc(w, h, body, css="", title=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">'
            f"<title>{title}</title><style>{BASE_CSS}{css}</style>{body}</svg>")
