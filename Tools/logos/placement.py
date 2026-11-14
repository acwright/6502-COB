#!/usr/bin/env python3
"""Where a board's logo goes (KICAD.md K40). The standard is standard.json, beside this file.

  placement.py --check [--all]     check the logo on every newest revision not yet made; exit 1 on any fault.
                                   derived-check.py runs it.
  placement.py [--all]             the same, and print every newest revision with its measures, made ones included
  placement.py REPO "Board" REV    move the logo of one revision not yet made to its place, in place

The logo is the board's footprint from the 6502 Logos library (named "6502 <Board> Logo <H>mm" on most boards, but
eleven helpers and the Clock Card leave out "Logo" until K32 renames them). Distances are measured on its printed shapes and on the
board's outline, so they don't depend on where a footprint's origin sits.

  A card or cart    (it has the 6502 Card Edge footprint) The logo reads bottom to top, at 90°, its left edge
                    card.edge_gap from the board's left edge, centred on the body (the card.body above the tab).
  Any other board   The logo runs along the edge it is nearest. If that edge has corner mounting holes, its centre
                    line is on their line, and along the edge it is centred or has its end board.end_gap from the
                    corner. If not, it takes the card rule, centred on the board's whole height.

Moving a logo edits the footprint's (at …) as text and nothing else. It is silk only: no copper moves, and a label
stays as it is (K16). On a board the owner routed, agents propose the move and the owner approves it (K36).

A newest revision waiting for its move is listed in Tools/data/logos.json under "pending", with the item that moves it.
It is reported but doesn't fail the check, and an entry that is no longer needed fails the check until it is removed.
A board whose logo has no other place to go (the owner rules each one) is listed under "exceptions", with the reason:
its logo stays where it is, and the check fails if the entry is no longer needed.
A made or ordered revision isn't checked: its next revision takes the rule."""
import os, re, sys, json
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(H)); sys.path.insert(0, os.path.join(os.path.dirname(H), 'cardedge'))
from common import SCOPE, files, load
import kpcb

S = json.load(open(H + '/standard.json', encoding='utf-8'))
C, B, TOL = S['card'], S['board'], S['tolerance']
LOGO = re.compile(S['footprint'])


def orders():
    return load('orders.json')


def status(O, repo, board, rev):
    k = f'{repo}|{board}|{rev}'
    return 'made' if k in O.get('made', {}) else 'ordered' if k in O.get('ordered', {}) else 'drawn'


def outline(root):
    """The board's outline box (x0, y0, x1, y1), on the cut's centre line."""
    pts = []
    for n in root.kids:
        if n.name in ('gr_line', 'gr_arc', 'gr_rect', 'gr_poly') and kpcb.layer(n) == 'Edge.Cuts':
            for k in ('start', 'mid', 'end'):
                if n.get(k): pts.append(n.get(k).nums()[:2])
            if n.get('pts'): pts += [p.nums()[:2] for p in n.get('pts').all('xy')]
    for fp in kpcb.footprints(root):
        for n in fp.kids:
            if n.name in ('fp_line', 'fp_arc') and kpcb.layer(n) == 'Edge.Cuts':
                pts += [kpcb.to_board(fp, *n.get(k).nums()[:2]) for k in ('start', 'mid', 'end') if n.get(k)]
    if not pts: raise SystemExit('no outline on Edge.Cuts')
    return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)


def shapes_box(fp):
    """The box round a footprint's printed shapes on the board, in the board's frame."""
    pts = []
    for n in fp.kids:
        if n.name.startswith('fp_') and 'SilkS' in (kpcb.layer(n) or ''):
            if n.get('pts'): pts += [kpcb.to_board(fp, *p.nums()[:2]) for p in n.get('pts').all('xy')]
            for k in ('start', 'mid', 'end'):
                if n.get(k): pts.append(kpcb.to_board(fp, *n.get(k).nums()[:2]))
    return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)


