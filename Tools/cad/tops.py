#!/usr/bin/env python3
"""A board's top panel, generated from its PCB, its STEP model, the assembly file and the standards. Needs build123d
and shapely: run it with Tools/work/venv (make.py does).

  tops.py REPO BOARD REV OUT.svg     write the top of that board, as the assembly file in REPO describes it
  tops.py --report REPO BOARD REV    print the openings and why each is there, as JSON
  tops.py --compare REPO BOARD REV OLD.svg   how the generated top differs from another (today's, from Fusion)

The top is drawn as the board sits on the plate, seen from above, with its back-left corner at (0, 0). What goes in it:
  - the board's outline, and a Ø3.2 hole at every M3 mounting hole;
  - an opening round every part that reaches into the top's sheet: its 3D body, cut at the height of the sheet
    (standoff to standoff + sheet), lies inside the outline. The opening goes round the part's whole body;
  - an opening round every part a builder needs to reach: pin headers and JST XH headers, card slots, bus box headers
    and DIP switches, by footprint; a Ø3.3 hole over a reset button; and whatever the assembly file names;
  - a crystal gets a slot with round ends, and keys a window round them;
  - a round hole the assembly file names is centred on the round feature at the top of the part's 3D model (a
    trimmer's rotor), or on its body if it has none;
  - each opening is the part's 3D body grown by its kind's margin, then grown again to whole 0.5 mm, centred;
  - openings that would leave less than 3 mm of acrylic between them become one: the narrow acrylic is cut away, and
    each keeps its own shape elsewhere;
  - no opening comes within keep_round_holes of a mounting hole: the screw head and standoff need the acrylic.
"""
import hashlib, json, math, os, sys
CAD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CAD)
import assembly  # noqa: E402
from assembly import repo_dir  # noqa: E402
from shapely.geometry import Point, Polygon, box as sbox  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

RULES = [  # (text in the footprint's name, kind)
    ('Crystal_HC49', 'crystal'),
    ('SW_Cherry_MX', 'keys'),
    ('PinHeader', 'access'),
    ('JST_XH', 'access'),
    ('Card Slot', 'tall'),
    ('Card Connector', 'tall'),
    ('Bus Connector', 'tall'),
    ('SW_DIP', 'tall'),
]


step_path = assembly.step_path
from bodies import norm, bodies  # noqa: E402


def grow(o, n):
    return n if o is None else [min(o[0], n[0]), min(o[1], n[1]), max(o[2], n[2]), max(o[3], n[3])]


def band(p, z0, z1=1e9):
    """The box of what of a part lies between z0 and z1 above the board, from its profile; None if nothing does."""
    out = None
    for z, b in p['profile']:
        if z + 1 > z0 + 1e-6 and z < z1 - 1e-6:
            out = grow(out, b)
    return out


def match(parts, bs):
    """Give each footprint the boxes of its STEP children: matched by model name, then by overlap."""
    for p in parts:
        p['body'] = None
        p['profile'] = []
        p['height'] = None
        p['top'] = None
        p['_top_z'] = None
    for label, bb, prof, tb in bs:
        best = None
        for p in parts:
            ref = p['courtyard'] or p['pads']
            if not ref or not any(norm(label)[:12] == norm(m)[:12] for m in p['models']):
                continue
            ox = min(bb[2], ref[2]) - max(bb[0], ref[0])
            oy = min(bb[3], ref[3]) - max(bb[1], ref[1])
            score = max(0, ox) * max(0, oy)
            if best is None or score > best[0]:
                best = (score, p)
        if best is None or best[0] <= 0:
            continue
        p = best[1]
        p['body'] = grow(p['body'], bb[:4])
        p['height'] = max(p['height'] or 0, bb[4])
        p['profile'] += prof
        if tb and (p['_top_z'] is None or bb[4] > p['_top_z']):
            p['top'], p['_top_z'] = tb, bb[4]


def round_out(b, step):
    """A box grown to whole multiples of step on each side, keeping its centre."""
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    w = math.ceil(round((b[2] - b[0]) / step, 6)) * step
    h = math.ceil(round((b[3] - b[1]) / step, 6)) * step
    return [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]


