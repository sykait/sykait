"""Section headers, player card, project cards, arsenal badges and the mascot footer."""
import random

from common import *  # noqa: F401,F403

LIGHT_SAFE = 'stroke="#fff" stroke-width="3" stroke-linejoin="round"'


# ================================================================ HEADERS

def section_header(num, title, kanji, seed):
    """Transparent-background divider that reads on both GitHub themes."""
    W, H = 1000, 104
    b = []
    nums, nw = ransom(num, 58, seed=seed, styles=["rw", "wb"], jitter=.7)
    tits, tw = ransom(title, 40, seed=seed + 50, styles=["ow", "wb", "ow", "bw", "ow", "wr", "ow", "ow", "bw"], jitter=.7, overlap=.88)
    kd, kw = text_d("jpd", kanji, 22, 0, 0)
    bar_end = 54 + nw + 26 + tw + 34
    poly = f"18,22 {fmt(bar_end + 18)},16 {fmt(bar_end)},86 8,92"
    b.append(f'<g class="slideL"><polygon points="{poly}" fill="{RED}" transform="translate(9 7)"/>'
             f'<polygon points="{poly}" fill="{BLACK}" {LIGHT_SAFE}/></g>')
    b.append(f'<defs><clipPath id="hc{seed}"><polygon points="{poly}"/></clipPath></defs>'
             f'<g clip-path="url(#hc{seed})"><g class="shine" style="animation-delay:{1.2 + (seed % 7) * .3:.1f}s"><polygon points="0,0 46,0 6,110 -40,110" fill="#fff" opacity=".18"/></g></g>')
    b.append(place(nums, 40, 54, delay=.15, step=.08, bob="hopL", bob_step=.14, bob_delay=1.4))
    b.append(place(tits, 54 + nw + 22, 54, delay=.3, step=.045, bob="hopL", bob_step=.07, bob_delay=1.7))
    kx = bar_end + 26
    b.append(f'<g transform="translate({fmt(kx)} 62) rotate(-4)"><g class="pop" style="animation-delay:.75s">'
             f'<g class="wig"><polygon points="-9,-28 {fmt(kw + 9)},-31 {fmt(kw + 12)},9 -6,11" fill="{BLACK}" transform="translate(4 4)"/>'
             f'<polygon points="-9,-28 {fmt(kw + 9)},-31 {fmt(kw + 12)},9 -6,11" fill="{RED}" stroke="#fff" stroke-width="2.5"/>'
             f'<path d="{kd}" fill="{WHITE}"/></g></g></g>')
    lx = kx + kw + 30
    if lx < W - 60:
        b.append(f'<g class="grow" style="animation-delay:.6s"><polygon points="{fmt(lx)},60 {W - 30},50 {W - 34},58 {fmt(lx)},66" fill="{RED}" {LIGHT_SAFE.replace("3", "1.5")}/></g>')
        b.append(f'<g transform="translate({W - 24} 52)"><polygon class="spinF" points="{star5(12)}" fill="{RED}" stroke="#fff" stroke-width="2"/></g>')
    css = ".grow{transform-box:fill-box;transform-origin:0 50%;animation:grow 1s cubic-bezier(.2,.9,.2,1) both}@keyframes grow{0%{transform:scaleX(0)}100%{transform:none}}"
    return svg_doc(W, H, "".join(b), css=css, title=f"{num} {title}")


# ================================================================ PLAYER CARD

STATS = [
    ("ANIMATION", "動き", 1.0, "MASTER"),
    ("DISCORD BOTS", "ボット", .92, "EXPERT"),
    ("UI / DESIGN", "デザイン", .8, "SKILLED"),
    ("SCRIPTING", "スクリプト", .84, "SKILLED"),
    ("SLEEP", "睡眠", .12, "???"),
]
TICKER = ["BUILDING Re:Kaixen", "ANIMATING EVERYTHING", "OPEN FOR COLLABS", "ONE BOT. EVERY FEATURE.", "TAKE YOUR SERVER"]


