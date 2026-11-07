#!/usr/bin/env python3
"""Prints the consistency table, or writes it with --out FILE: every board's newest revision against each P8 rule,
read from the PCB files. Read-only on the repos. With --all it covers all five repositories."""
import re,os,glob,json,collections,sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','bom'))
from apply import footprints,props,fp_ref,block,status,K,O,FIT,C
from common import files,load,SCOPE
H=os.path.dirname(os.path.abspath(__file__));A=load('assignment.json');AUD={(r['repo'],r['board'],r['rev']):r for r in load('audit.json')}
PHASE={('KIM','KIM Board'),('ACE','ACE Board'),('COB','VGA Card'),('COB','Backplane Pro'),('COB','Clock Card'),('COB','RAM Card'),('VCS','Main Board')}
CPU={'ACE Board','KIM Board','Main Board','CPU Card','CPU Card Pro','DEV Board'}
SHARED={'RESB','IRQB','NMIB','RDY','BE','SOB'};BUS=('RESB','IRQB','NMIB','RDY','BE')  # SOB isn't on the bus: tied to VCC or pulled up, either is fine
# The rule: one 10k pull-up on each bus line, on the board with the CPU, and none anywhere else.
# An ATmega's reset pin has its own pull-up inside the chip, 30-60 kΩ per the datasheets. On RESB it sits in parallel with the
# CPU board's 10k. That's accepted: everything that pulls RESB low sinks far more than the ~1 mA this adds.
RESET_PIN={'DIP-28':'1','DIP-40':'9'}  # ATmega328 and ATmega1284 reset pins
# Differences accepted by name, with the reason: (repo, board, column) -> (the cell's exact text, reason)
ACCEPT={('ACE','ACE RAM Patch','Footprints'):('DIP without a socket ×4','no IC sockets, on purpose (owner, 2026-11-06)')}
BADV=re.compile(r'^(D_Schottky|OCXO-14|65C21|LM555xM|R|74LS\d+|6551|65C51|Q_NPN_BEC|ATmega1284-P|MAX238xNG\+)$|DB9 (MALE|Male|FEMALE|Female)')
rows=[];diffs=[];revs=collections.defaultdict(list)
for f in files('Hardware/*/Rev */*.kicad_pcb'):
    p=f.split('/');revs[(p[-5].split('-')[-1],p[-3])].append((p[-2][4:],f))
