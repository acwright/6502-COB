#!/usr/bin/env python3
"""Reads a machine's assembly file, CAD/Assembly.json, and places its boards on the plate.

  assembly.py           check this repository's assembly file against its boards and today's CAD/Bases/Plate.svg
  assembly.py --all     the same for every repository that has one

The check: every mounting hole of every board, placed as the assembly file says, lands on a hole of today's plate or
on a position the file lists (a hole that screws to a printed part, or a standoff with no plate hole under it); every
hole of today's plate is used by a board, a printed part or a listed position; the boards keep the plate's margin and
the build's gap. Exit 1 on any fault.

Placing a board. Each board's position is its top-left corner, as the computer is used: looking down on the plate,
front edge at the bottom. "rot" turns the board from its PCB file: 0, 90 (clockwise, looking down), 180 or 270
(anticlockwise). Positions are mm in the plate's frame, x to the right and y towards the front.

The geometry of a placed board comes from its PCB through board_dump.py, run with KiCad's Python and cached in
Tools/work/cache.json by the PCB's bytes.
"""
import json, math, os, subprocess, sys
CAD = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(CAD)
sys.path.insert(0, TOOLS)
sys.path.insert(0, CAD)
from common import K, SCOPE, KPY, repo_dir  # noqa: E402
from cache import Cache, digest  # noqa: E402
import fusion  # noqa: E402

FILE = 'CAD/Assembly.json'
TOL = 0.05          # mm: a board hole and a plate hole are the same hole within this
_cache = None


def board_data(pcb):
    """board_dump.py's JSON for one PCB, cached by the PCB's bytes."""
    global _cache
    if _cache is None:
        _cache = Cache('cad', os.path.join(CAD, 'board_dump.py'))

    def run():
        out = subprocess.run([KPY, os.path.join(CAD, 'board_dump.py'), pcb], capture_output=True, text=True)
        if out.returncode:
            raise SystemExit(f'board_dump.py failed on {pcb}:\n{out.stderr[-2000:]}')
        return json.loads(out.stdout)
    return _cache.get('board ' + digest(pcb), run)


def save_cache():
    if _cache:
        _cache.save()


def pcb_path(repo, b):
    r = b.get('repo', repo)
    return f"{repo_dir(r)}/Hardware/{b['board']}/Rev {b['rev']}/{b['board']}.kicad_pcb"


class Placed:
    """One board of a build, read from its PCB and placed on the plate."""

    def __init__(self, repo, b):
        self.spec = b
        self.name = b['board']
        self.rev = b['rev']
        self.repo = b.get('repo', repo)
        self.pcb = pcb_path(repo, b)
        self.data = board_data(self.pcb)
        x0, y0, x1, y1 = self.data['edge_box']
        self.x0, self.y0, self.w, self.h = x0, y0, x1 - x0, y1 - y0
        self.rot = b.get('rot', 0)
        self.at = tuple(b['at'])
        sw, sh = (self.h, self.w) if self.rot in (90, 270) else (self.w, self.h)
        self.box = (self.at[0], self.at[1], self.at[0] + sw, self.at[1] + sh)

    def place(self, x, y):
        """A point in the PCB file's frame -> the plate's frame."""
        u, v = x - self.x0, y - self.y0
        if self.rot == 180:
            u, v = self.w - u, self.h - v
        elif self.rot == 90:
            u, v = self.h - v, u
        elif self.rot == 270:
            u, v = v, self.w - u
        elif self.rot:
            raise ValueError(f'{self.name}: rot must be 0, 90, 180 or 270')
        return (self.at[0] + u, self.at[1] + v)

    def holes(self):
        """[(ref, x, y, drill)] on the plate, the mounting holes only (M3)."""
        return [(h['ref'], *self.place(h['x'], h['y']), h['drill']) for h in self.data['holes'] if 2.9 <= h['drill'] <= 3.6]


def standards():
    return json.load(open(os.path.join(CAD, 'standards.json')))