def ticker(y, h, W, items, size=17, speed=55, fill=RED):
    segs, x = [], 0.0
    for it in items * 2:
        d, w = text_d("archivo", it, size, x, y + h / 2 + size * .36, tracking=1)
        segs.append(f'<path d="{d}" fill="{WHITE}"/>')
        x += w + 18
        segs.append(f'<path d="{sparkle(7)}" transform="translate({fmt(x)} {fmt(y + h / 2)})" fill="{BLACK}"/>')
        x += 22
    loop = x / 2
    css = (f".tick{{animation:tick {loop / speed:.1f}s linear infinite}}"
           f"@keyframes tick{{to{{transform:translateX(-{loop:.1f}px)}}}}")
    body = (f'<rect x="0" y="{y}" width="{W}" height="{h}" fill="{fill}"/>'
            f'<rect x="0" y="{y}" width="{W}" height="3" fill="#fff"/>'
            f'<g class="tick">{"".join(segs)}</g>')
    return body, css


def player_card():
    W, H = 1000, 480
    b = ['<defs>' + glow_def() + halftone_defs("pdots", "phm", 0, 0, .5, 1, color=BLACK, op=.4) + '</defs>']
    b.append(f'<rect width="{W}" height="{H}" fill="{BLACK}"/>')
    band = "-20,-20 400,-20 300,500 -20,500"
    b.append(f'<g transform="translate(175 190)"><g class="spin"><path d="{starburst(24, 700)}" fill="#fff" opacity=".05"/></g></g>')
    b.append(f'<g class="slideL" style="animation-delay:.06s"><polygon points="{band}" fill="none" stroke="#fff" stroke-width="5" transform="translate(14 0)"/></g>')
    b.append(f'<g class="slideL"><polygon points="{band}" fill="{RED}"/><rect width="420" height="{H}" fill="url(#pdots)" mask="url(#phm)"/></g>')
    b.append(rose_emblem(170, 180, 206, 126, 100, .3, seed=21))

    # name plate
    items, nw = ransom("kait", 52, seed=77, styles=["wb", "bw", "wr", "wb"], jitter=1.2)
    b.append(f'<g class="slideL" style="animation-delay:.5s"><polygon points="40,330 300,322 288,392 30,398" fill="{BLACK}" stroke="#fff" stroke-width="3"/></g>')
    b.append(place(items, 60, 360, delay=.65, step=.07))
    d, w = text_d("bowlby", "LV.MAX", 22, 0, 0)
    b.append(f'<g transform="translate({fmt(70 + nw)} 372) rotate(-6)"><g class="pop" style="animation-delay:1s">'
             f'<path d="{d}" fill="{RED}" stroke="#fff" stroke-width="3" paint-order="stroke"/></g></g>')

    # arcana card
    ad, aw = text_d("archivo", "THE FOOL", 11, 0, 0, tracking=1)
    kd, kw = text_d("jpd", "愚者", 15, 0, 0)
    b.append(f'<g transform="translate(318 236) rotate(9)"><g class="pop" style="animation-delay:1.1s"><g class="bob">'
             f'<rect x="-44" y="-66" width="88" height="132" rx="4" fill="{BLACK}" transform="translate(6 6)"/>'
             f'<rect x="-44" y="-66" width="88" height="132" rx="4" fill="{WHITE}" stroke="{BLACK}" stroke-width="3"/>'
             f'<rect x="-37" y="-59" width="74" height="118" rx="2" fill="none" stroke="{RED}" stroke-width="2"/>'
             f'<path d="{text_d("bowlby", "0", 22, -7, -36)[0]}" fill="{BLACK}"/>'
             f'<polygon points="{star5(22)}" fill="{RED}" stroke="{BLACK}" stroke-width="2.5" transform="translate(0 2)"/>'
             f'<path d="{kd}" transform="translate({fmt(-kw / 2)} 38)" fill="{BLACK}"/>'
             f'<path d="{ad}" transform="translate({fmt(-aw / 2)} 54)" fill="{RED}"/>'
             f"</g></g></g>")

    # status title
    items, tw = ransom("STATUS", 42, seed=88, styles=["bw", "wr", "wb", "ow", "wb", "rw"], jitter=.8)
    b.append(f'<g class="slideR" style="animation-delay:.2s"><polygon points="402,30 {fmt(430 + tw + 120)},24 {fmt(420 + tw + 120)},92 394,98" fill="#fff" opacity=".06"/></g>')
    b.append(place(items, 428, 62, delay=.35, step=.06))
    kd, kw = text_d("jpd", "能力", 20, 0, 0)
    b.append(f'<g transform="translate({fmt(448 + tw + 14)} 70) rotate(4)"><g class="pop" style="animation-delay:.8s">'
             f'<polygon points="-8,-25 {fmt(kw + 8)},-27 {fmt(kw + 10)},8 -6,9" fill="{WHITE}"/><path d="{kd}" fill="{RED}"/></g></g>')

    # stat rows
    css = [".fill{transform-box:fill-box;transform-origin:0 50%;animation:fill 1.3s cubic-bezier(.2,.9,.2,1) both}"
           "@keyframes fill{0%{transform:scaleX(0)}100%{transform:none}}"]
    for i, (label, kanji, val, rank) in enumerate(STATS):
        y = 140 + i * 50
        dl = .6 + i * .12
        d, lw = text_d("barlowx", label, 26, 432, y + 9)
        kd, _ = text_d("jp", kanji, 13, 434, y + 27)
        x1, x2 = 640, 880
        fx = x1 + (x2 - x1) * val
        rd, rw_ = text_d("anton", rank, 22, 896, y + 9)
        b.append(f'<g class="slideR" style="animation-delay:{dl:.2f}s">'
                 f'<path d="{d}" fill="{WHITE}"/><path d="{kd}" fill="{WHITE}" opacity=".55"/>'
                 f'<polygon points="{x1 + 6},{y - 12} {x2 + 6},{y - 15} {x2},{y + 7} {x1},{y + 10}" fill="#262626" stroke="#fff" stroke-width="2"/>'
                 f'<g class="fill" style="animation-delay:{dl + .25:.2f}s"><polygon points="{x1 + 6},{y - 12} {fmt(fx + 6)},{fmt(y - 12 - 3 * val)} {fmt(fx)},{fmt(y + 10 - 3 * val)} {x1},{y + 10}" fill="{RED}"/></g>'
                 f'<path d="{rd}" fill="{RED if rank == "MASTER" else WHITE}"/></g>')
        if rank == "MASTER":
            b.append(f'<g transform="translate({fmt(896 + rw_ + 14)} {y - 2})"><polygon class="beat" points="{star5(9)}" fill="{WHITE}"/></g>')

    # quest line
    qd, qw = text_d("archivo", "CURRENT QUEST", 15, 0, 0, tracking=1.5)
    vd, vw = text_d("archivo", "Re:Kaixen", 22, qw + 30, 1)
    b.append(f'<g transform="translate(438 410) rotate(-2)"><g class="slideR" style="animation-delay:1.35s">'
             f'<polygon points="-14,-26 {fmt(qw + vw + 56)},-30 {fmt(qw + vw + 50)},10 -18,12" fill="{WHITE}"/>'
             f'<path d="{qd}" fill="{BLACK}"/><path d="M{fmt(qw + 10)},-14 l10,5 l-10,5z" fill="{RED}"/>'
             f'<path d="{vd}" fill="{RED}"/></g></g>')

    tk, tcss = ticker(446, 34, W, TICKER)
    b.append(f'<g class="fade" style="animation-delay:1.4s">{tk}</g>')
    css.append(tcss)
    b.append(sparkles([(380, 60, 11, .4), (965, 110, 9, 1.4), (360, 420, 10, 2), (610, 410, 8, 1)]))
    return svg_doc(W, H, "".join(b), css="".join(css), title="kait — player status")


