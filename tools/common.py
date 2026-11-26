"""Shared paths, links and drawing helpers for the profile panels."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p5 import *  # noqa: F401,F403
from p5 import (BLACK, PETAL_CSS, PETAL_DEF, RED, RED_D, WHITE, fmt, heart, image_data_uri, measure, petals, place,
                ransom, sparkle, spiky, star5, starburst, svg_doc, text_d, vtext_d, wrap)

TOOLS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(TOOLS)
ASSETS = os.path.join(REPO, "assets")
SRC = os.path.join(TOOLS, "src")
WATERMARK = os.path.join(SRC, "watermark.png")
COVER = os.path.join(SRC, "trailer-cover.webp")

LINKS = {
    "site": "https://re.kaixen.online",
    "server": "https://discord.gg/kaixen",
    "discord": "https://discord.com/users/995728579868512308",
    "x": "https://x.com/soytarikait",
    "trailer": "https://www.youtube.com/watch?v=Ne1W0aU2w2E",
}

_rose_cache = {}


def rose(size):
    if size not in _rose_cache:
        _rose_cache[size] = image_data_uri(WATERMARK, size)
    return _rose_cache[size]


def halftone_defs(pid, mid, x1, y1, x2, y2, r=2.6, step=11, color=BLACK, op=0.38):
    return (f'<pattern id="{pid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">'
            f'<circle cx="{step / 2}" cy="{step / 2}" r="{r}" fill="{color}"/></pattern>'
            f'<linearGradient id="{mid}g" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
            f'<stop offset="0" stop-color="#fff" stop-opacity="{op}"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="{mid}"><rect width="100%" height="100%" fill="url(#{mid}g)"/></mask>')


def pivot(r):
    """Invisible circle centred on (0,0). Spinning groups use transform-box:fill-box, so an
    uneven spiky frame (plus its offset shadow) would otherwise rotate around the wrong point
    and drift away from whatever sits in the middle."""
    return f'<circle r="{fmt(r)}" fill="none"/>'


def rose_emblem(cx, cy, img, frame_out, frame_in, delay, seed=3):
    s = img
    return (f'<g transform="translate({cx} {cy})"><g class="pop" style="animation-delay:{delay}s"><g class="float">'
            f'<g class="spinR">{pivot(frame_out + 16)}<polygon points="{spiky(16, frame_out, frame_in, seed)}" fill="{BLACK}" transform="translate(9 9)"/>'
            f'<polygon points="{spiky(16, frame_out, frame_in, seed)}" fill="{WHITE}" stroke="{BLACK}" stroke-width="6" stroke-linejoin="round"/></g>'
            f'<circle r="{frame_in * 0.98}" fill="url(#glow)" class="pulse"/>'
            f'<g class="spinF"><circle r="{frame_in * 0.93}" fill="none" stroke="{BLACK}" stroke-width="3" stroke-dasharray="3 9"/></g>'
            f'<image href="{rose(360)}" x="{-s / 2}" y="{-s / 2}" width="{s}" height="{s}"/>'
            f"</g></g></g>")


def red_tex(uid, pts, rays=None, dots_op=.42):
    """Textured red area (like the Re:Kaixen panel): diagonal red gradient, fading halftone dots
    and, optionally, faint slowly turning rays. Flat red is tiring to look at."""
    out = (f'<defs><linearGradient id="{uid}g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff1a2e"/>'
           f'<stop offset=".6" stop-color="#e60012"/><stop offset="1" stop-color="#a8000d"/></linearGradient>'
           + halftone_defs(f"{uid}d", f"{uid}m", 0, 1, .7, 0, r=2.4, op=dots_op)
           + f'<clipPath id="{uid}c"><polygon points="{pts}"/></clipPath></defs>'
           f'<polygon points="{pts}" fill="url(#{uid}g)"/>'
           f'<g clip-path="url(#{uid}c)">')
    if rays:
        out += (f'<g transform="translate({rays[0]} {rays[1]})"><g class="spin">'
                f'<path d="{starburst(24, 700)}" fill="#fff" opacity=".07"/></g></g>')
    out += f'<rect x="-50" y="-50" width="2000" height="2000" fill="url(#{uid}d)" mask="url(#{uid}m)"/></g>'
    return out


def tile_tex_defs():
    """Shared gradient + dots for small red tiles (use fill="url(#tileg)" and tile_dots())."""
    return ('<linearGradient id="tileg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff2236"/>'
            '<stop offset="1" stop-color="#b3000e"/></linearGradient>'
            '<pattern id="tiled" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">'
            '<circle cx="4.5" cy="4.5" r="1.7" fill="#000" opacity=".22"/></pattern>')


def tile_dots(w=200, h=200):
    return f'<rect x="-20" y="-20" width="{w}" height="{h}" fill="url(#tiled)"/>'


def glow_def():
    return ('<radialGradient id="glow"><stop offset="0" stop-color="#ff1f3a" stop-opacity=".9"/>'
            '<stop offset=".6" stop-color="#e60012" stop-opacity=".35"/><stop offset="1" stop-color="#e60012" stop-opacity="0"/></radialGradient>')


def sparkles(pts, stroke=BLACK, fill=WHITE):
    out = []
    for x, y, r, dl in pts:
        out.append(f'<g transform="translate({x} {y})"><path class="tw" style="animation-delay:{dl}s" d="{sparkle(r)}" '
                   f'fill="{fill}" stroke="{stroke}" stroke-width="1.6" stroke-linejoin="round"/></g>')
    return "".join(out)


def strip_text(segments, size, x, y, font="barlow", gap=26):
    """Text segments separated by little red sparkles. Returns (svg, width)."""
    out, cx = [], x
    for i, seg in enumerate(segments):
        if i:
            out.append(f'<path d="{sparkle(8)}" transform="translate({fmt(cx + gap / 2)} {fmt(y - size * 0.36)})" fill="{RED}"/>')
            cx += gap
        d, w = text_d(font, seg, size, cx, y)
        out.append(f'<path d="{d}" fill="{WHITE}"/>')
        cx += w
    return "".join(out), cx - x



# ================================================================== BUTTONS

def button(label, kanji, accent, seed):
    """Call-to-action button. Each seed drifts on its own tempo and path (up/down and left/right)."""
    W, H = 400, 120
    poly = "22,22 384,14 368,86 10,92"
    size = 38
    d, tw = text_d("anton", label, size, 0, 0, tracking=1)
    if tw > 236:  # keep room for the star and the arrow
        size = 38 * 236 / tw
        d, tw = text_d("anton", label, size, 0, 0, tracking=1)
    kd, kw = text_d("jp", kanji, 15, 0, 0)
    tx = 86 + (250 - tw) / 2
    b = [f'<defs><clipPath id="bc{seed}"><polygon points="{poly}"/></clipPath></defs><g transform="translate(0 12)">']
    b.append(f'<g class="pop" style="animation-delay:{.1 + seed * .12:.2f}s"><g class="drift{seed}">'
             f'<polygon points="{poly}" fill="#000" stroke="#fff" stroke-width="1.5" transform="translate(13 11)"/>'
             f'<polygon points="{poly}" fill="{accent}" transform="translate(7 6)"/>'
             f'<polygon points="{poly}" fill="{BLACK}" stroke="#fff" stroke-width="4" stroke-linejoin="round"/>'
             f'<g clip-path="url(#bc{seed})"><g class="shine" style="animation-delay:{1 + seed * .7:.1f}s">'
             f'<polygon points="0,0 50,0 10,110 -40,110" fill="#fff" opacity=".22"/></g></g>'
             f'<path d="{d}" transform="translate({fmt(tx)} 68)" fill="{WHITE}"/>'
             f'<g transform="translate(58 53)"><g class="starB"><polygon points="{star5(17)}" fill="{accent}" stroke="#fff" stroke-width="2"/></g></g>'
             f'<g transform="translate({fmt(tx + tw + 14)} 54)"><path class="nudge" d="M0,-11 L14,0 L0,11 Z" fill="{accent}"/></g>'
             f'<g transform="translate(250 6) rotate(-4)"><g class="tagW"><polygon points="-8,-4 {fmt(kw + 10)},-6 {fmt(kw + 7)},20 -6,21" fill="{WHITE}" stroke="#000" stroke-width="2"/>'
             f'<path d="{kd}" transform="translate(1 14)" fill="{accent if accent != WHITE else BLACK}"/></g></g>'
             f'</g></g></g>')
    # a different drift path and tempo per button
    paths = {1: "0,0 4,-3 1,-5 -3,-2", 2: "0,0 -4,-2 -1,-5 3,-3", 3: "0,0 3,-4 -2,-5 -4,-1",
             4: "0,0 -3,-4 3,-5 4,-1", 5: "0,0 4,-1 2,-5 -3,-4"}
    pts = [p.split(",") for p in paths.get(seed, paths[1]).split()]
    steps = len(pts)
    kf = "".join(f"{k * 100 / steps:.0f}%{{transform:translate({x}px,{y}px)}}" for k, (x, y) in enumerate(pts)) + "100%{transform:translate(0,0)}"
    dur = {1: 3.4, 2: 4.1, 3: 2.9, 4: 3.7, 5: 4.6}.get(seed, 3.5)
    css = (f".drift{seed}{{animation:drift{seed} {dur}s ease-in-out infinite}}@keyframes drift{seed}{{{kf}}}"
           ".nudge{animation:nudge 1s ease-in-out infinite}@keyframes nudge{0%,100%{transform:translateX(0)}50%{transform:translateX(6px)}}"
           f".starB{{transform-box:fill-box;transform-origin:50% 50%;animation:starB {dur * .9:.1f}s cubic-bezier(.4,1.6,.5,1) infinite}}"
           "@keyframes starB{0%,70%,100%{transform:rotate(0) scale(1)}80%{transform:rotate(144deg) scale(1.35)}90%{transform:rotate(216deg) scale(.9)}}"
           f".tagW{{transform-box:fill-box;transform-origin:50% 100%;animation:tagW {dur * 1.3:.1f}s ease-in-out infinite}}"
           "@keyframes tagW{0%,100%{transform:rotate(0)}50%{transform:rotate(-6deg) translateY(-2px)}}")
    return svg_doc(W, H, "".join(b), css=css, title=label)
