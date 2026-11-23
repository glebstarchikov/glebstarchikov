"""Build every SVG for the Sprite profile.

python scripts/build.py            # live data from the GitHub API
python scripts/build.py data.json  # cached data, for offline previews
"""
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ghdata  # noqa: E402
from svgtext import face, text, wrap  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONT = str(ROOT / "fonts" / "DepartureMono-Regular.otf")
BLUE = "#0B5ED7"

BIO = ("Founder of AI Natives. Building for an AI-native future, where people "
       "and agents work well together. AI adoption at Philips, RSM student.")

BIO_LINES = ["Founder of AI Natives.", "Building for an AI-native future, where",
             "people and agents work well together.", "AI adoption at Philips, RSM student."]

PROJECTS = [
    ("plainly", "A no-code content editor on top of a site's git repo.", "TypeScript", "pencil"),
    ("good-eye", "A design-inspiration database Claude can search while it builds.", "TypeScript", "eye"),
    ("claude-widget", "The Claude Code critter that lives in your Mac menu bar.", "Swift", "menubar"),
    ("launchpad", "A self-hosted command center for a solo founder.", "TypeScript", "rocket"),
    ("rag-workshop", "A notebook that teaches RAG to people who don't already code.", "Jupyter Notebook", "notebook"),
]

# 12x12 hand-drawn icons. '#' = ink, '+' = accent, '.' = empty.
ICONS = {
    "pencil": [
        "..........##", ".........#+#", "........#++#", ".......#++#.",
        "......#++#..", ".....#++#...", "....#++#....", "...#++#.....",
        "..#++#......", "..###.......", ".##.........", "............",
    ],
    "eye": [
        "............", "............", "....####....", "..##....##..",
        ".#...++...#.", "#...++++...#", "#...++++...#", ".#...++...#.",
        "..##....##..", "....####....", "............", "............",
    ],
    "menubar": [
        "############", "#+#+#.....##", "############", "............",
        "...######...", "..#......#..", "..#.#..#.#..", "..#......#..",
        "..#.####.#..", "...######...", "...#.#.#....", "............",
    ],
    "rocket": [
        ".....##.....", "....#++#....", "....#++#....", "...#+##+#...",
        "...#+##+#...", "...#++++#...", "..##++++##..", ".#.#++++#.#.",
        ".#.######.#.", "....#..#....", "....+..+....", "...+....+...",
    ],
    "notebook": [
        ".#########..", "##.......#..", ".#.+++++.#..", "##.......#..",
        ".#.+++...#..", "##.......#..", ".#.++++..#..", "##.......#..",
        ".#.++....#..", "##.......#..", ".#########..", "............",
    ],
}

THEMES = {
    "dark": {"bg": "#0d1117", "card": "#111a2b", "line": "#1f3b66", "ink": "#e6edf3",
             "muted": "#9fb3cf", "icon": "#e6edf3", "accent": "#5b9bff",
             "ramp": ["#161b22", "#0a3a85", "#0B5ED7", "#4d8ff0", "#a9cbff"]},
    "light": {"bg": "#ffffff", "card": "#f5f8fe", "line": "#c9dbf7", "ink": "#0b1b33",
              "muted": "#4a5d78", "icon": "#0b1b33", "accent": BLUE,
              "ramp": ["#ebeff5", "#bcd4f6", "#6fa2ea", "#0B5ED7", "#073b8a"]},
}


def svg(w, h, body, title, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{title}"><title>{title}</title>'
            + (f"<style>{style}</style>" if style else "") + body + "</svg>\n")


# Pixel desk that replaces the portrait. GitHub shows the header at about
# 830px, so a cell of 2 user units is just under 2 CSS pixels there.
DESK_W, DESK_H = 150, 120
DESK_CELL = 2


class Desk:
    def __init__(self):
        self.g = [[None] * DESK_W for _ in range(DESK_H)]
        self.cursor = None

    def set(self, x, y, ch):
        if 0 <= x < DESK_W and 0 <= y < DESK_H and ch is not None:
            self.g[y][x] = ch

    def rect(self, x, y, w, h, ch):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, ch)

    def frame(self, x, y, w, h, stroke, fill=None, t=1):
        self.rect(x, y, w, h, stroke)
        if fill is not None and w > 2 * t and h > 2 * t:
            self.rect(x + t, y + t, w - 2 * t, h - 2 * t, fill)

    def ellipse(self, cx, cy, rx, ry, ch):
        if rx <= 0 or ry <= 0:
            return
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.05:
                    self.set(x, y, ch)

    def blade(self, x, top, height, fill):
        self.set(x + 2, top, "ink")
        self.rect(x + 1, top + 1, 3, 1, "ink")
        self.set(x + 2, top + 1, fill)
        body = height - 2
        self.rect(x, top + 2, 5, body, "ink")
        self.rect(x + 1, top + 3, 3, max(body - 2, 1), fill)
        self.rect(x + 2, top + 3, 1, max(body - 2, 1), "leaf2")


