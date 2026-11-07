#!/usr/bin/env python3
"""Renames the custom library parts in the five AC6502 KiCad repos to names that don't depend on a part number.

  python3 rename.py           apply mapping.json to the libraries, models, every revision's schematic and PCB,
                              and the old BOM exports in Hardware/

A footprint, symbol or model is named for what it is and its geometry, never for a manufacturer part number,
so a part with the same footprint and a different supplier number fits without renaming anything (owner,
2026-11-05). The part numbers live only in the BOM fields. Each footprint's description says which parts it
was checked against.

The libraries are re-saved by KiCad (Tools/library/resave.py, in KiCad's own Python), so every copy of a part
is in the same file format, and then made byte-identical across repos: Tools/library/check.py fails on a part
that differs between repos. Renames don't move a pad or a line, so the Gerbers don't change.
"""
import os,re,sys,json,glob,shutil,subprocess
H=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))));import common;from common import K,SCOPE,files,load,save
KPY='/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3'
M=json.load(open(H+'/mapping.json'))
REPOS=common.scope(['--all'])   # renames reach every repository at once
def fpmap(repo):
    m=dict(M['footprints']);m.update(M.get('footprints_by_repo',{}).get(repo,{}));return m
def git(repo,*a): subprocess.run(['git','-C',K+'6502-'+repo,*a],check=True,capture_output=True)
def model_sub(t):
    for o,n in M['models'].items():
        t=re.sub(r'(Models/)'+re.escape(o)+r'"',lambda m:m.group(1)+n+'"',t,flags=re.I)
    return t
# ---- 1. models
for repo in REPOS:
    d=K+f'6502-{repo}/Models'
    for f in sorted(os.listdir(d)):
        for o,n in M['models'].items():
            if f.lower()==o.lower():
                if os.path.exists(f'{d}/{n}'):
                    if open(f'{d}/{f}','rb').read()!=open(f'{d}/{n}','rb').read(): raise SystemExit(f'{repo}: {f} and {n} differ')
                    git(repo,'rm','-q',f'Models/{f}')
                else: git(repo,'mv',f'Models/{f}',f'Models/{n}')
                print(repo,'model',f,'->',n)
        if f in M['delete_models'] and os.path.exists(f'{d}/{f}'): git(repo,'rm','-q',f'Models/{f}');print(repo,'model deleted',f)
# ---- 2. footprint libraries: KiCad re-saves every footprint under its new name
for repo in REPOS:
    lib=K+f'6502-{repo}/Libraries/6502 Parts.pretty';fm=fpmap(repo)
    for n in M['delete_footprints']:
        if os.path.exists(f'{lib}/{n}.kicad_mod'): git(repo,'rm','-q',f'Libraries/6502 Parts.pretty/{n}.kicad_mod');print(repo,'footprint deleted',n)
    x=subprocess.run([KPY,H+'/resave.py',lib,json.dumps(fm)],capture_output=True,text=True)
    if x.returncode: raise SystemExit(x.stdout+x.stderr)
    for l in x.stdout.splitlines():
        if l.startswith('renamed'): print(repo,l)
    for f in glob.glob(lib+'/*.kicad_mod'):
        t=open(f,encoding='utf-8').read();u=model_sub(t)
        if u!=t: open(f,'w',encoding='utf-8').write(u)
    subprocess.run(['git','-C',K+'6502-'+repo,'add','-A','Libraries'],check=True)
def pads(t): return sorted(re.findall(r'\(pad "([^"]*)" (\w+) (\w+)\s*\(at ([-\d. ]+)\)\s*\(size ([-\d. ]+)\)',t))
def dedupe_symbols(t):
    """A merge can leave two top-level symbols with one name in a library; keep the first."""
    spans=[];seen=set();i=0
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
        if m.group(1) in seen: spans.append((m.start(),j+1))
        seen.add(m.group(1))
    for a,b in reversed(spans): t=t[:a]+t[b:]
    return t
# ---- 3. one copy of each part: the first repo's file, word for word, in every repo that has the part
seen={}
for repo in REPOS:
    for f in sorted(glob.glob(K+f'6502-{repo}/Libraries/6502 Parts.pretty/*.kicad_mod')):
        n=os.path.basename(f)
        if n in seen:
            if pads(open(seen[n]).read())!=pads(open(f).read()): raise SystemExit(f'{n}: pads differ between {seen[n]} and {f}')
            shutil.copyfile(seen[n],f)
        else: seen[n]=f
# ---- 4. symbols, in each library and in every schematic's cached copy
def symsub(t,sm,fm):
    for o,n in sm.items():
        t=t.replace(f'(lib_id "6502 Parts:{o}")',f'(lib_id "6502 Parts:{n}")')
        t=t.replace(f'(symbol "6502 Parts:{o}"',f'(symbol "6502 Parts:{n}"')
        t=re.sub(r'\(symbol "'+re.escape(o)+r'(_\d+_\d+)?"',lambda m:f'(symbol "{n}{m.group(1) or ""}"',t)
        t=t.replace(f'(extends "{o}")',f'(extends "{n}")')
    for o,n in fm.items():
        t=t.replace(f'"6502 Parts:{o}"',f'"6502 Parts:{n}"')
    return t
for repo in REPOS:
    fm=fpmap(repo);sm=dict(M['symbols']);sm.update(M.get('symbols_by_repo',{}).get(repo,{}))
    p=K+f'6502-{repo}/Libraries/6502 Parts.kicad_sym';t=open(p,encoding='utf-8').read();u=symsub(t,sm,fm)
    u=dedupe_symbols(u)
    if u!=t: open(p,'w',encoding='utf-8').write(u);print(repo,'symbol library')
    for f in glob.glob(K+f'6502-{repo}/Hardware/*/Rev */*.kicad_sch'):
        t=open(f,encoding='utf-8',newline='').read();u=symsub(t,sm,fm)
        if u!=t: open(f,'w',encoding='utf-8',newline='').write(u);print(repo,'schematic',f.split('Hardware/')[1])
    for f in glob.glob(K+f'6502-{repo}/Hardware/*/Rev */*.kicad_pcb'):
        t=open(f,encoding='utf-8',newline='').read();u=model_sub(t)
        for o,n in fm.items(): u=u.replace(f'"6502 Parts:{o}"',f'"6502 Parts:{n}"')
        if u!=t: open(f,'w',encoding='utf-8',newline='').write(u);print(repo,'pcb',f.split('Hardware/')[1])
    for f in glob.glob(K+f'6502-{repo}/Hardware/*/Rev */*.csv'):
        t=open(f,encoding='utf-8',newline='').read();u=t
        for o,n in fm.items(): u=re.sub(r'(?<![\w-])'+re.escape(o)+r'(?![\w-])',n,u)
        if u!=t: open(f,'w',encoding='utf-8',newline='').write(u);print(repo,'csv',f.split('Hardware/')[1])
