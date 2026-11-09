#!/usr/bin/env python3
"""One card edge for every card and cart (KICAD.md K28). The standard is standard.json, beside this file.

  cardedge.py --check [--all]     check every newest revision that has the 6502 Card Edge footprint, and the library's
                                  footprint; exit 1 on any fault. derived-check.py runs it.
  cardedge.py [--all]             the same, and print every board, passing or not
  cardedge.py REPO "Board" REV    apply the standard to one revision not yet made, in place

What the standard sets, and so what is checked and applied:
  outline   Edge.Cuts redrawn from the standard, placed by the fingers where they are. No copper moves.
  holes     a cart's four shell holes, at their places in the standard's frame, so they move with the outline.
  mask      one filled rectangle on F.Mask and one on B.Mask over the tab, from the fillets' ends down, and the rule in
            the board's .kicad_dru that lets them bridge the fingers' nets. They must be the only drawings on a mask
            layer outside a footprint, so the rule hides nothing else.
  paste     the footprint's pads lose F.Paste and B.Paste. Their pin functions and types are kept.

Applying edits the PCB as text, leaving what already matches the standard as it was; then KiCad refills the pours
against the new outline and holes, and saves the board. Tracks, pads and vias don't move: gproof.py --no-fill shows the
copper unchanged but for the pours. Then run DRC and the rest of KICAD.md's "For agents" steps (regen.py, the label
and the History entry).

A newest revision waiting for its fix (a made board needs a new revision) is listed in Tools/data/cardedge.json under
"pending", with the item that fixes it. It is reported but doesn't fail the check, and an entry that is no longer
needed, because the revision passes or is no longer the newest, fails the check until it is removed."""
import os, re, sys, math, json, uuid, subprocess, tempfile
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(H)); sys.path.insert(0, H)
from common import KC, SCOPE, repo_dir, files, load
import kpcb

S = json.load(open(H + '/standard.json', encoding='utf-8'))
O, M, F = S['outline'], S['mask'], S['fingers']
TOL = 0.0005        # mm: what counts as the same point. The flaws K28 fixes are 0.007 mm and more
r2 = math.sqrt(0.5)


def kind(board):
    return 'cart' if board in S['cart']['boards'] else 'card'


# --- the standard, in the board's frame ---------------------------------------------------------------------------
def shape(board):
    """The outline as (('line', a, b) | ('arc', a, mid, b)) in the standard's frame, clockwise from the top left."""
    k = S[kind(board)]; W, L = k['width'], k['tab_left']
    h, B, r, TW, f, c = O['height'], O['body'], O['corner'], O['tab_width'], O['tab_fillet'], O['tab_corner']
    R = L + TW
    def arc(cx, cy, rad, a, mx, my, b):
        return ('arc', a, (cx + rad * mx, cy + rad * my), b)
    return [
        ('line', (r, 0), (W - r, 0)),
        arc(W - r, r, r, (W - r, 0), r2, -r2, (W, r)),
        ('line', (W, r), (W, B - r)),
        arc(W - r, B - r, r, (W, B - r), r2, r2, (W - r, B)),
        ('line', (W - r, B), (R + f, B)),
        arc(R + f, B + f, f, (R + f, B), -r2, -r2, (R, B + f)),
        ('line', (R, B + f), (R, h - c)),
        arc(R - c, h - c, c, (R, h - c), r2, r2, (R - c, h)),
        ('line', (R - c, h), (L + c, h)),
        arc(L + c, h - c, c, (L + c, h), -r2, r2, (L, h - c)),
        ('line', (L, h - c), (L, B + f)),
        arc(L - f, B + f, f, (L, B + f), r2, -r2, (L - f, B)),
        ('line', (L - f, B), (r, B)),
        arc(r, B - r, r, (r, B), -r2, r2, (0, B - r)),
        ('line', (0, B - r), (0, r)),
        arc(r, r, r, (0, r), -r2, -r2, (r, 0)),
    ]


def mask_box(board):
    k = S[kind(board)]; L, TW, o = k['tab_left'], O['tab_width'], M['overhang']
    return (L - o, O['body'] + O['tab_fillet'], L + TW + o, O['height'] + o)


