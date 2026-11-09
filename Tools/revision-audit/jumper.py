#!/usr/bin/env python3
"""Set a two-pad solder jumper's default as made, or remove jumpers, on a revision not yet made:

  jumper.py REPO "Board" REV REF bridged|open
  jumper.py REPO "Board" REV remove REF...

remove: a jumper that ships bridged becomes a wire in the schematic and a track on the PCB where its copper strip
was; one that ships open goes, with the wires, tracks, vias, flags and junctions that served only it. The proof is the
netlist: the new one must be the old one with each bridged jumper's two nets joined and the jumpers' pins gone, or
nothing is written. On the PCB, KiCad's DRC finds what dangles, the pours are refilled, and DRC must then report
nothing unconnected.

KiCad draws the default as two library parts: Jumper:SolderJumper_2_Bridged, whose footprint carries a strip of copper
between the pads, and Jumper:SolderJumper_2_Open, whose footprint doesn't. This swaps one for the other by reference, in
the schematic (the symbol, its Value, its Footprint and the symbol's definition in lib_symbols) and in the PCB (the
footprint's name, its strip of copper and its net tie). The pads, their nets and every other item stay where they are,
so the only copper that changes is the strip between the two pads. The symbol and footprint are taken from KiCad's own
libraries. Then run DRC, regen.py and the rest of KICAD.md's "For agents" steps; Tools/data/jumpers.json says how
each jumper ships."""
import os, re, sys, uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import repo_dir, load

KIC = '/Applications/KiCad/KiCad.app/Contents/SharedSupport'
SYM = {'bridged': 'SolderJumper_2_Bridged', 'open': 'SolderJumper_2_Open'}
FP = {'bridged': 'SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm', 'open': 'SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm'}


def block_end(t, i):
    d = 0; j = i
    while True:
        c = t[j]
        if c == '"':
            j += 1
            while t[j] != '"': j += 2 if t[j] == '\\' else 1
        elif c == '(': d += 1
        elif c == ')':
            d -= 1
            if d == 0: return j + 1
        j += 1


def blocks(t, head):
    for m in re.finditer(head, t):
        s = m.start() + (1 if t[m.start()] == '\n' else 0)
        yield s, block_end(t, s)


def indent(b, n):
    return '\n'.join(('\t' * n + x) if x else x for x in b.split('\n'))