def desk_grid():
    """Open laptop, mug, and plant on a desk. One cell per entry."""
    g = Desk()
    desk_y = 98
    g.frame(2, desk_y, 146, 18, "ink", "edge", t=1)
    g.rect(3, desk_y + 1, 144, 6, "desk")
    g.rect(3, desk_y + 1, 144, 1, "hi")

    for bx, top, height, fill in (
        (10, 40, 36, "leaf"),
        (16, 28, 48, "leaf"),
        (22, 22, 54, "leaf2"),
        (28, 30, 46, "leaf"),
        (34, 42, 34, "leaf"),
    ):
        g.blade(bx, top, height, fill)
    g.frame(12, 78, 26, 22, "ink", "pot", t=1)
    g.frame(8, 74, 34, 6, "ink", "pot", t=1)
    g.rect(13, 79, 24, 3, "coffee")

    base_x, base_y, base_w, base_h = 52, 78, 62, 22
    g.frame(base_x, base_y, base_w, base_h, "ink", "deck", t=2)
    screen_w, screen_h = 50, 52
    screen_x = base_x + (base_w - screen_w) // 2
    screen_y = base_y - screen_h
    g.frame(screen_x, screen_y, screen_w, screen_h, "ink", "screen", t=3)
    g.rect(screen_x + 4, base_y, screen_w - 8, 3, "hinge")
    g.rect(screen_x + screen_w // 2 - 1, screen_y + 1, 2, 1, "key")

    key_w, key_h, gap = 4, 3, 1
    cols = 10
    row_w = cols * key_w + (cols - 1) * gap
    key_x0 = base_x + (base_w - row_w) // 2
    for ky in (base_y + 5, base_y + 10):
        for col in range(cols):
            g.rect(key_x0 + col * (key_w + gap), ky, key_w, key_h, "key")
    tp_w = 16
    g.frame(base_x + (base_w - tp_w) // 2, base_y + 15, tp_w, 4, "ink", "key", t=1)

    ix = screen_x + 6
    iy = screen_y + 9
    words = [
        [(0, 10), (12, 8), (22, 6)],
        [(0, 18), (20, 6)],
        [(0, 8), (10, 7)],
        [(0, 14), (16, 6)],
        [(0, 9)],
    ]
    for i, line in enumerate(words):
        for x0, w in line:
            g.rect(ix + x0, iy + i * 6, w, 2, "type")
    # Caret sits on bare screen, just after the third line.
    g.cursor = (ix + 17, iy + 10, 2, 6)

    mx, my, mw, mh = 122, 80, 16, 18
    g.frame(mx, my, mw, mh, "ink", "mug", t=1)
    g.ellipse(mx + mw // 2, my, mw // 2 + 1, 3, "ink")
    g.ellipse(mx + mw // 2, my, mw // 2 - 1, 2, "mug")
    g.ellipse(mx + mw // 2, my + 1, mw // 2 - 2, 1, "coffee")
    g.rect(mx + 2, my + 4, 1, 8, "hi")
    hy = my + 4
    g.rect(mx + mw - 1, hy, 2, 10, "ink")
    g.rect(mx + mw + 1, hy, 4, 2, "ink")
    g.rect(mx + mw + 1, hy + 8, 4, 2, "ink")
    g.rect(mx + mw + 4, hy + 1, 2, 8, "ink")
    for dx, dy in ((2, 0), (3, 4), (1, 8), (6, 2), (7, 6), (5, 10)):
        g.rect(mx + dx, my - 16 + dy, 2, 2, "steam")
    return g


def scene_colors(theme):
    """Sprite palette only. The banner stays Philips blue. The scene does not."""
    t = THEMES[theme]
    if theme == "light":
        colors = {
            "ink": t["ink"], "desk": t["card"], "edge": t["muted"], "screen": t["bg"],
            "type": t["muted"], "key": t["card"], "deck": t["muted"], "mug": t["bg"],
            "coffee": t["ink"], "leaf": t["muted"], "leaf2": t["ink"], "pot": t["line"],
            "steam": t["bg"], "hinge": t["ink"], "hi": t["bg"],
        }
    else:
        colors = {
            "ink": t["ink"], "desk": t["card"], "edge": t["line"], "screen": t["bg"],
            "type": t["muted"], "key": t["muted"], "deck": t["bg"], "mug": t["ink"],
            "coffee": t["card"], "leaf": t["muted"], "leaf2": t["ink"], "pot": t["line"],
            "steam": t["ink"], "hinge": t["muted"], "hi": t["muted"],
        }
    allowed = {v.lower() for v in t.values() if isinstance(v, str)}
    for role, hexc in colors.items():
        if hexc.lower() not in allowed or hexc.lower() in (BLUE.lower(), t["accent"].lower()):
            raise SystemExit(f"scene color {role}={hexc} is outside the {theme} palette")
        red, green, blue = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
        if red > 180 and green < 160 and blue < 120:
            raise SystemExit(f"scene color {role}={hexc} reads as orange")
    return colors


def desk_svg(theme):
    g = desk_grid()
    colors = scene_colors(theme)
    cx, cy, cw, caret_h = g.cursor
    for y in range(cy, cy + caret_h):
        for x in range(cx, cx + cw):
            if g.g[y][x] != "screen":
                raise SystemExit("laptop caret is not sitting on the screen")
    xs, ys = [], []
    for y, row in enumerate(g.g):
        for x, pixel in enumerate(row):
            if pixel is not None:
                xs.append(x)
                ys.append(y)
    x0, y0, x1, y1 = min(xs + [cx]), min(ys + [cy]), max(xs + [cx + cw - 1]), max(ys + [cy + caret_h - 1])
    cell = DESK_CELL
    pw, ph = (x1 - x0 + 1) * cell, (y1 - y0 + 1) * cell
    # Left of the name, and inset from the rounded banner so nothing clips.
    slot_x, slot_r, slot_y, slot_b = 18, 328, 16, 284
    place_x = slot_x + (slot_r - slot_x - pw) // 2
    place_y = slot_y + (slot_b - slot_y - ph) // 2
    if place_x < 16 or place_y < 16 or place_x + pw > slot_r or place_y + ph > slot_b:
        raise SystemExit(f"desk scene is clipped or short on padding ({place_x},{place_y},{pw},{ph})")
    parts = ['<g shape-rendering="crispEdges">']
    for y, row in enumerate(g.g):
        x = 0
        while x < DESK_W:
            ch = row[x]
            if ch is None:
                x += 1
                continue
            x1 = x + 1
            while x1 < DESK_W and row[x1] == ch:
                x1 += 1
            parts.append(
                f'<rect x="{place_x + (x - x0) * cell}" y="{place_y + (y - y0) * cell}" '
                f'width="{(x1 - x) * cell}" height="{cell}" fill="{colors[ch]}"/>'
            )
            x = x1
    # Drawn on top of the screen. Default opacity is 1, so a viewer with
    # animation turned off still sees the caret.
    parts.append(
        f'<rect class="cur" x="{place_x + (cx - x0) * cell}" y="{place_y + (cy - y0) * cell}" '
        f'width="{cw * cell}" height="{caret_h * cell}" fill="{colors["ink"]}"/>'
    )
    parts.append("</g>")
    return "".join(parts)


def header():
    W, H = 880, 300
    # The name stays in the column beside the old portrait slot.
    tx = 24 + 64 * 4.6 + 28
    # The caret stays visible when animation does not run. Blink only hides it
    # while the animation is actually playing.
    style = (".cur{animation:blink 1.1s steps(1) infinite 1.7s}"
             "@keyframes blink{50%{opacity:0}}"
             "@media (prefers-reduced-motion:reduce){.cur{animation:none;opacity:1}}")
    for theme in THEMES:
        body = [f'<rect width="{W}" height="{H}" rx="10" fill="{BLUE}"/>', desk_svg(theme)]
        body.append(text(FONT, "Gleb Starchikov", 44, tx, 100, "#ffffff"))
        y = 146
        for ln in BIO_LINES:
            body.append(text(FONT, ln, 16.5, tx, y, "#dce8fb"))
            y += 27
        last_w = face(FONT).width(BIO_LINES[-1], 16.5)
        body.append(f'<rect class="cur" x="{tx + last_w + 6:.1f}" y="{y - 27 - 14:.1f}" width="10" height="17" fill="#ffffff"/>')
        body.append(text(FONT, "glebstarchikov.nl", 16.5, tx, H - 34, "#ffffff", extra='opacity="0.75"'))
        out = svg(W, H, "".join(body), "Gleb Starchikov. " + BIO, style)
        if "shape-rendering=\"crispEdges\"" not in out or "avatar" in out:
            raise SystemExit(f"header-{theme}.svg is missing crisp pixels")
        (ASSETS / f"header-{theme}.svg").write_text(out)
    for dead in ("header.svg", "avatar.png"):
        path = ASSETS / dead
        if path.exists():
            path.unlink()


def icon(name, x, y, cell, ink, accent):
    out = []
    for r, row in enumerate(ICONS[name]):
        for c, ch in enumerate(row):
            if ch != ".":
                out.append(f'<rect x="{x + c * cell}" y="{y + r * cell}" width="{cell}" height="{cell}" '
                           f'fill="{ink if ch == "#" else accent}"/>')
    return "".join(out)


def card(project, theme):
    name, desc, lang, ic = project
    t = THEMES[theme]
    W, H = 432, 146
    b = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="{t["card"]}" stroke="{t["line"]}"/>',
         icon(ic, 22, 24, 4, t["icon"], t["accent"]),
         text(FONT, name, 22, 88, 46, t["ink"])]
    y = 74
    for ln in wrap(FONT, desc, 13.75, W - 88 - 22)[:2]:
        b.append(text(FONT, ln, 13.75, 88, y, t["muted"]))
        y += 20
    b.append(f'<rect x="88" y="{H - 31}" width="8" height="8" fill="{t["accent"]}"/>')
    b.append(text(FONT, lang, 13.75, 102, H - 22, t["muted"]))
    (ASSETS / f"card-{name}-{theme}.svg").write_text(svg(W, H, "".join(b), f"{name}: {desc}"))


def empty_slot(theme):
    t = THEMES[theme]
    W, H = 432, 146
    plus = ["....##....", "....##....", "....##....", "##########", "##########",
            "....##....", "....##....", "....##...."]
    b = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="8" fill="none" stroke="{t["line"]}" '
         f'stroke-width="2" stroke-dasharray="6 6"/>']
    for r, row in enumerate(plus):
        for c, ch in enumerate(row):
            if ch == "#":
                b.append(f'<rect x="{26 + c * 4}" y="{34 + r * 4}" width="4" height="4" fill="{t["accent"]}"/>')
    b.append(text(FONT, "next experiment", 22, 88, 46, t["ink"]))
    b.append(text(FONT, "Empty slot, saved for whatever I", 13.75, 88, 74, t["muted"]))
    b.append(text(FONT, "start next.", 13.75, 88, 94, t["muted"]))
    b.append(text(FONT, "all repositories", 13.75, 88, H - 22, t["accent"]))
    (ASSETS / f"card-next-{theme}.svg").write_text(svg(W, H, "".join(b), "Next experiment: empty slot"))


def contrib(days, theme):
    t = THEMES[theme]
    cell, gap = 12, 3
    first = dt.date.fromisoformat(days[0][0])
    pad = (first.weekday() + 1) % 7  # weeks start on Sunday, like GitHub
    cols = (pad + len(days) + 6) // 7
    W = cols * (cell + gap) - gap + 2
    H = 7 * (cell + gap) + 40
    b = []
    for i, (date, n, level) in enumerate(days):
        k = i + pad
        x, y = 1 + (k // 7) * (cell + gap), (k % 7) * (cell + gap)
        b.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{t["ramp"][level]}"/>')
    total = sum(n for _, n, _ in days)
    label = f"{total:,} contributions in the last year"
    updated = f"updated {days[-1][0]}"
    b.append(text(FONT, label, 13.75, 1, H - 8, t["muted"]))
    b.append(text(FONT, updated, 13.75, W - 1, H - 8, t["muted"], anchor="end"))
    title = f"{total} contributions in the last year"
    out = svg(W, H, "".join(b), title)
    if title not in out or "font-family" in out or "<text" in out:
        raise SystemExit(f"contrib-{theme}.svg did not outline the contribution total")
    (ASSETS / f"contrib-{theme}.svg").write_text(out)


def main():
    if len(sys.argv) > 1:
        days = [tuple(d) for d in json.loads(Path(sys.argv[1]).read_text())["contrib"]]
    else:
        days = ghdata.contributions()
    if not days:
        raise SystemExit("no contribution days to draw")
    total = sum(n for _, n, _ in days)
    print(f"drawing {total} contributions from {days[0][0]} to {days[-1][0]}")
    header()
    for theme in THEMES:
        for p in PROJECTS:
            card(p, theme)
        empty_slot(theme)
        contrib(days, theme)


if __name__ == "__main__":
    main()
