"""Build every SVG for the Sprite profile.

python scripts/build.py            # live data from the GitHub API
python scripts/build.py data.json  # cached data, for offline previews
"""
import datetime as dt
import json
import sys
from pathlib import Path

from PIL import Image

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


def portrait_rects(size=64, scale=4.5, ox=0.0, oy=0.0):
    """Downsample the avatar into a real pixel grid, one <g> per row."""
    im = Image.open(ASSETS / "avatar.png").convert("RGB").resize((size, size), Image.BOX)
    q = im.quantize(colors=22, method=Image.Quantize.MEDIANCUT).convert("RGB")
    rows = []
    for y in range(size - 2):  # the source has a light seam on its last rows
        runs, x = [], 0
        while x < size:
            c = q.getpixel((x, y))
            r, g, b = c
            if b > 150 and b > r + 90 and r < 90:  # background blue: let the banner show through
                x += 1
                continue
            start = x
            while x + 1 < size and q.getpixel((x + 1, y)) == c:
                x += 1
            hexc = "#%02x%02x%02x" % c
            x0, x1 = round(ox + start * scale), round(ox + (x + 1) * scale)
            y0, y1 = round(oy + y * scale), round(oy + (y + 1) * scale)
            runs.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{hexc}"/>')
            x += 1
        if runs:
            rows.append((y, "".join(runs)))
    return rows


def header():
    W, H = 880, 300
    scale = 4.6
    px = 64 * scale
    ox, oy = 24, H - 57.5 * scale
    body = [f'<rect width="{W}" height="{H}" rx="10" fill="{BLUE}"/>',
            f'<clipPath id="c"><rect width="{W}" height="{H}" rx="10"/></clipPath><g clip-path="url(#c)" shape-rendering="crispEdges">']
    for y, rects in portrait_rects(64, scale, ox, oy):
        body.append(f'<g class="r" style="animation-delay:{y * 0.025:.3f}s">{rects}</g>')
    body.append("</g>")
    tx = ox + px + 28
    body.append(text(FONT, "Gleb Starchikov", 44, tx, 100, "#ffffff"))
    lines = BIO_LINES
    y = 146
    for ln in lines:
        body.append(text(FONT, ln, 16.5, tx, y, "#dce8fb"))
        y += 27
    last_w = face(FONT).width(lines[-1], 16.5)
    body.append(f'<rect class="cur" x="{tx + last_w + 6:.1f}" y="{y - 27 - 14:.1f}" width="10" height="17" fill="#ffffff"/>')
    body.append(text(FONT, "glebstarchikov.nl", 16.5, tx, H - 34, "#ffffff", extra='opacity="0.75"'))
    # The portrait stays visible when a viewer skips SVG animation. The
    # keyframes only hide rows while the draw-in is actually running.
    style = (".r{animation:in .01s steps(1) both}"
             "@keyframes in{from{opacity:0}to{opacity:1}}"
             ".cur{animation:blink 1.1s steps(1) infinite 1.7s}"
             "@keyframes blink{50%{opacity:0}}"
             "@media (prefers-reduced-motion:reduce){.r,.cur{animation:none;opacity:1}}")
    (ASSETS / "header.svg").write_text(svg(W, H, "".join(body), "Gleb Starchikov. " + BIO, style))


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
