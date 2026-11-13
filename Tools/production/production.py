#!/usr/bin/env python3
"""The production files' settings, and a check that they were made with them (KICAD.md K38).

  production.py [--all] --sync    write options.json, byte for byte, as fabrication-toolkit-options.json in every
                                  revision's folder (the file the Fabrication Toolkit's window reads)
  production.py --pin VERSION     record the installed plugin's files in plugin.json, after reviewing an update
  production.py [--all] --check   exit 1 if: any revision's options file differs from options.json; the plugin's files
                                  differ from plugin.json; or a revision not yet made has a positions.csv whose parts
                                  or rotations aren't what the plugin gives with options.json, recomputed here from
                                  the PCB and the plugin's transformations.csv

The recomputation follows the plugin's own rules (process.py, generate_tables and generate_positions): a part is
placed unless it is marked exclude_from_pos_files or DNP, or its designator contains '**'; its rotation is the footprint's, mirrored on the bottom (180 - r), plus the first row
of transformations.csv whose pattern matches the footprint's name (or, failing that, its library's), modulo 360.
No board uses the plugin's per-part offset fields; the check fails if one appears. Made and ordered revisions keep
the files JLCPCB received and aren't checked here. Read-only except for --sync."""
import os, sys, re, csv, json, glob, hashlib
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(H)); sys.path.insert(0, os.path.join(os.path.dirname(H), 'bom'))
from common import K, SCOPE
STD = open(os.path.join(H, 'options.json'), 'rb').read()
PIN = json.load(open(os.path.join(H, 'plugin.json')))
PLUGIN = os.path.expanduser(PIN['folder'])
NAME = 'fabrication-toolkit-options.json'
OFFSET_FIELDS = ('FT Rotation Offset', 'Rotation Offset', 'RotOffset', 'FT Position Offset', 'Position Offset',
                 'PosOffset', 'FT Layer Override', 'Layer Override', 'LayerOverride')


def revisions():
    for r in SCOPE:
        for d in sorted(glob.glob(f'{K}6502-{r}/Hardware/*/Rev *')):
            if os.path.isdir(d):
                yield r, d.split('/')[-2], d.split('/')[-1][4:], d


def status(repo, board, rev):
    o = json.load(open(f'{K}6502-{repo}/Tools/data/orders.json'))
    k = f'{repo}|{board}|{rev}'
    return 'made' if k in o['made'] else 'ordered' if k in o['ordered'] else 'drawn'


def table():
    rows = list(csv.reader(open(os.path.join(PLUGIN, 'transformations.csv'), newline='')))
    return [(r[0], float(r[1] or 0)) for r in rows[1:] if r]


def footprints(text):
    """(reference, library nickname, footprint name, layer, rotation, attrs, value, fields) for each footprint."""
    out = []
    for m in re.finditer(r'\n\t\(footprint "([^"]*)"', text):
        i = m.start() + 1; d = 0; k = i; q = False
        while k < len(text):
            c = text[k]
            if q:
                if c == '\\': k += 1
                elif c == '"': q = False
            elif c == '"': q = True
            elif c == '(': d += 1
            elif c == ')':
                d -= 1
                if d == 0: break
            k += 1
        b = text[i:k + 1]
        lib = m.group(1); nick, _, name = lib.rpartition(':')
        layer = re.search(r'^\t\t\(layer "([^"]+)"\)', b, re.M).group(1)
        at = re.search(r'^\t\t\(at [-\d.]+ [-\d.]+(?: ([-\d.]+))?\)', b, re.M)
        rot = float(at.group(1) or 0)
        attr = re.search(r'^\t\t\(attr ([^)]*)\)', b, re.M)
        fields = dict(re.findall(r'^\t\t\(property "([^"]*)" "([^"]*)"', b, re.M))
        out.append((fields.get('Reference', '?'), nick, name, layer, rot, (attr.group(1).split() if attr else []),
                    fields.get('Value', ''), fields))
    return out


