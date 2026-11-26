"""Big story panels: hero, Re:Kaixen card, trailer."""
from common import *  # noqa: F401,F403


# ====================================================================== HERO

def hero():
    W, H = 1000, 420
    shard = [(-30, 46), (578, 16), (616, 96), (548, 236), (640, 264), (556, 394), (-30, 406)]
    pts = " ".join(f"{x},{y}" for x, y in shard)
    defs = ('<defs>'
            '<radialGradient id="bg" cx=".62" cy=".48" r=".75"><stop offset="0" stop-color="#ff1a2e"/>'
            '<stop offset=".55" stop-color="#e60012"/><stop offset="1" stop-color="#a1000d"/></radialGradient>'
            + glow_def() + halftone_defs("dots", "hm", 0, 1, .55, .35)
            + f'<clipPath id="shardclip"><polygon points="{pts}"/></clipPath></defs>')
    b = [defs, f'<rect width="{W}" height="{H}" fill="url(#bg)"/>']
    b.append(f'<g transform="translate(790 205)"><g class="spin"><path d="{starburst(30, 900)}" fill="#000" opacity=".12"/></g></g>')
    b.append(f'<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#hm)"/>')
    # floating background stars
    for x, y, r, dl in [(660, 395, 22, 0), (705, 40, 14, .6), (930, 395, 18, 1.2)]:
        b.append(f'<g transform="translate({x} {y})"><g class="spinF" style="animation-delay:-{dl * 7}s">'
                 f'<polygon points="{star5(r)}" fill="none" stroke="#000" stroke-width="3" opacity=".55"/></g></g>')
    # black shard + offset white edge
    b.append(f'<g class="slideL" style="animation-delay:.05s"><polygon points="{pts}" fill="none" stroke="{WHITE}" stroke-width="5" '
             f'stroke-linejoin="round" transform="translate(13 11)"/></g>')
    b.append(f'<g class="slideL"><polygon points="{pts}" fill="{BLACK}"/></g>')
    b.append(f'<g clip-path="url(#shardclip)"><g class="shine" style="animation-delay:2.2s">'
             f'<polygon points="0,0 70,0 -50,420 -120,420" fill="#fff" opacity=".13"/>'
             f'<polygon points="95,0 115,0 -5,420 -25,420" fill="#fff" opacity=".1"/></g></g>')
    # big faint kanji inside the shard
    d, _ = text_d("jp", "怪盗", 92, 418, 398)
    b.append(f'<g class="fade" style="animation-delay:.6s"><path d="{d}" fill="none" stroke="#fff" stroke-width="2" opacity=".16"/></g>')

    # top tag
    d, w = text_d("archivo", "PLAYER PROFILE", 15, 0, 0, tracking=1.5)
    b.append(f'<g transform="translate(58 76) rotate(-4)"><g class="slideL" style="animation-delay:.25s">'
             f'<polygon points="-12,-20 {fmt(w + 14)},-23 {fmt(w + 8)},7 -16,9" fill="{RED}"/>'
             f'<path d="{d}" fill="{WHITE}"/></g></g>')
    items, _ = ransom("No.01", 30, seed=4, styles=["bo", "wb", "ow", "wr", "bw"], jitter=.6)
    b.append(place(items, w + 98, 64, delay=.45, step=.05))

    # name
    items, nw = ransom("kait", 152, seed=7, styles=["wb", "rw", "ow", "wb"], jitter=1.6)
    b.append(place(items, 62, 172, delay=.35, step=.12))

    # speech bubble
    bx, by = 548, 96
    hi, hw = ransom("HI!", 34, seed=12, styles=["bo", "wr", "bo"], jitter=.5)
    b.append(f'<g transform="translate({bx} {by})"><g class="pop" style="animation-delay:1.05s"><g class="wig">'
             f'<polygon points="{spiky(11, 58, 42, seed=5, wobble=.18)}" fill="{BLACK}" transform="translate(6 6)"/>'
             f'<polygon points="{spiky(11, 58, 42, seed=5, wobble=.18)}" fill="{WHITE}" stroke="{BLACK}" stroke-width="4" stroke-linejoin="round"/>'
             f'{place(hi, -hw / 2 - 6, -4, pop=None, bob=None)}'
             f'<g transform="translate(30 -24)"><path class="beat" d="{heart(20)}" fill="{RED}" stroke="{BLACK}" stroke-width="2.5"/></g>'
             f"</g></g></g>")

    # subtitle strip
    segs = ["ANIMATOR", "BUILDS WITH AI", "FOUNDER OF Re:Kaixen"]
    st, sw = strip_text(segs, 21, 70, 290)
    x2 = 70 + sw + 26
    poly = f"46,262 {fmt(x2 + 14)},256 {fmt(x2 - 2)},304 36,310"
    b.append(f'<g class="slideL" style="animation-delay:.7s"><polygon points="{poly}" fill="{RED}" transform="translate(9 8)"/>'
             f'<polygon points="{poly}" fill="{WHITE}"/><polygon points="{poly}" fill="{BLACK}" transform="translate(3 3) scale(.995)"/>'
             f'{st}</g>')

    # japanese line
    d, _ = text_d("jp", "アニメーションとツールをつくってます", 18, 72, 346)
    nd, _ = text_d("jp", "♪", 22, 72 + measure("jp", "アニメーションとツールをつくってます", 18) + 8, 348)
    b.append(f'<g class="fade" style="animation-delay:1.35s"><path d="{d}" fill="{WHITE}"/>'
             f'<g transform="translate(0 0)"><path class="bob" d="{nd}" fill="{RED}" stroke="#fff" stroke-width="1"/></g></g>')

    # rose emblem
    b.append(rose_emblem(772, 206, 276, 168, 136, .55))

    # vertical kanji strip
    d = vtext_d("jp", "怪盗カイト", 23, 983, 34, gap=1.12)
    b.append(f'<g class="slideD" style="animation-delay:.4s"><polygon points="966,0 1000,0 1000,{H} 958,{H}" fill="{BLACK}"/>'
             f'<path d="{d}" fill="{WHITE}"/><rect x="971" y="186" width="24" height="3" fill="{RED}"/></g>')

    # handle tag
    d, w = text_d("archivo", "@sykait", 17, 0, 0)
    b.append(f'<g transform="translate(608 386) rotate(-5)"><g class="pop" style="animation-delay:1.25s">'
             f'<polygon points="-12,-20 {fmt(w + 12)},-23 {fmt(w + 9)},8 -9,6" fill="{WHITE}" stroke="{BLACK}" stroke-width="3"/>'
             f'<path d="{d}" fill="{BLACK}"/></g></g>')

    b.append(sparkles([(648, 62, 15, 0), (948, 96, 11, .8), (668, 322, 12, 1.5), (928, 338, 17, .4),
                       (622, 196, 9, 1.9), (336, 58, 9, 1.1), (478, 360, 11, .6), (230, 375, 8, 2.1)]))
    return svg_doc(W, H, "".join(b), title="kait — animator, builds with AI, founder of Re:Kaixen")


