"""A small pixel canvas that turns drawn pixels into compact SVG paths.

Drawing happens on an integer grid where later pixels overwrite earlier ones,
like a real pixel-art editor. When written out, every horizontal run of one
colour becomes a tiny path segment and all runs of a colour share one <path>,
which keeps a detailed scene to a few hundred kilobytes.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass

from .font import GLYPH_H, GLYPH_W, glyph

Color = str | None


class Raster:
    """A width x height grid of hex colours; None means transparent."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.grid: list[list[Color]] = [[None] * width for _ in range(height)]
        self.clip = (0, 0, width, height)

    def set_clip(self, x0: int, y0: int, x1: int, y1: int) -> None:
        """Ignore any pixel drawn outside this box."""
        self.clip = (x0, y0, x1, y1)

    def get(self, x: int, y: int) -> Color:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None

    def px(self, x: int, y: int, c: Color) -> None:
        x0, y0, x1, y1 = self.clip
        if c is not None and x0 <= x < x1 and y0 <= y < y1:
            self.grid[y][x] = c

    def clear(self, x: int, y: int, w: int, h: int) -> None:
        """Make a box transparent again."""
        for yy in range(max(0, y), min(self.height, y + h)):
            for xx in range(max(0, x), min(self.width, x + w)):
                self.grid[yy][xx] = None

    def rect(self, x: int, y: int, w: int, h: int, c: Color) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, c)

    def hline(self, x: int, y: int, w: int, c: Color) -> None:
        self.rect(x, y, w, 1, c)

    def vline(self, x: int, y: int, h: int, c: Color) -> None:
        self.rect(x, y, 1, h, c)

    def line(self, x0: int, y0: int, x1: int, y1: int, c: Color) -> None:
        """One-pixel line between two points (Bresenham)."""
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def poly(self, pts: list[tuple[float, float]], c: Color) -> None:
        """Fill a polygon, testing pixel centres (even-odd rule)."""
        ys = [p[1] for p in pts]
        n = len(pts)
        for yy in range(math.floor(min(ys)), math.ceil(max(ys)) + 1):
            cy = yy + 0.5
            xs = []
            for i in range(n):
                (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
                if (ay <= cy < by) or (by <= cy < ay):
                    xs.append(ax + (cy - ay) * (bx - ax) / (by - ay))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2], strict=False):
                for xx in range(math.ceil(a - 0.5), math.ceil(b - 0.5)):
                    self.px(xx, yy, c)

    def ellipse(self, cx: float, cy: float, rx: float, ry: float, c: Color) -> None:
        """Fill an ellipse. Centres are continuous: 10.5 is the middle of pixel 10."""
        for yy in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
            for xx in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
                dx = (xx + 0.5 - cx) / rx
                dy = (yy + 0.5 - cy) / ry
                if dx * dx + dy * dy <= 1.0:
                    self.px(xx, yy, c)

    def disc(self, cx: float, cy: float, r: float, c: Color) -> None:
        self.ellipse(cx, cy, r, r, c)

    def dither(self, x: int, y: int, w: int, h: int, c1: Color, c2: Color) -> None:
        """Checkerboard of two colours, the classic pixel-art blend."""
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, c1 if (xx + yy) % 2 == 0 else c2)

    def text(self, x: int, y: int, s: str, c: Color, scale: int = 1) -> None:
        for i, ch in enumerate(s):
            rows = glyph(ch)
            ox = x + i * (GLYPH_W + 1) * scale
            for ry in range(GLYPH_H):
                for rx in range(GLYPH_W):
                    if rows[ry][rx] == "#":
                        self.rect(ox + rx * scale, y + ry * scale, scale, scale, c)

    def to_svg(self) -> str:
        runs: dict[str, list[str]] = defaultdict(list)
        for y, row in enumerate(self.grid):
            if not any(row):
                continue
            x = 0
            w = self.width
            while x < w:
                c = row[x]
                if c is None:
                    x += 1
                    continue
                start = x
                while x < w and row[x] == c:
                    x += 1
                n = x - start
                runs[c].append(f"M{start} {y}h{n}v1h-{n}z")
        return "".join(f'<path fill="{c}" d="{"".join(d)}"/>' for c, d in runs.items())


class Mask(Raster):
    """Records which pixels a shape covers instead of colouring them."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.clip = (0, 0, width, height)
        self.points: set[tuple[int, int]] = set()

    def px(self, x: int, y: int, c: Color) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.points.add((x, y))

    def outline(self) -> set[tuple[int, int]]:
        """Covered pixels that touch an uncovered one."""
        pts = self.points
        return {
            (x, y)
            for (x, y) in pts
            if any((x + dx, y + dy) not in pts for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        }


@dataclass
class Sprite:
    """A separately animated layer, written out as its own <g> with a CSS class."""

    cls: str
    raster: Raster
    style: str = ""
    clip: str = ""  # id of a clipPath that keeps the layer inside a region

    def to_svg(self) -> str:
        body = self.raster.to_svg()
        if not body:
            return ""
        cls = f' class="{self.cls}"' if self.cls else ""
        style = f' style="{self.style}"' if self.style else ""
        g = f"<g{cls}{style}>{body}</g>"
        return f'<g clip-path="url(#{self.clip})">{g}</g>' if self.clip else g