# --- a board as it is -----------------------------------------------------------------------------------------------
class Board:
    def __init__(self, path):
        self.path = path = os.path.abspath(path)
        p = path.split('/'); self.repo, self.board, self.rev = p[-5].split('-')[-1], p[-3], p[-2][4:]
        self.t = open(path, encoding='utf-8', newline='').read()
        self.root = kpcb.parse(self.t)
        ce = [fp for fp in kpcb.footprints(self.root) if kpcb.lib_id(fp).split(':')[-1] == S['footprint']]
        if len(ce) != 1: raise SystemExit(f'{self.tag}: {len(ce)} "{S["footprint"]}" footprints, not one')
        self.fp = ce[0]
        self.pads = self.fp.all('pad')

    @property
    def tag(self):
        return f'{self.repo} {self.board} {self.rev}'

    def origin(self):
        """Where the standard's frame sits on this board, from its fingers: (x, y) of the board's top-left corner."""
        bx = [kpcb.pad_box(self.fp, p) for p in self.pads]
        x0, y0 = min(b[0] for b in bx), min(b[1] for b in bx)
        x1, y1 = max(b[2] for b in bx), max(b[3] for b in bx)
        if len(bx) != F['count'] or abs(x1 - x0 - F['span']) > TOL or abs(y1 - y0 - F['length']) > TOL:
            raise SystemExit(f'{self.tag}: the fingers are not the standard\'s: {len(bx)} pads, {x1 - x0:.4f} × {y1 - y0:.4f}')
        k = S[kind(self.board)]
        return (round(x0 - k['tab_left'] - (O['tab_width'] - F['span']) / 2, 6),
                round(y0 - O['body'] - F['from_tab_end'], 6))

    def edges(self):
        """Every outline item drawn on the board: (node, item)."""
        out = []
        for n in self.root.kids:
            if not n.name.startswith('gr_') or kpcb.layer(n) != 'Edge.Cuts': continue
            pt = lambda k: tuple(n.get(k).nums()[:2])
            if n.name == 'gr_line': out.append((n, ('line', pt('start'), pt('end'))))
            elif n.name == 'gr_arc': out.append((n, ('arc', pt('start'), pt('mid'), pt('end'))))
            else: raise SystemExit(f'{self.tag}: a {n.name} on Edge.Cuts: the tool draws lines and arcs only')
        for fp in kpcb.footprints(self.root):
            if any(kpcb.layer(n) == 'Edge.Cuts' for n in fp.kids):
                raise SystemExit(f'{self.tag}: {kpcb.ref(fp)} draws on Edge.Cuts; the tool can\'t place it')
        return out


def move(item, ox, oy):
    return (item[0],) + tuple((x + ox, y + oy) for x, y in item[1:])


def near(a, b):
    return abs(a[0] - b[0]) <= TOL and abs(a[1] - b[1]) <= TOL


def same(a, b):
    """Two outline items are the same, either way round."""
    if a[0] != b[0]: return False
    if near(a[1], b[1]) and near(a[-1], b[-1]) or near(a[1], b[-1]) and near(a[-1], b[1]):
        return a[0] == 'line' or near(a[2], b[2])
    return False


def inside(p, box):
    return box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3]


