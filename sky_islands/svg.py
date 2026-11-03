"""A tiny SVG builder: layers of shapes, gradients and batched rectangles.

Shapes are written with short attribute lists and rounded numbers so a
detailed scene stays a few hundred kilobytes, which keeps README images fast.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from xml.sax.saxutils import escape

_QUOTE = {'"': "&quot;"}


def num(v: float) -> str:
    """Format a number with at most two decimals and no trailing zeros."""
    if isinstance(v, int):
        return str(v)
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def attrs(a: dict) -> str:
    """Turn keyword arguments into SVG attributes: class_ -> class, clip_path -> clip-path."""
    out = []
    for k, v in a.items():
        if v is None:
            continue
        name = k.rstrip("_").replace("_", "-")
        text = num(v) if isinstance(v, int | float) else escape(str(v), _QUOTE)
        out.append(f' {name}="{text}"')
    return "".join(out)


def pts(points: Iterable[tuple[float, float]]) -> str:
    return " ".join(f"{num(x)},{num(y)}" for x, y in points)


class Layer:
    """An ordered list of SVG elements; later elements draw on top."""

    def __init__(self) -> None:
        self.items: list[str] = []

    def __bool__(self) -> bool:
        return bool(self.items)

    def raw(self, s: str) -> None:
        self.items.append(s)

    def el(self, tag: str, **a) -> None:
        self.items.append(f"<{tag}{attrs(a)}/>")

    def rect(self, x: float, y: float, w: float, h: float, fill: str, **a) -> None:
        self.el("rect", x=x, y=y, width=w, height=h, fill=fill, **a)

    def circle(self, cx: float, cy: float, r: float, fill: str, **a) -> None:
        self.el("circle", cx=cx, cy=cy, r=r, fill=fill, **a)

    def ellipse(self, cx: float, cy: float, rx: float, ry: float, fill: str, **a) -> None:
        self.el("ellipse", cx=cx, cy=cy, rx=rx, ry=ry, fill=fill, **a)

    def poly(self, points: Iterable[tuple[float, float]], fill: str, **a) -> None:
        self.el("polygon", points=pts(points), fill=fill, **a)

    def path(self, d: str, fill: str = "none", **a) -> None:
        self.el("path", d=d, fill=fill, **a)

    def line(self, x1: float, y1: float, x2: float, y2: float, stroke: str, w: float = 1,
             **a) -> None:
        self.el("line", x1=x1, y1=y1, x2=x2, y2=y2, stroke=stroke, stroke_width=w, **a)

    def text(self, x: float, y: float, s: str, size: float = 10, fill: str = "#e6edf3",
             **a) -> None:
        self.items.append(f"<text{attrs({'x': x, 'y': y, 'font_size': size, 'fill': fill, **a})}>"
                          f"{escape(s)}</text>")

    def group(self, child: Layer | Rects, **a) -> None:
        body = child.svg()
        if body:
            self.items.append(f"<g{attrs(a)}>{body}</g>")

    def add(self, child: Layer | Rects) -> None:
        body = child.svg()
        if body:
            self.items.append(body)

    def svg(self) -> str:
        return "".join(self.items)


class Rects:
    """Many small rectangles (windows, cells, bricks) batched into one path per colour."""

    def __init__(self) -> None:
        self.runs: dict[str, list[str]] = defaultdict(list)

    def add(self, x: float, y: float, w: float, h: float, fill: str) -> None:
        self.runs[fill].append(f"M{num(x)} {num(y)}h{num(w)}v{num(h)}h{num(-w)}z")

    def svg(self) -> str:
        return "".join(f'<path fill="{c}" d="{"".join(d)}"/>' for c, d in self.runs.items())


class Defs:
    """Gradients and clip paths shared by the whole drawing."""

    def __init__(self) -> None:
        self.items: list[str] = []
        self.ids: set[str] = set()

    def _stops(self, stops: Iterable[tuple]) -> str:
        out = []
        for stop in stops:
            off, color = stop[0], stop[1]
            op = stop[2] if len(stop) > 2 else None
            out.append(f"<stop{attrs({'offset': off, 'stop_color': color, 'stop_opacity': op})}/>")
        return "".join(out)

    def linear(self, id_: str, stops: Iterable[tuple], x2: float = 0, y2: float = 1) -> str:
        """A gradient that runs top to bottom unless x2/y2 say otherwise."""
        if id_ not in self.ids:
            self.ids.add(id_)
            self.items.append(
                f'<linearGradient id="{id_}" x1="0" y1="0" x2="{num(x2)}" y2="{num(y2)}">'
                f"{self._stops(stops)}</linearGradient>"
            )
        return f"url(#{id_})"

    def radial(self, id_: str, stops: Iterable[tuple], **a) -> str:
        """A round gradient; pass cx/cy/fx/fy/r (0-1) to move its centre or focus."""
        if id_ not in self.ids:
            self.ids.add(id_)
            self.items.append(
                f'<radialGradient id="{id_}"{attrs(a)}>{self._stops(stops)}</radialGradient>'
            )
        return f"url(#{id_})"

    def pattern(self, id_: str, w: float, h: float, body: str) -> str:
        """A tile repeated across whatever it fills, aligned to the drawing's origin."""
        if id_ not in self.ids:
            self.ids.add(id_)
            self.items.append(f'<pattern id="{id_}" width="{num(w)}" height="{num(h)}" '
                              f'patternUnits="userSpaceOnUse">{body}</pattern>')
        return f"url(#{id_})"

    def clip(self, id_: str, shape: str) -> str:
        if id_ not in self.ids:
            self.ids.add(id_)
            self.items.append(f'<clipPath id="{id_}">{shape}</clipPath>')
        return f"url(#{id_})"

    def mask(self, id_: str, body: str) -> str:
        """A soft mask: white in `body` shows what it covers, black hides it."""
        if id_ not in self.ids:
            self.ids.add(id_)
            self.items.append(f'<mask id="{id_}" maskUnits="userSpaceOnUse">{body}</mask>')
        return f"url(#{id_})"

    def blur(self, amount: float) -> str:
        """A soft-focus filter, for things far away or made of mist."""
        id_ = f"blur{num(amount).replace('.', '_')}"
        if id_ not in self.ids:
            self.ids.add(id_)
            self.items.append(
                f'<filter id="{id_}" x="-20%" y="-50%" width="140%" height="200%">'
                f'<feGaussianBlur stdDeviation="{num(amount)}"/></filter>'
            )
        return f"url(#{id_})"

    def grain(self) -> str:
        """Fine noise laid over everything for a soft, hand-made texture."""
        if "grain" not in self.ids:
            self.ids.add("grain")
            self.items.append(
                '<filter id="grain" x="0" y="0" width="100%" height="100%">'
                '<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" '
                'stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 .5 0 0 0 0 .5 0 0 0 0 .5 '
                '0 0 0 .9 0"/></filter>'
            )
        return "url(#grain)"

    def svg(self) -> str:
        return f"<defs>{''.join(self.items)}</defs>"
