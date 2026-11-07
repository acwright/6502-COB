#!/usr/bin/env python3
"""Checks that the schematic, PCB, bom.csv, BOM.md and cart files agree with each other and with the catalogue. Read-only. Exit 1 on any fault."""
import re,os,sys,glob,csv,json,collections
from apply import footprints,props,fp_ref,block,gen_bom,want_fields,JUNK,FIELDS,H,K,C,status
import gen_bom as G
from common import files,load,SCOPE
A=load('assignment.json');E=[];seen=collections.defaultdict(set);n=collections.Counter()
for f in files('Hardware/*/Rev */*.kicad_pcb'):
    p=f.split('/');repo=p[-5].split('-')[-1];b=p[-3];r=p[-2][4:];tag=f'{repo} {b} {r}';t=open(f,encoding='utf-8',newline='').read();PCB={}
    for s,e in footprints(t):
        x=t[s:e];ref=fp_ref(x);P={m[0]:m[1] for m in props(x,'\t\t')};PCB[ref]=P
        for j in JUNK&set(P): E.append(f'{tag} {ref}: junk field {j} in PCB')
        i=A.get(f'{repo}|{b}|{r}|{ref}')
        if i:
            at=re.search(r'\n\t\t\(attr ([^)]*)\)',x);a=at.group(1).split() if at else []
            if 'exclude_from_bom' in a and 'board_only' not in a: E.append(f'{tag} {ref}: excluded from BOM')
            if i in C:
                W=want_fields(C[i])
                for k,v in W.items():
                    if P.get(k,'').replace('\\"','"')!=v: E.append(f'{tag} {ref}: PCB {k}={P.get(k)!r}, catalogue {v!r}')
            else: E.append(f'{tag} {ref}: {i} not in catalogue')
            n['parts']+=1
    SCH={}
    for sf in glob.glob(os.path.dirname(f)+'/*.kicad_sch'):
        st=open(sf,encoding='utf-8',newline='').read()
        for m in re.finditer(r'\n\t\(symbol\n\t\t\(lib_id',st):
            x=st[m.start():block(st,m.start()+1)];P={q[0]:q[1] for q in props(x,'\t\t')};rr=re.findall(r'\(reference "([^"]+)"',x);ref=rr[0] if rr else P.get('Reference','')
            if ref.startswith('#'): continue
            SCH[ref]=P
            for j in JUNK&set(P): E.append(f'{tag} {ref}: junk field {j} in schematic')
    for ref,P in SCH.items():
        if ref not in PCB: continue
        for k in FIELDS+['Value']:
            if (P.get(k,'')!=PCB[ref].get(k,'')) and (k=='Value' or f'{repo}|{b}|{r}|{ref}' in A): E.append(f'{tag} {ref}: {k} schematic {P.get(k)!r}, PCB {PCB[ref].get(k)!r}')
    pd=f'{K}6502-{repo}/Production/{b}/Rev {r}/bom.csv'
    if os.path.exists(pd):
        if open(pd,encoding='utf-8',newline='').read()!=gen_bom(t): E.append(f'{tag}: bom.csv is out of date')
        n['bom.csv']+=1
    else: E.append(f'{tag}: no bom.csv') if status(repo,b,r)!='drawn' else None
    md=open(f'{K}6502-{repo}/BOM.md',encoding='utf-8').read();m=re.search(r'\n### '+re.escape(f'{b} Rev {r}')+r'\n(.*?)(?=\n### |\n## |\Z)',md,re.S)
    if not m: E.append(f'{tag}: not in BOM.md');continue
    n['revisions']+=1;sec=m.group(1)
    R,socks,dnp,pins=G.rev_rows(repo,b,r,f);DNP={x[0] for x in dnp}   # once per revision, not once per part
    for ref,P in PCB.items():
        i=A.get(f'{repo}|{b}|{r}|{ref}')
        if not i or i not in C or ref in DNP: continue
        for k in('Digikey','Mouser'):
            if P.get(k) and P[k] not in sec and not i.startswith('BREADBOARD'): E.append(f'{tag} {ref}: {P[k]} not in BOM.md')
    if sum(len(x['refs']) for x in R)+len(dnp)!=sum(1 for ref in PCB if f'{repo}|{b}|{r}|{ref}' in A): E.append(f'{tag}: parts lost in BOM rows')
    for sup in('digikey','mouser'):
        c=f'{K}6502-{repo}/BOM/{b}/Rev {r}/{sup}.csv'
        if not os.path.exists(c): E.append(f'{tag}: no {sup}.csv');continue
        have={x[0]:int(x[2]) for x in list(csv.reader(open(c,encoding='utf-8')))[1:]};want=G.cart_lines(repo,b,r,R,socks,pins,sup,False)
        if have!={k:v[1] for k,v in want.items()}: E.append(f'{tag}: {sup}.csv out of date')
        n[sup+' carts']+=1
    if 'amazon' in sec.lower():
        for ref,P in PCB.items():
            if 'amazon' in P.get('Other','').lower() and (P.get('Digikey') or P.get('Mouser')): E.append(f'{tag} {ref}: Amazon beside a supplier number')
# one part, one set of numbers
for i,e in C.items():
    if e['uses']: seen[(e.get('mpn'),)].add((e.get('digikey'),e.get('mouser'),e.get('lcsc'),e.get('jameco')))
for mp,v in seen.items():
    if mp[0] and len(v)>1 and not re.match(r'(PRPC|2PH|MX)',mp[0]): E.append(f'{mp[0]}: more than one set of numbers: {sorted(map(str,v))}')
for r in 'ACE COB DEV KIM VCS'.split():
    if 'BOM.md' not in open(f'{K}6502-{r}/README.md',encoding='utf-8').read(): E.append(f'{r}: README has no link to BOM.md')
print(dict(n));print('faults',len(E));[print(' ',x) for x in E[:40]]
sys.exit(1 if E else 0)