def outline(bd, ox, oy):
    """The outline the standard wants on this board, in the board's frame."""
    want = [move(i, ox, oy) for i in shape(bd.board)]
    ex = S['exceptions'].get(f'{bd.repo}|{bd.board}')
    if not ex: return want
    # the exception: inside the box the board's own outline stays as drawn; the standard's lines are cut to meet it
    box = (ex['keep'][0] + ox, ex['keep'][1] + oy, ex['keep'][2] + ox, ex['keep'][3] + oy)
    kept = [i for _, i in bd.edges() if all(inside(p, box) for p in i[1:])]
    if not kept: raise SystemExit(f'{bd.tag}: nothing of its own outline inside the exception\'s box')
    ends = [p for i in kept for p in (i[1], i[-1])]
    free = [p for p in ends if sum(near(p, q) for q in ends) == 1]
    if len(free) != 2: raise SystemExit(f'{bd.tag}: its own outline inside the box has {len(free)} loose ends, not 2')
    out = []
    for i in want:
        ins = [inside(p, box) for p in (i[1], i[-1])]
        if all(ins) and all(inside(p, box) for p in i[1:]): continue
        if not any(ins): out.append(i); continue
        if i[0] != 'line': raise SystemExit(f'{bd.tag}: an arc of the standard crosses the exception\'s box')
        a, b = (i[1], i[2]) if not ins[0] else (i[2], i[1])          # a outside, b inside
        d = (b[0] - a[0], b[1] - a[1]); n = math.hypot(*d); u = (d[0] / n, d[1] / n)
        p = min(free, key=lambda q: abs((q[0] - a[0]) * u[1] - (q[1] - a[1]) * u[0]))
        s = (p[0] - a[0]) * u[0] + (p[1] - a[1]) * u[1]
        e = (round(a[0] + u[0] * s, 6), round(a[1] + u[1] * s, 6))
        out.append(('line', a, e))
        if not near(e, p): out.append(('line', e, p))
    return out + kept


def holes(bd, ox, oy):
    """{reference: (footprint node, (x, y) wanted)} for a cart; {} for a card."""
    if kind(bd.board) != 'cart': return {}
    fps = {kpcb.ref(fp): fp for fp in kpcb.footprints(bd.root)}
    out = {}
    for ref, h in S['cart']['holes'].items():
        fp = fps.get(ref)
        if fp is None or kpcb.lib_id(fp) != h['footprint']:
            raise SystemExit(f'{bd.tag}: no {ref} {h["footprint"]}')
        out[ref] = (fp, (round(h['x'] + ox, 6), round(h['y'] + oy, 6)))
    return out


def masks(bd):
    """{layer: [(node, box)]}: every drawing on the mask layers outside a footprint. box is None but for a filled
    rectangle."""
    out = {l: [] for l in M['layers']}
    for n in bd.root.kids:
        l = kpcb.layer(n)
        if n.name.startswith('gr_') and l in out:
            box = None
            if n.name == 'gr_rect' and n.get('fill') and n.get('fill').atoms[0] in ('yes', 'solid'):
                a, b = n.get('start').nums(), n.get('end').nums()
                box = (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))
            out[l].append((n, box))
    return out


def tab_mask(bd, ox, oy):
    b = mask_box(bd.board); return (b[0] + ox, b[1] + oy, b[2] + ox, b[3] + oy)


def is_tab(box, bx):
    return box is not None and near(box[:2], bx[:2]) and near(box[2:], bx[2:])


def dru_path(path):
    return path[:-len('.kicad_pcb')] + '.kicad_dru'


def has_rule(path):
    p = dru_path(path)
    return os.path.exists(p) and M['drc_rule']['text'] in open(p, encoding='utf-8').read()


def pasted(bd):
    return [p for p in bd.pads if any(a.endswith('.Paste') for a in p.get('layers').atoms)]


# --- check ----------------------------------------------------------------------------------------------------------
def faults(bd):
    ox, oy = bd.origin(); E = []
    have = [i for _, i in bd.edges()]; want = outline(bd, ox, oy)
    extra = [i for i in have if not any(same(i, w) for w in want)]
    missing = [w for w in want if not any(same(i, w) for i in have)]
    if extra or missing:
        xs = [p for i in have for p in (i[1], i[-1])]
        E.append(f'outline: {len(missing)} of the standard\'s {len(want)} items missing, {len(extra)} others drawn; '
                 f'its corner is {min(x for x, _ in xs) - ox:+.4f}, {min(y for _, y in xs) - oy:+.4f} from where the fingers put it')
    for ref, (fp, (x, y)) in holes(bd, ox, oy).items():
        hx, hy, _ = kpcb.at(fp)
        if not near((hx, hy), (x, y)): E.append(f'{ref} at {hx}, {hy}, not {x}, {y}')
    bx = tab_mask(bd, ox, oy)
    for l, drawn in masks(bd).items():
        ok = [n for n, b in drawn if is_tab(b, bx)]
        if len(ok) != 1: E.append(f'{l}: no opening over the tab' if not ok else f'{l}: {len(ok)} openings over the tab')
        if len(drawn) > len(ok):
            E.append(f'{l}: {len(drawn) - len(ok)} other drawings; the DRC rule for the tab would hide their bridges')
    if not has_rule(bd.path): E.append(f'{os.path.basename(dru_path(bd.path))} lacks the rule for the tab\'s opening')
    p = pasted(bd)
    if p: E.append(f'paste on {len(p)} fingers')
    return E


