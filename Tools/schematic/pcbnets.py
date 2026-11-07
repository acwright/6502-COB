#!/usr/bin/env python3
"""Rename nets in a PCB to follow its schematic, as text. Only names change: no pad, track or zone moves.
  pcbnets.py PCB '{"old":"new",...}'"""
import sys,re,json
p,ren=sys.argv[1],json.loads(sys.argv[2]);t=open(p,encoding='utf-8',newline='').read()
have=set(re.findall(r'\(net(?:_name)? (?:\d+ )?"((?:[^"\\]|\\.)*)"\)',t))
for o,n in ren.items():
    if n in have and n not in ren: raise SystemExit(f'{p}: {n} already exists')
def sub(m):
    name=m.group(2);return m.group(1)+'"'+ren.get(name,name)+'"'+m.group(3)
t2=re.sub(r'(\(net(?:_name)? (?:\d+ )?)"((?:[^"\\]|\\.)*)"(\))',sub,t)
open(p,'w',encoding='utf-8',newline='').write(t2)
print(p.split('/Hardware/')[-1],sum(1 for o in ren if f'"{o}"' in t),'nets renamed')
