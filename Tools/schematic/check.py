#!/usr/bin/env python3
"""Checks every schematic's 6502 bus, cart and card connectors (KICAD.md K21, K22). Read-only.

  check.py [--no-cache]

K21: the connectors are drawn the standard way: busfix.py, run dry, would change nothing.
K22: bus pins 4 (EXP1) and 6 (EXP0) are one of
  - joined as HRDB (a board that reads it: the ROM's disable),
  - tied to GND (a cartridge),
  - not connected,
  - EXP1 and EXP0, two nets that reach only connectors and jumpers (a board that passes the bus through),
and their names match the silk. Only the COB Memory Card joins EXP0/EXP1 to HRDB through jumpers.
Prints one line per fault and exits 1 if there are any."""
import sys,os,re,glob,json,collections,tempfile,subprocess
H=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,H);sys.path.insert(0,os.path.dirname(H))
import busfix
from sch import Sch
from cache import Cache,digest
from common import K,files
KC='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
CACHE=Cache('schematic-check',os.path.abspath(__file__))
TOOLS=(os.path.join(H,'busfix.py'),os.path.join(H,'sch.py'))  # their bytes are part of every key
# Wired to something other than a connector or jumper on purpose, with the reason
ACCEPT_EXP={('COB','Mega Helper','1.0'):'Arduino D5 and D6, for an experimenter; its README says not to drive them with a cartridge fitted'}
# Jumpers between EXP0/EXP1 and HRDB: the Memory Card's, for the COB's experimenters (owner, 2026-11-06). Main Board
# 1.0 was made with them; Rev 1.1 drops them (K23).
JUMPERS={('COB','Memory Card'),('VCS','Main Board','1.0')}
def netlist(sch):
    o=tempfile.mktemp(suffix='.net');subprocess.run([KC,'sch','export','netlist','-o',o,sch],capture_output=True)
    t=open(o).read();os.remove(o);t=t[t.index('(nets'):];pm={}
    for part in re.split(r'\n\t\t\(net\n',t)[1:]:
        name=re.search(r'\(name "([^"]*)"',part).group(1)
        for r,p in re.findall(r'\(ref "([^"]*)"\)\s*\(pin "([^"]*)"',part): pm[(r,p)]=name
    return pm
def faults(sch):
    p=sch.split('/');repo,board,rev=p[-5].split('-')[-1],p[-3],p[-2][4:]
    nets=netlist(sch);out=[]
    tmp=tempfile.mktemp(suffix='.kicad_sch');import shutil;shutil.copy(sch,tmp)
    log=busfix.main(tmp,nets,dry=True);os.remove(tmp)
    ch={k:v for k,v in log.items() if v}
    if ch: out.append(f'K21 not drawn to the standard: {ch}')
    S=Sch(sch);members=collections.defaultdict(set)
    for (r,pn),n in nets.items(): members[n].add(r)
    pcb=sch[:-4]+'_pcb';silk=set(re.findall(r'\(gr_text "(HRDB|EXP0|EXP1)[" |]',open(pcb,errors='replace').read())) if os.path.exists(pcb) else set()
    for sym in S.symbols:
        if not busfix.is_conn(sym): continue
        card=sym['lib']==busfix.CARD;p4,p6=('EXP1','EXP0') if card else ('4','6')
        n4,n6=nets.get((sym['ref'],p4),''),nets.get((sym['ref'],p6),'')
        b4,b6=n4.lstrip('/'),n6.lstrip('/')
        un=lambda n:not n or n.startswith('unconnected-') or len(members[n])==1 and sum(1 for v in nets.values() if v==n)==1
        if un(n4) and un(n6): continue
        if b4==b6=='GND': continue
        if b4==b6=='HRDB':
            if 'EXP0' in silk or 'EXP1' in silk:
                if not('HRDB' in silk): out.append(f'K22 {sym["ref"]}: pins 4 and 6 are HRDB but the silk says EXP0/EXP1')
            continue
        if (b4,b6)==('EXP1','EXP0'):
            if 'HRDB' in silk and not silk&{'EXP0','EXP1'}: out.append(f'K22 {sym["ref"]}: pins 4 and 6 are EXP1/EXP0 but the silk says HRDB')
            for n in(n4,n6):
                odd={r for r in members[n] if not re.match(r'(J|JP|P)\d',r)}
                if odd and (repo,board,rev) not in ACCEPT_EXP: out.append(f'K22 {sym["ref"]}: {n} reaches {sorted(odd)}, not only connectors and jumpers')
                # a jumper from EXP to HRDB
                for r in members[n]:
                    if r.startswith(('JP','J')) and any(nets.get((r,q),'').lstrip('/')=='HRDB' for (rr,q) in nets if rr==r):
                        if (repo,board) not in JUMPERS and (repo,board,rev) not in JUMPERS: out.append(f'K22 {r} joins {n} to HRDB: only the Memory Card keeps that jumper')
            continue
        out.append(f'K22 {sym["ref"]}: pins 4 and 6 are {b4 or "-"} and {b6 or "-"}, none of the allowed ways')
    return sorted(set(out))
if __name__=='__main__':
    bad=0;n=0
    for sch in files('Hardware/*/Rev */*.kicad_sch'):
        S=Sch(sch)
        if not any(busfix.is_conn(s) for s in S.symbols): continue
        n+=1;pcb=sch[:-4]+'_pcb'
        f=CACHE.get('sch '+digest(sch,*TOOLS,*([pcb] if os.path.exists(pcb) else [])),lambda sch=sch:faults(sch))
        for x in f: print(sch.split('/Hardware/')[-1],'|',x);bad+=1
    CACHE.save()
    print(f'{n} schematics, {bad} faults');sys.exit(1 if bad else 0)
