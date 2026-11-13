#!/usr/bin/env python3
"""Check every board revision against the standard. Read-only on the boards.
Usage: audit.py [--all] [out.json]. Writes Tools/work/audit.json in each repository it checks, or out.json if named.
Exports go to a temp folder; the KiCad files are never written."""
import re,os,sys,json,glob,math,subprocess,tempfile,zipfile,io,shutil,collections
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))));import common;from common import K,SCOPE,files,load,save
BASE=K;REPOS=['6502-'+r for r in SCOPE]
KC='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
HOLD5={'ACE Board','ACE CF Adapter','Keyboard Helper'}
# Cards and carts have no corner holes: what's near a corner is a connector's lug or a cart standoff.
NO_CORNERS={'Flash Cart','ROM Cart'}
# Revisions whose holes are old on purpose, because they are the boards that were made. Each has a Rev 1.1 at standard.
OLD_HOLES={('Clock Helper','1.0'),('DB25 Helper','1.0'),('GPIO Helper','1.0'),('Joystick Helper','1.0'),('Keyboard Encoder Helper','1.0'),('PS2 Helper','1.0'),('VERA Helper','1.0'),('Keypad LCD Helper','1.0')}
# Parity net conflicts reviewed 2026-11-04: the symbol has pins the footprint doesn't, not a wrong connection.
_args=[a for a in sys.argv[1:] if not a.startswith('--')]
OUT=os.path.abspath(_args[0]) if _args else None
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))));from cache import Cache,digest
CACHE=Cache('audit',os.path.abspath(__file__))  # DRC and zip comparisons, reused while their input files are unchanged  # before the chdir below
KNOWN_SILK={('ROM Cart','1.0a'):'1.0',('ROM Cart','1.0b'):'1.0'}  # as made: these boards say Rev 1.0, and U1's label tells them apart
KNOWN_TITLE={('CPU Card Pro','1.0'):'A.C. Wright Design / bahamutkotd'}  # a deliberate credit (owner, 2026-11-04)
KNOWN_UNCONNECTED={}
# Copper in the order that today's KiCad draws differently from the same file (2026-11-05). Every version in the file's history
# shows it. Keypad Helper: the zip has thermal spokes on the second row of pads, which KiCad 10 doesn't draw. Storage Card: 18
# segments differ in every version, and 24 come from the 2025-09-29 footprint refresh that changed pad shapes, accepted in P10.
KNOWN_COPPER={('Keypad Helper','1.0'):{'gtl':62,'gbl':35},('Storage Card','1.0'):{'gtl':42}}
KNOWN_NET={('DEV Output Board','1.0'):'Teensy back-side pads',('DEV Output Board','1.1'):'Teensy back-side pads',('VGA Card Pro','1.0'):'Pico pins 41-43',('Mega Helper','1.0'):'Arduino header pins',('Flash Helper','1.0'):'Arduino Mega pads with no symbol pin',('Backplane Pro','1.0'):'J2 shield pin',('DEV Board','1.0'):'J6 shield pads',('Main Board','1.0'):'J3 shield pads'}
def run(*a): return subprocess.run(a,capture_output=True)
def blocks(t,head):
    out=[]
    for m in re.finditer(r'\n\s*\('+head,t):
        j=t.index('(',m.start());d=0;k=j;q=False
        while k<len(t):
            c=t[k]
            if q:
                if c=='\\':k+=1
                elif c=='"':q=False
            elif c=='"':q=True
            elif c=='(':d+=1
            elif c==')':
                d-=1
                if d==0:break
            k+=1
        out.append(t[j:k+1])
    return out
def holes(t):
    xs=[];ys=[]
    for b in blocks(t,r'gr_(?:line|rect|arc|circle|poly)\b'):
        if 'Edge.Cuts' not in b: continue
        for m in re.finditer(r'\((?:start|end|mid|xy|center) ([\d.\-]+) ([\d.\-]+)\)',b): xs.append(float(m.group(1)));ys.append(float(m.group(2)))
    if not xs: return None,None,[]
    W,H=max(xs)-min(xs),max(ys)-min(ys);hs=[]
    for b in blocks(t,r'footprint "'):
        m=re.match(r'\(footprint "([^"]*)"',b);lib=m.group(1) if m else ''
        r=re.search(r'\(property "Reference" "([^"]*)"',b);ref=r.group(1) if r else '?'
        if not('MountingHole' in lib or re.fullmatch(r'H\d+',ref)): continue
        at=re.search(r'\n\s*\(at ([\d.\-]+) ([\d.\-]+)(?: ([\d.\-]+))?\)',b);fx,fy,rot=float(at.group(1)),float(at.group(2)),float(at.group(3) or 0);a=math.radians(rot)
        p=re.search(r'\(pad "[^"]*" (?:np_)?thru_hole \w+\s*\(at ([\d.\-]+) ([\d.\-]+)',b)
        if not p: continue
        x,y=float(p.group(1)),float(p.group(2));X=fx+x*math.cos(a)+y*math.sin(a);Y=fy-x*math.sin(a)+y*math.cos(a)
        hs.append((min(X-min(xs),max(xs)-X),min(Y-min(ys),max(ys)-Y)))
    return W,H,hs