def expected(text, tab):
    """{DESIGNATOR: (rotation, layer)} as the plugin would write positions.csv with AUTO TRANSLATE on; and problems."""
    exp, probs = {}, []
    for ref, nick, name, layer, rot, attrs, value, fields in footprints(text):
        if any(f in fields for f in OFFSET_FIELDS):
            probs.append(f'{ref} has a per-part offset field, which this check does not model')
        dnp = 'dnp' in attrs or value.upper() == 'DNP' or 'dnp' in fields
        # the plugin leaves out exclude_from_pos_files and DNP parts, and writes no row for a designator with '**'
        # in it (a logo's G***, a graphic's REF**)
        if 'exclude_from_pos_files' in attrs or dnp or '**' in ref:
            continue
        side = 'bottom' if layer == 'B.Cu' else 'top'
        r = 180.0 - rot if side == 'bottom' else rot
        add = next((v for p, v in tab if re.search(p, name)), None)
        if add is None and nick:
            add = next((v for p, v in tab if re.search(p, nick)), 0.0)
        exp[ref.upper()] = ((r + (add or 0.0)) % 360.0, side)
    return exp, probs


def sync():
    n = 0
    for repo, board, rev, d in revisions():
        p = os.path.join(d, NAME)
        if not os.path.exists(p) or open(p, 'rb').read() != STD:
            open(p, 'wb').write(STD); n += 1; print(f'{repo} {board} {rev}: {NAME} written')
    print(f'{n} written')


def check():
    bad = []
    for f, h in PIN['sha256'].items():
        p = os.path.join(PLUGIN, f)
        if not os.path.exists(p) or hashlib.sha256(open(p, 'rb').read()).hexdigest() != h:
            bad.append(f'plugin file {f} differs from plugin.json (see README.md, "Updating the plugin")')
    tab = table()
    n = 0
    for repo, board, rev, d in revisions():
        p = os.path.join(d, NAME)
        if not os.path.exists(p): bad.append(f'{repo} {board} {rev}: no {NAME} (run production.py --sync)')
        elif open(p, 'rb').read() != STD: bad.append(f'{repo} {board} {rev}: {NAME} differs from Tools/production/options.json')
        if status(repo, board, rev) != 'drawn': continue
        pos = f'{K}6502-{repo}/Production/{board}/Rev {rev}/positions.csv'
        if not os.path.exists(pos): continue
        exp, probs = expected(open(os.path.join(d, f'{board}.kicad_pcb'), encoding='utf-8').read(), tab)
        bad += [f'{repo} {board} {rev}: {x}' for x in probs]
        got = {row[0].upper(): (float(row[3]) % 360.0, row[4]) for row in list(csv.reader(open(pos, encoding='utf-8-sig')))[1:] if row}
        for ref in sorted(set(exp) | set(got)):
            if ref not in got: bad.append(f'{repo} {board} {rev}: {ref} missing from positions.csv')
            elif ref not in exp: bad.append(f'{repo} {board} {rev}: {ref} in positions.csv but not placed by the PCB')
            elif abs((got[ref][0] - exp[ref][0] + 180) % 360 - 180) > 0.01 or got[ref][1] != exp[ref][1]:
                bad.append(f'{repo} {board} {rev}: {ref} at {got[ref][0]:g}° {got[ref][1]}, '
                           f'the plugin gives {exp[ref][0]:g}° {exp[ref][1]} (regenerate with Tools/regen.py)')
        n += 1
    for b in bad: print(b)
    print(f'production check: {n} placement files, {len(bad)} faults')
    return not bad


def pin(version):
    """Record the installed plugin as the reviewed one (README.md, "Updating the plugin")."""
    files = {f: hashlib.sha256(open(os.path.join(PLUGIN, f), 'rb').read()).hexdigest()
             for f in sorted(os.listdir(PLUGIN)) if f.endswith(('.py', '.csv'))}
    PIN.update(version=version, sha256=files)
    open(os.path.join(H, 'plugin.json'), 'w').write(json.dumps(PIN, indent=1) + '\n')
    print(f'plugin.json: version {version}, {len(files)} files')


if __name__ == '__main__':
    if '--pin' in sys.argv: pin(sys.argv[sys.argv.index('--pin') + 1])
    elif '--sync' in sys.argv: sync()
    elif '--check' in sys.argv: sys.exit(0 if check() else 1)
    else: print(__doc__)
