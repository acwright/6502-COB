"""Reading and writing KiCad 10 schematics as text: top-level items, symbols and their pin positions, and the
wires, labels and flags attached to each pin. Shared by busfix.py and the connector check."""
import re,math,uuid as _uuid
R=lambda v:round(v,3)
def blk(t,i):
    d=0;j=i
    while True:
        c=t[j]
        if c=='"':
            j+=1
            while t[j]!='"': j+=2 if t[j]=='\\' else 1
        elif c=='(':d+=1
        elif c==')':
            d-=1
            if d==0:return j+1
        j+=1
BUS=['GND','VCC','RESB','EXP1','IRQB','EXP0','NMIB','A15','RDY','A14','BE','A13','RWB','A12','SYNC','A11','PHI2','A10',
     'EXP3','A9','EXP2','A8','D7','A7','D6','A6','D5','A5','D4','A4','D3','A3','D2','A2','D1','A1','D0','A0','VCC','GND']
SIG=set(BUS)|{'HRDB','5V'}
def shape(n):
    if re.fullmatch(r'A\d+|RWB|SYNC|PHI2',n): return 'output'
    if re.fullmatch(r'D\d|EXP\d|HRDB',n): return 'bidirectional'
    if n in('RESB','IRQB','NMIB','RDY','BE'): return 'input'
    if n in('VCC','GND','5V'): return 'passive'
class Sch:
    def __init__(s,path):
        s.path=path;s.t=open(path,encoding='utf-8',newline='').read();s.parse()
    def items(s):
        """(kind, start, end) of every top-level item; start is the newline before it"""
        out=[]
        for m in re.finditer(r'\n\t\((\w+)',s.t):
            st=m.start()+2;out.append((m.group(1),m.start(),blk(s.t,st)))
        return out
    def parse(s):
        t=s.t;s.libpins={}
        ls=t.index('\n\t(lib_symbols');le=blk(t,ls+2);L=t[ls:le]
        for m in re.finditer(r'\n\t\t\(symbol "([^"]*)"',L):
            st=m.start()+3;b=L[st:blk(L,st)];pins={}
            for pm in re.finditer(r'\(pin (\w+) \w+\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)\s*\(length ([-\d.]+)\)[\s\S]*?\(name "([^"]*)"[\s\S]*?\(number "([^"]*)"',b):
                pins[pm.group(7)]=dict(x=float(pm.group(2)),y=float(pm.group(3)),a=float(pm.group(4)),name=pm.group(6),type=pm.group(1))
            s.libpins[m.group(1)]=pins
        s.wires=[];s.labels=[];s.ncs=[];s.junctions=[];s.entries=[];s.buses=[];s.symbols=[];s.texts=[]
        for k,a,e in s.items():
            b=t[a+2:e]
            u=re.findall(r'\n\t\t\(uuid "([^"]*)"',b);u=u[0] if u else None
            if k=='wire' or k=='bus':
                p=[(R(float(x)),R(float(y))) for x,y in re.findall(r'\(xy ([-\d.]+) ([-\d.]+)\)',b)]
                (s.wires if k=='wire' else s.buses).append(dict(p=p,a=a,e=e,uuid=u))
            elif k=='bus_entry':
                at=re.search(r'\(at ([-\d.]+) ([-\d.]+)\)',b);sz=re.search(r'\(size ([-\d.]+) ([-\d.]+)\)',b)
                x,y=float(at.group(1)),float(at.group(2));dx,dy=float(sz.group(1)),float(sz.group(2))
                s.entries.append(dict(p=[(R(x),R(y)),(R(x+dx),R(y+dy))],a=a,e=e,uuid=u))
            elif k in('no_connect','junction'):
                at=re.search(r'\(at ([-\d.]+) ([-\d.]+)',b);(s.ncs if k=='no_connect' else s.junctions).append(dict(p=(R(float(at.group(1))),R(float(at.group(2)))),a=a,e=e,uuid=u))
            elif k in('label','global_label','hierarchical_label'):
                n=re.match(r'\((?:global_|hierarchical_)?label "([^"]*)"',b).group(1);at=re.search(r'\(at ([-\d.]+) ([-\d.]+) ?([-\d.]*)\)',b)
                sh=re.search(r'\(shape (\w+)\)',b)
                s.labels.append(dict(kind=k,name=n,p=(R(float(at.group(1))),R(float(at.group(2)))),rot=float(at.group(3) or 0),shape=sh.group(1) if sh else None,a=a,e=e,uuid=u))
            elif k=='symbol':
                lid=re.search(r'\(lib_id "([^"]*)"',b).group(1);at=re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)',b)
                ref=re.search(r'\(property "Reference" "([^"]*)"',b).group(1);val=re.search(r'\(property "Value" "([^"]*)"',b).group(1)
                mir=re.search(r'\n\t\t\(mirror (\w)\)',b)
                s.symbols.append(dict(lib=lid,ref=ref,value=val,X=float(at.group(1)),Y=float(at.group(2)),rot=float(at.group(3)),mirror=mir.group(1) if mir else '',a=a,e=e,uuid=u))
            elif k=='text':
                s.texts.append(dict(a=a,e=e,body=b))
    def pins(s,sym):
        """pin number -> (point, outward unit vector, name)"""
        out={}
        for num,p in s.libpins.get(sym['lib'],{}).items():
            x,y=p['x'],-p['y'];ang=math.radians(p['a']);dx,dy=-math.cos(ang),math.sin(ang)  # the pin points into the body at angle a
            r=math.radians(-sym['rot']);c,sn=math.cos(r),math.sin(r)   # KiCad rotates, then mirrors
            x,y,dx,dy=x*c-y*sn,x*sn+y*c,dx*c-dy*sn,dx*sn+dy*c
            if sym['mirror']=='x': y=-y;dy=-dy
            if sym['mirror']=='y': x=-x;dx=-dx
            X=sym['X']+x;Y=sym['Y']+y;DX=dx;DY=dy
            out[num]=((R(X),R(Y)),(round(DX),round(DY)),p['name'])
        return out
    def all_pin_points(s):
        pts={}
        for sym in s.symbols:
            for num,(P,d,n) in s.pins(sym).items(): pts.setdefault(P,[]).append((sym,num))
        return pts
def on_seg(q,a,b):
    (x,y),(x1,y1),(x2,y2)=q,a,b
    if abs((x2-x1)*(y-y1)-(y2-y1)*(x-x1))>1e-6: return False
    return min(x1,x2)-1e-6<=x<=max(x1,x2)+1e-6 and min(y1,y2)-1e-6<=y<=max(y1,y2)+1e-6
def new_uuid(key): return str(_uuid.uuid5(_uuid.NAMESPACE_URL,'ac6502/schematic/'+key))

def seg_touch(p1,p2,q1,q2):
    """would KiCad connect two wires: an end of one on the other. Wires that only cross don't connect."""
    return on_seg(p1,q1,q2) or on_seg(p2,q1,q2) or on_seg(q1,p1,p2) or on_seg(q2,p1,p2)
def seg_cross(p1,p2,q1,q2):
    """do two segments share any point"""
    def o(a,b,c):
        v=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
        return 0 if abs(v)<1e-9 else (1 if v>0 else -1)
    a,b,c,d=o(p1,p2,q1),o(p1,p2,q2),o(q1,q2,p1),o(q1,q2,p2)
    if a!=b and c!=d: return True
    return (a==0 and on_seg(q1,p1,p2)) or (b==0 and on_seg(q2,p1,p2)) or (c==0 and on_seg(p1,q1,q2)) or (d==0 and on_seg(p2,q1,q2))
