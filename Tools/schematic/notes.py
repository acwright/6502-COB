#!/usr/bin/env python3
"""KICAD.md K22: a note by each bus connector whose pins 4 and 6 are EXP1/EXP0 or tied to GND, saying what HRDB
does with them. Schematic text only. Run again and it changes nothing.

  notes.py SCHEMATIC..."""
import sys,os,re,math,json,subprocess,tempfile
H=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,H)
from sch import *
import busfix,check
PASS=('EXP0 and EXP1 carry HRDB (High ROM disable bar) in a build that uses cartridges:\n'
      'a cartridge grounds them to take $C000-$FFFF from the ROM. They are free only in\n'
      'a build that never uses cartridges. EXP2 and EXP3 are always free.')
CART=('Pins 4 and 6 (EXP1, EXP0) ground HRDB (High ROM disable bar),\n'
      'which takes $C000-$FFFF from the ROM.')
TEXT='''
	(text "{t}"
		(exclude_from_sim no)
		(at {x} {y} 0)
		(effects
			(font
				(size 1.27 1.27)
			)
			(justify left bottom)
		)
		(uuid "{u}")
	)'''
def esc(s): return s.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')
def bbox_items(S):
    """rough boxes of what is drawn: wires, labels, symbol bodies from their pins, texts"""
    out=[]
    for w in S.wires: (x1,y1),(x2,y2)=w['p'][0],w['p'][-1];out.append((min(x1,x2)-1,min(y1,y2)-1,max(x1,x2)+1,max(y1,y2)+1))
    for l in S.labels:
        x,y=l['p'];n=len(l['name'])*1.3+3;r=l['rot']
        out.append((x-n,y-1.5,x,y+1.5) if r==180 else (x,y-1.5,x+n,y+1.5) if r==0 else (x-1.5,y-n,x+1.5,y+n))
    for s in S.symbols:
        ps=[p for p,d,n in S.pins(s).values()] or [(s['X'],s['Y'])]
        xs=[p[0] for p in ps];ys=[p[1] for p in ps]
        out.append((min(xs)-2,min(ys)-6,max(xs)+2,max(ys)+6))
        body=S.t[s['a']:s['e']]
        for m in re.finditer(r'\(property "[^"]*" "((?:[^"\\]|\\.)*)"\s*\(at ([-\d.]+) ([-\d.]+)',body):
            blk_=body[m.start():m.start()+400]
            if '(hide yes)' in blk_.split('(property',2)[1] if blk_.count('(property')>1 else '(hide yes)' in blk_: continue
            x,y=float(m.group(2)),float(m.group(3));n=len(m.group(1))*1.3
            out.append((x-n,y-1.5,x+n,y+1.5))
    for t in S.texts:
        m=re.search(r'\(at ([-\d.]+) ([-\d.]+)',t['body']);s=re.match(r'\(text "((?:[^"\\]|\\.)*)"',t['body'])
        if m and s:
            x,y=float(m.group(1)),float(m.group(2));lines=s.group(1).split('\\n')
            out.append((x,y-2.6*len(lines),x+max(len(l) for l in lines)*1.3,y+0.5))
    return out
def free(box,items): return not any(box[0]<b[2] and b[0]<box[2] and box[1]<b[3] and b[1]<box[3] for b in items)
PAPER={'A4':(297,210),'A3':(420,297),'USLetter':(279.4,215.9),'USLedger':(431.8,279.4)}
def page(t):
    m=re.search(r'\(paper "([^"]+)"(?: ([\d.]+) ([\d.]+))?( portrait)?\)',t)
    w,h=(float(m.group(2)),float(m.group(3))) if m.group(2) else PAPER.get(m.group(1),(279.4,215.9))
    return (w,h) if not m.group(4) else (h,w)
def place(path,which,replace=False):
    S=Sch(path);t=S.t
    if 'High ROM disable bar' in t:
        if not replace: return 'already'
        u=new_uuid(path+'k22-note');i=t.index(f'(uuid "{u}")');s=t.rfind('\n\t(text ',0,i);e=blk(t,s+2)
        t=t[:s]+t[e:];open(path,'w',encoding='utf-8',newline='').write(t);S=Sch(path)
    con=[s for s in S.symbols if busfix.is_conn(s)][0]
    ps=[p for p,d,n in S.pins(con).values()];xs=[p[0] for p in ps];ys=[p[1] for p in ps]
    txt=PASS if which=='pass' else CART;lines=txt.split('\n');w=max(len(l) for l in lines)*1.3;h=2.6*len(lines)
    items=bbox_items(S);g=lambda v:round(v/1.27)*1.27
    x0=g(min(xs)-15);W,Hh=page(t)
    cands=[(x0,g(max(ys)+12+h)),(x0,g(min(ys)-14)),(g(max(xs)+20),g(min(ys)+h)),(g(min(xs)-25-w),g(min(ys)+h))]
    cx,cy=(min(xs)+max(xs))/2,(min(ys)+max(ys))/2
    grid=[(g(x),g(y)) for x in [12+2.54*i for i in range(int((W-24)/2.54))] for y in [12+h+2.54*j for j in range(int((Hh-24-h)/2.54))]]
    cands+=sorted(grid,key=lambda q:math.dist((q[0]+w/2,q[1]-h/2),(cx,cy)))
    inside=lambda x,y:x>=12 and x+w<=W-12 and y-h>=12 and y<=Hh-12 and not(x+w>W-125 and y>Hh-45)
    for x,y in cands:
        if inside(x,y) and free((x-1,y-h-1,x+w+1,y+1),items): break
    else: return 'NO ROOM'
    u=new_uuid(path+'k22-note')
    item=TEXT.format(t=esc(txt),x=busfix.fmt(x),y=busfix.fmt(y),u=u)
    m=re.search(r'\n\t\(sheet_instances',t) or re.search(r'\n\t\(embedded_fonts',t)
    pos=m.start() if m else t.rstrip().rfind(')')
    open(path,'w',encoding='utf-8',newline='').write(t[:pos]+item+t[pos:])
    return f'placed at {x:.2f},{y:.2f}'
def kind(path):
    """'pass' when a connector's pins 4 and 6 are EXP1/EXP0, 'cart' when tied to GND, else None"""
    nets=check.netlist(path);S=Sch(path)
    for sym in S.symbols:
        if not busfix.is_conn(sym): continue
        card=sym['lib']==busfix.CARD;p4,p6=('EXP1','EXP0') if card else ('4','6')
        n4,n6=nets.get((sym['ref'],p4),'').lstrip('/'),nets.get((sym['ref'],p6),'').lstrip('/')
        if (n4,n6)==('EXP1','EXP0'): return 'pass'
        if n4==n6=='GND': return 'cart'
    return None
if __name__=='__main__':
    rp='--replace' in sys.argv
    for p in [a for a in sys.argv[1:] if not a.startswith('--')]:
        k=kind(p);print(p.split('/Hardware/')[-1],k,place(p,k,rp) if k else '-')