# ================================================================ REKAIXEN

def rekaixen():
    W, H = 1000, 600
    slab = "-20,-20 604,-20 474,620 -20,620"
    defs = ('<defs>' + glow_def() + halftone_defs("dots2", "hm2", 0, 1, .7, 0, r=2.4, op=.42)
            + '<clipPath id="slabclip"><polygon points="' + slab + '"/></clipPath>'
            + '<linearGradient id="slabg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff1a2e"/>'
            + '<stop offset="1" stop-color="#c3000f"/></linearGradient></defs>')
    b = [defs, f'<rect width="{W}" height="{H}" fill="{BLACK}"/>']
    b.append(f'<g transform="translate(860 150)"><g class="spin"><path d="{starburst(26, 900)}" fill="#fff" opacity=".055"/></g></g>')
    for x, y, r, dl in [(960, 560, 26, 0), (640, 40, 15, 3), (985, 300, 13, 6), (560, 575, 17, 9)]:
        b.append(f'<g transform="translate({x} {y})"><g class="spinF" style="animation-delay:-{dl}s">'
                 f'<polygon points="{star5(r)}" fill="none" stroke="#fff" stroke-width="2.5" opacity=".35"/></g></g>')

    b.append(f'<g class="slideL" style="animation-delay:.08s"><polygon points="{slab}" fill="none" stroke="{WHITE}" stroke-width="5" transform="translate(16 0)"/></g>')
    b.append(f'<g class="slideL"><polygon points="{slab}" fill="url(#slabg)"/>'
             f'<rect width="{W}" height="{H}" fill="url(#dots2)" mask="url(#hm2)" clip-path="url(#slabclip)"/></g>')
    b.append(f'<g clip-path="url(#slabclip)"><g class="shine" style="animation-delay:3s">'
             f'<polygon points="0,0 80,0 -60,600 -140,600" fill="#fff" opacity=".14"/></g></g>')

    # tag
    d, w = text_d("archivo", "MAIN PROJECT", 19, 0, 0, tracking=1.5)
    kd, kw = text_d("jp", "本命", 22, w + 30, 1)
    b.append(f'<g transform="translate(52 52) rotate(-3)"><g class="slideL" style="animation-delay:.2s">'
             f'<polygon points="-16,-24 {fmt(w + kw + 52)},-28 {fmt(w + kw + 46)},10 -20,12" fill="{BLACK}" stroke="#fff" stroke-width="2.5"/>'
             f'<path d="{d}" fill="{WHITE}"/>'
             f'<polygon points="{fmt(w + 20)},-22 {fmt(w + kw + 40)},-25 {fmt(w + kw + 37)},6 {fmt(w + 17)},8" fill="{WHITE}"/>'
             f'<path d="{kd}" fill="{RED}"/></g></g>')
    b.append(f'<g transform="translate({fmt(w + kw + 92)} 48)"><polygon class="beat" points="{star5(13)}" fill="{WHITE}" stroke="#000" stroke-width="2"/></g>')

    # big name
    items, nw = ransom("Re:Kaixen", 100, seed=21, styles=["wb", "bw", "rw", "wb", "bw", "wr", "ow", "wb", "bw"])
    b.append(place(items, 40, 160, delay=.35, step=.08))

    # tagline
    d, tw = text_d("anton", "ONE BOT. EVERY FEATURE.", 56, 44, 300)
    b.append(f'<g class="slideL" style="animation-delay:.95s"><path d="{d}" fill="{BLACK}" transform="translate(5 5)"/><path d="{d}" fill="{WHITE}"/></g>')

    # description
    desc = ("Why invite 15 different bots when one can do it all? Re:Kaixen packs everything your server "
            "needs into a single bot, and its built-in AI assistant helps you build and run your server "
            "just by chatting, right in Discord or on the web.")
    lines = wrap("barlow", desc, 20, 455)
    parts = []
    for i, ln in enumerate(lines):
        d, _ = text_d("barlow", ln, 20, 46, 342 + i * 27)
        parts.append(f'<path d="{d}" fill="{WHITE}"/>')
    b.append(f'<g class="fade" style="animation-delay:1.25s">{"".join(parts)}</g>')

    # footer
    st, sw = strip_text(["re.kaixen.online", "discord.gg/kaixen"], 17, 58, 562, font="archivo", gap=24)
    b.append(f'<g class="slideL" style="animation-delay:1.45s"><polygon points="34,536 {fmt(58 + sw + 24)},532 {fmt(58 + sw + 16)},574 28,578" fill="{BLACK}"/>{st}</g>')

    # feature menu (Persona-style staircase with a moving selector)
    feats = [("MODERATION", "管理"), ("LEVELING", "成長"), ("TICKETS", "窓口"), ("GIVEAWAYS", "抽選"),
             ("ANTI-NUKE", "防衛"), ("AI ASSISTANT", "相棒"), ("& MUCH MORE", "もっと")]
    mx, my, dy, dx = 640, 312, 40, -14
    n = len(feats)
    # Game-menu cursor: hop down one item at a time (overshoot + squash on landing, a flash and
    # a star pop), and from the last item keep going down off the list, then drop back in from
    # above onto the first item.
    S, m = 1.55, .32            # time per item, move time
    a = n * S - m               # leave the last item
    b2 = a + .22                # gone below the list
    c = b2 + .02                # teleported above the list
    T = c + .32                 # landed on the first item again (= start of the loop)
    P = lambda t: f"{t / T * 100:.2f}%"
    pos = lambda i, extra=0: f"translate({i * dx}px,{i * dy + extra}px)"
    kf = [f"0%{{transform:{pos(0)} scale(1,1);opacity:1}}"]
    arrivals = [0.0]
    for i in range(1, n):
        t0, t2 = i * S - m, i * S
        kf.append(f"{P(t0)}{{transform:{pos(i - 1)} scale(1,1);opacity:1}}")
        kf.append(f"{P(t2 - m * .35)}{{transform:{pos(i, 8)} scale(1.05,.84);opacity:1}}")
        kf.append(f"{P(t2)}{{transform:{pos(i)} scale(1,1);opacity:1}}")
        arrivals.append(t2)
    kf.append(f"{P(a)}{{transform:{pos(n - 1)} scale(1,1);opacity:1}}")
    kf.append(f"{P(b2)}{{transform:{pos(n)} scale(1,.55);opacity:0}}")
    kf.append(f"{P(c)}{{transform:{pos(-1)} scale(1,.55);opacity:0}}")
    kf.append(f"{P(T - .32 * .35)}{{transform:{pos(0, 8)} scale(1.05,.84);opacity:1}}")
    kf.append(f"100%{{transform:{pos(0)} scale(1,1);opacity:1}}")
    css = ("@keyframes sel{" + "".join(kf) + "}"
           f".sel{{transform-box:fill-box;transform-origin:50% 50%;animation:sel {T:.2f}s ease-in-out 1.8s infinite both}}")
    # landing flash + star pop, one keyframe set each, synced to the same loop
    fl, sp = ["0%{opacity:.75}"], ["0%{transform:scale(1.5) rotate(40deg)}"]
    for t in arrivals[1:]:
        fl += [f"{P(t - .02)}{{opacity:0}}", f"{P(t)}{{opacity:.75}}", f"{P(t + .28)}{{opacity:0}}"]
        sp += [f"{P(t - .02)}{{transform:scale(1) rotate(0)}}", f"{P(t + .06)}{{transform:scale(1.5) rotate(40deg)}}", f"{P(t + .35)}{{transform:scale(1) rotate(0)}}"]
    fl += [f"{P(.28)}{{opacity:0}}", f"{P(T - .03)}{{opacity:0}}", "100%{opacity:.75}"]
    sp += [f"{P(.35)}{{transform:scale(1) rotate(0)}}", f"{P(T - .03)}{{transform:scale(1) rotate(0)}}", "100%{transform:scale(1.5) rotate(40deg)}"]
    fl.sort(key=lambda s: float(s.split("%")[0])); sp.sort(key=lambda s: float(s.split("%")[0]))
    css += ("@keyframes flash{" + "".join(fl) + "}" + f".flash{{animation:flash {T:.2f}s linear 1.8s infinite both}}"
            "@keyframes starP{" + "".join(sp) + "}" + f".starP{{transform-box:fill-box;transform-origin:50% 50%;animation:starP {T:.2f}s ease-out 1.8s infinite both}}")
    poly = f"{mx - 34},{my - 26} {mx + 320},{my - 31} {mx + 306},{my + 13} {mx - 42},{my + 15}"
    b.append(f'<g class="fade" style="animation-delay:1.6s"><g class="sel">'
             f'<polygon points="{poly}" fill="{BLACK}" stroke="#fff" stroke-width="2" transform="translate(6 5)"/>'
             f'<polygon points="{poly}" fill="{RED}"/>'
             f'<polygon class="flash" points="{poly}" fill="#fff"/>'
             f'<g transform="translate({mx - 52} {my - 7})"><g class="starP"><polygon points="{star5(14)}" fill="{WHITE}" stroke="#000" stroke-width="2.5"/></g></g>'
             f"</g></g>")
    # each item slides right and grows a little while the cursor sits on it
    for i, (en, jp) in enumerate(feats):
        x, y = mx + i * dx, my + i * dy
        s_ = 0.0 if i == 0 else i * S
        e_ = a if i == n - 1 else (i + 1) * S - m
        on, off = "transform:translateX(16px) scale(1.08)", "transform:none"
        if i == 0:
            hk = f"0%{{{on}}}{P(e_)}{{{on}}}{P(e_ + .16)}{{{off}}}{P(T - .14)}{{{off}}}100%{{{on}}}"
        else:
            hk = f"0%{{{off}}}{P(s_ - .14)}{{{off}}}{P(s_)}{{{on}}}{P(e_)}{{{on}}}{P(e_ + .16)}{{{off}}}100%{{{off}}}"
        css += (f"@keyframes hl{i}{{{hk}}}"
                f".hl{i}{{transform-box:fill-box;transform-origin:0% 50%;animation:hl{i} {T:.2f}s cubic-bezier(.3,1.6,.5,1) 1.8s infinite both}}")
        its, ww = ransom(en, 27, seed=100 + i, styles=["ow", "ow", "ow", "wb", "ow", "ow", "bw", "ow", "ow", "ow", "wr", "ow"], jitter=.55, overlap=.86)
        kd, _ = text_d("jp", jp, 16, x + ww + 12, y + 6)
        b.append(f'<g class="slideR" style="animation-delay:{1.0 + i * .08:.2f}s"><g class="hl{i}">{place(its, x - 8, y - 6, pop=None, bob=None)}'
                 f'<path d="{kd}" fill="{WHITE}" opacity=".85"/></g></g>')

    b.append(rose_emblem(866, 160, 220, 136, 110, .6, seed=8))
    b.append(sparkles([(735, 50, 12, .3), (975, 230, 10, 1.2), (742, 258, 13, 2), (520, 470, 9, .9), (590, 120, 8, 1.6)]))
    return svg_doc(W, H, "".join(b), css=css, title="Re:Kaixen — one Discord bot, every feature")