class Board:
    def __init__(self, path):
        p = path.split('/'); self.path = path
        self.repo, self.board, self.rev = p[-5].split('-')[-1], p[-3], p[-2][4:]
        self.t = open(path, encoding='utf-8', newline='').read()
        self.root = kpcb.parse(self.t)
        fps = kpcb.footprints(self.root)
        self.card = any(kpcb.lib_id(f).split(':')[-1] == '6502 Card Edge' for f in fps)
        self.logos = [f for f in fps if LOGO.match(kpcb.lib_id(f))]
        self.holes = [kpcb.at(f)[:2] for f in fps if B['hole_footprint'] in kpcb.lib_id(f)]
        self.box = outline(self.root)

    @property
    def tag(self):
        return f'{self.repo} {self.board} {self.rev}'

    def place(self):
        """(where the logo's box is, where it should be, the rule it follows) for its one logo."""
        if len(self.logos) != 1: return None
        fp = self.logos[0]; x0, y0, x1, y1 = self.box
        L = shapes_box(fp); w, h = L[2] - L[0], L[3] - L[1]
        rot = round(kpcb.at(fp)[2]) % 360
        if self.card:
            return L, self._card(L, w, h, y0 + C['body'] / 2), f'card, {C["edge_gap"]} mm from the left, centred on the body'
        upright = rot in (90, 270)   # the logo's long side runs up and down
        cx, cy = (L[0] + L[2]) / 2, (L[1] + L[3]) / 2
        if upright: side, off = ('left', cx - x0) if cx - x0 <= x1 - cx else ('right', x1 - cx)
        else: side, off = ('top', cy - y0) if cy - y0 <= y1 - cy else ('bottom', y1 - cy)
        line = self._hole_line(side)
        if line is None:
            return L, self._card(L, w, h, (y0 + y1) / 2), f'no corner holes by its edge: {C["edge_gap"]} mm from the left, centred'
        if upright:
            nx = x0 + line - w / 2 if side == 'left' else x1 - line - w / 2
            ny = self._along(L[1], L[3], y0, y1)
            return L, (nx, ny, nx + w, ny + h), f'on the {side} holes\' line, {line:.2f} mm in'
        ny = y0 + line - h / 2 if side == 'top' else y1 - line - h / 2
        nx = self._along(L[0], L[2], x0, x1)
        return L, (nx, ny, nx + w, ny + h), f'on the {side} holes\' line, {line:.2f} mm in'

    def _card(self, L, w, h, mid):
        nx = self.box[0] + C['edge_gap']; ny = mid - h / 2
        return nx, ny, nx + w, ny + h

    def _hole_line(self, side):
        x0, y0, x1, y1 = self.box; r = B['hole_reach']
        d = {'left': lambda p: p[0] - x0, 'right': lambda p: x1 - p[0], 'top': lambda p: p[1] - y0, 'bottom': lambda p: y1 - p[1]}[side]
        a = {'left': lambda p: p[1], 'right': lambda p: p[1], 'top': lambda p: p[0], 'bottom': lambda p: p[0]}[side]
        lo, hi = (y0, y1) if side in ('left', 'right') else (x0, x1)
        near = [h for h in self.holes if d(h) < r]
        corner = [h for h in near if a(h) - lo < r or hi - a(h) < r]
        if len(corner) < 2: return None
        offs = sorted(round(d(h), 3) for h in corner)
        return offs[0] if offs[-1] - offs[0] <= TOL else None

    @staticmethod
    def _along(a0, a1, lo, hi):
        """Where the logo should start along its edge: as it is, if it is centred or its end is end_gap from a corner;
        otherwise the nearer of the two."""
        n = a1 - a0; centred = (lo + hi) / 2 - n / 2
        ends = (lo + B['end_gap'], hi - B['end_gap'] - n)
        best = min((centred,) + ends, key=lambda v: abs(v - a0))
        return best


def faults(bd):
    if not bd.logos: return None, 'no board logo'
    if len(bd.logos) > 1: return [f'{len(bd.logos)} board logos'], ''
    have, want, rule = bd.place()
    rot = round(kpcb.at(bd.logos[0])[2]) % 360
    e = []
    if bd.card and rot != C['rotation']: e.append(f'turned {rot}°, not {C["rotation"]}°')
    if 'SilkS' not in ''.join(kpcb.layer(n) or '' for n in bd.logos[0].kids if n.name == 'fp_poly'): e.append('not on a silkscreen')
    dx, dy = want[0] - have[0], want[1] - have[1]
    if abs(dx) > TOL or abs(dy) > TOL: e.append(f'{dx:+.2f} mm across, {dy:+.2f} mm down from its place ({rule})')
    x0, y0, x1, y1 = bd.box
    return e, f'{rule}; logo {have[0] - x0:.2f} from the left, {have[1] - y0:.2f} from the top'