def newest():
    """Every newest revision with the footprint: {key: path}."""
    by = {}
    for f in files('Hardware/*/Rev */*.kicad_pcb'):
        p = f.split('/'); by.setdefault((p[-5], p[-3]), []).append(f)
    out = {}
    for (repo, board), fs in by.items():
        f = sorted(fs, key=lambda x: [int(v) if v.isdigit() else v for v in re.findall(r'\d+|[a-z]+', x.split('/')[-2][4:])])[-1]
        if f':{S["footprint"]}"' in open(f, encoding='utf-8').read():
            out[f'{repo.split("-")[-1]}|{board}|{f.split("/")[-2][4:]}'] = f
    return out


def check(verbose):
    E = []; P = load('cardedge.json').get('pending', {}); N = newest(); good = 0
    for key, f in sorted(N.items()):
        bd = Board(f); e = faults(bd); why = P.get(key)
        if e and why: print(f'pending  {bd.tag}: {why}') if verbose else None
        elif e: E.append(f'{bd.tag}: ' + '; '.join(e))
        elif why: E.append(f'{bd.tag} passes: remove it from "pending" in Tools/data/cardedge.json')
        else:
            good += 1
            if verbose: print(f'ok       {bd.tag}')
    for key in P:
        if key not in N and key.split('|')[0] in SCOPE:
            E.append(f'{key} in "pending" in Tools/data/cardedge.json is not a newest revision with the footprint: remove it')
    # the library's footprint: no paste on its pads
    for r in SCOPE:
        lib = f'{repo_dir(r)}/Libraries/6502 Parts.pretty/{S["footprint"]}.kicad_mod'
        if os.path.exists(lib) and '.Paste"' in open(lib, encoding='utf-8').read():
            E.append(f'{r}: the library\'s "{S["footprint"]}" has paste on its pads')
    for e in E: print(e)
    print(f'card edges: {len(N)} newest revisions, {good} to the standard, {sum(1 for k in N if k in P)} pending, {len(E)} faults')
    return not E


# --- apply ----------------------------------------------------------------------------------------------------------
def num(v):
    s = f'{round(v, 6):.6f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def node_text(item, line):
    pts = ''.join(f'\n\t\t({k} {num(p[0])} {num(p[1])})' for k, p in zip(('start', 'mid', 'end') if item[0] == 'arc' else ('start', 'end'), item[1:]))
    return (f'\t(gr_{item[0]}{pts}\n\t\t(stroke\n\t\t\t(width {num(line)})\n\t\t\t(type solid)\n\t\t)\n'
            f'\t\t(layer "Edge.Cuts")\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n')


def rect_text(box, l):
    return (f'\t(gr_rect\n\t\t(start {num(box[0])} {num(box[1])})\n\t\t(end {num(box[2])} {num(box[3])})\n'
            f'\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type solid)\n\t\t)\n\t\t(fill yes)\n\t\t(layer "{l}")\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n')


def whole(t, n):
    """A top-level node's span with its own line: from the line's start to after its newline."""
    a, b = n.span
    a = t.rindex('\n', 0, a) + 1
    return a, b + 1 if t[b:b + 1] == '\n' else b


