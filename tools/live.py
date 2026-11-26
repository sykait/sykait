"""Live panels (GitHub stats, contribution skyline, Re:Kaixen status).

Runs on a schedule in GitHub Actions (see .github/workflows/live.yml) and
locally. Uses GITHUB_TOKEN when present; otherwise falls back to public pages.
"""
import datetime as dt
import json
import os
import re
import time
import urllib.error
import urllib.request

from common import *  # noqa: F401,F403

USER = "sykait"
STATUS_URL = "https://re.kaixen.online"
DATA = os.path.join(TOOLS, "data")
HISTORY = os.path.join(DATA, "status-history.json")
UA = {"User-Agent": "profile-live-panels", "Accept": "application/vnd.github+json"}
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def http(url, data=None, headers=None, timeout=20):
    h = dict(UA, **(headers or {}))
    if TOKEN and "api.github.com" in url:
        h["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, data=data, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()


def gh(path):
    return json.loads(http("https://api.github.com" + path)[1])


# ------------------------------------------------------------------ data

def contributions():
    """Return list of (date, count) for the last year."""
    if TOKEN:
        try:
            return _contributions_graphql()
        except Exception as e:  # token without access, API hiccup: fall back to the public page
            print("graphql failed, using public calendar:", e)
    return _contributions_public()


def _contributions_graphql():
    if True:
        q = {"query": 'query{user(login:"%s"){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}' % USER}
        _, body = http("https://api.github.com/graphql", data=json.dumps(q).encode(), headers={"Content-Type": "application/json"})
        weeks = json.loads(body)["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        return [(d["date"], d["contributionCount"]) for w in weeks for d in w["contributionDays"]]


def _contributions_public():
    _, body = http(f"https://github.com/users/{USER}/contributions", headers={"Accept": "text/html"})
    html = body.decode("utf-8", "replace")
    cells = dict(re.findall(r'data-date="(\d{4}-\d\d-\d\d)"[^>]*?id="([^"]+)"', html))
    if not cells:
        cells = {d: i for i, d in re.findall(r'id="([^"]+)"[^>]*?data-date="(\d{4}-\d\d-\d\d)"', html)}
    tips = dict(re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html))
    out = []
    for date, cid in cells.items():
        m = re.match(r"\s*(\d+) contribution", tips.get(cid, ""))
        out.append((date, int(m.group(1)) if m else 0))
    return sorted(out)


def streaks(days):
    best = cur = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        best = max(best, run)
    seq = list(reversed(days))
    if seq and seq[0][1] == 0:  # today may simply not have a commit yet
        seq = seq[1:]
    for _, c in seq:
        if not c:
            break
        cur += 1
    return cur, best


def stats():
    u = gh(f"/users/{USER}")
    repos = gh(f"/users/{USER}/repos?per_page=100&type=owner")
    stars = sum(r.get("stargazers_count", 0) for r in repos)
    langs = {}
    for r in repos:
        if r.get("fork"):
            continue
        try:
            for k, v in gh(f"/repos/{USER}/{r['name']}/languages").items():
                langs[k] = langs.get(k, 0) + v
        except urllib.error.HTTPError:
            pass
    days = contributions()
    cur, best = streaks(days)
    return {
        "repos": u.get("public_repos", 0), "followers": u.get("followers", 0), "stars": stars,
        "contrib": sum(c for _, c in days), "streak": cur, "best": best, "langs": langs, "days": days,
    }


def check_status():
    t0 = time.perf_counter()
    try:
        code, _ = http(STATUS_URL, headers={"Accept": "text/html"}, timeout=15)
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception:
        code = 0
    ms = int((time.perf_counter() - t0) * 1000)
    hist = []
    if os.path.exists(HISTORY):
        with open(HISTORY, encoding="utf-8") as f:
            hist = json.load(f)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    hist = (hist + [{"t": now, "code": code, "ms": ms}])[-48:]
    os.makedirs(DATA, exist_ok=True)
    with open(HISTORY, "w", encoding="utf-8") as f:
        json.dump(hist, f, indent=0)
    return hist


# ------------------------------------------------------------------ drawing

def odometer(value, x, y, size, delay, ink=WHITE, font="anton"):
    """Digits roll up to their value (pure CSS)."""
    s = f"{value:,}"
    _, adv, _ = glyph(font, "0", size)
    h = size * 1.05
    out, cx = [], x
    uid = f"o{abs(hash((x, y, value))) % 99999}"
    out.append(f'<clipPath id="{uid}"><rect x="{fmt(x - 4)}" y="{fmt(y - size * .92)}" width="{fmt(len(s) * adv + 12)}" height="{fmt(size * 1.02)}"/></clipPath><g clip-path="url(#{uid})">')
    for i, ch in enumerate(s):
        if not ch.isdigit():
            d, a, _ = glyph(font, ch, size, cx, y)
            out.append(f'<path d="{d}" fill="{ink}"/>')
            cx += a
            continue
        n = int(ch)
        col = "".join(f'<path d="{glyph(font, str(k % 10), size, cx, y + k * h)[0]}" fill="{ink}"/>' for k in range(n + 11))
        target = (n + 10) * h
        out.append(f'<g class="roll" style="--to:-{target:.1f}px;animation-delay:{delay + i * .08:.2f}s">{col}</g>')
        cx += adv
    out.append("</g>")
    return "".join(out), cx - x


LANG_COLORS = [RED, WHITE, "#8a8a8a", RED_D, "#d4d4d4", "#4a4a4a"]


def stats_panel(s):
    W, H = 1000, 360
    b = ['<defs>' + halftone_defs("sdots", "shm", 1, 0, .5, 1, color=RED, op=.3) + '</defs>']
    b.append(f'<rect width="{W}" height="{H}" fill="{BLACK}"/><rect width="{W}" height="{H}" fill="url(#sdots)" mask="url(#shm)"/>')
    b.append(f'<g class="slideR"><polygon points="640,-10 1010,-10 1010,370 560,370" fill="{RED}"/>'
             f'<polygon points="640,-10 1010,-10 1010,370 560,370" fill="none" stroke="#fff" stroke-width="4" transform="translate(-14 0)"/></g>')
    items, tw = ransom("PLAYER RECORD", 36, seed=515, styles=["wb", "ow", "bw", "ow", "wr", "ow", "ow", "wb", "ow", "rw", "ow", "bw"], jitter=.7, overlap=.88)
    b.append(place(items, 30, 50, delay=.15, step=.04))
    kd, kw = text_d("jpd", "戦績", 20, 0, 0)
    b.append(f'<g transform="translate({fmt(52 + tw)} 58) rotate(-4)"><g class="pop" style="animation-delay:.7s">'
             f'<polygon points="-8,-25 {fmt(kw + 8)},-27 {fmt(kw + 10)},8 -6,9" fill="{RED}" stroke="#fff" stroke-width="2"/><path d="{kd}" fill="#fff"/></g></g>')
    tiles = [("REPOS", s["repos"]), ("STARS", s["stars"]), ("FOLLOWERS", s["followers"]),
             ("CONTRIBUTIONS", s["contrib"]), ("CURRENT STREAK", s["streak"]), ("BEST STREAK", s["best"])]
    for i, (label, val) in enumerate(tiles):
        col, row = i % 3, i // 3
        x, y = 34 + col * 188, 104 + row * 120
        box, ink = [(WHITE, BLACK), (RED, WHITE), (WHITE, BLACK), (RED, WHITE), (WHITE, BLACK), (RED, WHITE)][(i + row) % 6]
        rot = [-2, 1.5, -1, 2, -1.5, 1][i]
        num, nw = odometer(val, 18, 66, 52, .4 + i * .1, ink=ink)
        ld, lw = text_d("barlowx", label, 15, 18, 92, tracking=.6)
        b.append(f'<g transform="translate({x} {y}) rotate({rot})"><g class="pop" style="animation-delay:{.25 + i * .08:.2f}s">'
                 f'<polygon points="0,4 172,0 168,104 -4,108" fill="{BLACK if box != BLACK else RED}" transform="translate(6 6)" stroke="#fff" stroke-width="2"/>'
                 f'<polygon points="0,4 172,0 168,104 -4,108" fill="{box}" stroke="{BLACK}" stroke-width="3"/>'
                 f'{num}<path d="{ld}" fill="{ink}" opacity=".85"/></g></g>')
    # languages
    langs = sorted(s["langs"].items(), key=lambda kv: -kv[1])[:6]
    total = sum(v for _, v in langs) or 1
    td, _ = text_d("archivo", "TOP LANGUAGES", 17, 660, 74, tracking=1.5)
    b.append(f'<g class="slideR" style="animation-delay:.3s"><polygon points="648,50 880,46 876,84 644,86" fill="{BLACK}"/><path d="{td}" fill="#fff"/></g>')
    x0, x1, by = 650, 965, 118
    cx = x0
    segs = []
    for i, (name, v) in enumerate(langs):
        w = (x1 - x0) * v / total
        segs.append(f'<rect x="{fmt(cx)}" y="{by}" width="{fmt(max(w, 2))}" height="22" fill="{LANG_COLORS[i]}" stroke="#000" stroke-width="2"/>')
        cx += w
    b.append(f'<rect x="{x0 - 6}" y="{by - 6}" width="{x1 - x0 + 12}" height="34" fill="{BLACK}" stroke="#fff" stroke-width="2"/>'
             f'<g class="growL" style="animation-delay:.6s">{"".join(segs)}</g>')
    for i, (name, v) in enumerate(langs):
        y = 172 + i * 30
        nd, _ = text_d("barlowx", name.upper(), 20, 690, y + 7)
        pd, pw = text_d("anton", f"{v * 100 / total:.1f}%", 20, 965, y + 7, anchor="end")
        b.append(f'<g class="slideR" style="animation-delay:{.7 + i * .07:.2f}s"><rect x="660" y="{y - 9}" width="18" height="18" fill="{LANG_COLORS[i]}" stroke="#000" stroke-width="2" transform="rotate(8 669 {y})"/>'
                 f'<path d="{nd}" fill="#fff"/><path d="{pd}" fill="#fff"/></g>')
    if not langs:
        nd, _ = text_d("barlowx", "NO LANGUAGE DATA YET", 18, 660, 180)
        b.append(f'<path d="{nd}" fill="#fff"/>')
    stamp = dt.datetime.now(dt.timezone.utc).strftime("UPDATED %Y-%m-%d %H:%M UTC")
    sd, sw = text_d("mono", stamp, 12, 0, 0)
    b.append(f'<g transform="translate({fmt(W - sw - 24)} 344)"><path d="{sd}" fill="#fff" opacity=".7"/></g>')
    css = (".roll{animation:roll 1.6s cubic-bezier(.2,.8,.2,1) both}@keyframes roll{0%{transform:translateY(0)}100%{transform:translateY(var(--to))}}"
           ".growL{transform-box:fill-box;transform-origin:0 50%;animation:growL 1.2s cubic-bezier(.2,.9,.2,1) both}@keyframes growL{0%{transform:scaleX(0)}100%{transform:none}}")
    return svg_doc(W, H, "".join(b), css=css, title="GitHub stats for sykait")


def skyline_panel(days):
    W, H = 1000, 360
    weeks = [days[i:i + 7] for i in range(0, len(days), 7)][-53:]
    mx = max([c for _, c in days] + [1])
    total = sum(c for _, c in days)
    b = [f'<rect width="{W}" height="{H}" fill="{BLACK}"/>']
    b.append(f'<g transform="translate(500 330)"><g class="spin"><path d="{starburst(28, 800)}" fill="{RED}" opacity=".07"/></g></g>')
    items, tw = ransom("SKYLINE", 34, seed=616, styles=["wb", "ow", "rw", "ow", "bw", "ow", "wr"], jitter=.7)
    b.append(place(items, 30, 46, delay=.1, step=.05))
    kd, kw = text_d("jpd", "摩天楼", 18, 0, 0)
    b.append(f'<g transform="translate({fmt(50 + tw)} 54) rotate(-4)"><g class="pop" style="animation-delay:.5s">'
             f'<polygon points="-8,-23 {fmt(kw + 8)},-25 {fmt(kw + 10)},8 -6,9" fill="{RED}" stroke="#fff" stroke-width="2"/><path d="{kd}" fill="#fff"/></g></g>')
    td, tdw = text_d("anton", f"{total:,} CONTRIBUTIONS IN THE LAST YEAR", 22, W - 30, 54, anchor="end")
    b.append(f'<g class="slideR" style="animation-delay:.3s"><path d="{td}" fill="#fff"/></g>')
    cw, dx, dy, ox, oy, hmax = 14.2, 5.2, -6.5, 70, 300, 150

    def colors(c):
        if c == 0:
            return "#1d1d1d", "#2a2a2a", "#141414"
        lv = c / mx
        if lv > .85:
            return "#f2f2f2", "#ffffff", "#bdbdbd"
        if lv > .55:
            return "#ff3347", "#ff6b78", "#b30010"
        if lv > .3:
            return "#e60012", "#ff2a3c", "#8f000c"
        return "#8f000c", "#b3000f", "#5c0008"
    peak = None
    for d in range(6, -1, -1):
        for w, week in enumerate(weeks):
            if d >= len(week):
                continue
            date, c = week[d]
            x = ox + w * cw + d * dx
            y = oy + d * dy
            h = 3 if c == 0 else 6 + (hmax - 6) * (c / mx) ** .8
            front, top, side = colors(c)
            bw = cw - 2.4
            g = (f'<rect x="{fmt(x)}" y="{fmt(y - h)}" width="{fmt(bw)}" height="{fmt(h)}" fill="{front}"/>'
                 f'<polygon points="{fmt(x)},{fmt(y - h)} {fmt(x + dx)},{fmt(y - h + dy)} {fmt(x + bw + dx)},{fmt(y - h + dy)} {fmt(x + bw)},{fmt(y - h)}" fill="{top}"/>'
                 f'<polygon points="{fmt(x + bw)},{fmt(y - h)} {fmt(x + bw + dx)},{fmt(y - h + dy)} {fmt(x + bw + dx)},{fmt(y + dy)} {fmt(x + bw)},{fmt(y)}" fill="{side}"/>')
            if c:
                g = f'<g class="rise" style="animation-delay:{.3 + w * .025 + (6 - d) * .02:.2f}s">{g}</g>'
            b.append(g)
            if c == mx and peak is None and c:
                peak = (x + bw / 2 + dx / 2, y - h + dy, c)
    if peak:
        px, py, pc = peak
        pd, pw = text_d("archivo", f"PEAK {pc}", 13, 0, 0, tracking=1)
        b.append(f'<g transform="translate({fmt(px)} {fmt(py - 16)})"><g class="pop" style="animation-delay:2s">'
                 f'<polygon points="{fmt(-pw / 2 - 9)},-22 {fmt(pw / 2 + 9)},-24 {fmt(pw / 2 + 7)},2 {fmt(-pw / 2 - 7)},3" fill="#fff" stroke="#000" stroke-width="2"/>'
                 f'<path d="{pd}" transform="translate({fmt(-pw / 2)} -5)" fill="{RED}"/><path d="M-5,3 L0,12 L5,3Z" fill="#fff"/></g></g>')
    # month labels
    seen = set()
    for w, week in enumerate(weeks):
        m = week[0][0][:7]
        if m not in seen and week[0][0][8:] <= "07":
            seen.add(m)
            name = dt.date.fromisoformat(week[0][0]).strftime("%b").upper()
            md, _ = text_d("barlowx", name, 13, ox + w * cw, 328)
            b.append(f'<path d="{md}" fill="#fff" opacity=".6"/>')
    css = ".rise{transform-box:fill-box;transform-origin:50% 100%;animation:rise .9s cubic-bezier(.2,1.3,.4,1) both}@keyframes rise{0%{transform:scaleY(0)}100%{transform:none}}"
    return svg_doc(W, H, "".join(b), css=css, title=f"{total} contributions in the last year as a skyline")


def status_panel(hist):
    W, H = 1000, 200
    last = hist[-1]
    up = 200 <= last["code"] < 400
    b = [f'<rect width="{W}" height="{H}" fill="{BLACK}"/>']
    b.append(f'<polygon points="0,0 300,0 250,{H} 0,{H}" fill="{RED}"/>')
    items, tw = ransom("STATUS", 32, seed=717, styles=["wb", "bw", "wr", "bw", "wb", "bw"], jitter=.7)
    b.append(place(items, 28, 46, delay=.1, step=.05))
    kd, kw = text_d("jpd", "稼働状況", 15, 34, 92)
    b.append(f'<g class="fade" style="animation-delay:.4s"><path d="{kd}" fill="#fff"/></g>')
    b.append(f'<g transform="translate(70 145)"><g class="pop" style="animation-delay:.5s"><g class="float">'
             f'<circle r="32" fill="url(#glow)" class="pulse"/><image href="{rose(360)}" x="-30" y="-30" width="60" height="60"/></g></g></g>')
    nd, nw = text_d("archivo", "Re:Kaixen", 30, 300, 66)
    ud, uw = text_d("mono", "re.kaixen.online", 15, 300, 92)
    b.append(f'<g class="slideR" style="animation-delay:.2s"><path d="{nd}" fill="#fff"/><path d="{ud}" fill="#fff" opacity=".6"/></g>')
    label = "ONLINE" if up else "DOWN"
    ld, lw = text_d("anton", label, 34, 0, 0)
    b.append(f'<g transform="translate({fmt(320 + nw + 40)} 70) rotate(-4)"><g class="pop" style="animation-delay:.6s">'
             f'<polygon points="-14,-38 {fmt(lw + 44)},-41 {fmt(lw + 40)},8 -18,10" fill="{WHITE if up else RED}" stroke="#000" stroke-width="3"/>'
             f'<circle cx="2" cy="-15" r="8" fill="{RED if up else WHITE}" class="ping"/>'
             f'<path d="{ld}" transform="translate(18 0)" fill="{BLACK if up else WHITE}"/></g></g>')
    md, mw = text_d("anton", f"{last['code'] or 'ERR'} · {last['ms']} MS", 26, W - 30, 70, anchor="end")
    b.append(f'<g class="slideR" style="animation-delay:.5s"><path d="{md}" fill="#fff"/></g>')
    # history bars
    n = len(hist)
    x0, x1 = 300, W - 30
    bw = (x1 - x0) / 48
    mxms = max([h["ms"] for h in hist] + [1])
    for i, h in enumerate(hist):
        ok = 200 <= h["code"] < 400
        bh = 14 + 38 * min(h["ms"] / mxms, 1) if ok else 52
        x = x1 - (n - i) * bw
        b.append(f'<g class="rise" style="animation-delay:{.6 + i * .02:.2f}s"><rect x="{fmt(x)}" y="{fmt(170 - bh)}" width="{fmt(bw - 3)}" height="{fmt(bh)}" fill="{WHITE if ok else RED}" opacity="{.55 + .45 * (i == n - 1)}"/></g>')
    cd, _ = text_d("mono", "CHECKED " + last["t"].replace("T", " ").replace("Z", " UTC"), 12, x0, 192)
    up_n = sum(1 for h in hist if 200 <= h["code"] < 400)
    pd, _ = text_d("mono", f"UPTIME {up_n * 100 / n:.1f}% (LAST {n} CHECKS)", 12, x1, 192, anchor="end")
    b.append(f'<path d="{cd}" fill="#fff" opacity=".6"/><path d="{pd}" fill="#fff" opacity=".6"/>')
    css = (".rise{transform-box:fill-box;transform-origin:50% 100%;animation:rise .7s cubic-bezier(.2,1.3,.4,1) both}@keyframes rise{0%{transform:scaleY(0)}100%{transform:none}}"
           ".ping{transform-box:fill-box;transform-origin:50% 50%;animation:ping 1.4s ease-out infinite}@keyframes ping{0%{transform:scale(.6);opacity:1}100%{transform:scale(1.6);opacity:.2}}")
    return svg_doc(W, H, '<defs>' + glow_def() + '</defs>' + "".join(b), css=css, title=f"Re:Kaixen is {label}")


def main():
    os.makedirs(ASSETS, exist_ok=True)
    s = stats()
    hist = check_status()
    for fn, svg in [("live-stats.svg", stats_panel(s)), ("live-skyline.svg", skyline_panel(s["days"])), ("live-status.svg", status_panel(hist))]:
        with open(os.path.join(ASSETS, fn), "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"{fn:18} {len(svg.encode()) / 1024:7.1f} KB")
    print(f"contrib={s['contrib']} streak={s['streak']}/{s['best']} repos={s['repos']} stars={s['stars']} langs={list(s['langs'])} status={hist[-1]}")


if __name__ == "__main__":
    main()
