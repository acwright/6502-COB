#!/usr/bin/env python3
"""For every global label on a schematic: the pins its local wiring reaches (not through other labels).
  labels.py SCHEMATIC  -> JSON list on stdout"""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sch import Sch, on_seg

import re, math
from sch import blk, R
def unit_pins(S):
    """lib_id -> list of (unit, body, num, x, y, a, name, type)"""
    t = S.t; ls = t.index('\n\t(lib_symbols'); le = blk(t, ls + 2); L = t[ls:le]; out = {}
    for m in re.finditer(r'\n\t\t\(symbol "([^"]*)"', L):
        st = m.start() + 3; b = L[st:blk(L, st)]; pins = []
        for sm in re.finditer(r'\n\t\t\t\(symbol "[^"]*_(\d+)_(\d+)"', b):
            s2 = sm.start() + 4; sb = b[s2:blk(b, s2)]
            for pm in re.finditer(r'\(pin (\w+) \w+\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)\s*\(length ([-\d.]+)\)[\s\S]*?\(name "([^"]*)"[\s\S]*?\(number "([^"]*)"', sb):
                pins.append((int(sm.group(1)), int(sm.group(2)), pm.group(7), float(pm.group(2)), float(pm.group(3)), float(pm.group(4)), pm.group(6), pm.group(1)))
        out[m.group(1)] = pins
    return out
def sym_pins(S, UP, sym):
    b = S.t[sym['a']:sym['e']]
    um = re.search(r'\n\t\t\(unit (\d+)\)', b); unit = int(um.group(1)) if um else 1
    bm = re.search(r'\n\t\t\((?:body_style|convert) (\d+)\)', b); body = int(bm.group(1)) if bm else 1
    res = {}
    for (u, bs, num, x, y, a, name, typ) in UP.get(sym['lib'], []):
        if u not in (0, unit) or bs not in (0, body): continue
        y = -y
        r = math.radians(-sym['rot']); c, sn = math.cos(r), math.sin(r)   # KiCad rotates, then mirrors
        x, y = x * c - y * sn, x * sn + y * c
        if sym['mirror'] == 'x': y = -y
        if sym['mirror'] == 'y': x = -x
        res[num] = ((R(sym['X'] + x), R(sym['Y'] + y)), name, typ, unit)
    return res
def analyse(path):
    S = Sch(path); UP = unit_pins(S)
    pts = {}  # point -> list of (ref, num, name, type, lib)
    for sym in S.symbols:
        if sym['lib'].startswith('power:'):
            continue
        for num, (P, name, typ, unit) in sym_pins(S, UP, sym).items():
            pts.setdefault(P, []).append((sym['ref'] + ('ABCDEFGH'[unit-1] if len({u for u,*_ in UP.get(sym['lib'],[]) if u}) > 1 else ''), num, name, typ, sym['lib'], sym['value']))
    # power symbols: their pin point joins a named net
    pw = {}
    for sym in S.symbols:
        if sym['lib'].startswith('power:') and 'PWR_FLAG' not in sym['lib']:
            for num, (P, d, name) in S.pins(sym).items():
                pw[P] = sym['value']
    # union-find over wires
    W = S.wires
    par = list(range(len(W)))
    def f(i):
        while par[i] != i:
            par[i] = par[par[i]]; i = par[i]
        return i
    def u(a, b): par[f(a)] = f(b)
    for i, a in enumerate(W):
        for j in range(i + 1, len(W)):
            b = W[j]
            if any(on_seg(p, b['p'][0], b['p'][-1]) for p in (a['p'][0], a['p'][-1])) or \
               any(on_seg(p, a['p'][0], a['p'][-1]) for p in (b['p'][0], b['p'][-1])):
                u(i, j)
    groups = collections.defaultdict(list)
    for i in range(len(W)):
        groups[f(i)].append(i)
    def group_of(P):
        for i, w in enumerate(W):
            if on_seg(P, w['p'][0], w['p'][-1]):
                return f(i)
        return None
    gpins = collections.defaultdict(list); glabels = collections.defaultdict(list)
    for P, lst in pts.items():
        g = group_of(P)
        if g is not None:
            gpins[g] += lst
    for l in S.labels:
        g = group_of(l['p'])
        glabels[g].append(l)
    out = []
    for l in S.labels:
        if l['kind'] != 'global_label':
            continue
        g = group_of(l['p'])
        if g is None:
            pins = pts.get(l['p'], [])  # label straight on a pin
            others = []
        else:
            pins = gpins[g]
            others = [(o['kind'], o['name']) for o in glabels[g] if o is not l]
        out.append(dict(name=l['name'], shape=l['shape'], uuid=l['uuid'], p=l['p'],
                        pins=[dict(ref=r, pin=n, pname=nm, type=t, lib=lb, value=v) for r, n, nm, t, lb, v in pins],
                        others=others))
    return out

if __name__ == '__main__':
    print(json.dumps(analyse(sys.argv[1]), indent=1))