def load(repo):
    path = f'{repo_dir(repo)}/{FILE}'
    if not os.path.exists(path):
        return None
    a = json.load(open(path))
    std = standards()
    a['plate'] = {**std['plate'], **a.get('plate', {})}
    a['_std'] = std
    a['_repo'] = repo
    a['_path'] = path
    for build in a['builds']:
        build['_placed'] = [Placed(repo, b) for b in build['boards']]
    # a top drawn for one revision serves the others "also" names, which have the same outline and parts: each
    # revision's folder gets its own copy, generated from that revision's PCB
    a['_also'] = [Placed(repo, {**q.spec, 'rev': r}) for b in a['builds'] for q in b['_placed']
                  for r in (q.spec.get('top') or {}).get('also', [])]
    return a


def plate_size(a):
    """The plate: every build's boards, with the margin all round."""
    m = a['plate']['margin']
    boxes = [p.box for b in a['builds'] for p in b['_placed']]
    x1, y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    return (round(x1 + m, 3), round(y1 + m, 3))


def today_plate(a):
    """Today's CAD/Bases/Plate.svg: its holes turned into the plate's frame as used. Fusion's exports are sometimes
    turned 180° and sometimes not, so the way round that puts the most board holes on plate holes is taken."""
    p = fusion.read(f"{repo_dir(a['_repo'])}/CAD/Bases/Plate.svg")
    board = [(x, y) for b in a['builds'] for q in b['_placed'] for _, x, y, _ in q.holes()]
    best = None
    for turned in (0, 180):
        hs = [((p.w - h.x, p.h - h.y) if turned else (h.x, h.y)) + (h.d,) for h in p.holes]
        n = sum(any(math.hypot(x - hx, y - hy) < TOL for hx, hy, _ in hs) for x, y in board)
        if best is None or n > best[0]:
            best = (n, turned, hs)
    return p, best[1], best[2]


def check(a):
    faults, notes = [], []
    repo = a['_repo']
    W, H = plate_size(a)
    p, turned, plate = today_plate(a)
    notes.append(f'{repo}: plate {W:g} × {H:g} from the boards and the {a["plate"]["margin"]} mm margin; today\'s Plate.svg is '
                 f'{p.w:g} × {p.h:g}, drawn turned {turned}° from the view as used')
    if abs(W - p.w) > TOL or abs(H - p.h) > TOL:
        faults.append(f"{repo}: the boards and margin make a {W:g} × {H:g} plate; today's is {p.w:g} × {p.h:g}")
    used = {i: [] for i in range(len(plate))}
    listed = {k: v for k, v in a.get('positions', {}).items()}

    def on_plate(x, y):
        return next((i for i, (hx, hy, _) in enumerate(plate) if math.hypot(x - hx, y - hy) < TOL), None)
    for build in a['builds']:
        m, gap = a['plate']['margin'], build.get('gap', a['plate']['gap'])
        gap_y = build.get('gap_y', gap)
        for q in build['_placed']:
            bx0, by0, bx1, by1 = q.box
            if bx0 < m - TOL or by0 < m - TOL or bx1 > W - m + TOL or by1 > H - m + TOL:
                faults.append(f"{repo} {build['name']}: {q.name} is inside the {m} mm margin")
            for ref, x, y, d in q.holes():
                i = on_plate(x, y)
                if i is not None:
                    used[i].append(f"{build['name']}: {q.name} {ref}")
                    continue
                pos = next((k for k, v in listed.items() if math.hypot(x - v['at'][0], y - v['at'][1]) < TOL), None)
                if pos is None:
                    faults.append(f"{repo} {build['name']}: {q.name} {ref} at ({x:.3f}, {y:.3f}) is on no plate hole and no listed position")
                elif build['name'] not in listed[pos]['builds']:
                    faults.append(f"{repo} {build['name']}: {q.name} {ref} is on {pos}, which doesn't list this build")
        # neighbours: the build's gap between boards side by side or one behind the other
        ps = build['_placed']
        for i, q in enumerate(ps):
            for r in ps[i + 1:]:
                a0, b0 = q.box, r.box
                if a0[1] < b0[3] and b0[1] < a0[3]:
                    g, want = max(b0[0] - a0[2], a0[0] - b0[2]), gap        # side by side
                elif a0[0] < b0[2] and b0[0] < a0[2]:
                    g, want = max(b0[1] - a0[3], a0[1] - b0[3]), gap_y      # one behind the other
                else:
                    continue
                if g < 0:
                    faults.append(f"{repo} {build['name']}: {q.name} and {r.name} overlap")
                elif abs(g - want) > TOL and g < want + 20:
                    faults.append(f"{repo} {build['name']}: {g:.3f} mm between {q.name} and {r.name}, not {want}")
    for build in a['builds']:
        for q in build['_placed']:
            t = q.spec.get('top')
            if t is None or t.get('generated'):
                continue
            f = top_path(repo, q.spec)
            if not os.path.exists(f):
                faults.append(f"{repo} {build['name']}: {q.name}'s top {os.path.relpath(f, K)} doesn't exist")
    for part in a.get('printed_parts', []):
        holes = part['holes'] if part['holes'] != 'corners' else corner_holes(a, W, H)
        for x, y in holes:
            i = on_plate(x, y)
            if i is None:
                faults.append(f"{repo}: {part['name']} hole ({x}, {y}) is on no plate hole")
            else:
                used[i].append(part['name'])
    for i, u in used.items():
        if not u:
            x, y, d = plate[i]
            faults.append(f"{repo}: today's plate hole at ({x:.3f}, {y:.3f}) is used by nothing in the assembly file")
    for i, (x, y, d) in enumerate(plate):
        if abs(d - a['plate']['hole']) > 0.01:
            notes.append(f"{repo}: today's plate hole at ({x:g}, {y:g}) is Ø{d:g}, not Ø{a['plate']['hole']:g}: {', '.join(used[i])}")
    return faults, notes, plate, used


