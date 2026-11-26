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
    odometer.n = getattr(odometer, "n", 0) + 1  # unique and stable between runs
    uid = f"odo{odometer.n}"
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
        b.append(f'<g transform="translate({x} {y}) rotate({rot})"><g class="riseT" style="animation-delay:{.25 + i * .08:.2f}s"><g class="floatT" style="animation-delay:-{i * .55:.2f}s">'
                 f'<clipPath id="st{i}"><polygon points="0,4 172,0 168,104 -4,108"/></clipPath>'
                 f'<polygon points="0,4 172,0 168,104 -4,108" fill="#000" stroke="#fff" stroke-width="1.5" transform="translate(12 12)"/>'
                 f'<polygon points="0,4 172,0 168,104 -4,108" fill="{BLACK if box != BLACK else RED}" transform="translate(6 6)" stroke="#fff" stroke-width="2"/>'
                 f'<polygon points="0,4 172,0 168,104 -4,108" fill="{box}" stroke="{BLACK}" stroke-width="3"/>'
                 f'{num}<path d="{ld}" fill="{ink}" opacity=".85"/>'
                 f'<g clip-path="url(#st{i})"><g class="shine" style="animation-delay:{2.4 + i * .3:.1f}s"><polygon points="0,0 34,0 0,120 -34,120" fill="#fff" opacity=".35"/></g></g>'
                 f'</g></g></g>')
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
    b.append(f'<clipPath id="lbar"><rect x="{x0}" y="{by}" width="{x1 - x0}" height="22"/></clipPath>'
             f'<rect x="{x0 - 6}" y="{by - 6}" width="{x1 - x0 + 12}" height="34" fill="{BLACK}" stroke="#fff" stroke-width="2"/>'
             f'<g class="growL" style="animation-delay:.6s">{"".join(segs)}</g>'
             f'<g clip-path="url(#lbar)"><g class="sweep"><rect x="{x0 - 80}" y="{by}" width="60" height="22" fill="#fff" opacity=".35"/></g></g>')
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
    b.append(sparkles([(600, 28, 9, .5), (975, 330, 8, 1.6), (40, 330, 8, 2.4)]))
    css = (".roll{animation:roll 1.6s cubic-bezier(.2,.8,.2,1) both}@keyframes roll{0%{transform:translateY(0)}100%{transform:translateY(var(--to))}}"
           ".riseT{animation:riseT .6s cubic-bezier(.2,1.3,.4,1) both}@keyframes riseT{0%{opacity:0;transform:translateY(26px)}100%{opacity:1;transform:none}}"
           ".floatT{animation:floatT 3.4s ease-in-out infinite}@keyframes floatT{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}"
           ".sweep{animation:sweep 3.8s ease-in-out 2s infinite}@keyframes sweep{0%{transform:translateX(0)}60%,100%{transform:translateX(420px)}}"
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
    b.append('<defs><linearGradient id="scan" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
             '<stop offset=".5" stop-color="#ff2a3c" stop-opacity=".22"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>'
             f'<g class="scan"><rect x="-220" y="70" width="200" height="{H - 70}" fill="url(#scan)"/></g>')
    b.append(sparkles([(160, 110, 9, .4), (420, 96, 8, 1.3), (700, 120, 10, 2.2), (880, 100, 7, .9), (300, 140, 7, 1.8)]))
    css = (".rise{transform-box:fill-box;transform-origin:50% 100%;animation:rise .9s cubic-bezier(.2,1.3,.4,1) both}@keyframes rise{0%{transform:scaleY(0)}100%{transform:none}}"
           ".scan{animation:scan 6s ease-in-out 1.5s infinite}@keyframes scan{0%{transform:translateX(0)}70%,100%{transform:translateX(1240px)}}")
    return svg_doc(W, H, "".join(b), css=css, title=f"{total} contributions in the last year as a skyline")


def bot_stats():
    """Public numbers from the Re:Kaixen site (/api/stats). Falls back to the last good reading."""
    path = os.path.join(DATA, "bot-stats.json")
    try:
        _, body = http(STATUS_URL + "/api/stats", headers={"Accept": "application/json"}, timeout=15)
        j = json.loads(body)
        data = {"guilds": int(j.get("guilds") or 0), "users": int(j.get("users") or 0),
                "uptimeMs": int(j.get("uptimeMs") or 0), "live": True}
        os.makedirs(DATA, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({k: v for k, v in data.items() if k != "live"}, f)
        return data
    except Exception:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return dict(json.load(f), live=False)
        return None


def fmt_uptime(ms):
    m = ms // 60000
    d, h, mm = m // 1440, (m % 1440) // 60, m % 60
    return f"{d}D {h}H" if d else f"{h}H {mm}M"


def status_panel(hist, bot):
    W, H = 1000, 430
    last = hist[-1]
    up = 200 <= last["code"] < 400
    b = ['<defs>' + glow_def() + halftone_defs("stdots", "stm", 1, 0, .3, 1, color=RED, op=.28) + '</defs>']
    b.append(f'<rect width="{W}" height="{H}" fill="{BLACK}"/><rect width="{W}" height="{H}" fill="url(#stdots)" mask="url(#stm)"/>')
    b.append(f'<g transform="translate(700 210)"><g class="spin"><path d="{starburst(28, 760)}" fill="{RED}" opacity=".06"/></g></g>')
    gd, gw = text_d("anton", "RE:KAIXEN RE:KAIXEN", 170, 300, 300, tracking=4)
    b.append(f'<g class="ghost"><path d="{gd}" fill="none" stroke="#fff" stroke-width="2" opacity=".07"/></g>')
    # left slab: title + emblem
    b.append(f'<g class="slideR"><polygon points="0,0 330,0 268,{H} 0,{H}" fill="{RED}"/>'
             f'<polygon points="338,0 350,0 288,{H} 276,{H}" fill="#fff"/></g>')
    items, tw = ransom("STATUS", 42, seed=717, styles=["wb", "bw", "wr", "bw", "wb", "bw"], jitter=.8)
    b.append(place(items, 30, 66, delay=.15, step=.06))
    kd, kw = text_d("jpd", "稼働状況", 18, 0, 0)
    b.append(f'<g transform="translate(36 108) rotate(-4)"><g class="pop" style="animation-delay:.6s">'
             f'<polygon points="-8,-24 {fmt(kw + 8)},-26 {fmt(kw + 10)},8 -6,9" fill="{BLACK}" stroke="#fff" stroke-width="2"/><path d="{kd}" fill="#fff"/></g></g>')
    b.append(rose_emblem(140, 262, 150, 94, 76, .45, seed=17))
    ld, lw = text_d("archivo", "LIVE", 15, 0, 0, tracking=2)
    b.append(f'<g transform="translate(34 398) rotate(-3)"><g class="pop" style="animation-delay:.9s">'
             f'<polygon points="-6,-20 {fmt(lw + 40)},-22 {fmt(lw + 37)},8 -9,9" fill="{BLACK}" stroke="#fff" stroke-width="2"/>'
             f'<circle cx="10" cy="-6" r="6" fill="{RED}" class="blinkL"/><path d="{ld}" transform="translate(24 0)" fill="#fff"/></g></g>')
    # header: name, url, online stamp, response
    nd, nw = text_d("archivo", "Re:Kaixen", 36, 360, 74)
    ud, uw = text_d("mono", "re.kaixen.online", 15, 362, 100)
    b.append(f'<g class="slideL" style="animation-delay:.2s"><path d="{nd}" fill="#fff"/><path d="{ud}" fill="#fff" opacity=".6"/></g>')
    label = "ONLINE" if up else "DOWN"
    sd, sw = text_d("anton", label, 36, 0, 0)
    b.append(f'<g transform="translate({fmt(380 + nw + 30)} 80) rotate(-5)"><g class="stamp" style="animation-delay:.7s">'
             f'<polygon points="-14,-42 {fmt(sw + 46)},-45 {fmt(sw + 42)},9 -18,11" fill="{RED}" transform="translate(6 5)"/>'
             f'<polygon points="-14,-42 {fmt(sw + 46)},-45 {fmt(sw + 42)},9 -18,11" fill="{WHITE if up else RED}" stroke="#000" stroke-width="3"/>'
             f'<circle cx="3" cy="-17" r="8" fill="{RED if up else WHITE}"/><circle cx="3" cy="-17" r="8" fill="none" stroke="{RED if up else WHITE}" stroke-width="3" class="ping"/>'
             f'<path d="{sd}" transform="translate(20 0)" fill="{BLACK if up else WHITE}"/></g></g>')
    # heartbeat line
    pts, x = [], 360
    beat = [(0, 0), (14, 0), (20, -8), (26, 0), (34, 0), (40, 10), (46, -34), (53, 22), (59, 0), (74, 0), (82, -6), (92, 0)]
    while x < 975:
        for bx, byy in beat:
            if x + bx <= 975:
                pts.append(f"{x + bx},{150 + byy}")
        x += 128
    ecg = " ".join(pts)
    b.append(f'<polyline points="{ecg}" fill="none" stroke="#fff" stroke-width="2" opacity=".15"/>'
             f'<polyline class="ecg" points="{ecg}" fill="none" stroke="{RED}" stroke-width="7" opacity=".45" stroke-linejoin="round" pathLength="100"/>'
             f'<polyline class="ecg" points="{ecg}" fill="none" stroke="#fff" stroke-width="2.6" stroke-linejoin="round" pathLength="100"/>')
    # stat tiles
    tiles = [("SERVERS", "サーバー", bot["guilds"] if bot else None),
             ("USERS", "ユーザー", bot["users"] if bot else None),
             ("BOT UPTIME", "稼働時間", fmt_uptime(bot["uptimeMs"]) if bot else None),
             ("RESPONSE", "応答", f"{last['ms']}MS" if up else "—")]
    # Tiles only ever translate (no rotate/scale animation), so the moving shine and the rolling
    # digits inside them can't shift a transform origin and make the tiles jump around.
    tw_, th_ = 128, 112
    shape = f"0,3 {tw_},0 {tw_ - 3},{th_} -3,{th_ + 3}"
    for i, (lab, jp, val) in enumerate(tiles):
        x, y = 362 + i * 154, 186
        box, ink = [(WHITE, BLACK), (RED, WHITE), (WHITE, BLACK), (RED, WHITE)][i]
        rot = [-1.5, 1, -1, 1.5][i]
        if isinstance(val, int):
            num, _ = odometer(val, 14, 60, 44, .5 + i * .12, ink=ink)
        else:
            vd, _ = text_d("anton", val or "—", 38, 14, 58)
            num = f'<path d="{vd}" fill="{ink}"/>'
        labd, _ = text_d("barlowx", lab, 15, 14, 84, tracking=.6)
        jd, _ = text_d("jp", jp, 12, 14, 101)
        cid = f"tc{i}"
        b.append(f'<g transform="translate({x} {y}) rotate({rot})"><g class="riseT" style="animation-delay:{.35 + i * .1:.2f}s"><g class="floatT" style="animation-delay:-{i * .8:.1f}s">'
                 f'<clipPath id="{cid}"><polygon points="{shape}"/></clipPath>'
                 f'<polygon points="{shape}" fill="#000" stroke="#fff" stroke-width="1.5" transform="translate(10 10)"/>'
                 f'<polygon points="{shape}" fill="{BLACK if box != BLACK else RED}" stroke="#fff" stroke-width="2" transform="translate(5 5)"/>'
                 f'<polygon points="{shape}" fill="{box}" stroke="#000" stroke-width="3"/>'
                 f'{num}<path d="{labd}" fill="{ink}"/><path d="{jd}" fill="{ink}" opacity=".7"/>'
                 f'<g clip-path="url(#{cid})"><g class="shine" style="animation-delay:{2.2 + i * .35:.2f}s"><polygon points="0,0 30,0 0,130 -30,130" fill="#fff" opacity=".35"/></g></g>'
                 f'</g></g></g>')
    # history
    n = len(hist)
    x0, x1 = 360, W - 30
    bw = (x1 - x0) / 48
    mxms = max([h["ms"] for h in hist] + [1])
    hd, _ = text_d("archivo", "LAST CHECKS", 12, x0, 340, tracking=1.5)
    b.append(f'<path d="{hd}" fill="#fff" opacity=".7"/>')
    # empty slots until the history fills up, so the strip never looks bare
    b.append("".join(f'<rect x="{fmt(x0 + k * bw)}" y="380" width="{fmt(bw - 3)}" height="12" fill="#fff" opacity=".08"/>' for k in range(48 - n)))
    for i, h in enumerate(hist):
        ok = 200 <= h["code"] < 400
        bh = 12 + 30 * min(h["ms"] / mxms, 1) if ok else 42
        xx = x1 - (n - i) * bw
        b.append(f'<g class="rise" style="animation-delay:{.8 + i * .02:.2f}s"><rect x="{fmt(xx)}" y="{fmt(392 - bh)}" width="{fmt(bw - 3)}" height="{fmt(bh)}" fill="{WHITE if ok else RED}" opacity="{.5 + .5 * (i == n - 1)}"/></g>')
    cd, _ = text_d("mono", "CHECKED " + last["t"].replace("T", " ").replace("Z", " UTC"), 12, x0, 416)
    up_n = sum(1 for h in hist if 200 <= h["code"] < 400)
    pd, _ = text_d("mono", f"UPTIME {up_n * 100 / n:.1f}% · LAST {n} CHECKS", 12, x1, 416, anchor="end")
    b.append(f'<path d="{cd}" fill="#fff" opacity=".6"/><path d="{pd}" fill="#fff" opacity=".6"/>')
    b.append(sparkles([(330, 30, 10, .4), (980, 120, 9, 1.3), (606, 320, 8, 2.1)]))
    css = (".rise{transform-box:fill-box;transform-origin:50% 100%;animation:rise .7s cubic-bezier(.2,1.3,.4,1) both}@keyframes rise{0%{transform:scaleY(0)}100%{transform:none}}"
           ".roll{animation:roll 1.6s cubic-bezier(.2,.8,.2,1) both}@keyframes roll{0%{transform:translateY(0)}100%{transform:translateY(var(--to))}}"
           ".ping{transform-box:fill-box;transform-origin:50% 50%;animation:ping 1.4s ease-out infinite}@keyframes ping{0%{transform:scale(1);opacity:1}100%{transform:scale(2.6);opacity:0}}"
           ".blinkL{animation:blinkL 1s steps(1) infinite}@keyframes blinkL{50%{opacity:.15}}"
           ".ecg{stroke-dasharray:22 78;animation:ecg 2.6s linear infinite}@keyframes ecg{0%{stroke-dashoffset:22}100%{stroke-dashoffset:-78}}"
           f".ghost{{animation:ghost 22s linear infinite}}@keyframes ghost{{0%{{transform:translateX(0)}}100%{{transform:translateX(-{gw / 2:.0f}px)}}}}"
           ".riseT{animation:riseT .6s cubic-bezier(.2,1.3,.4,1) both}@keyframes riseT{0%{opacity:0;transform:translateY(26px)}100%{opacity:1;transform:none}}"
           ".floatT{animation:floatT 3.4s ease-in-out infinite}@keyframes floatT{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}"
           ".stamp{transform-box:fill-box;transform-origin:50% 50%;animation:stamp .5s cubic-bezier(.3,1.6,.5,1) both}"
           "@keyframes stamp{0%{transform:scale(2.4) rotate(-12deg);opacity:0}100%{transform:none;opacity:1}}")
    return svg_doc(W, H, "".join(b), css=css, title=f"Re:Kaixen is {label}")


def main():
    os.makedirs(ASSETS, exist_ok=True)
    s = stats()
    hist = check_status()
    bot = bot_stats()
    for fn, svg in [("live-stats.svg", stats_panel(s)), ("live-skyline.svg", skyline_panel(s["days"])), ("live-status.svg", status_panel(hist, bot))]:
        with open(os.path.join(ASSETS, fn), "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"{fn:18} {len(svg.encode()) / 1024:7.1f} KB")
    print(f"contrib={s['contrib']} streak={s['streak']}/{s['best']} repos={s['repos']} stars={s['stars']} langs={list(s['langs'])} status={hist[-1]} bot={bot}")


if __name__ == "__main__":
    main()
