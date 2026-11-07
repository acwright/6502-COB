#!/usr/bin/env python3
"""Writes the parts catalogue into every schematic and PCB. Only metadata: supplier fields, BOM flags, DNP, and Value where the silk doesn't print it.
Usage: apply.py [--dry] [--bom-test]. assignment.json remembers which catalogue entry each reference is, so a second run gives the same result."""
import re,os,sys,glob,json,uuid,csv,io,collections
import draft
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))));import common;from common import K,SCOPE,files,load,save
H=os.path.dirname(os.path.abspath(__file__))
C=json.load(open(H+'/catalogue.json'));O=load('orders.json')
FIELDS=['Digikey','Mouser','Jameco','LCSC','Other']
# MPN goes too: the Fabrication Toolkit falls back to MPN when LCSC is blank, which would put it in bom.csv's LCSC column.
JUNK={'Price','Availability','Check_prices','SnapEDA_Link','MP','MF','MANUFACTURER','MAXIMUM_PACKAGE_HEIGHT','Package','PARTREV','STANDARD','Description_1','Sparkfun','MPN'}
VALUE={'32pF|disc-p2.5':'33pF','22pF|disc-p2.5':'20pF','schottky|D_DO-35_SOD27_P7.62mm_Horizontal':'BAT85','74LS138|SOIC-16_3.9x9.9mm_P1.27mm':'74HC138','6551|DIP-28_W15.24mm':'R6551AP','65C51|DIP-28_W15.24mm':'R6551AP','65C21|DIP-40_W15.24mm':'W65C21N','OCXO-14|Oscillator_DIP-14':'1 MHz','R|axial':'DNP: parallel with VR1 to make ~10 k','Q_NPN_BEC|SOT-23':'SS8050','LM555xM|SOIC-8_3.9x4.9mm_P1.27mm':'NE555','MAX238xNG+|DIP-24_W7.62mm':'MAX238CNG+','ATmega1284-P|DIP-40_W15.24mm':'ATmega1284','ATmega328|DIP-28_W7.62mm':'ATmega328P','DS1511Y|DIP-28_W15.24mm':'DS1511Y+','BAT-HLD-001-THM|BAT_BAT-HLD-001-THM':'CR2032','1k|axial':'1k','1.8432 MHz|Crystal_HC49-U_Vertical':'1.8432 MHz'}
COSMETIC={'1k|axial','1.8432 MHz|Crystal_HC49-U_Vertical','ATmega1284-P|DIP-40_W15.24mm','ATmega328|DIP-28_W7.62mm','DS1511Y|DIP-28_W15.24mm','MAX238xNG+|DIP-24_W7.62mm','65C21|DIP-40_W15.24mm'}   # never worth changing silk for
SET_DNP={'R|axial'}
# Made or drawn boards whose build notes say to fit something else: the BOM has to order what is fitted.
def _r(repo,b,rev,refs,i): return {f'{repo}|{b}|{rev}|{x}':i for x in refs}
FIT={**_r('ACE','ACE Board','1.0',['R1','R2','R3','R4','R5','R27'],'10k|axial'),**_r('COB','CPU Card','1.0',['R1','R2','R3','R4','R5','R6'],'10k|R_0805_2012Metric'),**_r('DEV','DEV Board','1.0',['R1','R2','R3','R4'],'10k|R_0805_2012Metric'),**_r('VCS','Main Board','1.0',['R4','R10','R11','R12','R13','R14'],'10k|R_0805_2012Metric')}
DNP_REF={'COB|Backplane Pro|1.0|R3':'DNP: the RESB pull-up is on the CPU Card','COB|Backplane Pro|1.1|R5':'DNP: the RESB pull-up is on the CPU Card'}
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
            if d==0:return j+1
        j+=1
