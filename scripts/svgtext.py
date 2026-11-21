"""Turn text into SVG path outlines so the README never depends on a web font.

GitHub serves README images through its camo proxy inside <img>, which blocks
external font loads. Outlining the glyphs keeps the type exact everywhere.
"""
from functools import lru_cache

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont


class Face:
    def __init__(self, path):
        self.src = path
        with open(path, "rb") as fh:
            blob = hb.Blob(fh.read())
        self.hb_font = hb.Font(hb.Face(blob))
        self.tt = TTFont(path)
        self.upem = self.tt["head"].unitsPerEm
        self.glyphs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()

    def shape(self, text, features=None):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb_font, buf, features or {"kern": True, "liga": True})
        return buf.glyph_infos, buf.glyph_positions

    def width(self, text, size, tracking=0.0):
        _, pos = self.shape(text)
        scale = size / self.upem
        return sum(p.x_advance for p in pos) * scale + tracking * size * max(len(pos) - 1, 0)

    def path(self, text, size, x, y, tracking=0.0):
        """Return the `d` attribute for `text` with its baseline at (x, y)."""
        infos, pos = self.shape(text)
        scale = size / self.upem
        pen = SVGPathPen(self.glyphs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        cx = 0.0
        for info, p in zip(infos, pos):
            name = self.order[info.codepoint]
            gx = x + (cx + p.x_offset) * scale
            gy = y - p.y_offset * scale
            tpen = TransformPen(pen, (scale, 0, 0, -scale, gx, gy))
            self.glyphs[name].draw(tpen)
            cx += p.x_advance + tracking * self.upem
        return pen.getCommands()


@lru_cache(maxsize=None)
def face(path):
    return Face(path)


def text(path, s, size, x, y, fill, anchor="start", tracking=0.0, extra=""):
    f = face(path)
    if anchor != "start":
        w = f.width(s, size, tracking)
        x = x - (w if anchor == "end" else w / 2)
    d = f.path(s, size, x, y, tracking)
    if not d:
        return ""
    return f'<path d="{d}" fill="{fill}"{(" " + extra) if extra else ""}/>'


def wrap(path, s, size, max_width):
    f = face(path)
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if f.width(trial, size) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines
