#!/usr/bin/env python3
"""Run busfix.py on schematics and prove nothing electrical changed.

  verify.py SCHEMATIC... [--dry]

For each schematic: the netlist before and after (kicad-cli), compared as groups of pins; the ERC before and after;
and the net renames the PCB needs, written to <schematic>.renames.json beside nothing (printed only)."""
import sys,os,re,json,subprocess,tempfile,collections,glob
H=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,H)
import busfix
KC='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def netlist(sch):
    o=tempfile.mktemp(suffix='.net');subprocess.run([KC,'sch','export','netlist','-o',o,sch],capture_output=True)
    t=open(o).read();os.remove(o);t=t[t.index('(nets'):];pm={}
    for part in re.split(r'\n\t\t\(net\n',t)[1:]:
        name=re.search(r'\(name "([^"]*)"',part).group(1)
        for r,p in re.findall(r'\(ref "([^"]*)"\)\s*\(pin "([^"]*)"',part): pm[(r,p)]=name
    return pm
def erc(sch):
    o=tempfile.mktemp(suffix='.json');subprocess.run([KC,'sch','erc','--format','json','-o',o,sch],capture_output=True)
    d=json.load(open(o));os.remove(o)
    return collections.Counter(v['type'] for s in d['sheets'] for v in s['violations'])
def groups(pm):
    g=collections.defaultdict(set)
    for k,n in pm.items(): g[n].add(k)
    return {frozenset(v):n for n,v in g.items()}
def silk_names(sch):
    pcb=sch[:-4]+'_pcb'
    if not os.path.exists(pcb): return False
    t=open(pcb,errors='replace').read()
    return len(set(re.findall(r'\(gr_text "(A1[0-5]|RESB|SYNC|D[0-7])"',t)))>=3
def run(sch,dry=False):
    before=netlist(sch);e0=erc(sch)
    log=busfix.main(sch,before,dry=dry,keep_nc_header=not silk_names(sch))
    if dry: return dict(log=log)
    after=netlist(sch);e1=erc(sch)
    gb,ga=groups(before),groups(after)
    same=set(gb)==set(ga)
    ren={gb[k]:ga[k] for k in gb if k in ga and gb[k]!=ga[k]}
    return dict(log=log,connectivity='identical' if same else 'CHANGED',lost=[sorted(k)[:4] for k in set(gb)-set(ga)][:5],
                gained=[sorted(k)[:4] for k in set(ga)-set(gb)][:5],renames=ren,erc_before=dict(e0),erc_after=dict(e1))
if __name__=='__main__':
    dry='--dry' in sys.argv
    for s in [a for a in sys.argv[1:] if not a.startswith('--')]:
        r=run(s,dry);print(json.dumps({'file':s.split('Hardware/')[-1],**r},default=str))