# ================================================================ PROJECT CARDS

def chips(tags, x, y, maxw, seed, dark=True):
    rng = random.Random(seed)
    out, cx, cy = [], x, y
    for i, t in enumerate(tags):
        d, w = text_d("barlowx", t.upper(), 16, 0, 0, tracking=.6)
        bw = w + 20
        if cx + bw > x + maxw:
            cx, cy = x, cy + 34
        style = i % 3
        box, ink = [(WHITE, BLACK), (RED, WHITE), (BLACK, WHITE)][style]
        if not dark and box == BLACK:
            pass
        edge = "#fff" if box == BLACK else BLACK
        r = rng.uniform(-3, 3)
        out.append(f'<g transform="translate({fmt(cx + bw / 2)} {cy}) rotate({r:.1f})"><g class="pop" style="animation-delay:{.9 + i * .06:.2f}s">'
                   f'<polygon points="{fmt(-bw / 2)},-14 {fmt(bw / 2)},-16 {fmt(bw / 2 - 2)},12 {fmt(-bw / 2 - 2)},13" fill="{edge}" transform="translate(3 3)" opacity=".9"/>'
                   f'<polygon points="{fmt(-bw / 2)},-14 {fmt(bw / 2)},-16 {fmt(bw / 2 - 2)},12 {fmt(-bw / 2 - 2)},13" fill="{box}" stroke="{edge}" stroke-width="1.5"/>'
                   f'<path d="{d}" transform="translate({fmt(-w / 2)} 6)" fill="{ink}"/></g></g>')
        cx += bw + 10
    return "".join(out)