def gerb(p):
    """lines and flash centres, ignoring aperture sizes; arcs and regions are not compared"""
    t=open(p,errors='replace').read();fs=1e6;x=y=0;s=set()
    for line in re.split(r'[\n*]+',t):
        line=line.strip().lstrip('%')
        m=re.match(r'FSLAX(\d)(\d)Y',line)
        if m: fs=10**int(m.group(2));continue
        m=re.match(r'(?:G0?1)?(?:X(-?\d+))?(?:Y(-?\d+))?D0?([123])$',line)
        if not m: continue
        nx=int(m.group(1))/fs if m.group(1) else x;ny=int(m.group(2))/fs if m.group(2) else y
        if m.group(3)=='1': s.add(('l',)+tuple(sorted(((round(x,2),round(y,2)),(round(nx,2),round(ny,2))))))
        elif m.group(3)=='3': s.add(('c',round(nx,2),round(ny,2)))
        x,y=nx,ny
    return s
def regions(p):
    """filled regions (G36/G37) as polygons"""
    t=open(p,errors='replace').read();fs=1e6;polys=[];cur=None;x=y=0
    for line in re.split(r'[\n*]+',t):
        line=line.strip().lstrip('%')
        m=re.match(r'FSLAX(\d)(\d)Y',line)
        if m: fs=10**int(m.group(2));continue
        if line.startswith('G36'): cur=[];continue
        if line.startswith('G37'):
            if cur: polys.append(cur)
            cur=None;continue
        m=re.match(r'(?:G0?1)?(?:X(-?\d+))?(?:Y(-?\d+))?D0?([12])$',line)
        if m:
            nx=int(m.group(1))/fs if m.group(1) else x;ny=int(m.group(2))/fs if m.group(2) else y
            if cur is not None: cur.append((nx,ny))
            x,y=nx,ny
    return polys