for (repo,b),L in sorted(revs.items()):
    r,f=sorted(L)[-1];t=open(f,encoding='utf-8',newline='').read();st=status(repo,b,r);fp=collections.Counter();val=[];pu=collections.defaultdict(list);ids=set();vals=set();hidden=[]
    for s,e in footprints(t):
        x=t[s:e];ref=fp_ref(x);i=A.get(f'{repo}|{b}|{r}|{ref}')
        if not i: continue
        ids.add(i);P={m[0]:m[1] for m in props(x,'\t\t')};name=re.match(r'\n\t\(footprint "([^"]*)"',x).group(1).split(':')[-1];v=P.get('Value','');vals.add(v)
        if name.startswith('R_Axial') and 'DIN0204' not in name: fp['axial resistor '+name[:24]]+=1
        if v.startswith('ATmega'):
            rp=next((n for k,n in RESET_PIN.items() if name.startswith(k)),None)
            for pad,net in re.findall(r'\(pad "(\d+)"[^\n]*\n(?:(?!\(pad )[\s\S])*?\(net (?:\d+ )?"([^"]*)"\)',x):
                if pad==rp and net.lstrip('/')=='RESB': hidden.append(f'{ref} {v} reset pin')
        if name.startswith('C_Disc') and 'P2.50' not in name: fp['disc capacitor at 5 mm']+=1
        if name.startswith('CP_Radial') and 'D4.0mm_P1.50' not in name: fp[name]+=1
        if name.startswith('DIP-') and 'Socket' not in name: fp['DIP without a socket']+=1
        if re.search('axial|Radial|DO-35|DO-41',name) and 0: pass
        if BADV.search(v) and i!='keyswitch-mx': val.append(f'{ref} {v}')
        if ref.startswith('R'):
            N=[re.sub(r'^/','',m) for m in re.findall(r'\(pad "[12]"[^\n]*\n(?:(?!\(pad)[\s\S])*?\(net (?:\d+ )?"([^"]*)"\)',x)]
            hit=[n for n in N if n in SHARED]
            if hit and any(n in('VCC','+5V','5V') for n in N): pu[hit[0]].append(('10k' if f'{repo}|{b}|{r}|{ref}' in FIT else v,ref))
    power=[]
    bj=any(i.startswith('5V DC|Barrel') for i in ids)
    if bj:
        if not any(i.startswith('1N5819') for i in ids): power.append('no 1N5819')
        if not any(i.startswith('POWER|') for i in ids) and b!='Clock Card': power.append('no power switch')
    pul=[]
    if pu:
        for n,x in sorted(pu.items()):
            vs={q[0] for q in x}
            if b not in CPU: pul.append(f'{n} pull-up on a non-CPU board ({"/".join(sorted(vs))})')
            elif vs-{'10k'}: pul.append(f'{n} {"/".join(sorted(vs))}')
            elif len(x)>1: pul.append(f'{n} has {len(x)}')
    if b in CPU: pul+=[f'{n} no pull-up' for n in BUS if n not in pu]
    pacc=f'✓ (accepted: {", ".join(hidden)}, the chip\'s own pull-up on RESB)' if hidden and not pul else None
    clock=[v for i,v in ((i,None) for i in ())]
    osc=sorted({C[i]['mpn'] for i in ids if 'Oscillator' in i and i in C});oscv=sorted(v for v in vals if re.search(r'MHz',v))
    fl=[]
    d=f'{K}6502-{repo}';rv=f'Rev {r}'
    if not glob.glob(f'{d}/Production/{b}/{rv}/*.zip'): fl.append('zip')
    if not os.path.exists(f'{d}/Schematics/{b}/{rv}/{b}.pdf'): fl.append('schematic PDF')
    if not os.path.exists(f'{d}/CAD/Images/{b}/{rv}/Front.png'): fl.append('images')
    if not os.path.exists(f'{d}/BOM/{b}/{rv}/digikey.csv'): fl.append('carts')
    au=AUD.get((repo,b,r),{});names='✓' if 'A.C. Wright Design' in (au.get('silk_label') or '') else (au.get('silk_label') or 'no silk label')
    op=[i for i in ids if C.get(i,{}).get('review')]
    def cell(x,col=None):
        s='✓' if not x else '; '.join(x);a=ACCEPT.get((repo,b,col))
        return f'✓ (accepted: {s}, {a[1]})' if a and s==a[0] else s
    rows.append((repo,b,r,st,('★' if (repo,b) in PHASE else ''),cell([f'{k} ×{n}' for k,n in fp.items()],'Footprints'),cell(val),cell(power),pacc or cell(pul),names,cell([C[i]['mpn'] for i in op]),cell(fl)))
o=['# Consistency table','', 'Generated by `Tools/consistency/table.py --all`, from the PCB files. One row per board, at its newest revision. ★ marks the boards P8 names. A produced revision is never changed, so a difference on a made or ordered board goes into `BOM.md` or the next revision, and `KICAD.md` lists those revisions. A difference marked *accepted* is intended, and its reason is recorded in `table.py`.','','**Pull-ups:** each bus line (`RESB`, `IRQB`, `NMIB`, `RDY`, `BE`) has one 10k pull-up, on the board with the CPU (the ACE Board, KIM Board, VCS Main Board, CPU Card, CPU Card Pro and DEV Board), and no pull-up on any other board. A pull-up on two boards would sit in parallel and lower the value. `SOB` isn\'t on the bus, so it may be tied to VCC or pulled up.','','| Repo | Board | Rev | Status | ★ | Footprints | Values | Power | Pull-ups | Names on silk | Part open | Files missing |','|---|---|---|---|---|---|---|---|---|---|---|---|']
for x in rows: o.append('| '+' | '.join(x)+' |')
miss=[x for x in rows if any(not c.startswith('✓') for c in x[5:9])]
o+=['','## Not covered by this table','','- **Off-board switch headers and the clock** need reading board by board, so they aren\'t scored here. `Tools/revision-audit/` and the schematic checks cover the clock on the ACE, COB and KIM.','- **Listings and DOCS wording** aren\'t in the PCB files.','- **Supplier fields** are checked by `tools/bom/check.py`, across every revision.','']
OUT=sys.argv[sys.argv.index('--out')+1] if '--out' in sys.argv else None
if OUT: open(OUT,'w',encoding='utf-8').write('\n'.join(o)+'\n');print('wrote',OUT)
else: print('\n'.join(o))
print(len(rows),'boards; with a difference:',len(miss))
for x in miss: print(' ',x[0],x[1],x[2],x[3],x[4],'|F',x[5][:50],'|V',x[6][:60],'|P',x[7][:30],'|U',x[8][:70])
print('names',[(x[1],x[2],x[9][:30]) for x in rows if x[9]!='✓']);print('files',[(x[1],x[2],x[11]) for x in rows if x[11]!='✓'])