def cube(s):
    """Little isometric block (red/black/white) for SyHost."""
    h = s * .58
    top = f"0,{fmt(-s)} {fmt(s * .87)},{fmt(-s / 2)} 0,0 {fmt(-s * .87)},{fmt(-s / 2)}"
    left = f"{fmt(-s * .87)},{fmt(-s / 2)} 0,0 0,{fmt(s)} {fmt(-s * .87)},{fmt(s / 2)}"
    right = f"0,0 {fmt(s * .87)},{fmt(-s / 2)} {fmt(s * .87)},{fmt(s / 2)} 0,{fmt(s)}"
    grid = "".join(f'<line x1="{fmt(-s * .87 + k * s * .29)}" y1="{fmt(-s / 2 + k * s / 6)}" x2="{fmt(k * s * .29)}" y2="{fmt(-s + k * s / 6)}" stroke="#000" stroke-width="1.5" opacity=".35"/>' for k in (1, 2))
    return (f'<polygon points="{top}" fill="{WHITE}" stroke="#000" stroke-width="3" stroke-linejoin="round"/>'
            f'<polygon points="{left}" fill="{RED}" stroke="#000" stroke-width="3" stroke-linejoin="round"/>'
            f'<polygon points="{right}" fill="{RED_D}" stroke="#000" stroke-width="3" stroke-linejoin="round"/>{grid}')


