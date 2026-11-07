"""Reads the laser-cut parts drawn in Fusion 360 and exported with the Shaper Origin add-in.

Every plate, top and enclosure top in CAD/ was made that way. Each file is one black path, the part's outline, and a
white path for every hole and cut-out. The paths use M, L, A and a, in centimetres, under a transform that flips y.
The files Tools/cad/ generates are drawn the same way, in millimetres and with no transform, so this reads them too.
read() turns a file into millimetres, in the SVG's own frame: x to the right and y down from the file's top-left
corner, as LightBurn and a browser show it.

  read(path) -> Part(w, h, outline, holes, cutouts)
    outline   Shape: the part's edge
    holes     [Hole(x, y, d)]: every round hole, its centre and diameter
    cutouts   [Shape]: every other opening
  Shape(points, arcs, box)
    points    the edge as a closed polygon, arcs flattened to segments of at most 0.05 mm
    arcs      [(radius, cx, cy)] of every arc on the edge: the corner radii
    box       (x0, y0, x1, y1)
"""
import math, re
from collections import namedtuple

Hole = namedtuple('Hole', 'x y d')
Shape = namedtuple('Shape', 'points arcs box')
Part = namedtuple('Part', 'path w h outline holes cutouts')
STEP = 0.05   # mm, the longest chord an arc is flattened to


def _num(s):
    return [float(v) for v in re.findall(r'-?[\d.]+(?:e-?\d+)?', s)]


def _arc(p0, rx, large, sweep, p1):
    """The centre of the SVG arc from p0 to p1 of radius rx, and its start and end angles, in the path's own frame."""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = (x0 - x1) / 2, (y0 - y1) / 2
    d2 = dx * dx + dy * dy
    r = max(rx, math.sqrt(d2))
    k = math.sqrt(max(0.0, (r * r - d2) / d2)) if d2 else 0
    if large == sweep:
        k = -k
    cx, cy = (x0 + x1) / 2 + k * dy, (y0 + y1) / 2 - k * dx
    a0 = math.atan2(y0 - cy, x0 - cx)
    a1 = math.atan2(y1 - cy, x1 - cx)
    da = a1 - a0
    if sweep and da < 0:
        da += 2 * math.pi
    if not sweep and da > 0:
        da -= 2 * math.pi
    return cx, cy, r, a0, da


def _path(d, tx, ty, k, flip=True):
    """One path's commands -> (points, arcs) in mm, in the SVG's frame."""
    pts, arcs = [], []
    cur = start = None
    if flip:
        out = lambda x, y: ((x + tx) * k, (ty - y) * k)
    else:
        out = lambda x, y: (x * k, y * k)
    for c, args in re.findall(r'([MLAaz])([^MLAaz]*)', d):
        a = _num(args)
        if c in 'ML':
            # Fusion sometimes writes several points after one L, and SVG reads more points after M as lines
            for j in range(0, len(a), 2):
                cur = (a[j], a[j + 1])
                if c == 'M' and j == 0:
                    start = cur
                pts.append(out(*cur))
        elif c in 'Aa':
            for j in range(0, len(a), 7):
                rx, _, _, large, sweep, x, y = a[j:j + 7]
                end = (cur[0] + x, cur[1] + y) if c == 'a' else (x, y)
                cx, cy, r, a0, da = _arc(cur, rx, int(large), int(sweep), end)
                n = max(2, int(math.ceil(abs(da) * r * k / STEP)))
                for s in range(1, n + 1):
                    t = a0 + da * s / n
                    pts.append(out(cx + r * math.cos(t), cy + r * math.sin(t)))
                arcs.append((round(r * k, 4), *out(cx, cy)))
                cur = end
        elif c == 'z':
            cur = start
    return pts, arcs


def _shape(pts, arcs):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return Shape(pts, arcs, (min(xs), min(ys), max(xs), max(ys)))


def read(path):
    s = open(path, errors='replace').read()
    vb = _num(re.search(r'viewBox="([^"]+)"', s).group(1))
    w = re.search(r'\bwidth="([\d.]+)(cm|mm|in)"', s)
    k = float(w.group(1)) * {'cm': 10, 'mm': 1, 'in': 25.4}[w.group(2)] / vb[2]
    outline, holes, cutouts = None, [], []
    for m in re.finditer(r'<path\b([^>]*)>', s):
        attrs = m.group(1)
        d = re.search(r'\bd="([^"]+)"', attrs).group(1)
        tr = re.search(r'transform="matrix\(1,0,0,-1,([-\d.]+),([-\d.]+)\)"', attrs)
        tx, ty = (float(tr.group(1)), float(tr.group(2))) if tr else (0.0, 0.0)
        pts, arcs = _path(d, tx, ty, k, flip=bool(tr))   # the generated files are drawn in the SVG's own frame
        black = 'fill="rgb(0,0,0)"' in attrs
        circle = re.fullmatch(r'M[-\d.,]+ a([\d.]+),\1 0 1,1 [-\d.]+,0 a\1,\1 0 1,1 [-\d.]+,0z', d.strip())
        if black:
            if outline is not None:
                raise ValueError(f'{path}: more than one outline')
            outline = _shape(pts, arcs)
        elif circle:
            r, cx, cy = arcs[0]
            holes.append(Hole(round(cx, 4), round(cy, 4), round(2 * r, 4)))
        else:
            cutouts.append(_shape(pts, arcs))
    if outline is None:
        raise ValueError(f'{path}: no outline')
    return Part(path, round(vb[2] * k, 4), round(vb[3] * k, 4), outline, holes, cutouts)


def corner_radii(shape):
    """The distinct arc radii on a shape's edge, smallest first."""
    return sorted({round(r, 3) for r, _, _ in shape.arcs})
