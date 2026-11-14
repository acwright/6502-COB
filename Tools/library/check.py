#!/usr/bin/env python3
"""Checks the five repos' own libraries agree. Read-only. Exit 1 on any fault.

- A footprint, a 3D model or a symbol with one name is the same in every repo that has it, byte for byte (symbols:
  the same definition).
- Every footprint and symbol a board uses from "6502 Parts" is in its repo's library, and every project model a
  footprint points to is in its repo's Models/.
- No old part-number name from mapping.json is left in a library, a board, or a model's file name.
- Every board logo a PCB uses is in its repo's "6502 Logos" library, and no old logo name from mapping.json is left
  (KICAD.md K32). The logos' shapes are checked by Tools/logos/generate.py --check.
"""
import os,re,sys,glob,json,hashlib,collections
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))));import common;from common import K,SCOPE,files,load,save
H=os.path.dirname(os.path.abspath(__file__));M=json.load(open(H+'/mapping.json'))
REPOS=common.present()   # the libraries must be the same in every repository checked out here
E=[];n=collections.Counter()
def symbols(t):
    out={}
    for m in re.finditer(r'\n\t\(symbol "([^"]+)"',t):
        a=m.start()+1;d=0;j=a;q=False
        while True:
            c=t[j]
            if c=='"' and t[j-1]!='\\': q=not q
            elif not q:
                if c=='(':d+=1
                elif c==')':
                    d-=1
                    if d==0:break
            j+=1
        out[m.group(1)]=re.sub(r'\(uuid "[^"]+"\)','',t[a:j+1])
    return out
def same(kind,get):
    have=collections.defaultdict(dict)
    for r in REPOS:
        for name,v in get(r).items(): have[name][r]=hashlib.sha1(v if isinstance(v,bytes) else v.encode()).hexdigest()
    for name,v in have.items():
        n[kind]+=1
        if len(set(v.values()))>1: E.append(f'{kind} "{name}" differs between repos: {sorted(v)}')
fp=lambda r:{os.path.basename(f)[:-10]:open(f,'rb').read() for f in glob.glob(K+f'6502-{r}/Libraries/6502 Parts.pretty/*.kicad_mod')}
mo=lambda r:{os.path.basename(f):open(f,'rb').read() for f in glob.glob(K+f'6502-{r}/Models/*')}
sy=lambda r:symbols(open(K+f'6502-{r}/Libraries/6502 Parts.kicad_sym',encoding='utf-8').read())
same('footprint',fp);same('model',mo);same('symbol',sy)
old_fp=set(M['footprints'])|{k for v in M.get('footprints_by_repo',{}).values() for k in v}|set(M['delete_footprints']);old_sym=set(M['symbols'])|{k for v in M.get('symbols_by_repo',{}).values() for k in v}
old_mo={x.lower() for x in M['models']}|{x.lower() for x in M['delete_models']}
for r in SCOPE:
    F=set(fp(r));Mo={x.lower() for x in mo(r)};S=set(sy(r))
    for x in F&old_fp: E.append(f'{r}: library still has footprint "{x}"')
    for x in Mo&old_mo: E.append(f'{r}: Models/ still has "{x}"')
    for x in S&old_sym: E.append(f'{r}: library still has symbol "{x}"')
    for f in glob.glob(K+f'6502-{r}/Hardware/*/Rev */*.kicad_pcb'):
        t=open(f,encoding='utf-8').read();tag=f'{r} '+f.split('Hardware/')[1].rsplit('/',1)[0]
        for x in set(re.findall(r'\(footprint "6502 Parts:([^"]+)"',t)):
            n['footprints used']+=1
            if x not in F: E.append(f'{tag}: footprint "{x}" is not in the library')
        for x in set(re.findall(r'\(model "\$\{KIPRJMOD\}/\.\./\.\./\.\./Models/([^"]+)"',t)):
            if x.lower() not in Mo: E.append(f'{tag}: model "{x}" is not in Models/')
    for f in glob.glob(K+f'6502-{r}/Hardware/*/Rev */*.kicad_sch'):
        t=open(f,encoding='utf-8').read();tag=f'{r} '+f.split('Hardware/')[1].rsplit('/',1)[0]
        for x in set(re.findall(r'\(lib_id "6502 Parts:([^"]+)"',t)):
            n['symbols used']+=1
            if x not in S: E.append(f'{tag}: symbol "{x}" is not in the library')
        for x in set(re.findall(r'"6502 Parts:([^"]+)"',t))&(old_fp|old_sym): E.append(f'{tag}: still names "{x}"')
# the board logos (KICAD.md K32)
old_logo=set(M.get('logos',{}))|{k for v in M.get('logos_by_repo',{}).values() for k in v}|set(M.get('delete_logos',[]))
for r in SCOPE:
    L={os.path.basename(f)[:-10] for f in glob.glob(K+f'6502-{r}/Libraries/6502 Logos.pretty/*.kicad_mod')}
    for x in L&old_logo: E.append(f'{r}: 6502 Logos still has "{x}"')
    for f in glob.glob(K+f'6502-{r}/Hardware/*/Rev */*.kicad_pcb'):
        t=open(f,encoding='utf-8').read();tag=f'{r} '+f.split('Hardware/')[1].rsplit('/',1)[0]
        for x in set(re.findall(r'\(footprint "6502 Logos:([^"]+)"',t)):
            n['logos used']+=1
            if x not in L: E.append(f'{tag}: logo "{x}" is not in 6502 Logos')
print(dict(n));print('faults',len(E));[print(' ',x) for x in E[:60]];sys.exit(1 if E else 0)