def off_copper(S,T,polys,tol=0.15):
    """the lines and flashes of S that lie on none of T's lines or flashes, nor inside one of polys"""
    import math
    def sd(p,a,b):
        (x,y),(x1,y1),(x2,y2)=p,a,b;dx,dy=x2-x1,y2-y1;L=dx*dx+dy*dy
        t=0 if L==0 else max(0,min(1,((x-x1)*dx+(y-y1)*dy)/L));return math.hypot(x-(x1+t*dx),y-(y1+t*dy))
    def inside(p,q):
        x,y=p;c=False
        for i in range(len(q)):
            (x1,y1),(x2,y2)=q[i],q[(i+1)%len(q)]
            if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
        return c
    segs=[s for s in T if s[0]=='l'];fl=[s for s in T if s[0]=='c'];grid=collections.defaultdict(list)
    for s in segs:
        (a,b)=s[1],s[2]
        for gx in range(int(min(a[0],b[0])//2)-1,int(max(a[0],b[0])//2)+2):
            for gy in range(int(min(a[1],b[1])//2)-1,int(max(a[1],b[1])//2)+2): grid[(gx,gy)].append(s)
    out=[]
    for s in S:
        pts=[(s[1],s[2])] if s[0]=='c' else [s[1],s[2],((s[1][0]+s[2][0])/2,(s[1][1]+s[2][1])/2)]
        for p in pts:
            if s[0]=='c' and any(abs(p[0]-f[1])<=tol and abs(p[1]-f[2])<=tol for f in fl): continue
            if s[0]=='l' and any(sd(p,c[1],c[2])<=tol for c in grid[(int(p[0]//2),int(p[1]//2))]): continue
            if any(inside(p,q) for q in polys): continue
            out.append(s);break
    return out
def drill(p):
    s=set();u=25.4 if re.search(r'^INCH',open(p,errors='replace').read(),re.M) else 1.0
    for l in open(p,errors='replace'):
        # slots are written two ways: X..Y..G85X..Y.. on one line (KiCad 10) or G00/G01 over several (older)
        if l.startswith(('X','G00','G01','G0X','G1X')):
            for m in re.finditer(r'X(-?[\d.]+)Y(-?[\d.]+)',l): s.add((round(float(m.group(1))*u,1),round(float(m.group(2))*u,1)))
    return s
FF=(('Copper,L1','F.Cu'),('Copper,L2','B.Cu'))
def zip_vs_pcb(zp,pcb):
    d=tempfile.mkdtemp();out={}
    try:
        run(KC,'pcb','export','gerbers','-o',d+'/','--layers','F.Cu,B.Cu',pcb);run(KC,'pcb','export','drill','--excellon-separate-th','-o',d+'/',pcb)
        z=zipfile.ZipFile(zp);n={x.lower().rsplit('.',1)[-1]+('n' if 'NPTH' in x else ''):x for x in z.namelist() if not x.endswith('map.gbr')}
        for f in os.listdir(d):
            p=os.path.join(d,f)
            if f.endswith('.drl'):
                k='drln' if 'NPTH' in f else 'drl'
                if k in n:
                    # within 0.05 mm: old drill files are in inches, and rounding must not count as a move
                    q=os.path.join(d,'z'+k);open(q,'wb').write(z.read(n[k]));a,b=drill(p),drill(q)
                    near=lambda P,Q:sum(1 for x in P if not any(abs(x[0]-c[0])<=0.15 and abs(x[1]-c[1])<=0.15 for c in Q))
                    out[k]=near(a,b)+near(b,a)
            elif f.endswith(('.gbr','.gtl','.gbl')):
                # KiCad names these .gtl and .gbl; until 2026-11-05 only .gbr was read, so copper was never compared
                ff=re.search(r'FileFunction,([^*]+)',open(p,errors='replace').read(2000))
                k='gtl' if f.endswith('.gtl') or (ff and ff.group(1).startswith('Copper,L1')) else 'gbl' if f.endswith('.gbl') or (ff and ff.group(1).startswith('Copper,L2')) else None
                if k and k in n:
                    q=os.path.join(d,'z'+k);open(q,'wb').write(z.read(n[k]));a,b=gerb(p),gerb(q)
                    # copper that is in one file and not on the other's copper: the other's lines, flashes or filled regions,
                    # within 0.15 mm. Arcs split into different segments, and zone fills drawn as strokes, are the same copper.
                    out[k]=len(off_copper(a-b,b,regions(q)))+len(off_copper(b-a,a,regions(p)))
    finally: shutil.rmtree(d,ignore_errors=True)
    return out
rows=[]
for repo in REPOS:
    R=BASE+repo;os.chdir(R)
    revs=collections.defaultdict(list);_o=json.load(open('Tools/data/orders.json'));ORD=set(_o['made'])|set(_o['ordered'])
    for f in glob.glob('Hardware/*/Rev */*.kicad_pcb'):
        n=f.split('/');revs[n[1]].append((n[2],f))
    for board,lst in sorted(revs.items()):
        newest=sorted(lst,key=lambda x:[int(v) if v.isdigit() else v for v in re.findall(r'\d+|[a-z]+',x[0][4:])])[-1][0]
        for rev,f in sorted(lst):
            v=rev[4:];I=[];t=open(f,errors='replace').read();sf=f[:-4]+'_sch'
            s=open(sf,errors='replace').read() if os.path.exists(sf) else ''
            r=dict(repo=repo[5:],board=board,rev=v,newest=rev==newest)
            for lab,p in (('schematic',sf),('schematic PDF',f'Schematics/{board}/{rev}/{board}.pdf'),('front image',f'CAD/Images/{board}/{rev}/Front.png'),('back image',f'CAD/Images/{board}/{rev}/Back.png'),('STEP',f'CAD/Models/{board}/{rev}/{board}.step')):
                if not os.path.exists(p): I.append('no '+lab)
            zs=[x for x in glob.glob(f'Production/{board}/{rev}/*.zip')]
            if not zs: I.append('no production zip')
            for x in('designators.csv','positions.csv','netlist.ipc'):
                if not os.path.exists(f'Production/{board}/{rev}/{x}'): I.append('no '+x)
            for lab,tx in (('PCB',t),('schematic',s)):
                m=re.search(r'\(rev "([^"]*)"',tx)
                if not m: I.append(f'{lab} title block has no rev')
                elif m.group(1)!=v: I.append(f'{lab} title says rev {m.group(1)}')
                c=re.search(r'\(company "([^"]*)"',tx)
                if not c or c.group(1)!=KNOWN_TITLE.get((board,v),'A.C. Wright Design'): I.append(f'{lab} company {c.group(1) if c else "missing"!r}')
            silk=[re.sub(r'\s+',' ',m.group(1)) for b in blocks(t,r'gr_text "') for m in [re.match(r'\(gr_text "([^"]*)"',b)] if m and re.search(r'\(layer "?[FB]\.Silk',b)]
            lab=[x for x in silk if re.search(r'Rev ?\d',x)]
            r['silk_label']=lab[0] if lab else None
            if not lab: I.append('no revision on silk')
            elif not re.search(r'Rev ?'+re.escape(KNOWN_SILK.get((board,v),v))+r'\b',lab[0]): I.append('silk says '+re.search(r'Rev ?[\d.a-z]+',lab[0]).group(0))
            if lab and 'A.C. Wright Design' not in lab[0]: I.append('silk copyright: '+lab[0][:40])
            # JLCPCB stopped printing order numbers in May 2026 and asks for no JLCJLCJLCJLC on the silk. Made boards keep theirs.
            if 'JLCJLCJLCJLC' in t and f'{repo[5:]}|{board}|{v}' not in ORD: I.append('JLCPCB order-number marker on the silk')
            W,H,hs=holes(t);r['size']=(round(W,2),round(H,2)) if W else None
            corner=[h for h in hs if h[0]<=9 and h[1]<=9]
            r['corner']=sorted({(round(a,2),round(b,2)) for a,b in corner})
            cardlike=board in NO_CORNERS or (H and abs(H-57.62)<0.1)
            if corner and not cardlike and (board,v) not in OLD_HOLES:
                want=5 if board in HOLD5 else 6
                off=[h for h in corner if abs(h[0]-want)>0.1 or abs(h[1]-want)>0.1]
                if off: I.append(f'holes not at {want} mm')
            def drc_run(f=f):
                rp=tempfile.mktemp(suffix='.json');run(KC,'pcb','drc','--schematic-parity','--severity-all','--format','json','-o',rp,f)
                d=json.load(open(rp));os.remove(rp)
                return dict(parity=dict(collections.Counter(x['type'] for x in d['schematic_parity'])),unconnected=len(d['unconnected_items']),drc=dict(collections.Counter(x['type'] for x in d['violations'] if x.get('severity')=='error' and not x.get('excluded'))))
            try:
                pdir=os.path.dirname(f);dd=CACHE.get('drc '+digest(f,sf,*sorted(glob.glob(pdir+'/*.kicad_pro')+glob.glob(pdir+'/*.kicad_dru'))),drc_run)
                p=collections.Counter(dd['parity']);r['parity']=dict(p);r['unconnected']=dd['unconnected'];r['drc']=dd['drc']
                if (board,v) in KNOWN_NET and set(p)<={'net_conflict'}: r['known']=KNOWN_NET[(board,v)];p=collections.Counter()
                if sum(p.values()): I.append('parity: '+', '.join(f'{k.replace("footprint_symbol_","").replace("_"," ")} {n}' for k,n in p.items()))
                ku=KNOWN_UNCONNECTED.get((board,v))
                if ku and r['unconnected']==ku[0]: r['note']=ku[1]
                elif r['unconnected']: I.append(f'{r["unconnected"]} unconnected')
                if r['drc']: I.append('DRC errors: '+', '.join(f'{k} {n}' for k,n in r['drc'].items()))
            except Exception as e: I.append('DRC failed')
            if zs:
                g=CACHE.get('zip '+digest(zs[0],f),lambda:zip_vs_pcb(zs[0],f));r['zip_vs_pcb']=g
                b={k:n for k,n in g.items() if n}
                kc=KNOWN_COPPER.get((board,v))
                if kc and b=={k:n for k,n in kc.items()}: r['note']=((r.get('note')+'; ') if r.get('note') else '')+'copper drawn differently by today\'s KiCad, as recorded in audit.py';b={}
                if b: I.append('zip differs from PCB: '+', '.join(f'{k} {n}' for k,n in b.items()))
                if not re.search(r'_'+re.escape(v)+r'\.zip$',zs[0]): I.append('zip name '+os.path.basename(zs[0]))
            r['issues']=I;rows.append(r);print(repo[5:],board,v,len(I),flush=True,file=sys.stderr)
if OUT: json.dump(rows,open(OUT,'w'),indent=1)
else: save('audit.json',rows,repos=SCOPE)
CACHE.save();print(f'cache: {CACHE.hits} reused, {CACHE.misses} computed',file=sys.stderr)