def top_path(repo, b):
    """A board's top: CAD/Tops/<board>/Rev <rev>/<board> Top.svg in the board's own repository, at the board's
    revision unless "top" names another."""
    t = b.get('top') or {}
    r = t.get('repo', b.get('repo', repo))
    rev = t.get('rev', b['rev'])
    return f"{repo_dir(r)}/CAD/Tops/{b['board']}/Rev {rev}/{b['board']} Top.svg"


def step_path(repo, b):
    r = b.get('repo', repo)
    return f"{repo_dir(r)}/CAD/Models/{b['board']}/Rev {b['rev']}/{b['board']}.step"


def top_inputs(a, q):
    """The sha1 of everything a generated top depends on: its PCB, its STEP model, the assembly file, the standards and
    tops.py and bodies.py. A generated top carries it, so a stale top can be told without reading 3D models."""
    import hashlib
    h = hashlib.sha1()
    for p in (q.pcb, step_path(a['_repo'], q.spec), a['_path'], os.path.join(CAD, 'standards.json'), os.path.join(CAD, 'tops.py'),
              os.path.join(CAD, 'bodies.py')):
        h.update(open(p, 'rb').read())
    return h.hexdigest()


def generated_tops(a):
    """[(placed board, path)] for every top this repository generates: its own boards whose top says generated,
    once each. A top marked draft is left out until the owner approves it."""
    out, seen = [], set()
    for b in a['builds'] + [{'_placed': a.get('_also', [])}]:
        for q in b['_placed']:
            t = q.spec.get('top') or {}
            if not t.get('generated') or t.get('draft') or q.repo != a['_repo'] or (q.name, q.rev) in seen:
                continue
            seen.add((q.name, q.rev))
            out.append((q, top_path(a['_repo'], q.spec)))
    return out


def corner_holes(a, W, H):
    c = a['plate']['corner_hole']
    return [(c, c), (W - c, c), (c, H - c), (W - c, H - c)]


if __name__ == '__main__':
    bad = 0
    n = 0
    for r in SCOPE:
        a = load(r)
        if a is None:
            continue
        n += 1
        faults, notes, plate, used = check(a)
        for x in notes:
            print(x)
        if '-v' in sys.argv:
            for i, (x, y, d) in enumerate(plate):
                print(f'  ({x:7.3f}, {y:7.3f}) Ø{d:g}: {"; ".join(used[i])}')
        for x in faults:
            print('FAULT', x)
        bad += len(faults)
    save_cache()
    print(f'{n} assembly files checked, {bad} faults')
    sys.exit(1 if bad else 0)