def project_card(key):
    W, H = 500, 330
    if key == "rekaixen":
        title, seed, kanji, badge = "Re:Kaixen", 301, "本命", "MAIN QUEST"
        desc = "One Discord bot for moderation, leveling, tickets, giveaways and more, with a built-in AI assistant."
        tags = ["discord.js", "Node.js", "AI", "Express", "SQLite", "Stripe"]
        dark = True
    else:
        title, seed, kanji, badge = "SyHost", 302, "道具", "SIDE QUEST"
        desc = "One-click modded Minecraft servers (NeoForge, Forge, Fabric) with an animated terminal UI."
        tags = ["PowerShell", "NeoForge", "Fabric", "playit.gg"]
        dark = False
    bg, ink = (BLACK, WHITE) if dark else (WHITE, BLACK)
    b = ['<defs>' + glow_def() + halftone_defs(f"cd{key}", f"cm{key}", 1, 0, .4, .7, color=RED if dark else BLACK, op=.35)
         + f'<clipPath id="cc{key}"><polygon points="8,8 492,4 486,316 4,322"/></clipPath></defs>']
    b.append(f'<g class="pop" style="animation-delay:.05s"><polygon points="8,8 492,4 486,316 4,322" fill="{RED}" transform="translate(6 6)"/>'
             f'<polygon points="8,8 492,4 486,316 4,322" fill="{bg}" stroke="{ink if not dark else "#fff"}" stroke-width="4" stroke-linejoin="round"/></g>')
    b.append(f'<g clip-path="url(#cc{key})"><g class="fade" style="animation-delay:.2s">'
             f'<polygon points="336,0 520,0 520,340 276,340" fill="{RED if dark else BLACK}" opacity="{.9 if dark else 1}"/>'
             f'<rect width="{W}" height="{H}" fill="url(#cd{key})" mask="url(#cm{key})"/></g>'
             f'<g class="shine" style="animation-delay:{2 + (seed % 3):.1f}s"><polygon points="0,0 50,0 -40,340 -90,340" fill="#fff" opacity=".14"/></g></g>')
    # badge
    d, w = text_d("archivo", badge, 13, 0, 0, tracking=1.5)
    kd, kw = text_d("jpd", kanji, 15, w + 14, 1)
    b.append(f'<g transform="translate(30 40) rotate(-3)"><g class="slideL" style="animation-delay:.25s">'
             f'<polygon points="-10,-19 {fmt(w + kw + 28)},-22 {fmt(w + kw + 23)},8 -13,9" fill="{RED if not dark else WHITE}"/>'
             f'<path d="{d}" fill="{WHITE if not dark else BLACK}"/><path d="{kd}" fill="{BLACK if not dark else RED}"/></g></g>')
    items, tw = ransom(title, 40 if len(title) > 7 else 54, seed=seed,
                       styles=["wb", "bw", "rw", "wb", "bw", "wr", "ow", "wb", "bw"] if dark else ["bw", "wr", "bw", "rw", "wb", "bw"], jitter=1)
    b.append(place(items, 28, 98, delay=.35, step=.06))
    lines = wrap("barlow", desc, 16.5, 262)
    for i, ln in enumerate(lines):
        d, _ = text_d("barlow", ln, 16.5, 30, 156 + i * 22)
        b.append(f'<g class="fade" style="animation-delay:{.7 + i * .05:.2f}s"><path d="{d}" fill="{ink}"/></g>')
    b.append(chips(tags, 30, 156 + len(lines) * 22 + 22, 300, seed))
    # art
    if key == "rekaixen":
        b.append(rose_emblem(398, 124, 124, 78, 63, .5, seed=4))
    else:
        b.append(syhost_logo(398, 124))
    od, ow = text_d("archivo", "OPEN", 15, 0, 0, tracking=2)
    b.append(f'<g transform="translate({W - ow - 70} 296)"><g class="pop" style="animation-delay:1.2s">'
             f'<polygon points="-12,-20 {fmt(ow + 40)},-22 {fmt(ow + 36)},8 -15,9" fill="{WHITE if dark else BLACK}" stroke="{BLACK if dark else WHITE}" stroke-width="2"/>'
             f'<path d="{od}" fill="{BLACK if dark else WHITE}"/>'
             f'<g transform="translate({fmt(ow + 14)} -6)"><path class="nudge" d="M0,-7 L10,0 L0,7 Z" fill="{RED}"/></g></g></g>')
    css = (".nudge{animation:nudge 1s ease-in-out infinite}@keyframes nudge{0%,100%{transform:translateX(0)}50%{transform:translateX(5px)}}"
           ".caret{animation:caret 1s steps(1) infinite}@keyframes caret{50%{opacity:0}}")
    return svg_doc(W, H, "".join(b), css=css, title=f"{title} project card")


# ================================================================ ARSENAL

ARSENAL = ["JavaScript", "Node.js", "discord.js", "TypeScript", "Express", "SQLite", "OpenAI API", "Stripe",
           "PowerShell", "HTML", "CSS", "SVG Animation", "Blender", "Git", "Claude Code"]


def arsenal():
    W = 1000
    rng = random.Random(404)
    rows, cur, cw = [], [], 0
    sized = []
    for t in ARSENAL:
        d, w = text_d("barlowx", t.upper(), 24, 0, 0, tracking=.8)
        sized.append((t, d, w))
    for t, d, w in sized:
        bw = w + 34
        if cur and cw + bw > W - 80:
            rows.append((cur, cw))
            cur, cw = [], 0
        cur.append((t, d, w, bw))
        cw += bw + 14
    rows.append((cur, cw))
    H = 40 + len(rows) * 62
    b, k = [], 0
    for r, (row, rw_) in enumerate(rows):
        x = (W - rw_ + 14) / 2
        y = 46 + r * 62
        for t, d, w, bw in row:
            style = rng.choice(["wb", "bw", "rw", "wb", "bw"])
            box, ink = {"wb": (WHITE, BLACK), "bw": (BLACK, WHITE), "rw": (RED, WHITE)}[style]
            edge = "#fff" if box != WHITE else BLACK
            rot = rng.uniform(-5, 5)
            pts = f"{fmt(-bw / 2)},-21 {fmt(bw / 2)},-24 {fmt(bw / 2 - 3)},19 {fmt(-bw / 2 - 3)},21"
            b.append(f'<g transform="translate({fmt(x + bw / 2)} {y}) rotate({rot:.1f})"><g class="pop" style="animation-delay:{.1 + k * .06:.2f}s">'
                     f'<g class="bob" style="animation-delay:-{(k * .37) % 3:.2f}s"><g class="spot" style="animation-delay:{2 + k * .4:.2f}s">'
                     f'<polygon points="{pts}" fill="{RED if box != RED else BLACK}" transform="translate(5 5)"/>'
                     f'<polygon points="{pts}" fill="{box}" stroke="{edge}" stroke-width="2.5" stroke-linejoin="round"/>'
                     f'<path d="{d}" transform="translate({fmt(-w / 2)} 9)" fill="{ink}"/></g></g></g></g>')
            x += bw + 14
            k += 1
    cyc = len(ARSENAL) * .4
    css = (f".spot{{transform-box:fill-box;transform-origin:50% 50%;animation:spot {cyc:.1f}s cubic-bezier(.3,1.6,.5,1) infinite both}}"
           f"@keyframes spot{{0%,{100 * .9 / cyc:.1f}%,100%{{transform:none}}{100 * .3 / cyc:.1f}%{{transform:translateY(-12px) scale(1.16) rotate(-5deg)}}}}")
    b.append(sparkles([(40, 30, 10, .3), (W - 40, H - 30, 9, 1.4), (W - 60, 28, 8, 2.2), (60, H - 24, 8, 1)]))
    return svg_doc(W, H, "".join(b), css=css, title="Arsenal: tools and languages")


