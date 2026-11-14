#!/usr/bin/env python3
"""Every board not yet made prints the library's logo, as generate.py draws it (KICAD.md K32b).

  embed.py --check [--all]          exit 1 if the logo embedded in any revision not yet made differs from its footprint
                                    in Libraries/6502 Logos.pretty/. derived-check.py runs it.
  embed.py [--all]                  the same, printing every revision with a board logo, made ones included
  embed.py REPO "Board" REV         put the library's logo into one revision not yet made, in place
  embed.py --apply [--all]          the same for every revision not yet made whose logo differs

KiCad copies a footprint into the PCB when it is placed, and a change to the library reaches a board only when the
footprint is updated there. So after generate.py redraws a logo, every board not yet made takes it with this tool.
A made or ordered revision keeps the logo it was made with, and isn't checked.

Putting a logo in replaces the footprint's drawn shapes (its fp_poly items, as text) with the library's and keeps
everything else: its place, reference, uuid and properties. The library's origin is the centre of the print, where a
traced logo's was the centre of its picture, so the footprint's (at …) then moves by the difference, keeping the
print's centre where it was. Run placement.py --check after: a logo that changed size can need placement.py to put its
ends back in place. Silk only: no copper moves, and a label stays as it is (K16)."""
import os, re, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(H)); sys.path.insert(0, os.path.join(os.path.dirname(H), 'cardedge'))
from common import files, load, repo_dir
import kpcb
from placement import shapes_box, status, num, LOGO

LIB = 'Libraries/6502 Logos.pretty'


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def polys(node, t=None):
    return [k for k in node.kids if k.name == 'fp_poly']


def library(repo_root, name):
    p = f'{repo_root}/{LIB}/{name}.kicad_mod'
    if not os.path.exists(p): return None, None
    t = open(p, encoding='utf-8', newline='').read()
    return t, kpcb.parse(t)


def logo(t):
    root = kpcb.parse(t)
    fps = [f for f in kpcb.footprints(root) if LOGO.match(kpcb.lib_id(f))]
    return fps[0] if len(fps) == 1 else None


def state(path):
    """(repo, board, rev, the logo's footprint name, 'same' / 'differs' / a fault)."""
    p = path.split('/'); repo, board, rev = p[-5].split('-')[-1], p[-3], p[-2][4:]
    t = open(path, encoding='utf-8', newline='').read()
    if '6502 Logos:' not in t: return repo, board, rev, None, None
    fp = logo(t)
    if fp is None: return repo, board, rev, None, 'more than one board logo'
    name = kpcb.lib_id(fp).split(':', 1)[1]
    lt, lroot = library('/'.join(p[:-4]), name)
    if lt is None: return repo, board, rev, name, f'no footprint "{name}" in {LIB}'
    if kpcb.layer(fp) != kpcb.layer(lroot): return repo, board, rev, name, f'on {kpcb.layer(fp)}, the library\'s on {kpcb.layer(lroot)}'
    a = [norm(k.text(t)) for k in polys(fp, t)]; b = [norm(k.text(lt)) for k in polys(lroot, lt)]
    return repo, board, rev, name, 'same' if a == b else 'differs'


def indent(block, by):
    return block.replace('\n', '\n' + by)


def apply_one(path):
    repo, board, rev, name, st = state(path)
    if st != 'differs': return st
    t = open(path, encoding='utf-8', newline='').read()
    fp = logo(t); old = polys(fp, t)
    cx0, cy0 = (lambda b: ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2))(shapes_box(fp))
    lt, lroot = library('/'.join(path.split('/')[:-4]), name)
    # the board's footprint children sit one tab deeper than the library's
    first = old[0].span[0]; line0 = t.rfind('\n', 0, first) + 1; pad = t[line0:first]
    new = ('\n' + pad).join(indent(k.text(lt), '\t') for k in polys(lroot, lt))
    # remove every old poly with its line, then put the library's where the first one was
    out, last = [], 0
    for k in old:
        s = t.rfind('\n', 0, k.span[0]); out.append(t[last:s]); last = k.span[1]
    out.append(t[last:])
    t2 = out[0] + '\n' + pad + new + ''.join(out[1:])
    fp2 = logo(t2)
    cx1, cy1 = (lambda b: ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2))(shapes_box(fp2))
    a = fp2.get('at'); x, y, r = kpcb.at(fp2)
    at = f'(at {num(x + cx0 - cx1)} {num(y + cy0 - cy1)}' + (f' {num(r)}' if len(a.atoms) > 2 else '') + ')'
    t3 = t2[:a.span[0]] + at + t2[a.span[1]:]
    open(path, 'w', encoding='utf-8', newline='').write(t3)
    st2 = state(path)[4]
    if st2 != 'same': raise SystemExit(f'{repo} {board} {rev}: still {st2} after putting the logo in')
    c = (lambda b: ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2))(shapes_box(logo(t3)))
    if abs(c[0] - cx0) > 1e-4 or abs(c[1] - cy0) > 1e-4: raise SystemExit(f'{repo} {board} {rev}: the print\'s centre moved')
    return 'put in'


def run(mode):
    O = load('orders.json'); E = []; n = dict(same=0, put=0, made=0, none=0)
    for f in files('Hardware/*/Rev */*.kicad_pcb'):
        repo, board, rev, name, st = state(f)
        if st is None: n['none'] += 1; continue
        s = status(O, repo, board, rev)
        tag = f'{repo} {board} {rev}'
        if s != 'drawn':
            n['made'] += 1
            if mode == 'list': print(f'{s:8} {tag}: {st}')
            continue
        if st == 'same':
            n['same'] += 1
            if mode == 'list': print(f'ok       {tag}: {name}')
        elif st == 'differs' and mode == 'apply':
            apply_one(f); n['put'] += 1; print(f'put in   {tag}: {name}')
        else:
            E.append(f'{tag}: its logo {st if st != "differs" else "differs from the library"} ({name}): run embed.py {repo} "{board}" {rev}')
    for e in E: print(e)
    print(f'logo footprints: {n["same"]} revisions not yet made match the library, {n["put"]} put in, {n["made"]} made or '
          f'ordered (not checked), {n["none"]} without a board logo, {len(E)} faults')
    return not E


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if x != '--all']
    if a and a[0] == '--apply': sys.exit(0 if run('apply') else 1)
    if a and a[0] != '--check':
        if len(a) != 3: raise SystemExit(__doc__)
        repo, board, rev = a
        f = files(f'Hardware/{board}/Rev {rev}/{board}.kicad_pcb', repos=(repo,))
        if not f: raise SystemExit(f'no PCB for {repo} {board} {rev}')
        st = status(load('orders.json'), repo, board, rev)
        if st != 'drawn': raise SystemExit(f'{repo} {board} {rev} is {st}: never edit it')
        print(f'{repo} {board} {rev}: {apply_one(f[0])}')
    else:
        sys.exit(0 if run('check' if a else 'list') else 1)
