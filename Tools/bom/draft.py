#!/usr/bin/env python3
"""First draft of the parts catalogue, read from every schematic: which real part each symbol is, and every
supplier number the repos give it today. Read-only: python3 draft.py [out.json]"""
import re,os,glob,json,collections,sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))));import common;from common import K,SCOPE,files,load,save
def block(t,i):
    d=0;j=i
    while True:
        c=t[j]
        if c=='"':
            j+=1
            while t[j]!='"': j+=2 if t[j]=='\\' else 1
        elif c=='(':d+=1
        elif c==')':
            d-=1
            if d==0:return t[i:j+1]
        j+=1
def parts():
    for repo in SCOPE:
        for f in sorted(glob.glob(f'{K}6502-{repo}/Hardware/*/Rev */*.kicad_sch')):
            t=open(f,errors='replace').read();seen=set();b=f.split('/')[-3];v=f.split('/')[-2][4:]
            for m in re.finditer(r'\n\t\(symbol\n\t\t\(lib_id "([^"]+)"',t):
                x=block(t,m.start()+1);P=dict(re.findall(r'\(property "([^"]+)" "((?:[^"\\]|\\.)*)"',x));rr=re.findall(r'\(reference "([^"]+)"',x);ref=rr[0] if rr else P.get('Reference','')
                if ref.startswith('#') or ref in seen: continue
                seen.add(ref);dnp=re.search(r'\(dnp yes\)',x) is not None
                yield dict(repo=repo,board=b,rev=v,ref=ref,lib=m.group(1),val=P.get('Value',''),fp=P.get('Footprint','').split(':')[-1],f=P,dnp=dnp)
def norm_val(v):
    v=v.strip();m=re.match(r'^([\d.]+)\s*([kKM]?)(?:Ω|ohm|R)?$',v)
    if m and m.group(2): return m.group(1)+{'K':'k','k':'k','M':'M'}[m.group(2)]
    v=v.replace('µ','u').replace('Mhz','MHz')
    v=re.sub(r'^([\d.]+)\s*MHz$',r'\1 MHz',v)
    return v
def classify(p):
    """(id, description): the real part, whatever its label on this board."""
    fp,v=p['fp'],norm_val(p['val']);ref=p['ref']
    if re.match(r'^(TP|JP|H\d|G\*|REF|LOGO)',ref) or 'SolderJumper' in fp or 'TestPoint' in fp or fp.startswith('MountingHole') or 'Logo' in fp or 'CARDEDGE' in fp or 'Card Edge' in fp or 'CardEdge' in fp: return None
    m=re.match(r'SW_Cherry_MX_([\d.]+)u',fp)
    if m: return ('keyswitch-mx','Cherry MX compatible keyswitch, PCB mount')
    m=re.match(r'(PinHeader|PinSocket)_(\d+)x(\d+)_P([\d.]+)mm_(\w+)',fp)
    if m: return (f"{m.group(1).lower()}-{m.group(2)}x{m.group(3)}-{m.group(4)}-{m.group(5).lower()}",f"{'Pin header' if m.group(1)=='PinHeader' else 'Pin socket'} {m.group(2)}×{m.group(3)}, {m.group(4)} mm, {m.group(5).lower()}")
    if fp=='6502 GPIO Connector': return ('conn-gpio','GPIO connector, shrouded 2×6 header')
    if fp in('6502 Bus Connector',): return ('conn-bus','6502 bus connector, 2×20 header')
    if fp.startswith('RHDR40W82'): return ('conn-card-edge','6502 card connector, 2×20 card edge socket')
    if fp.startswith('JST_XH_B2B-XH-A_1x02'): return ('jst-xh-2','JST XH 2-pin header')
    if fp.startswith('LED_0805'):
        col={'C2297':'green','C2296':'yellow','C2295':'red','C2293':'blue'}.get(p['f'].get('LCSC',''),'green')
        return ('led-0805-'+col,'LED, 0805, '+col)
    if fp.startswith('LED_D3.0'): return ('led-3mm-'+('red' if re.search('POWER',v) else 'any'),'LED, 3 mm')
    if fp.startswith('SW_PUSH_6mm'): return ('sw-tact-6mm','Tactile switch, 6 mm')
    if fp.startswith('SW_TS-1187'): return ('sw-tact-smd','Tactile switch, SMD, TS-1187A')
    if fp=='XKB5858':
        w='W' in p['f'].get('LCSC','').split('-')[-1]
        return ('sw-xkb5858-w','Push switch, XKB5858-W, momentary') if w else ('sw-xkb5858-z','Push switch, XKB5858-Z, latching')
    if fp.startswith('SWITCHCRAFT_'):
        n=re.search(r'PJRAN1X1U0(\d)X',(p['f'].get('Digikey') or '')+(p['f'].get('Mouser') or ''))
        j=f'pjran1x1u0{n.group(1)}x' if n else fp.split('_')[1].lower()
        return ('jack-'+j,'RCA jack, '+j.upper())
    if fp.startswith('DSUB-9_Pins'): return ('dsub9-male-ra','DB-9 male, right angle')
    if fp.startswith('DSUB-9_Socket'): return ('dsub9-female-ra','DB-9 female, right angle')
    if fp.startswith('DSUB-25_Pins'): return ('dsub25-male-ra','DB-25 male, right angle')
    if fp.startswith('DSUB-15-HD'): return ('vga-hd15-ra','VGA HD-15 female, right angle')
    if fp=='KMDGX-6S-BS': return ('minidin6','6-pin mini-DIN, PS/2')
    if fp.startswith('USB_C_Receptacle'): return ('usb-c-hro','USB-C receptacle, HRO TYPE-C-31-M-12')
    # plain parts: the value names them, and the footprint says the package
    pk=re.sub(r'_(Socket_)?LongPads$','',fp);pk=re.sub(r'R_Axial.*','axial',pk);pk=re.sub(r'C_Disc_D5.0mm_W2.5mm_P2.50mm','disc-p2.5',pk);pk=re.sub(r'C_Disc_D5.0mm_W2.5mm_P5.00mm','disc-p5',pk)
    vv=re.sub(r' \(U\d+\)$','',v)
    if vv in('R','C','D','LED','D_Schottky'): vv={'D_Schottky':'schottky'}.get(vv,vv)
    return (f'{vv}|{pk}',f'{vv}, {pk}')