def main():
    repo, board, rev, ref, to = sys.argv[1:6]
    assert to in SYM, to
    frm = 'open' if to == 'bridged' else 'bridged'
    d = load('orders.json')
    assert f'{repo}|{board}|{rev}' in d['drawn'] + d['never'], f'{repo} {board} {rev} has been made or ordered: draw a new revision'
    base = f'{repo_dir(repo)}/Hardware/{board}/Rev {rev}/{board}'

    # Schematic: the symbol instance, then the definition it needs in lib_symbols.
    p = base + '.kicad_sch'; t = open(p, encoding='utf-8', newline='').read()
    hits = [(s, e) for s, e in blocks(t, r'\n\t\(symbol\n\t\t\(lib_id "Jumper:SolderJumper_2_')
            if re.search(r'\(property "Reference" "' + re.escape(ref) + '"', t[s:e])]
    assert len(hits) == 1, (p, ref, len(hits))
    s, e = hits[0]; b = t[s:e]
    if f'Jumper:{SYM[to]}"' in b.split('\n')[1]:
        print(f'{ref} is already {to} in the schematic')
    else:
        b = b.replace(f'(lib_id "Jumper:{SYM[frm]}")', f'(lib_id "Jumper:{SYM[to]}")', 1)
        b = re.sub(r'(\(property "Value" )"[^"]*"', r'\1"' + SYM[to] + '"', b, count=1)
        b = re.sub(r'(\(property "Footprint" )"[^"]*"', r'\1"Jumper:' + FP[to] + '"', b, count=1)
        t = t[:s] + b + t[e:]
    if f'(symbol "Jumper:{SYM[to]}"' not in t:
        lib = open(f'{KIC}/symbols/Jumper.kicad_sym', encoding='utf-8').read()
        (ls, le), = [x for x in blocks(lib, r'\n\t\(symbol "' + SYM[to] + '"\n')]
        sym = lib[ls:le].replace(f'(symbol "{SYM[to]}"', f'(symbol "Jumper:{SYM[to]}"', 1)
        i = t.index('\t(lib_symbols\n') + len('\t(lib_symbols\n')
        t = t[:i] + indent(sym, 1) + '\n' + t[i:]
    open(p, 'w', encoding='utf-8', newline='').write(t)

    # PCB: the footprint by reference. Its pads are the same in both parts; only the strip of copper and the net tie
    # differ, with the names and the descriptions.
    p = base + '.kicad_pcb'; t = open(p, encoding='utf-8', newline='').read()
    hits = [(s, e) for s, e in blocks(t, r'\n\t\(footprint "Jumper:SolderJumper-2_P1\.3mm_')
            if re.search(r'\(property "Reference" "' + re.escape(ref) + '"', t[s:e])]
    assert len(hits) == 1, (p, ref, len(hits))
    s, e = hits[0]; b = t[s:e]
    lib = open(f'{KIC}/footprints/Jumper.pretty/{FP[to]}.kicad_mod', encoding='utf-8').read()
    descr = re.search(r'\(descr "[^"]*"\)', lib).group(0); tags = re.search(r'\(tags "[^"]*"\)', lib).group(0)
    b = re.sub(r'\(footprint "[^"]*"', f'(footprint "Jumper:{FP[to]}"', b, count=1)
    b = re.sub(r'\(descr "[^"]*"\)', descr, b, count=1); b = re.sub(r'\(tags "[^"]*"\)', tags, b, count=1)
    b = re.sub(r'(\(property "Value" )"[^"]*"', r'\1"' + SYM[to] + '"', b, count=1)
    b = re.sub(r'(\(property "Footprint" )"[^"]*"', r'\1"Jumper:' + FP[to] + '"', b, count=1)
    b = re.sub(r'\(property ki_fp_filters "[^"]*"\)', f'(property ki_fp_filters "SolderJumper*{SYM[to].split("_")[-1]}*")', b, count=1)
    # The strip of copper: an fp_poly on F.Cu, and the net tie that lets it join the pads' two nets.
    cu = [(x, y) for x, y in blocks(b, r'\n\t\t\(fp_poly\n') if '(layer "F.Cu")' in b[x:y]]
    for x, y in reversed(cu):
        b = b[:x - 1] + b[y:]
    b = re.sub(r'\n\t\t\(net_tie_pad_groups "[^"]*"\)', '', b)
    if to == 'bridged':
        (fs, fe), = [x for x in blocks(lib, r'\n\t\(fp_poly\n') if '(layer "F.Cu")' in lib[x[0]:x[1]]]
        poly = re.sub(r'\(uuid "[^"]*"\)', f'(uuid "{uuid.uuid4()}")', lib[fs:fe])
        m = re.search(r'\n\t\t\(attr [^\n]*\)', b)
        b = b[:m.end()] + '\n\t\t(net_tie_pad_groups "1, 2")' + b[m.end():]
        i = re.search(r'\n\t\t\(fp_(line|rect|arc|circle|poly|text)\b', b).start()
        b = b[:i] + '\n' + indent(poly, 1) + b[i:]
    t = t[:s] + b + t[e:]
    open(p, 'w', encoding='utf-8', newline='').write(t)
    print(f'{repo} {board} {rev} {ref}: {to} as made')


# ---- remove

KC = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def netlist(sch):
    import subprocess, tempfile
    o = tempfile.mktemp(suffix='.net'); subprocess.run([KC, 'sch', 'export', 'netlist', '-o', o, sch], capture_output=True)
    t = open(o).read(); os.remove(o); t = t[t.index('(nets'):]; nets = {}
    for part in re.split(r'\n\t\t\(net\n', t)[1:]:
        name = re.search(r'\(name "([^"]*)"', part).group(1)   # as the PCB names it: '/X' for a local label
        nets[name] = frozenset(re.findall(r'\(ref "([^"]*)"\)\s*\(pin "([^"]*)"\)', part))
    return nets


def allpins(S, R):
    """point -> [(ref, number)] for every pin of every symbol, counting pins that share a number (a card edge's two VCC
    and two GND pins), which Sch.pins keys away"""
    import math
    lib = {}
    ls = S.t.index('\n\t(lib_symbols'); L = S.t[ls:block_end(S.t, ls + 2)]
    for s, e in blocks(L, r'\n\t\t\(symbol "'):
        name = re.search(r'\(symbol "([^"]*)"', L[s:e]).group(1)
        lib[name] = [(float(x), float(y), num) for x, y, num in
                     re.findall(r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) [-\d.]+\)[\s\S]*?\(number "([^"]*)"', L[s:e])]
    out = {}
    for sym in S.symbols:
        ln = re.search(r'\n\t\t\(lib_name "([^"]*)"\)', S.t[sym['a']:sym['e']])   # an instance may name its symbol so
        for x, y in [(p[0], p[1]) for p in lib.get(ln.group(1) if ln else sym['lib'], [])]:
            y = -y; r = math.radians(-sym['rot']); c, sn = math.cos(r), math.sin(r)
            x, y = x * c - y * sn, x * sn + y * c
            if sym['mirror'] == 'x': y = -y
            if sym['mirror'] == 'y': x = -x
            out.setdefault((R(sym['X'] + x), R(sym['Y'] + y)), []).append(sym['ref'])
    return out