def apply(repo, board, rev):
    sys.path.insert(0, os.path.join(os.path.dirname(H), 'bom')); cwd = os.getcwd()
    os.chdir(os.path.join(os.path.dirname(H), 'bom')); from apply import status; os.chdir(cwd)
    if status(repo, board, rev) == 'made': raise SystemExit(f'{repo} {board} {rev} is made: never edit it. Start a new revision with newrev.py')
    apply_to(f'{repo_dir(repo)}/Hardware/{board}/Rev {rev}/{board}.kicad_pcb')


def apply_to(path):
    bd = Board(path); board = bd.board; t = bd.t; ox, oy = bd.origin(); ed = []; said = []
    # outline: keep what matches, remove the rest, add what's missing where the outline was
    have = bd.edges(); want = outline(bd, ox, oy); add = list(want); at = None
    for n, i in have:
        m = next((w for w in add if same(i, w)), None)
        if m: add.remove(m)
        else: ed.append(whole(t, n) + ('',))
        at = whole(t, n)[0] if at is None else at
    line = O['line']
    if add:
        ed.append((at, at, ''.join(node_text(i, line) for i in add)))
        said.append(f'outline: {len(add)} of {len(want)} items redrawn')
    # a cart's holes: the footprint's own (at) moves; its pads and drawings are relative to it
    for ref, (fp, (x, y)) in holes(bd, ox, oy).items():
        a = fp.get('at'); v = a.atoms
        if not near(tuple(map(float, v[:2])), (x, y)):
            ed.append((*a.span, f'(at {num(x)} {num(y)}{"".join(" " + s for s in v[2:])})'))
            said.append(f'{ref} moved {x - float(v[0]):+.4f}, {y - float(v[1]):+.4f}')
    # the mask opening: keep a match, remove an older opening over the tab; any other drawing is the check's to report
    bx = tab_mask(bd, ox, oy)
    for l, drawn in masks(bd).items():
        ok = False
        for n, b in drawn:
            if not ok and is_tab(b, bx): ok = True; continue
            if b and b[0] < bx[2] and b[2] > bx[0] and b[1] < bx[3] and b[3] > bx[1]: ed.append(whole(t, n) + ('',))
        if not ok:
            at2 = at if at is not None else t.rindex(')')
            ed.append((at2, at2, rect_text(bx, l))); said.append(f'{l} opened over the tab')
    # paste: drop the paste layer from each pad's (layers …), nothing else of the pad changes
    for p in pasted(bd):
        ly = p.get('layers')
        ed.append((*ly.span, '(layers ' + ' '.join(f'"{a}"' for a in ly.atoms if not a.endswith('.Paste')) + ')'))
    if pasted(bd): said.append(f'paste removed from {len(pasted(bd))} fingers')
    for a, b, s in sorted(ed, key=lambda e: (e[0], e[1]), reverse=True):
        t = t[:a] + s + t[b:]
    if t != bd.t:
        open(path, 'w', encoding='utf-8', newline='').write(t)
    # the DRC rule that lets the tab's opening bridge the fingers' nets
    if not has_rule(path):
        d = dru_path(path); old = open(d, encoding='utf-8').read() if os.path.exists(d) else '(version 1)\n'
        open(d, 'w', encoding='utf-8').write(old.rstrip('\n') + '\n\n' + M['drc_rule']['text']); said.append('DRC rule added')
    # the pours were filled against the old outline and holes: KiCad refills them and saves the board in its own format
    if said and t != bd.t:
        rp = tempfile.mktemp(suffix='.json')
        subprocess.run([KC, 'pcb', 'drc', '--refill-zones', '--save-board', '--format', 'json', '-o', rp, path], capture_output=True)
        if os.path.exists(rp): os.remove(rp)
        said.append('pours refilled')
    left = faults(Board(path))
    print(f'{bd.tag}: ' + ('; '.join(said) if said else 'already to the standard'))
    if left: raise SystemExit('still differs: ' + '; '.join(left))
    if said: print('Next: kicad-cli pcb drc, then KICAD.md "For agents": regen.py, gproof.py --no-fill, the label and the History entry')


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if x != '--all']
    if a and a[0] != '--check':
        if len(a) != 3: raise SystemExit(__doc__)
        apply(*a)
    else:
        sys.exit(0 if check(verbose=not a) else 1)