def esc(v): return (v or '').replace('\\','\\\\').replace('"','\\"')
def props(b,ind):
    """(name,value,start,end) of each property at this indent; start includes the newline and indent"""
    out=[]
    for m in re.finditer(r'\n'+ind+r'\(property "((?:[^"\\]|\\.)*)" "((?:[^"\\]|\\.)*)"',b):
        out.append((m.group(1),m.group(2),m.start(),block(b,m.start()+1+len(ind))))
    return out
def edit(b,ind,want,drop,new):
    """want: name->value to set or add. drop: names to remove. new(name,value) renders a property that doesn't exist yet."""
    P=props(b,ind);have={p[0] for p in P}
    for n,v,s,e in reversed(P):
        if n in drop: b=b[:s]+b[e:]
        elif n in want and v!=esc(want[n]):
            head=f'\n{ind}(property "{n}" "{v}"'
            assert b[s:s+len(head)]==head,(n,v)
            b=b[:s]+f'\n{ind}(property "{n}" "{esc(want[n])}"'+b[s+len(head):]
    add=[n for n in want if n not in have]
    if add:
        P=props(b,ind);e=P[-1][3]
        b=b[:e]+''.join(new(n,want[n]) for n in add)+b[e:]
    return b
def want_fields(e): return {'Digikey':e.get('digikey') or '','Mouser':e.get('mouser') or '','Jameco':e.get('jameco') or '','LCSC':e.get('lcsc') or '','Other':e.get('other') or ''}
def status(repo,board,rev):
    k=f'{repo}|{board}|{rev}'
    if k in O['made']: return 'made'
    if k in O['ordered']: return 'ordered'
    return 'drawn'
def silk_value(fb):
    for n,v,s,e in props(fb,'\t\t'):
        if n=='Value':
            x=fb[s:e]
            return 'SilkS' in re.search(r'\(layer "([^"]+)"',x).group(1) and '(hide yes)' not in x
    return False
def footprints(t):
    return [(m.start(),block(t,m.start()+1)) for m in re.finditer(r'\n\t\(footprint "',t)]
def fp_ref(fb):
    m=re.search(r'\(property "Reference" "([^"]*)"',fb);return m.group(1) if m else ''
def gen_bom(t):
    """The Fabrication Toolkit's bom.csv, from the PCB text. Tested byte for byte against the KIM Board and Clock Card."""
    F=[]
    for s,e in footprints(t):
        b=t[s:e];name=re.match(r'\n\t\(footprint "([^"]*)"',b).group(1).split(':')[-1];at=re.search(r'\n\t\t\(attr ([^)]*)\)',b);a=at.group(1).split() if at else [];P={n:v for n,v,_,_ in props(b,'\t\t')}
        F.append(dict(ref=P.get('Reference',''),name=name,attr=a,val=P.get('Value','').replace('\\"','"').replace('\\\\','\\'),lcsc=P.get('LCSC','')))
    F.sort(key=lambda f:f['ref'].upper());n=collections.Counter(f['ref'].upper() for f in F);rows=[]
    for f in F:
        if 'exclude_from_bom' in f['attr'] or 'dnp' in f['attr'] or f['val'].upper()=='DNP': continue
        u=''
        if n[f['ref'].upper()]>1: u='_'+str(n[f['ref'].upper()]);n[f['ref'].upper()]-=1
        fn=re.sub(r'^(\w*_SMD:)?\w{1,4}_(\d+)_\d+Metric.*$',r'\2',f['name']);des=f['ref'].upper()+u
        for r in rows:
            if r[1]==fn and r[3].upper()==f['val'].upper() and r[4]==f['lcsc'] and r[2]<200:
                r[0]+=', '+des;r[2]+=1;break
        else: rows.append([des,fn,1,f['val'],f['lcsc']])
    o=io.StringIO(newline='');w=csv.writer(o);w.writerow(['Designator','Footprint','Quantity','Value','LCSC Part #'])
    for r in rows:
        if '**' not in r[0]: w.writerow(r)
    return '﻿'+o.getvalue()
