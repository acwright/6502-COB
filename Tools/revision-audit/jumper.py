#!/usr/bin/env python3
"""Set a two-pad solder jumper's default as made, on a revision not yet made:

  jumper.py REPO "Board" REV REF bridged|open

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


if __name__ == '__main__':
    main()