def remove(repo, board, rev, refs):
    import json, math, subprocess, tempfile, shutil
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'schematic'))
    from sch import Sch, on_seg, R
    d = load('orders.json')
    assert f'{repo}|{board}|{rev}' in d['drawn'] + d['never'], f'{repo} {board} {rev} has been made or ordered: draw a new revision'
    base = f'{repo_dir(repo)}/Hardware/{board}/Rev {rev}/{board}'
    sp, pp = base + '.kicad_sch', base + '.kicad_pcb'
    pcb = open(pp, encoding='utf-8', newline='').read()
    fps = {}
    for s, e in blocks(pcb, r'\n\t\(footprint "'):
        r = re.search(r'\(property "Reference" "([^"]*)"', pcb[s:e]).group(1); fps[r] = (s, e)
    bridged = {r for r in refs if 'Bridged' in pcb[fps[r][0]:fps[r][1]].split('\n')[0]}

    # Schematic. The expected netlist first: the jumpers' pins gone, a bridged jumper's two nets one.
    old = netlist(sp)
    groups = [set(v) for v in old.values()]
    for r in bridged:
        a = [g for g in groups if any(x[0] == r for x in g)]
        if len(a) == 2: groups.remove(a[0]); groups.remove(a[1]); groups.append(a[0] | a[1])
    want = {frozenset(x for x in g if x[0] not in refs) for g in groups}; want.discard(frozenset())
    S = Sch(sp); t = S.t
    jp = {sym['ref']: sym for sym in S.symbols if sym['ref'] in refs}
    assert set(jp) == set(refs), (set(refs) - set(jp))
    new_wires = [tuple(p[0] for p in S.pins(jp[r]).values()) for r in sorted(bridged)]
    for sym in sorted(jp.values(), key=lambda x: -x['a']): t = t[:sym['a']] + t[sym['e']:]
    tmpl = '\n\t(wire\n\t\t(pts\n\t\t\t(xy {:g} {:g}) (xy {:g} {:g})\n\t\t)\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "{}")\n\t)'
    i = t.index('\n\t(wire\n') if '\n\t(wire\n' in t else t.index('\n\t(sheet_instances')
    t = t[:i] + ''.join(tmpl.format(*a, *b, uuid.uuid4()) for a, b in new_wires) + t[i:]
    gone = []
    while True:   # what served only the removed jumpers: dangling wires, then lone power flags, then spare junctions
        tmp = sp + '.tmp'; open(tmp, 'w', encoding='utf-8', newline='').write(t); S = Sch(tmp); os.remove(tmp)
        pins = allpins(S, R); anchors = [l['p'] for l in S.labels] + [n['p'] for n in S.ncs] + [j['p'] for j in S.junctions]
        def held(q, w):
            if q in pins or q in anchors: return True
            return any(o is not w and (q in o['p'] or on_seg(q, o['p'][0], o['p'][1])) for o in S.wires)
        cut = [(w['a'], w['e'], f"wire {w['p']}") for w in S.wires if not (held(w['p'][0], w) and held(w['p'][1], w))]
        if not cut:
            for sym in S.symbols:
                if not sym['lib'].startswith('power:'): continue
                for q, _, _ in S.pins(sym).values():
                    if not any(q in w['p'] or on_seg(q, *w['p']) for w in S.wires) and len(pins.get(q, [])) == 1:
                        cut.append((sym['a'], sym['e'], f"{sym['ref']} {sym['value']}"))
        if not cut:
            for j in S.junctions:
                n = sum((j['p'] in w['p']) + 2 * (on_seg(j['p'], *w['p']) and j['p'] not in w['p']) for w in S.wires) + len(pins.get(j['p'], []))
                if n < 3: cut.append((j['a'], j['e'], f"junction {j['p']}"))
        if not cut: break
        for a, e, what in sorted(cut, reverse=True): t = t[:a] + t[e:]; gone.append(what)
    tmp = sp + '.check.kicad_sch'; open(tmp, 'w', encoding='utf-8', newline='').write(t)
    for ext in ('kicad_pro',):
        if os.path.exists(base + '.' + ext): shutil.copy(base + '.' + ext, sp + '.check.' + ext)
    got = netlist(tmp)
    for f in (tmp, sp + '.check.kicad_pro'):
        if os.path.exists(f): os.remove(f)
    have = set(got.values()); have.discard(frozenset())
    if have != want:
        print('netlist differs; nothing written'); print(' missing', [sorted(x) for x in want - have][:6]); print(' extra', [sorted(x) for x in have - want][:6]); sys.exit(1)
    open(sp, 'w', encoding='utf-8', newline='').write(t)
    print(f'{board} {rev} schematic: removed {sorted(refs)}, {len(bridged)} wired as bridged; also removed {gone}')

    # PCB: the footprints, a track for each bridged one, the nets renamed from the new netlist, then DRC's danglers.
    t = pcb; pads = {}
    for r in refs:
        s, e = fps[r]; b = t[s:e]
        at = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', b); X, Y, A = float(at.group(1)), float(at.group(2)), float(at.group(3) or 0)
        lay = re.search(r'\n\t\t\(layer "([^"]*)"\)', b).group(1); pads[r] = []
        for ps, pe in blocks(b, r'\n\t\t\(pad "'):
            pa = re.search(r'\(at ([-\d.]+) ([-\d.]+)', b[ps:pe]); px, py = float(pa.group(1)), float(pa.group(2))
            a = math.radians(-A); pads[r].append((round(X + px * math.cos(a) - py * math.sin(a), 4), round(Y + px * math.sin(a) + py * math.cos(a), 4), lay))
    mine = set()   # the nets the removed jumpers sat on: only these are renamed
    for r in refs:
        mine |= set(re.findall(r'\(pad "[^"]*"[\s\S]*?\(net "([^"]*)"\)', t[fps[r][0]:fps[r][1]]))
    for r in sorted(refs, key=lambda r: -fps[r][0]):
        s, e = fps[r]; t = t[:s - 1] + t[e:]
    newnet = {x: n for n, g in got.items() for x in g}
    ren = {}
    for s, e in blocks(t, r'\n\t\(footprint "'):
        b = t[s:e]; r = re.search(r'\(property "Reference" "([^"]*)"', b).group(1)
        for ps, pe in blocks(b, r'\n\t\t\(pad "'):
            num = re.search(r'\(pad "([^"]*)"', b[ps:pe]).group(1); n = re.search(r'\(net "([^"]*)"\)', b[ps:pe])
            if n and n.group(1) in mine and (r, num) in newnet and n.group(1) != newnet[(r, num)]: ren[n.group(1)] = newnet[(r, num)]
    for o, n in ren.items(): t = t.replace(f'(net "{o}")', f'(net "{n}")')
    seg = '\n\t(segment\n\t\t(start {} {})\n\t\t(end {} {})\n\t\t(width 0.2)\n\t\t(layer "{}")\n\t\t(net "{}")\n\t\t(uuid "{}")\n\t)'
    for r in sorted(bridged):
        (x1, y1, lay), (x2, y2, _) = pads[r][:2]
        i = t.index('\n\t(segment\n'); t = t[:i] + seg.format(x1, y1, x2, y2, lay, '@@' + r, uuid.uuid4()) + t[i:]
    open(pp, 'w', encoding='utf-8', newline='').write(t)
    # a bridged jumper's track takes the net of whatever track already ends at either pad
    for r in sorted(bridged):
        (x1, y1, lay), (x2, y2, _) = pads[r][:2]
        n = None
        for s, e in blocks(t, r'\n\t\(segment\n'):
            b = t[s:e]
            if '@@' in b: continue
            pts = [(float(a), float(c)) for a, c in re.findall(r'\((?:start|end) ([-\d.]+) ([-\d.]+)\)', b)]
            if any(math.dist(q, (x1, y1)) < 0.01 or math.dist(q, (x2, y2)) < 0.01 for q in pts):
                n = re.search(r'\(net "([^"]*)"\)', b).group(1); break
        assert n, f'no track reaches {r}'
        t = t.replace(f'(net "@@{r}")', f'(net "{n}")')
    removed = []
    for _ in range(20):
        open(pp, 'w', encoding='utf-8', newline='').write(t)
        o = tempfile.mktemp(suffix='.json')
        subprocess.run([KC, 'pcb', 'drc', '--refill-zones', '--save-board', '--schematic-parity', '--format', 'json', '-o', o, pp], capture_output=True)
        dr = json.load(open(o)); os.remove(o); t = open(pp, encoding='utf-8', newline='').read()
        dead = {i['uuid'] for v in dr['violations'] if v['type'] in ('track_dangling', 'via_dangling') for i in v['items']}
        if not dead: break
        for kind in ('segment', 'via', 'arc'):
            for s, e in sorted(blocks(t, r'\n\t\(' + kind + r'\n'), reverse=True):
                u = re.search(r'\(uuid "([^"]*)"\)', t[s:e]).group(1)
                if u in dead: removed.append(kind + ' ' + ' '.join(re.findall(r'\((?:start|end|at) [-\d. ]+\)', t[s:e]))); t = t[:s - 1] + t[e:]
    print(f'{board} {rev} PCB: nets renamed {ren}; removed {removed}')
    print(f'  DRC: {len(dr["violations"])} violations, {len(dr["unconnected_items"])} unconnected, {len(dr["schematic_parity"])} parity')


if __name__ == '__main__':
    if sys.argv[4:5] == ['remove']: remove(*sys.argv[1:4], sys.argv[5:])
    else: main()