# ================================================================ FOOTER

def tape(cls, y, angle, fill, ink, edge, items, speed, size=15):
    """Tape band with scrolling text, wide enough to still cover the panel when rotated."""
    parts = []
    for it in items:
        d, w = text_d("archivo", it, size, 0, 0, tracking=1.2)
        parts.append((d, w))
    cycle = sum(w + 40 for _, w in parts)
    reps = int(1500 / cycle) + 2
    segs, x = [], 0.0
    for _ in range(reps):
        for d, w in parts:
            segs.append(f'<path d="{d}" transform="translate({fmt(x)} {fmt(y + size * .36)})" fill="{ink}"/>')
            x += w + 14
            segs.append(f'<path d="{sparkle(6)}" transform="translate({fmt(x + 6)} {fmt(y)})" fill="{RED if fill != RED else BLACK}"/>')
            x += 26
    css = (f".{cls}{{animation:{cls} {cycle / speed:.1f}s linear infinite}}"
           f"@keyframes {cls}{{to{{transform:translateX(-{cycle:.1f}px)}}}}")
    body = (f'<g transform="rotate({angle} 500 {y})"><g transform="translate(-250 0)">'
            f'<rect x="0" y="{y - 15}" width="1500" height="30" fill="{fill}" stroke="{edge}" stroke-width="2.5"/>'
            f'<g class="{cls}">{"".join(segs)}</g></g></g>')
    return body, css


def syhost_logo(cx, cy):
    """SyHost emblem: a tilted terminal window with a blinking prompt and a little block."""
    sd, sw = text_d("bungee", "SY", 34, 0, 0)
    pd, pw = text_d("mono", ">", 26, 0, 0)
    total = pw + 6 + sw
    x0 = -total / 2 - 6
    leds = "".join(f'<circle cx="{-46 + i * 11}" cy="-35" r="3.6" fill="{c}" stroke="#000" stroke-width="1.2"/>'
                   for i, c in enumerate([WHITE, BLACK, WHITE]))
    return (f'<g transform="translate({cx} {cy})"><g class="pop" style="animation-delay:.5s"><g class="float">'
            f'<g class="spinR">{pivot(96)}<polygon points="{spiky(13, 80, 64, seed=6)}" fill="{BLACK}" transform="translate(7 7)"/>'
            f'<polygon points="{spiky(13, 80, 64, seed=6)}" fill="{WHITE}" stroke="#000" stroke-width="4" stroke-linejoin="round"/></g>'
            f'<g transform="rotate(-7)">'
            f'<rect x="-56" y="-44" width="116" height="84" rx="7" fill="{RED}" transform="translate(6 6)"/>'
            f'<rect x="-56" y="-44" width="116" height="84" rx="7" fill="{BLACK}" stroke="#000" stroke-width="3"/>'
            f'<path d="M-56,-37 Q-56,-44 -49,-44 L53,-44 Q60,-44 60,-37 L60,-26 L-56,-26 Z" fill="{RED}" stroke="#000" stroke-width="3"/>'
            f'{leds}'
            f'<path d="{pd}" transform="translate({fmt(x0)} 16)" fill="{RED}"/>'
            f'<path d="{sd}" transform="translate({fmt(x0 + pw + 6)} 18)" fill="{WHITE}"/>'
            f'<rect class="caret" x="{fmt(x0 + total + 4)}" y="-2" width="9" height="20" fill="{WHITE}"/>'
            f'<path d="M-44,30 L-12,30 M-4,30 L14,30" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".35"/></g>'
            f'<g transform="translate(58 46)"><g class="bob">{cube(18)}</g></g>'
            f'<g transform="translate(-66 -54)"><path d="{sparkle(10)}" fill="{RED}" stroke="#000" stroke-width="1.5" class="tw"/></g>'
            f'</g></g></g>')