def newest():
    by = {}
    for f in files('Hardware/*/Rev */*.kicad_pcb'):
        p = f.split('/'); by.setdefault((p[-5], p[-3]), []).append(f)
    out = {}
    for (repo, board), fs in by.items():
        f = sorted(fs, key=lambda x: [int(v) if v.isdigit() else v for v in re.findall(r'\d+|[a-z]+', x.split('/')[-2][4:])])[-1]
        out[f'{repo.split("-")[-1]}|{board}|{f.split("/")[-2][4:]}'] = f
    return out


def check(verbose):
    D = load('logos.json'); P, X = D.get('pending', {}), D.get('exceptions', {})
    E = []; N = newest(); O = orders(); good = made = none = kept = 0
    for key in sorted(set(P) & set(X)): E.append(f'{key} is both pending and an exception in Tools/data/logos.json')
    for key, f in sorted(N.items()):
        bd = Board(f); e, how = faults(bd); why = P.get(key); st = status(O, bd.repo, bd.board, bd.rev)
        if key in X:
            if e is None or st != 'drawn' or not e:
                E.append(f'{bd.tag} needs no exception: remove it from "exceptions" in Tools/data/logos.json')
            else:
                kept += 1
                if verbose: print(f'except   {bd.tag}: {"; ".join(e)}  [{X[key]}]')
            continue
        if e is None:
            none += 1
            if verbose: print(f'no logo  {bd.tag}')
            if why: E.append(f'{bd.tag} has no board logo: remove it from "pending" in Tools/data/logos.json')
            continue
        if st != 'drawn':
            made += 1
            if verbose: print(f'{st:8} {bd.tag}: {"; ".join(e) if e else "to the rule"}')
            if why: E.append(f'{bd.tag} is {st}: remove it from "pending" in Tools/data/logos.json')
            continue
        if e and why:
            if verbose: print(f'pending  {bd.tag}: {"; ".join(e)}  [{why}]')
        elif e: E.append(f'{bd.tag}: ' + '; '.join(e))
        elif why: E.append(f'{bd.tag} passes: remove it from "pending" in Tools/data/logos.json')
        else:
            good += 1
            if verbose: print(f'ok       {bd.tag}: {how}')
    for sec, L in (('pending', P), ('exceptions', X)):
        for key in L:
            if key not in N and key.split('|')[0] in SCOPE:
                E.append(f'{key} in "{sec}" in Tools/data/logos.json is not a newest revision: remove it')
    for e in E: print(e)
    print(f'logos: {len(N)} newest revisions, {good} to the rule, {sum(1 for k in N if k in P)} pending, {kept} exceptions, '
          f'{made} made or ordered (not checked), {none} without a board logo, {len(E)} faults')
    return not E


def num(v):
    s = f'{round(v, 6):.6f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def apply(repo, board, rev):
    f = files(f'Hardware/{board}/Rev {rev}/{board}.kicad_pcb', repos=(repo,))
    if not f: raise SystemExit(f'no PCB for {repo} {board} {rev}')
    st = status(orders(), repo, board, rev)
    if st != 'drawn': raise SystemExit(f'{repo} {board} {rev} is {st}: never edit it')
    x = load('logos.json').get('exceptions', {}).get(f'{repo}|{board}|{rev}')
    if x: raise SystemExit(f'{repo} {board} {rev} is an exception, its logo stays: {x}')
    bd = Board(f[0]); e, how = faults(bd)
    if e is None or not bd.logos: raise SystemExit(f'{bd.tag} has no board logo')
    if not e: print(f'{bd.tag}: already to the rule ({how})'); return
    have, want, rule = bd.place(); fp = bd.logos[0]
    if bd.card and round(kpcb.at(fp)[2]) % 360 != C['rotation']: raise SystemExit(f'{bd.tag}: turn the logo to {C["rotation"]}° first')
    a = fp.get('at'); x, y, r = kpcb.at(fp); dx, dy = want[0] - have[0], want[1] - have[1]
    new = f'(at {num(x + dx)} {num(y + dy)}' + (f' {num(r)}' if len(a.atoms) > 2 else '') + ')'
    t = bd.t[:a.span[0]] + new + bd.t[a.span[1]:]
    open(bd.path, 'w', encoding='utf-8', newline='').write(t)
    left, _ = faults(Board(bd.path))
    if left: raise SystemExit('still off: ' + '; '.join(left))
    print(f'{bd.tag}: logo moved {dx:+.3f} mm across, {dy:+.3f} mm down ({rule})')


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if x != '--all']
    if a and a[0] != '--check':
        if len(a) != 3: raise SystemExit(__doc__)
        apply(*a)
    else:
        sys.exit(0 if check(verbose=not a) else 1)