class Top:
    def __init__(self, a, q):
        self.a, self.q = a, q
        std = a['_std']
        self.std = std
        spec = q.spec.get('top') or {}
        self.spec = spec
        sh = std['sheet']
        z0 = std['standoff']
        self.z0, self.z1 = z0, z0 + sh
        match(q.data['parts'], bodies(step_path(a['_repo'], q.spec), z0, z0 + sh))
        for p in q.data['parts']:
            p['slice'] = band(p, z0, z0 + sh)
        x0, y0 = q.at
        self.W, self.H = q.box[2] - q.box[0], q.box[3] - q.box[1]
        P = lambda x, y: (q.place(x, y)[0] - x0, q.place(x, y)[1] - y0)
        self.P = P

        def tb(b):
            pts = [P(b[0], b[1]), P(b[2], b[3])]
            return [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)]
        self.tb = tb
        self.outline = Polygon([P(x, y) for x, y in q.data['outlines'][0]])
        self.radius = q.data['radius']
        self.mount = [P(h['x'], h['y']) for h in q.data['holes'] if 2.9 <= h['drill'] <= 3.6]
        self.openings, self.holes, self.notes = [], [], []
        self.build()

    def kind_of(self, p):
        for k, v in RULES:
            if k in p['fpid']:
                return v
        return None

    def through(self, p):
        """The box an opening goes round for a part that reaches into the top: the part as it is in the top's sheet,
        so a tab or pin at board level doesn't pull the opening off centre; grown only if something of it above the
        sheet (a ZIF socket's lever, standing up) wouldn't pass through the opening."""
        b = self.tb(p['slice'])
        up = band(p, self.z1)
        m = self.std['openings']['tall']['margin']
        if up:
            u = self.tb(up)
            if u[0] < b[0] - m or u[1] < b[1] - m or u[2] > b[2] + m or u[3] > b[3] + m:
                b = grow(b, u)
        return b

    def lever(self, o):
        """A window for a lever that swings down: from the centre of what of the part stands above 'above' mm (its
        knob), 'length' mm towards 'towards' (back, front, left or right, as the board sits on the plate)."""
        lv = o['lever']
        p = next(p for p in self.q.data['parts'] if p['ref'] == lv['ref'])
        k = self.tb(band(p, lv['above']))
        cx, cy = (k[0] + k[2]) / 2, (k[1] + k[3]) / 2
        L = lv['length']
        box = {'back': [k[0], cy - L, k[2], k[3]], 'front': [k[0], k[1], k[2], cy + L],
               'left': [cx - L, k[1], k[2], k[3]], 'right': [k[0], k[1], cx + L, k[3]]}[lv['towards']]
        return box

    def add(self, refs, kind, box, why, **kw):
        o = self.std['openings']
        if kind == 'keys':
            m = o['keys']
            b = [box[0] - m['margin_x'], box[1] - m['margin_y'], box[2] + m['margin_x'], box[3] + m['margin_y']]
            r = m['radius']
        else:
            m = kw.get('margin', o[kind]['margin'])
            b = [box[0] - m, box[1] - m, box[2] + m, box[3] + m]
            r = o[kind].get('radius')
        b = round_out(b, o['round_to'])
        if kind == 'crystal':
            r = min(b[2] - b[0], b[3] - b[1]) / 2
        self.openings.append({'refs': list(refs), 'kind': kind, 'box': b, 'radius': r, 'why': why})

    def build(self):
        q, spec = self.q, self.spec
        named = {}
        for o in spec.get('openings', []):
            for r in o.get('refs', []):
                named[r] = o
        holes_named = {h['ref']: h for h in spec.get('holes', [])}
        keys = []
        parts = {p['ref']: p for p in q.data['parts']}
        for p in q.data['parts']:
            if p['side'] != 'F' or p['ref'] in named or p['ref'] in holes_named:
                continue
            body = self.tb(p['body']) if p['body'] else None
            kind = self.kind_of(p)
            reaches = p['slice'] is not None and self.outline.intersection(sbox(*self.tb(p['slice']))).area > 0.01
            if kind == 'keys':
                keys.append(p)
            elif kind and body:
                self.add([p['ref']], kind, body, f"{p['fpid'].split(':')[-1]}" + (', reaches into the top' if reaches else ''))
            elif 'SW_PUSH' in p['fpid'] and 'RESET' in p['value'].upper():
                c = self.tb(p['pads'])
                d = self.std['openings']['reset_button']['hole']
                self.holes.append({'refs': [p['ref']], 'x': (c[0] + c[2]) / 2, 'y': (c[1] + c[3]) / 2, 'd': d,
                                   'why': 'the reset button, under the printed Reset Button'})
            elif reaches:
                self.add([p['ref']], 'tall', self.through(p), f"{p['value']}: {p['height']:.1f} mm tall, reaches into the top")
        # one window per key; the merge rule below joins keys that sit together into one window
        for p in keys:
            self.add([p['ref']], 'keys', self.tb(p['body']), 'the keys')
        e = q.data['edge_box']
        for o in spec.get('openings', []):
            if 'lever' in o:
                self.add([o['lever']['ref'] + ' lever'], o['kind'], self.lever(o), o.get('why', 'a lever'),
                         margin=o.get('margin', self.std['openings'][o['kind']]['margin']))
                continue
            if o.get('body') == 'through':
                self.add(o['refs'], o['kind'], self.through(parts[o['refs'][0]]), o.get('why', o['kind']))
                continue
            if 'block' in o:
                (bx, by), (bw, bh) = o['block']['at'], o['block']['size']
                self.add([o['block'].get('name', 'block')], o['kind'], self.tb([e[0] + bx, e[1] + by, e[0] + bx + bw, e[1] + by + bh]), o.get('why', ''))
                continue
            if 'zone' in o:
                z = next(z for z in q.data['zones'] if z['name'] == o['zone'])
                self.add([o['zone']], o['kind'], self.tb(z['box']), o.get('why', o['zone']), margin=o.get('margin', self.std['openings'][o['kind']]['margin']))
                continue
            bs = [self.tb(parts[r]['body'] or parts[r]['courtyard']) for r in o['refs']]
            self.add(o['refs'], o['kind'], [min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)], o.get('why', o['kind']))
        for h in spec.get('holes', []):
            p = parts[h['ref']]
            c = self.tb(p['top'] or p['body'] or p['pads'])
            self.holes.append({'refs': [h['ref']], 'x': (c[0] + c[2]) / 2, 'y': (c[1] + c[3]) / 2, 'd': h['d'], 'why': h.get('why', '')})
        self.clear_holes()
        self.merge()

    def clear_holes(self):
        """An opening that comes within keep_round_holes of a mounting hole has that side pulled straight back, when
        that costs less than a quarter of the opening; otherwise geometry() cuts a round bite out of it."""
        R = self.std['top']['keep_round_holes']
        for o in self.openings:
            for x, y in self.mount:
                if not self.shape(o).intersects(Point(x, y).buffer(R, quad_segs=32)):
                    continue
                b = o['box']
                options = []
                if y - R > b[1]:
                    options.append([b[0], b[1], b[2], min(b[3], y - R)])
                if y + R < b[3]:
                    options.append([b[0], max(b[1], y + R), b[2], b[3]])
                if x - R > b[0]:
                    options.append([b[0], b[1], min(b[2], x - R), b[3]])
                if x + R < b[2]:
                    options.append([max(b[0], x + R), b[1], b[2], b[3]])
                area = lambda r: (r[2] - r[0]) * (r[3] - r[1])
                best = max(options, key=area, default=None)
                if best and area(best) >= 0.75 * area(b):
                    o['box'] = best
                    self.notes.append(f"{'+'.join(o['refs'][:3])}: one side pulled back {area(b) and round(max(abs(p - q) for p, q in zip(b, best)), 2)} mm to keep {R} mm round a mounting hole")

    def shape(self, o):
        if o.get('poly') is not None:
            return o['poly']
        b, r = o['box'], o['radius'] or 0
        return sbox(b[0] + r, b[1] + r, b[2] - r, b[3] - r).buffer(r, quad_segs=32) if r else sbox(*b)

    def merge(self):
        """Openings that would leave less than merge_below of acrylic between them become one: the acrylic narrower
        than that is cut away, and each opening keeps its own shape everywhere else."""
        gap = self.std['openings']['merge_below']
        shapes = [(o, self.shape(o)) for o in self.openings]
        # less than gap: a web of exactly gap stays
        h = (gap - 0.01) / 2
        closed = unary_union([s for _, s in shapes]).buffer(h, quad_segs=32).buffer(-h, quad_segs=32)
        groups = list(closed.geoms) if closed.geom_type == 'MultiPolygon' else [closed]
        out = []
        for g in groups:
            members = [o for o, s in shapes if s.intersects(g)]
            if len(members) == 1 and self.shape(members[0]).symmetric_difference(g).area < 0.05:
                out.append(members[0])
                continue
            kinds = {o['kind'] for o in members}
            if kinds == {'keys'}:
                # keys that sit together: one window, a rectangle round them all, as the ACE's keyboard has
                box = round_out([min(o['box'][0] for o in members), min(o['box'][1] for o in members),
                                 max(o['box'][2] for o in members), max(o['box'][3] for o in members)], self.std['openings']['round_to'])
                out.append({'refs': [r for o in members for r in o['refs']], 'kind': 'keys', 'box': box,
                            'radius': self.std['openings']['keys']['radius'], 'why': 'the keys'})
                continue
            whys = []
            for o in members:
                if o['why'] not in whys:
                    whys.append(o['why'])
            out.append({'refs': [r for o in members for r in o['refs']], 'kind': kinds.pop() if len(kinds) == 1 else 'merged',
                        'box': list(g.bounds), 'radius': None, 'why': '; '.join(whys), 'poly': g})
        self.openings = out

    def geometry(self):
        """(material polygon, [opening polygons], [(x, y, d)] round holes), after the keep-out round mounting holes."""
        keep = self.std['top']['keep_round_holes']
        keepout = unary_union([Point(x, y).buffer(keep, quad_segs=32) for x, y in self.mount])
        ops = []
        for o in self.openings:
            s = self.shape(o).simplify(0.01)
            if s.intersects(keepout):
                self.notes.append(f"{'+'.join(o['refs'][:3])}{'…' if len(o['refs']) > 3 else ''}: opening kept {keep} mm clear of a mounting hole")
                s = s.difference(keepout)
            o['poly'] = s
            if not self.outline.buffer(-0.01).contains(s):
                self.notes.append(f"{'+'.join(o['refs'][:3])}: opening reaches the board's edge, a notch in the outline")
            ops.append(s)
        holes = [(x, y, self.std['top']['hole']) for x, y in self.mount] + [(h['x'], h['y'], h['d']) for h in self.holes]
        return self.outline, ops, holes

    def svg(self, digest=''):
        outline, ops, holes = self.geometry()
        W, H, r = self.W, self.H, self.radius
        f = lambda v: f'{round(v, 3):g}'
        out = ['<?xml version="1.0" encoding="utf-8"?>',
               f'<!-- Generated by Tools/cad/make.py from CAD/Assembly.json, the board\'s PCB and STEP model. Edit those, not this file. inputs sha1 {digest} -->',
               f'<!-- {self.q.name} Rev {self.q.rev}: its top, as the board sits on the plate, seen from above. {self.std["sheet"]:g} mm {self.std["material"]}. -->',
               f'<svg xmlns="http://www.w3.org/2000/svg" width="{f(W)}mm" height="{f(H)}mm" viewBox="0 0 {f(W)} {f(H)}" version="1.1">']
        rr = sbox(r, r, W - r, H - r).buffer(r, quad_segs=64)
        notched = [s for s in ops if not outline.buffer(-0.01).contains(s)]
        if abs(rr.symmetric_difference(outline).area) < 1.0 and not notched:
            d = (f'M{f(r)},0 L{f(W - r)},0 A{f(r)},{f(r)} 0 0,1 {f(W)},{f(r)} L{f(W)},{f(H - r)} A{f(r)},{f(r)} 0 0,1 {f(W - r)},{f(H)} '
                 f'L{f(r)},{f(H)} A{f(r)},{f(r)} 0 0,1 0,{f(H - r)} L0,{f(r)} A{f(r)},{f(r)} 0 0,1 {f(r)},0z')
        else:
            shape = outline.difference(unary_union(notched)) if notched else outline
            d = 'M' + ' L'.join(f'{f(x)},{f(y)}' for x, y in list(shape.exterior.coords)[:-1]) + 'z'
        out.append(f'<path d="{d}" fill="rgb(0,0,0)" stroke-linecap="round" stroke-linejoin="round" />')
        white = 'fill="rgb(255,255,255)" stroke="rgb(0,0,0)" stroke-width="0.01" stroke-linecap="round" stroke-linejoin="round"'
        for o, s in zip(self.openings, ops):
            if s in notched:
                continue
            b, rad = o['box'], o['radius'] or 0
            if s.equals(self.shape(o)) and rad:
                x0, y0, x1, y1 = b
                d = (f'M{f(x0 + rad)},{f(y0)} L{f(x1 - rad)},{f(y0)} A{f(rad)},{f(rad)} 0 0,1 {f(x1)},{f(y0 + rad)} L{f(x1)},{f(y1 - rad)} '
                     f'A{f(rad)},{f(rad)} 0 0,1 {f(x1 - rad)},{f(y1)} L{f(x0 + rad)},{f(y1)} A{f(rad)},{f(rad)} 0 0,1 {f(x0)},{f(y1 - rad)} '
                     f'L{f(x0)},{f(y0 + rad)} A{f(rad)},{f(rad)} 0 0,1 {f(x0 + rad)},{f(y0)}z')
            else:
                polys = list(s.geoms) if s.geom_type == 'MultiPolygon' else [s]
                rings = [r for p in polys for r in [p.exterior] + list(p.interiors)]
                d = ' '.join('M' + ' L'.join(f'{f(x)},{f(y)}' for x, y in list(r.coords)[:-1]) + 'z' for r in rings)
            out.append(f'<path d="{d}" {white} />')
        for x, y, dd in holes:
            rr_ = dd / 2
            out.append(f'<path d="M{f(x - rr_)},{f(y)} a{f(rr_)},{f(rr_)} 0 1,1 {f(2 * rr_)},0 a{f(rr_)},{f(rr_)} 0 1,1 {f(-2 * rr_)},0z" {white} />')
        out.append('</svg>')
        return '\n'.join(out) + '\n'

    def report(self):
        self.geometry()
        return {'board': f'{self.q.name} Rev {self.q.rev}', 'size': [round(self.W, 3), round(self.H, 3)],
                'openings': [{k: (v if k != 'box' else [round(x, 3) for x in v]) for k, v in o.items() if k != 'poly'} for o in self.openings],
                'holes': [{'at': [round(h['x'], 3), round(h['y'], 3)], 'd': h['d'], 'refs': h['refs'], 'why': h['why']} for h in self.holes],
                'mount': [[round(x, 3), round(y, 3)] for x, y in self.mount], 'notes': self.notes}


