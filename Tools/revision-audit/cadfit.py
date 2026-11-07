#!/usr/bin/env python3
"""Which board revisions does each top panel or enclosure top fit? Read-only.
A top fits when every corner mounting hole of the board lands on one of the top's M3 holes, under some rotation,
mirror and translation. Prints JSON to stdout with --json."""
import re,os,glob,math,subprocess,sys,json
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'audit.py')).read().split('def gerb(p):')[0])
def pcb_holes(f):
    t=open(f,errors='replace').read();W,H,_=holes(t)
    xs=[];ys=[]
    for b in blocks(t,r'gr_(?:line|rect|arc|circle|poly)\b'):
        if 'Edge.Cuts' not in b: continue
        for m in re.finditer(r'\((?:start|end|mid|xy|center) ([\d.\-]+) ([\d.\-]+)\)',b): xs.append(float(m.group(1)));ys.append(float(m.group(2)))
    if not xs: return None
    out=[]
    for b in blocks(t,r'footprint "'):
        m=re.match(r'\(footprint "([^"]*)"',b);lib=m.group(1) if m else ''
        r=re.search(r'\(property "Reference" "([^"]*)"',b);ref=r.group(1) if r else '?'
        if not('MountingHole' in lib or re.fullmatch(r'H\d+',ref)): continue
        at=re.search(r'\n\s*\(at ([\d.\-]+) ([\d.\-]+)(?: ([\d.\-]+))?\)',b);fx,fy,rot=float(at.group(1)),float(at.group(2)),float(at.group(3) or 0);a=math.radians(rot)
        p=re.search(r'\(pad "[^"]*" (?:np_)?thru_hole \w+\s*\(at ([\d.\-]+) ([\d.\-]+)',b)
        if not p: continue
        x,y=float(p.group(1)),float(p.group(2));X=fx+x*math.cos(a)+y*math.sin(a);Y=fy-x*math.sin(a)+y*math.cos(a)
        d=(min(X-min(xs),max(xs)-X),min(Y-min(ys),max(ys)-Y))
        if d[0]<=9 and d[1]<=9: out.append((X,Y))
    return out
def svg_holes(s):
    vb=re.search(r'viewBox="(-?[\d.]+) (-?[\d.]+) ([\d.]+) ([\d.]+)"',s);w=re.search(r'\bwidth="([\d.]+)(cm|mm|in)"',s)
    k=1.0
    if vb and w: k=float(w.group(1))*{'cm':10,'mm':1,'in':25.4}[w.group(2)]/float(vb.group(3))
    hs=[]
    for m in re.finditer(r'd="M(-?[\d.]+),(-?[\d.]+) a([\d.]+),[\d.]+ 0 1,1',s):
        x,y,r=map(float,m.groups());hs.append(((x+r)*k,y*k,2*r*k))
    for m in re.finditer(r'<circle\b[^>]*>',s):
        g=lambda a:re.search(r'\b'+a+r'="(-?[\d.]+)',m.group(0))
        if g('cx') and g('cy') and g('r'): hs.append((float(g('cx').group(1))*k,float(g('cy').group(1))*k,2*float(g('r').group(1))*k))
    return [(x,y) for x,y,d in hs if 2.4<=d<=4.2]
def fits(top,board,tol=0.3):
    if not board: return None
    if not top: return False
    best=0;
    for sw in(0,1):
        for sx in(1,-1):
            for sy in(1,-1):
                B=[((y*sx,x*sy) if sw else (x*sx,y*sy)) for x,y in board]
                for tx,ty in top:
                    ox,oy=tx-B[0][0],ty-B[0][1]
                    n=sum(1 for bx,by in B if any(math.hypot(bx+ox-a,by+oy-c)<=tol for a,c in top));best=max(best,n)
    return best==len(board)
if __name__=='__main__':
    R={}
    for repo in REPOS:
        os.chdir(BASE+repo);revs={}
        for f in glob.glob('Hardware/*/Rev */*.kicad_pcb'):
            n=f.split('/');revs.setdefault(n[1].lower(),[]).append((n[1],n[2],f))
        items=[(os.path.basename(f)[:-8],'Tops',f) for f in glob.glob('CAD/Tops/*Top.svg')]+[(f.split('/')[-2],'Enclosures',f) for f in glob.glob('CAD/Enclosures/*/Top.svg')]
        for name,kind,f in sorted(items):
            s=open(f,errors='replace').read();h=svg_holes(s);rows=[]
            for B,rev,p in sorted(revs.get(name.lower(),[])):
                c=pcb_holes(p);rows.append((rev,fits(h,c),len(c) if c else 0))
            R[f'{repo}:{kind}:{name}']=dict(holes=len(h),revs=rows)
            print(f'{repo[5:]} {kind:10} {name:26} {len(h)} M3 holes | '+'; '.join(f"{r}: {'fits' if v else ('no corner holes' if v is None else 'NO')} ({n})" for r,v,n in rows) if rows else f'{repo[5:]} {kind:10} {name:26} {len(h)} M3 holes | NO BOARD IN THIS REPO')
    if '--json' in sys.argv: json.dump(R,open('/tmp/x','w'))