def footer():
    W, H = 1000, 330
    b = ['<defs>' + PETAL_DEF + glow_def() + '</defs>']
    ta, ca = tape("tapeA", 58, -7, WHITE, BLACK, BLACK, ["SEE YOU NEXT TIME", "またね", "TAKE YOUR SERVER"], 40)
    tb, cb = tape("tapeB", 104, 5, RED, WHITE, "#fff", ["怪盗カイト", "Re:Kaixen", "ONE BOT. EVERY FEATURE."], -34)
    b.append(f'<g class="fade" style="animation-delay:.1s">{ta}{tb}</g>')
    # heading bar
    bar = f"0,150 {W},136 {W},210 0,222"
    b.append(f'<polygon points="{bar}" fill="{RED}" transform="translate(0 10)"/><polygon points="{bar}" fill="{BLACK}" {LIGHT_SAFE}/>')
    items, tw = ransom("SEE YOU NEXT TIME!", 40, seed=909, styles=["ow", "wb", "ow", "ow", "bw", "wr", "ow", "ow", "wb", "ow", "rw", "ow"], jitter=.8, overlap=.88)
    b.append(place(items, (W - tw) / 2 - 60, 184, delay=.4, step=.04, bob="hopL", bob_step=.06, bob_delay=1.6))
    kd, kw = text_d("jpd", "またね", 24, 0, 0)
    b.append(f'<g transform="translate({fmt((W + tw) / 2 - 30)} 196) rotate(-5)"><g class="pop" style="animation-delay:1.1s">'
             f'<g class="wig"><polygon points="-9,-29 {fmt(kw + 9)},-32 {fmt(kw + 12)},9 -6,11" fill="{RED}" stroke="#fff" stroke-width="2.5"/><path d="{kd}" fill="{WHITE}"/></g>'
             f'<g transform="translate({fmt(kw + 16)} -30)"><path class="beat" d="{heart(16)}" fill="{RED}" stroke="#fff" stroke-width="2"/></g></g></g>')
    # bottom line + watermark
    d, w = text_d("archivo", "MADE WITH", 14, 0, 0, tracking=2)
    d2, w2 = text_d("archivo", "AND WAY TOO MANY ANIMATIONS", 14, w + 34, 0, tracking=2)
    total = w + 34 + w2
    b.append(f'<g transform="translate({fmt((W - total) / 2 + 30)} 276)"><g class="fade" style="animation-delay:1.3s">'
             f'<polygon points="-16,-22 {fmt(total + 16)},-25 {fmt(total + 12)},10 -20,12" fill="{BLACK}" {LIGHT_SAFE}/>'
             f'<path d="{d}" fill="#fff"/><g transform="translate({fmt(w + 17)} -6)"><path class="beat" d="{heart(13)}" fill="{RED}"/></g><path d="{d2}" fill="#fff"/></g></g>')
    b.append(f'<g transform="translate({fmt((W - total) / 2 - 22)} 268)"><g class="pop" style="animation-delay:1.4s"><g class="float">'
             f'<circle r="34" fill="url(#glow)" class="pulse"/><image href="{rose(360)}" x="-30" y="-30" width="60" height="60"/></g></g></g>')
    b.append(petals(10, W, H, seed=12, scale=(.9, 1.7)))
    css = (PETAL_CSS + ca + cb)
    # shifted down a little so the tilted tapes have room at the top
    body = '<g transform="translate(0 20)">' + "".join(b[1:]) + "</g>"
    return svg_doc(W, H + 20, b[0] + body, css=css, title="See you next time! — kait")
