"""The half of generate.py that needs KiCad: run in KiCad's own Python, with a JSON job on stdin and a JSON answer as
the last line of stdout. generate.py runs it; it isn't run by hand.

  {"do": "write", "path": ..., "name": ..., "letters": [[ch, [contour, ...]], ...]}
      write the footprint: each letter one filled polygon on F.SilkS, its contours combined even-odd (a contour
      inside another is a hole) and fractured, so its holes join its outline in a single polygon.
  {"do": "compare", "jobs": [{"repo", "fp", "path", "letters"}, ...]}
      load each library footprint, unfracture its polygons back into outlines and holes, and measure each letter
      against the generated one: the furthest any point of either boundary is from the other boundary.

Coordinates are mm, y down, as in the footprint. The rules for scripting pcbnew are in Tools/README.md.
"""
import sys, os, json, uuid
import pcbnew
import numpy as np

def letter_set(contours):
    """One letter's contours, combined even-odd, as a SHAPE_POLY_SET with real outlines and holes."""
    acc = None
    for c in contours:
        one = pcbnew.SHAPE_POLY_SET()
        one.NewOutline()
        for x, y in c: one.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
        if acc is None: acc = one
        else: acc.BooleanXor(one)
    return acc

def write(job):
    fp = pcbnew.FOOTPRINT(None)
    fp.SetFPID(pcbnew.LIB_ID('', job['name']))
    fp.SetAttributes(pcbnew.FP_BOARD_ONLY | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM)
    for field, text, x in ((fp.Reference(), 'G***', 0), (fp.Value(), 'LOGO', 0.75)):
        field.SetText(text); field.SetLayer(pcbnew.F_SilkS); field.SetVisible(False)
        field.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), 0))
        field.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.5), pcbnew.FromMM(1.5)))
        field.SetTextThickness(pcbnew.FromMM(0.3))
    for ch, contours in job['letters']:
        ps = letter_set(contours)
        ps.Fracture()
        for i in range(ps.OutlineCount()):
            one = pcbnew.SHAPE_POLY_SET(); one.AddOutline(ps.Outline(i))
            sh = pcbnew.PCB_SHAPE(fp, pcbnew.SHAPE_T_POLY)
            sh.SetPolyShape(one); sh.SetFilled(True); sh.SetWidth(0); sh.SetLayer(pcbnew.F_SilkS)
            fp.Add(sh)
    lib = os.path.dirname(job['path'])
    pcbnew.PCB_IO_KICAD_SEXPR().FootprintSave(lib, fp)
    # The same logo gives the same file: every uuid comes from the footprint's name and its place in the file.
    t = open(job['path']).read()
    n = [0]
    def fixed(m):
        n[0] += 1
        return f'(uuid "{uuid.uuid5(uuid.NAMESPACE_URL, "6502-logo/" + job["name"] + "/" + str(n[0]))}")'
    import re
    t = re.sub(r'\(uuid "[0-9a-f-]+"\)', fixed, t)
    open(job['path'], 'w').write(t)
    return {'ok': True}

def boundary(ps):
    """Every edge of a SHAPE_POLY_SET's outlines and holes, as (start, end) arrays in mm."""
    segs = []
    for i in range(ps.OutlineCount()):
        chains = [ps.Outline(i)] + [ps.Hole(i, h) for h in range(ps.HoleCount(i))]
        for ch in chains:
            pts = np.array([[pcbnew.ToMM(ch.CPoint(k).x), pcbnew.ToMM(ch.CPoint(k).y)] for k in range(ch.PointCount())])
            segs.append(np.stack([pts, np.roll(pts, -1, axis=0)], axis=1))
    return np.concatenate(segs)

def sample(segs, step=0.004):
    out = []
    for a, b in segs:
        n = max(1, int(np.ceil(np.hypot(*(b - a)) / step)))
        t = np.arange(n)[:, None] / n
        out.append(a + (b - a) * t)
    return np.concatenate(out)

def far(points, segs):
    """The furthest any of points is from the nearest of segs."""
    a, b = segs[:, 0], segs[:, 1]
    ab = b - a
    L = np.maximum((ab ** 2).sum(1), 1e-18)
    worst = 0.0
    for chunk in np.array_split(points, max(1, len(points) // 400)):
        ap = chunk[:, None, :] - a[None]
        t = np.clip((ap * ab[None]).sum(2) / L[None], 0, 1)
        d = np.hypot(*(ap - t[..., None] * ab[None]).transpose(2, 0, 1)).min(1)
        worst = max(worst, float(d.max()))
    return worst

def bbox(sets):
    xs, ys = [], []
    for s in sets:
        b = s.BBox()
        xs += [pcbnew.ToMM(b.GetLeft()), pcbnew.ToMM(b.GetRight())]
        ys += [pcbnew.ToMM(b.GetTop()), pcbnew.ToMM(b.GetBottom())]
    return min(xs), min(ys), max(xs), max(ys)

def compare(job):
    lib, name = os.path.dirname(job['path']), os.path.basename(job['path'])[:-10]
    fp = pcbnew.PCB_IO_KICAD_SEXPR().FootprintLoad(lib, name)
    have = []
    for item in fp.GraphicalItems():
        if item.GetClass() == 'PCB_SHAPE' and item.GetShape() == pcbnew.SHAPE_T_POLY and item.GetLayer() == pcbnew.F_SilkS:
            ps = pcbnew.SHAPE_POLY_SET(item.GetPolyShape())
            ps.Unfracture()
            for i in range(ps.OutlineCount()):
                one = pcbnew.SHAPE_POLY_SET(); one.AddOutline(ps.Outline(i))
                for h in range(ps.HoleCount(i)): one.AddHole(ps.Hole(i, h))
                have.append(one)
    want = [letter_set(c) for _, c in job['letters']]
    hb, wb = bbox(have), bbox(want)
    # align the printed shapes' centres
    dx, dy = (wb[0] + wb[2]) / 2 - (hb[0] + hb[2]) / 2, (wb[1] + wb[3]) / 2 - (hb[1] + hb[3]) / 2
    have.sort(key=lambda s: s.BBox().GetLeft()); order = sorted(range(len(want)), key=lambda i: want[i].BBox().GetLeft())
    per = []
    if len(have) == len(want):
        for h, i in zip(have, order):
            hs = boundary(h) + np.array([dx, dy]); ws = boundary(want[i])
            per.append([job['letters'][i][0], max(far(sample(hs), ws), far(sample(ws), hs))])
    return {'repo': job['repo'], 'fp': job['fp'], 'letters': len(have), 'want': len(want),
            'size': [hb[2] - hb[0], hb[3] - hb[1]], 'gen_size': [wb[2] - wb[0], wb[3] - wb[1]],
            'origin': [-(hb[0] + hb[2]) / 2, -(hb[1] + hb[3]) / 2], 'per_letter': per or [['?', 99.0]]}

def main():
    job = json.loads(sys.stdin.read())
    if job['do'] == 'write': ans = write(job)
    elif job['do'] == 'compare': ans = {'results': [compare(j) for j in job['jobs']]}
    else: ans = {'error': 'unknown job'}
    sys.stdout.write(json.dumps(ans) + '\n'); sys.stdout.flush()

try:
    main()
except Exception:
    import traceback; traceback.print_exc(file=sys.stdout)
finally:
    sys.stdout.flush(); os._exit(0)