# ================================================================= TRAILER

def trailer():
    W, H = 1000, 600
    sw_, sh_ = 704, 396
    cx, cy = 492, 368
    x0, y0 = cx - sw_ / 2, cy - sh_ / 2
    cover = image_data_uri(COVER, 1056, quality=80, height=594)
    defs = ('<defs>' + glow_def() + PETAL_DEF
            + '<radialGradient id="tbg" cx=".5" cy=".55" r=".7"><stop offset="0" stop-color="#7a0010"/>'
            + '<stop offset=".7" stop-color="#2a0005"/><stop offset="1" stop-color="#0a0a0a"/></radialGradient>'
            + halftone_defs("dots3", "hm3", 1, 0, .3, .8, r=2.3, color="#ff1a2e", op=.32)
            + f'<clipPath id="scr"><rect x="{x0}" y="{y0}" width="{sw_}" height="{sh_}"/></clipPath></defs>')
    b = [defs, f'<rect width="{W}" height="{H}" fill="url(#tbg)"/>']
    b.append(f'<g transform="translate({cx} {cy})"><g class="spin"><path d="{starburst(32, 900)}" fill="#000" opacity=".35"/></g></g>')
    b.append(f'<rect width="{W}" height="{H}" fill="url(#dots3)" mask="url(#hm3)"/>')
    # red slash lines
    b.append(f'<g class="slideL" style="animation-delay:.1s"><polygon points="-20,520 1020,430 1020,446 -20,540" fill="{RED}"/>'
             f'<polygon points="-20,92 1020,10 1020,16 -20,100" fill="#fff" opacity=".8"/></g>')

    # screen (tilted) with layered frames
    b.append(f'<g transform="rotate(-2.2 {cx} {cy})"><g class="pop" style="animation-delay:.25s">'
             f'<rect x="{x0 - 14}" y="{y0 - 14}" width="{sw_ + 28}" height="{sh_ + 28}" fill="{RED}" transform="translate(16 14)"/>'
             f'<rect x="{x0 - 14}" y="{y0 - 14}" width="{sw_ + 28}" height="{sh_ + 28}" fill="{BLACK}" transform="translate(8 7)"/>'
             f'<rect x="{x0 - 14}" y="{y0 - 14}" width="{sw_ + 28}" height="{sh_ + 28}" fill="{WHITE}"/>'
             f'<g clip-path="url(#scr)"><rect x="{x0}" y="{y0}" width="{sw_}" height="{sh_}" fill="#000"/>'
             f'<g class="kb"><image href="{cover}" x="{x0}" y="{y0}" width="{sw_}" height="{sh_}" preserveAspectRatio="xMidYMid slice"/></g>'
             f'<rect x="{x0}" y="{y0}" width="{sw_}" height="{sh_}" fill="#000" opacity=".18"/>'
             f'<g class="shine" style="animation-delay:2.4s"><polygon points="0,0 90,0 -60,700 -150,700" fill="#fff" opacity=".16"/></g></g>'
             # play button
             f'<g transform="translate({cx - 34} {y0 + sh_ - 64}) scale(.68)"><g class="pop" style="animation-delay:.9s"><g class="beatS">'
             f'<g class="spinR">{pivot(92)}<polygon points="{spiky(14, 78, 60, seed=11, wobble=.1)}" fill="{BLACK}" transform="translate(6 6)"/>'
             f'<polygon points="{spiky(14, 78, 60, seed=11, wobble=.1)}" fill="{WHITE}" stroke="{BLACK}" stroke-width="5" stroke-linejoin="round"/></g>'
             f'<circle r="50" fill="{RED}" stroke="{BLACK}" stroke-width="4"/>'
             f'<path d="M-15,-25 L28,0 L-15,25 Z" fill="{WHITE}" stroke="{BLACK}" stroke-width="3" stroke-linejoin="round"/>'
             f"</g></g></g>"
             # REC-style corner label
             f'<g transform="translate({x0 + 22} {y0 + 30})"><g class="fade" style="animation-delay:1.1s">'
             f'<circle r="7" fill="{RED}" class="blink"/></g></g>'
             f"</g></g>")
    d, w = text_d("archivo", "NOW PLAYING", 13, 0, 0, tracking=1.5)
    b.append(f'<g transform="translate({x0 + 40} {y0 + 22}) rotate(-2.2)"><g class="fade" style="animation-delay:1.1s">'
             f'<path d="{d}" transform="translate(0 13)" fill="{WHITE}"/></g></g>')

    # title
    items, tw = ransom("TRAILER", 60, seed=31, styles=["bw", "wr", "wb", "ow", "bw", "wb", "rw"])
    b.append(place(items, 34, 78, delay=.3, step=.07))
    kd, kw = text_d("jp", "予告編", 24, 0, 0)
    b.append(f'<g transform="translate({fmt(tw + 58)} 72) rotate(5)"><g class="pop" style="animation-delay:.85s">'
             f'<polygon points="-10,-30 {fmt(kw + 10)},-33 {fmt(kw + 13)},8 -7,10" fill="{RED}" transform="translate(5 5)"/>'
             f'<polygon points="-10,-30 {fmt(kw + 10)},-33 {fmt(kw + 13)},8 -7,10" fill="{WHITE}" stroke="#000" stroke-width="3"/>'
             f'<path d="{kd}" fill="{RED}"/></g></g>')

    # TAKE YOUR SERVER strip (top right)
    d, w = text_d("anton", "TAKE YOUR SERVER", 40, 0, 0, tracking=1)
    sx = W - w - 74
    b.append(f'<g transform="translate({fmt(sx)} 92) rotate(-4)"><g class="slideR" style="animation-delay:.6s">'
             f'<polygon points="-22,-44 {fmt(w + 24)},-50 {fmt(w + 16)},10 -28,14" fill="{BLACK}" transform="translate(7 6)"/>'
             f'<polygon points="-22,-44 {fmt(w + 24)},-50 {fmt(w + 16)},10 -28,14" fill="{RED}" stroke="#fff" stroke-width="3"/>'
             f'<path d="{d}" fill="{WHITE}"/></g></g>')

    # bottom-left: click to watch tag
    d, w = text_d("archivo", "CLICK TO WATCH", 18, 0, 0, tracking=1)
    kd, kw = text_d("jp", "今すぐ見る", 15, w + 22, -1)
    b.append(f'<g transform="translate(70 572) rotate(-3)"><g class="slideL" style="animation-delay:1.2s"><g class="bobB">'
             f'<polygon points="-18,-26 {fmt(w + kw + 40)},-29 {fmt(w + kw + 34)},10 -22,12" fill="{WHITE}" stroke="#000" stroke-width="3"/>'
             f'<path d="{d}" fill="{BLACK}"/><path d="{kd}" fill="{RED}"/></g></g></g>')

    # vertical kanji + small watermark
    vd = vtext_d("jp", "サーバーを奪え", 20, 976, 166, gap=1.1)
    b.append(f'<g class="slideD" style="animation-delay:.5s"><polygon points="958,150 994,146 996,330 960,334" fill="{BLACK}" stroke="#fff" stroke-width="2"/>'
             f'<path d="{vd}" fill="{WHITE}"/></g>')
    b.append(f'<g transform="translate(938 532)"><g class="pop" style="animation-delay:1.3s"><g class="float">'
             f'<circle r="50" fill="url(#glow)" class="pulse"/><image href="{rose(360)}" x="-44" y="-44" width="88" height="88"/></g></g></g>')

    b.append(petals(14, W, H, seed=5))
    b.append(sparkles([(60, 160, 10, .2), (905, 210, 12, 1.1), (150, 470, 9, 1.8), (880, 455, 11, .7)]))
    css = (PETAL_CSS
           + ".kb{transform-box:fill-box;transform-origin:50% 50%;animation:kb 14s ease-in-out infinite alternate}"
           + "@keyframes kb{0%{transform:scale(1)}100%{transform:scale(1.035)}}"
           + ".beatS{transform-box:fill-box;transform-origin:50% 50%;animation:beatS 1.8s ease-in-out infinite}"
           + "@keyframes beatS{0%,100%{transform:scale(1)}12%{transform:scale(1.1)}24%{transform:scale(.98)}36%{transform:scale(1.05)}}"
           + ".blink{animation:blink 1.2s steps(2,start) infinite}@keyframes blink{to{visibility:hidden}}"
           + ".bobB{animation:bobB 2.8s ease-in-out infinite}@keyframes bobB{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}")
    return svg_doc(W, H, "".join(b), css=css, title="Re:Kaixen trailer — Take Your Server")