FIELDS=('Digikey','Mouser','Jameco','LCSC','Other','MPN')
if __name__=='__main__':
    C=collections.defaultdict(lambda:dict(n=0,desc='',fp=collections.Counter(),val=collections.Counter(),nums={k:collections.Counter() for k in FIELDS},boards=set(),dnp=0))
    tot=0
    for p in parts():
        c=classify(p)
        if not c: continue
        g=C[c[0]];g['desc']=c[1];tot+=1;g['n']+=1;g['fp'][p['fp']]+=1;g['val'][p['val']]+=1;g['boards'].add(f"{p['repo']}/{p['board']} {p['rev']}")
        g['dnp']+=p['dnp']
        for k in FIELDS:
            v=p['f'].get(k,'').strip()
            if v: g['nums'][k][v]+=1
    out={k:dict(n=g['n'],desc=g['desc'],fp=dict(g['fp']),val=dict(g['val']),nums={a:dict(b) for a,b in g['nums'].items() if b},boards=sorted(g['boards'])) for k,g in sorted(C.items())}
    json.dump(out,open(sys.argv[1] if len(sys.argv)>1 else os.path.dirname(os.path.abspath(__file__))+'/catalogue-draft.json','w'),indent=1,ensure_ascii=False)
    print('fitted parts',tot,'real parts',len(C))
    dk=sum(1 for g in C.values() if g['nums']['Digikey']);mo=sum(1 for g in C.values() if g['nums']['Mouser']);lc=sum(1 for g in C.values() if g['nums']['LCSC']);am=sum(1 for g in C.values() if any('amazon' in x.lower() for x in g['nums']['Other']))
    print('with Digi-Key',dk,'Mouser',mo,'both',sum(1 for g in C.values() if g['nums']['Digikey'] and g['nums']['Mouser']),'LCSC',lc,'Amazon',am,'nothing',sum(1 for g in C.values() if not any(g['nums'][k] for k in('Digikey','Mouser','LCSC','Other'))))
    print('\nSAME PART, MORE THAN ONE NUMBER OR SOURCE:')
    n=0
    for k,g in sorted(C.items(),key=lambda x:-x[1]['n']):
        multi={a:list(b) for a,b in g['nums'].items() if len(b)>1}
        if multi:
            n+=1;print(f" {k[:38]:38} x{g['n']:<4}",{a:[x[:34] for x in b][:4] for a,b in multi.items()})
    print('count',n)