def assignment():
    A=load('assignment.json')
    if any(not k.startswith('_') for k in A): return A
    for x in draft.parts():
        r=draft.classify(x)
        if r: A[f"{x['repo']}|{x['board']}|{x['rev']}|{x['ref']}"]=r[0]
    save('assignment.json',A);return A
def sch_new(x,y):
    def f(n,v): return f'\n\t\t(property "{n}" "{esc(v)}"\n\t\t\t(at {x} {y} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)'
    return f
def run(dry):
    A=assignment();A.update(FIT);save('assignment.json',A);rep=dict(silk_kept=[],value_changed=[],drawn_silk=[],missing=[],flags=0,files=0)
    for f in files('Hardware/*/Rev */*.kicad_pcb'):
        parts=f.split('/');repo=parts[-5].split('-')[-1];board=parts[-3];rev=parts[-2][4:];st=status(repo,board,rev)
        d=os.path.dirname(f);pt=open(f,encoding='utf-8',newline='').read();sch=sorted(glob.glob(d+'/*.kicad_sch'))
        # what the silk prints decides Value, per reference
        silk={};
        for s,e in footprints(pt): silk[fp_ref(pt[s:e])]=silk_value(pt[s:e])
        newval={};
        for ref in {k.split('|')[3] for k in A if k.startswith(f'{repo}|{board}|{rev}|')}:
            i=A[f'{repo}|{board}|{rev}|{ref}']
            if i in VALUE:
                nv=VALUE[i]
                if silk.get(ref):
                    if st=='drawn' and i not in COSMETIC: newval[ref]=nv;rep['drawn_silk'].append([repo,board,rev,ref,nv])
                    elif i not in COSMETIC: rep['silk_kept'].append([repo,board,rev,ref,i,nv,st])
                else: newval[ref]=nv
            k=f'{repo}|{board}|{rev}|{ref}'
            if k in FIT and not silk.get(ref): newval[ref]='10k'
            if k in DNP_REF and not silk.get(ref): newval[ref]=DNP_REF[k]
        # schematics
        for sf in sch:
            t=open(sf,encoding='utf-8',newline='').read();spans=[(m.start(),block(t,m.start()+1)) for m in re.finditer(r'\n\t\(symbol\n\t\t\(lib_id',t)];o=t
            for s,e in reversed(spans):
                b=t[s:e];rr=re.findall(r'\(reference "([^"]+)"',b);P={n:v for n,v,_,_ in props(b,'\t\t')};ref=rr[0] if rr else P.get('Reference','')
                if ref.startswith('#'): continue
                i=A.get(f'{repo}|{board}|{rev}|{ref}');drop=set(JUNK);want={}
                if i:
                    if i not in C: rep['missing'].append([repo,board,rev,ref,i]);continue
                    want=want_fields(C[i])
                    if ref in newval: want['Value']=newval[ref]
                at=re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)',b)
                nb=edit(b,'\t\t',want,drop,sch_new(at.group(1),at.group(2)))
                if i:
                    nb=nb.replace('\n\t\t(in_bom no)','\n\t\t(in_bom yes)',1)
                    if i in SET_DNP or f'{repo}|{board}|{rev}|{ref}' in DNP_REF: nb=nb.replace('\n\t\t(dnp no)','\n\t\t(dnp yes)',1)
                t=t[:s]+nb+t[e:]
            # the schematic's own copy of library symbols loses the imported junk too
            m=re.search(r'\n\t\(lib_symbols',t)
            if m:
                ls,le=m.start(),block(t,m.start()+1);lb=t[ls:le]
                for n,v,a,z in reversed(props(lb,'\t\t\t')):
                    if n in JUNK: lb=lb[:a]+lb[z:]
                t=t[:ls]+lb+t[le:]
            if t!=o and not dry: open(sf,'w',encoding='utf-8',newline='').write(t);rep['files']+=1
        # PCB
        t=pt
        for s,e in reversed(footprints(t)):
            b=t[s:e];ref=fp_ref(b);i=A.get(f'{repo}|{board}|{rev}|{ref}');drop=set(JUNK);want={}
            lay=re.search(r'\n\t\t\(layer "([FB])\.Cu"\)',b);L=(lay.group(1) if lay else 'F')+'.Fab'
            if i and i in C:
                want=want_fields(C[i])
                if ref in newval: want['Value']=newval[ref]
            def new(n,v,key=f'{repo}|{board}|{rev}|{ref}',L=L):
                u=uuid.uuid5(uuid.NAMESPACE_URL,'ac6502-bom/'+key+'/'+n)
                return f'\n\t\t(property "{n}" "{esc(v)}"\n\t\t\t(at 0 0 0)\n\t\t\t(unlocked yes)\n\t\t\t(layer "{L}")\n\t\t\t(hide yes)\n\t\t\t(uuid "{u}")\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t(thickness 0.15)\n\t\t\t\t)\n\t\t\t)\n\t\t)'
            nb=edit(b,'\t\t',want,drop,new) if props(b,'\t\t') else b
            if i:
                m=re.search(r'\n\t\t\(attr ([^)]*)\)',nb)
                a=m.group(1).split() if m else []
                if 'board_only' not in a:
                    a2=[x for x in a if x!='exclude_from_bom']
                    if (i in SET_DNP or f'{repo}|{board}|{rev}|{ref}' in DNP_REF) and 'dnp' not in a2: a2.append('dnp')
                    if a2!=a:
                        rep['flags']+=1
                        if m: nb=nb[:m.start()]+('\n\t\t(attr '+' '.join(a2)+')' if a2 else '')+nb[m.end():]
                        else:
                            k=nb.rfind('\n\t\t(property');z=block(nb,k+3);nb=nb[:z]+'\n\t\t(attr '+' '.join(a2)+')'+nb[z:]
            t=t[:s]+nb+t[e:]
        if t!=pt and not dry: open(f,'w',encoding='utf-8',newline='').write(t);rep['files']+=1
        for ref,v in newval.items(): rep['value_changed'].append([repo,board,rev,ref,v])
        # bom.csv
        pd=f"{K}6502-{repo}/Production/{board}/Rev {rev}"
        if os.path.isdir(pd) and not dry:
            open(pd+'/bom.csv','w',encoding='utf-8',newline='').write(gen_bom(t))
    for lf in files('Libraries/*.kicad_sym'):
        t=open(lf,encoding='utf-8',newline='').read();o=t
        for n,v,x,z in reversed(props(t,'\t\t')):
            if n in JUNK: t=t[:x]+t[z:]
        if t!=o and not dry: open(lf,'w',encoding='utf-8',newline='').write(t);rep['libs']=rep.get('libs',0)+1
    os.makedirs(common.WORK,exist_ok=True);json.dump(rep,open(common.WORK+'/apply-report.json','w'),indent=0,ensure_ascii=False)
    print({k:(len(v) if isinstance(v,list) else v) for k,v in rep.items()})
if __name__=='__main__':
    if '--bom-test' in sys.argv:
        for repo,board,rev in [('KIM','KIM Board','1.0'),('COB','Clock Card','1.0')]:
            d=f'{K}6502-{repo}';pcb=open(f'{d}/Hardware/{board}/Rev {rev}/{board}.kicad_pcb',encoding='utf-8',newline='').read();ex=open(f'{d}/Production/{board}/Rev {rev}/bom.csv',encoding='utf-8',newline='').read()
            print(board,'identical' if gen_bom(pcb)==ex else 'DIFFERS')
            if gen_bom(pcb)!=ex:
                import difflib
                for l in list(difflib.unified_diff(ex.splitlines(),gen_bom(pcb).splitlines(),lineterm='',n=0))[:12]: print('  ',l[:150])
    else: run('--dry' in sys.argv)