def compare(t, path):
    """How the generated top differs from another top's SVG (today's, from Fusion): that file is turned and shifted to
    lie on the generated one by the mounting holes first. Returns lines of text."""
    import fusion
    old = fusion.read(path)
    rep = t.report()
    mount = rep['mount']
    best = None
    for rot in (0, 90, 180, 270):
        a_ = math.radians(rot)
        R = lambda x, y: (x * math.cos(a_) - y * math.sin(a_), x * math.sin(a_) + y * math.cos(a_))
        M = [R(h.x, h.y) for h in old.holes if 2.9 <= h.d <= 3.6]
        for mx, my in M[:1] if M else []:
            for gx, gy in mount:
                dx, dy = gx - mx, gy - my
                n = sum(any(math.hypot(x + dx - u, y + dy - v) < 0.6 for u, v in mount) for x, y in M)
                # holes in a rectangle fit several ways round: take the one where the openings overlap most
                ov = 0
                for c in old.cutouts:
                    pts = [R(c.box[0], c.box[1]), R(c.box[2], c.box[3])]
                    b = [min(p[0] for p in pts) + dx, min(p[1] for p in pts) + dy, max(p[0] for p in pts) + dx, max(p[1] for p in pts) + dy]
                    for o in rep['openings']:
                        g = o['box']
                        ov += max(0, min(g[2], b[2]) - max(g[0], b[0])) * max(0, min(g[3], b[3]) - max(g[1], b[1]))
                for h in old.holes:
                    if h.d > 3.6 or h.d < 2.9:
                        x, y = R(h.x, h.y)
                        ov -= min((math.hypot(x + dx - g['at'][0], y + dy - g['at'][1]) for g in rep['holes']), default=0)
                if best is None or (n, ov) > best[0]:
                    best = ((n, ov), rot, dx, dy)
    (n, _), rot, dx, dy = best
    a_ = math.radians(rot)
    T = lambda x, y: (x * math.cos(a_) - y * math.sin(a_) + dx, x * math.sin(a_) + y * math.cos(a_) + dy)

    def tbox(b):
        pts = [T(b[0], b[1]), T(b[2], b[3])]
        return [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)]
    lines = [f"today's top lies on the generated one turned {rot}°, {n} of {len(mount)} mounting holes matched"]
    ob = tbox(old.outline.box)
    gb = [0, 0] + rep['size']
    d = [round(g - o, 2) for g, o in zip(gb, ob)]
    if max(abs(x) for x in d) > 0.05:
        lines.append(f'outline: today {ob[2] - ob[0]:.2f} × {ob[3] - ob[1]:.2f}, generated {rep["size"][0]:g} × {rep["size"][1]:g}; edges move {d} (left, back, right, front)')
    olds = [tbox(c.box) for c in old.cutouts]
    used = set()
    for o in rep['openings']:
        g = o['box']
        ov = [(max(0, min(g[2], b[2]) - max(g[0], b[0])) * max(0, min(g[3], b[3]) - max(g[1], b[1])), i) for i, b in enumerate(olds)]
        ov = [x for x in ov if x[0] > 0]
        name = '+'.join(o['refs'][:4]) + ('…' if len(o['refs']) > 4 else '')
        if not ov:
            lines.append(f"new opening: {name} ({o['why']}), {g[2] - g[0]:g} × {g[3] - g[1]:g}")
            continue
        i = max(ov)[1]
        used.add(i)
        b = olds[i]
        mv = [round(g[0] - b[0], 2), round(g[1] - b[1], 2), round(g[2] - b[2], 2), round(g[3] - b[3], 2)]
        if max(abs(x) for x in mv) > 0.05:
            lines.append(f"{name}: today {b[2] - b[0]:.2f} × {b[3] - b[1]:.2f}, generated {g[2] - g[0]:g} × {g[3] - g[1]:g}; edges move {mv}")
        else:
            lines.append(f"{name}: the same within 0.05 mm")
    for i, b in enumerate(olds):
        if i not in used:
            lines.append(f"today's opening at ({b[0]:.1f}, {b[1]:.1f}), {b[2] - b[0]:.2f} × {b[3] - b[1]:.2f}, isn't in the generated top")
    gh = [(m[0], m[1], t.std['top']['hole'], 'mounting') for m in mount] + [(h['at'][0], h['at'][1], h['d'], '+'.join(h['refs'])) for h in rep['holes']]
    for h in old.holes:
        x, y = T(h.x, h.y)
        m = min(gh, key=lambda g: math.hypot(g[0] - x, g[1] - y))
        dist = math.hypot(m[0] - x, m[1] - y)
        if dist > 0.05 or abs(m[2] - h.d) > 0.01:
            lines.append(f"hole {m[3]}: today Ø{h.d:g} at ({x:.2f}, {y:.2f}), generated Ø{m[2]:g} at ({m[0]:.2f}, {m[1]:.2f}), {dist:.2f} mm apart")
    return lines + [f'note: {x}' for x in rep['notes']]


def find(a, board, rev):
    for b in a['builds'] + [{'_placed': a.get('_also', [])}]:
        for q in b['_placed']:
            if q.name == board and q.rev == rev:
                return q
    raise SystemExit(f'{board} Rev {rev} is in no build of the assembly file')


inputs_digest = assembly.top_inputs


if __name__ == '__main__':
    args = [x for x in sys.argv[1:] if not x.startswith('--')]
    a = assembly.load(args[0])
    q = find(a, args[1], args[2])
    t = Top(a, q)
    if '--report' in sys.argv:
        print(json.dumps(t.report(), indent=1))
    elif '--compare' in sys.argv:
        print('\n'.join(compare(t, args[3])))
    else:
        open(args[3], 'w').write(t.svg(inputs_digest(a, q)))
        for n in t.notes:
            print(' ', n)
    assembly.save_cache()
