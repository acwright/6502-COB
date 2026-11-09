#!/usr/bin/env python3
"""Draw a silk/value revision: newrev.py REPO "Board" OLD NEW 'REF=Value;REF=Value' ['REF=catalogue id;...']
Copies the tracked files, sets rev and date in both title blocks and the silk copyright line, sets each Value by
reference in the schematic and PCB, adds REPO|Board|NEW to drawn in Tools/data/orders.json, and copies the Tools/data/assignment.json entries. Add the
revision's label to labels in orders.json by hand."""
import os, re, sys, json, shutil, subprocess, collections
repo, board, old, new = sys.argv[1:5]
vals = dict(x.split('=', 1) for x in sys.argv[5].split(';') if x) if len(sys.argv) > 5 else {}
ids = dict(x.split('=', 1) for x in sys.argv[6].split(';') if x) if len(sys.argv) > 6 else {}
import datetime; DATE = datetime.date.today().isoformat()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); from common import repo_dir, load, save
R = repo_dir(repo)
src, dst = f'{R}/Hardware/{board}/Rev {old}', f'{R}/Hardware/{board}/Rev {new}'
assert not os.path.exists(dst), dst
files = subprocess.run(['git', 'ls-files', '-z'], cwd=src, capture_output=True, text=True).stdout.split('\0')
os.makedirs(dst)
for f in filter(None, files): shutil.copy2(f'{src}/{f}', f'{dst}/{f}')

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

def set_values(t, head, done):
    out = []; last = 0
    for m in re.finditer(head, t):
        s = m.start(); e = block_end(t, s + 1 + t[s+1:].index('(') if t[s] != '(' else s)
        b = t[s:e]; r = re.search(r'\(property "Reference" "([^"]*)"', b)
        if r and r.group(1) in vals:
            b2, n = re.subn(r'(\(property "Value" )"(?:[^"\\]|\\.)*"', lambda x: x.group(1) + '"' + vals[r.group(1)] + '"', b, count=1)
            assert n == 1; done[r.group(1)] += 1; out.append(t[last:s] + b2); last = e
    out.append(t[last:]); return ''.join(out)

for ext, head in (('kicad_sch', r'\n\t\(symbol\n\t\t\(lib_id'), ('kicad_pcb', r'\n\t\(footprint "')):
    p = f'{dst}/{board}.{ext}'; t = open(p, encoding='utf-8', newline='').read()
    t, n = re.subn(r'(\(title_block\n(?:\t\t\(title [^\n]*\n)?)\t\t\(date "[^"]*"\)\n\t\t\(rev "' + re.escape(old) + '"\)',
                   lambda m: m.group(1) + f'\t\t(date "{DATE}")\n\t\t(rev "{new}")', t)
    assert n == 1, (p, 'title block', n)
    if ext == 'kicad_pcb':
        t, n = re.subn(r'(gr_text "© \d{4} A\.C\. Wright Design \| acwrightdesign\.com \| Rev )[0-9][0-9.a-z]*"', r'\g<1>' + new + '"', t)  # a made board's silk can lag its rev (ROM Cart 1.0a says 1.0)
        assert n == 1, (p, 'silk rev', n)
    done = collections.Counter(); t = set_values(t, head, done)
    assert set(done) == set(vals) and all(v == 1 for v in done.values()), (p, done)
    open(p, 'w', encoding='utf-8', newline='').write(t)

d = load('orders.json')
k = f'{repo}|{board}|{new}'
if k not in d['drawn']: d['drawn'].append(k); d['drawn'].sort(key=lambda x: (x.split('|')[0], x))
save('orders.json', d)
a = load('assignment.json')
pre = f'{repo}|{board}|{old}|'
add = {f'{repo}|{board}|{new}|' + x[len(pre):]: v for x, v in a.items() if x.startswith(pre)}
for ref, i in ids.items():
    key = f'{repo}|{board}|{new}|{ref}'
    if i == '-': add.pop(key)
    else: assert key in add, key; add[key] = i
assert not any(x in a for x in add); a.update(add)
save('assignment.json', a)
print(k, 'drawn;', len(add), 'BOM entries;', dict(vals))
