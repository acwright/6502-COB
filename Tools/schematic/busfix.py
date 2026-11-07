#!/usr/bin/env python3
"""Draws every 6502 bus, cart and card connector on a schematic the one standard way (KICAD.md K21).

  busfix.py SCHEMATIC [--dry]

- A used pin gets a short wire (2.54 mm on the card edge, 3.81 mm on a 2x20 header, longer if that would touch another wire) and a global label named for its
  net. An unused pin, one whose net reaches no other pin, gets a no-connect flag at the pin and no label: KiCad's ERC
  warns about a global label on a single pin.
- What was attached to a pin and to nothing else (wires, local labels, power symbols, bus entries) is replaced. A pin
  whose wire also reaches another part (a decoupling capacitor, a cart's GND tie) keeps its wiring; its local labels
  and power symbols become global labels in place.
- Bus lines left without entries are deleted. Every remaining local label named for a bus signal becomes global.
- Label shapes are left as they are (KICAD.md K25). A label this script adds is passive, a placeholder: run
  flow.py SCHEMATIC --apply afterwards, or derived-check.py's label shape check fails.
Connectivity is never changed: check it with kicad-cli's netlist before and after (verify.py).
"""
import sys,re,os,math,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from sch import *
CARD='6502 Parts:6502 Card Edge'
def is_conn(sym): return sym['ref'].startswith('J') and (sym['lib']==CARD or 'Conn_02x20' in sym['lib'])
def fmt(v): s=f'{v:.4f}'.rstrip('0').rstrip('.');return s if s not in('-0','') else '0'
def main(path,nets,dry=False,keep_nc_header=False):
    """nets: (ref,pin) -> net name from the schematic's own netlist, before any change"""
    S=Sch(path);t=S.t;kill=set();add=[];log=collections.Counter()
    tmpl={k:None for k in('wire','global_label','no_connect','pwr')}
    for k,a,e in S.items():
        if k in('wire','global_label','no_connect') and not tmpl[k]: tmpl[k]=t[a:e]
    pf=[s for s in S.symbols if s['lib']=='power:PWR_FLAG']
    if pf: tmpl['pwr']=t[pf[0]['a']:pf[0]['e']]
    def min_len(P,d,L0,own):
        """the shortest stub from P that touches no other wire, pin or label (own: the pin's present wires)"""
        others=[(w['p'][0],w['p'][-1]) for w in S.wires if w not in own]
        lp={l['p'] for l in S.labels}
        for L in [L0+1.27*i for i in range(12)]:
            Q=(R(P[0]+d[0]*L),R(P[1]+d[1]*L))
            if any(seg_touch(P,Q,a,b) for a,b in others): continue
            if any(q!=P and q!=Q and on_seg(q,P,Q) for q in set(pts)|lp): continue
            return L
        return L0
    pts=S.all_pin_points();netsize=collections.Counter(nets.values())
    def wire_item(P,Q,key):
        w=tmpl['wire'];w=re.sub(r'\(xy [-\d.]+ [-\d.]+\)\s*\(xy [-\d.]+ [-\d.]+\)',f'(xy {fmt(P[0])} {fmt(P[1])}) (xy {fmt(Q[0])} {fmt(Q[1])})',w,count=1)
        return re.sub(r'\(uuid "[^"]*"\)',f'(uuid "{new_uuid(path+key)}")',w,count=1)
    def label_item(name,Q,rot,key):
        g=tmpl['global_label'] or GL
        g=re.sub(r'\(global_label "[^"]*"',f'(global_label "{name}"',g,count=1)
        g=re.sub(r'\(shape \w+\)','(shape passive)',g,count=1)   # a placeholder: flow.py --apply sets it (KICAD.md K25)
        g=re.sub(r'\(at [-\d.]+ [-\d.]+ [-\d.]+\)',f'(at {fmt(Q[0])} {fmt(Q[1])} {int(rot)})',g)
        j='right' if rot in(180,270) else 'left'   # as KiCad writes them: the body away from the wire
        g=re.sub(r'\(justify (left|right)\)',f'(justify {j})',g,count=1)
        if '(justify' not in g.split('(uuid')[0]: g=g.replace('\n\t\t\t)\n\t\t)',f'\n\t\t\t)\n\t\t\t(justify {j})\n\t\t)',1)
        made.add(new_uuid(path+key))
        return re.sub(r'\(uuid "[^"]*"\)',f'(uuid "{new_uuid(path+key)}")',g,count=1)
    def nc_item(P,key):
        n=tmpl['no_connect'] or NC
        n=re.sub(r'\(at [-\d.]+ [-\d.]+\)',f'(at {fmt(P[0])} {fmt(P[1])})',n,count=1)
        return re.sub(r'\(uuid "[^"]*"\)',f'(uuid "{new_uuid(path+key)}")',n,count=1)
    def pwr_item(Q,key):
        p=tmpl['pwr'];p=re.sub(r'\n\t\t\(at [-\d.]+ [-\d.]+ [-\d.]+\)',f'\n\t\t(at {fmt(Q[0])} {fmt(Q[1])} 0)',p,count=1)
        ox,oy=re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)',tmpl['pwr']).groups()
        p=p.replace(f'(at {ox} {oy} ',f'(at {fmt(Q[0])} {fmt(Q[1])} ')
        old=re.search(r'#FLG\w+',p).group(0);flags[0]+=1;p=p.replace(f'"{old}"',f'"#FLG{flags[0]:02d}"')
        for u in set(re.findall(r'\(uuid "([^"]*)"\)',p)): p=p.replace(u,new_uuid(path+key+u))
        return p
    made=set()
    flags=[max([int(x) for x in re.findall(r'"#FLG0*(\d+)"',t)] or [0])+100]
    touched=set();plans=[];prune=[];newpts=set();pulled=[]
    for sym in S.symbols:
        if not is_conn(sym): continue
        header=sym['lib']!=CARD;L=3.81 if header else 2.54
        for num,(P,d,pname) in sorted(S.pins(sym).items()):
            net=nets.get((sym['ref'],num),'')
            # the cluster: wires reachable from P, and what sits on them
            seen={P};stack=[P];ws=[]
            while stack:
                q=stack.pop()
                for w in S.wires:
                    if w in ws: continue
                    a,b=w['p'][0],w['p'][-1]
                    if q in(a,b) or on_seg(q,a,b):
                        ws.append(w)
                        for e in(a,b):
                            if e not in seen: seen.add(e);stack.append(e)
            touched|=seen
            others=[]
            for q in seen:
                for (osym,on) in pts.get(q,[]):
                    if osym is sym and on==num: continue
                    if osym['lib'].startswith('power:'): continue
                    others.append((osym['ref'],on))
            onw=lambda p:p in seen or any(on_seg(p,w['p'][0],w['p'][-1]) for w in ws)
            labs=[l for l in S.labels if onw(l['p'])]
            pws=[s for s in S.symbols if s['lib'].startswith('power:') and onw((R(s['X']),R(s['Y'])))]
            ents=[e for e in S.entries if any(p in seen for p in e['p'])]
            ncs=[n for n in S.ncs if n['p'] in seen]
            unused=net.startswith('unconnected-') or not net or netsize[net]==1
            if others:
                # wired to another part: keep the wiring, drop its bus entries, keep one global label per name
                for x in ents: kill.add((x['a'],x['e']))
                byname=collections.defaultdict(list)
                for l in labs: byname[l['name']].append(l)
                for name,ls in byname.items():
                    ls=[l for l in ls if (l['a'],l['e']) not in kill]
                    if not ls: continue
                    ls.sort(key=lambda l:math.dist(l['p'],P));k=ls[0]
                    for l in ls[1:]: kill.add((l['a'],l['e']));log['duplicate label']+=1
                    if k['kind']=='label':
                        kill.add((k['a'],k['e']));add.append(label_item(name,k['p'],k['rot'],f'{sym["ref"]}.{num}.g{k["p"]}'));newpts.add(k['p']);log['local->global']+=1
                for s in pws:
                    if s['lib']=='power:PWR_FLAG': continue
                    if (s['a'],s['e']) in kill: continue
                    name=s['value'];kill.add((s['a'],s['e']))
                    if name in byname: log['power symbol dropped']+=1;continue
                    q=(R(s['X']),R(s['Y']));newpts.add(q);log['power->global']+=1
                    add.append(label_item(name,q,270 if name=='GND' else 90,f'{sym["ref"]}.{num}.p'))
                prune.extend(ws);pulled.append((P,d,L,sym['ref'],num))
                continue
            Q=(R(P[0]+d[0]*L),R(P[1]+d[1]*L));rot=0 if d[0]>0 else 180
            if unused:
                # an unused pin: a no-connect flag at the pin, nothing else
                if ncs and [n['p'] for n in ncs]==[P] and not ws: continue
                for w in ws: kill.add((w['a'],w['e']))
                for x in labs+ncs+ents: kill.add((x['a'],x['e']))
                add.append(nc_item(P,f'{sym["ref"]}.{num}.nc'));log['nc']+=1;continue
            name=net.lstrip('/')
            gl=[l for l in labs if l['kind']=='global_label']
            want_nc=False
            nonflag=[s for s in pws if s['lib']!='power:PWR_FLAG']
            ok=len(ws)==1 and P in(ws[0]['p'][0],ws[0]['p'][-1]) and len(labs)==1 and gl and gl[0]['name']==name and not nonflag and not ents and len(ncs)==(1 if want_nc else 0)
            if ok:
                o=ws[0]['p'][-1] if ws[0]['p'][0]==P else ws[0]['p'][0]
                ok=gl[0]['p']==o and abs(math.dist(P,o)-min_len(P,d,L,ws))<0.01 and (not want_nc or ncs[0]['p']==o)
                ok=ok and all((R(s['X']),R(s['Y']))==o for s in pws)
            if ok: continue
            flag=[s for s in pws if s['lib']=='power:PWR_FLAG']
            for w in ws: kill.add((w['a'],w['e']))
            for x in labs+ncs+ents: kill.add((x['a'],x['e']))
            for s in pws: kill.add((s['a'],s['e']))
            plans.append(dict(P=P,d=d,L=L,rot=rot,name=name,flag=bool(flag),nc=want_nc,key=f'{sym["ref"]}.{num}'))
    # second pass: each new stub as short as the standard allows without touching a wire, pin or label that stays
    pinpts={q for q,lst in pts.items() if any((s['a'],s['e']) not in kill for s,_ in lst)}
    keep=[(w['p'][0],w['p'][-1]) for w in S.wires if (w['a'],w['e']) not in kill]
    lab_keep={l['p'] for l in S.labels if (l['a'],l['e']) not in kill}
    for pl in plans:
        P,d=pl['P'],pl['d']
        for L in [pl['L']+1.27*i for i in range(12)]:
            Q=(R(P[0]+d[0]*L),R(P[1]+d[1]*L))
            if any(seg_touch(P,Q,a,b) for a,b in keep): continue
            if any(q!=P and on_seg(q,P,Q) for q in pinpts|lab_keep): continue
            break
        else: raise SystemExit(f'no clear stub for {pl["key"]} in {path}')
        keep.append((P,Q))
        add.append(wire_item(P,Q,pl['key']+'.w'));add.append(label_item(pl['name'],Q,pl['rot'],pl['key']+'.l'));log['redrawn']+=1
        if L!=pl['L']: log['longer stub']+=1
        if pl['nc']: add.append(nc_item(Q,pl['key']+'.nc'))
        if pl['flag']: add.append(pwr_item(Q,pl['key']+'.f'));log['flag kept']+=1
    # any bus entry left elsewhere on the sheet (CPU Card 1.0 draws its 65C02 that way) goes too, and its wire is cut back
    for x in S.entries:
        if (x['a'],x['e']) in kill: continue
        kill.add((x['a'],x['e']));log['other bus entry']+=1
        for w in S.wires:
            if (w['a'],w['e']) not in kill and any(q in(w['p'][0],w['p'][-1]) for q in x['p']): prune.append(w)
    # wires on a kept pin's cluster left hanging once its entries and power symbols went: a wire with a label on it is
    # cut back to that label, a bare one is deleted
    geo={id(w):(w['p'][0],w['p'][-1]) for w in S.wires}
    def dead(w): return w.get('dead') or (('syn' not in w) and (w['a'],w['e']) in kill)
    def drop(w):
        if 'syn' in w: add[w['syn']]='';w['dead']=True
        else: kill.add((w['a'],w['e']))
    def lab_pts():
        return {l['p'] for l in S.labels if (l['a'],l['e']) not in kill}|newpts
    while True:
        live=[w for w in S.wires if not dead(w)]
        cut=0
        for w in prune:
            if dead(w): continue
            a,b=geo[id(w)]
            for end,other in((a,b),(b,a)):
                n=sum(1 for v in live if v is not w and seg_touch(end,end,*geo[id(v)]))
                n+=1 if end in pinpts else 0
                n+=1 if end in lab_pts() else 0
                n+=sum(1 for x in S.ncs if x['p']==end and (x['a'],x['e']) not in kill)
                n+=sum(1 for x in S.entries for q in x['p'] if q==end and (x['a'],x['e']) not in kill)
                n+=sum(1 for s in S.symbols if s['lib']=='power:PWR_FLAG' and (R(s['X']),R(s['Y']))==end and (s['a'],s['e']) not in kill)
                if n: continue
                on=[q for q in lab_pts() if on_seg(q,a,b) and q!=end]
                drop(w);cut+=1
                if on:
                    q=min(on,key=lambda q:math.dist(q,end))
                    if q!=other:
                        nw={'p':[other,q],'syn':len(add)}
                        geo[id(nw)]=(other,q);S.wires.append(nw);prune.append(nw)
                        add.append(wire_item(other,q,f'trim{other}{q}'));log['wire cut back']+=1
                else: log['dangling wire']+=1
                break
        if not cut: break
    # bus lines without entries left, and junctions left with fewer than three connections
    left_entries=[e for e in S.entries if (e['a'],e['e']) not in kill]
    for b in S.buses:
        if not any(any(on_seg(p,b['p'][0],b['p'][-1]) for p in e['p']) for e in left_entries): kill.add((b['a'],b['e']));log['bus line']+=1
    # remaining local labels named for a bus signal, or sharing a name with a global label, become global
    gnames={l['name'] for l in S.labels if l['kind']=='global_label'}
    for l in S.labels:
        if l['kind']=='label' and (l['name'] in SIG or l['name'] in gnames) and (l['a'],l['e']) not in kill:
            kill.add((l['a'],l['e']));add.append(label_item(l['name'],l['p'],l['rot'],f'loc{l["p"]}{l["name"]}'));log['local->global']+=1
    # apply
    out=t
    for a,e in sorted(kill,reverse=True): out=out[:a]+out[e:]
    m=re.search(r'\n\t\(sheet_instances',out) or re.search(r'\n\t\(embedded_fonts',out)
    pos=m.start() if m else out.rstrip().rfind(')')
    out=out[:pos]+''.join(add)+out[pos:]
    # junctions: keep only those with three or more connections
    S2=Sch.__new__(Sch);S2.path=path;S2.t=out;S2.parse();pp=S2.all_pin_points();jk=[]
    for j in S2.junctions:
        q=j['p']
        n=0
        for w in S2.wires+S2.buses:
            a,b=w['p'][0],w['p'][-1]
            if q in(a,b): n+=1
            elif on_seg(q,a,b): n+=2
        n+=len(pp.get(q,[]))+sum(1 for e in S2.entries for x in e['p'] if x==q)
        if n<3: jk.append((j['a'],j['e']))
    for a,e in sorted(jk,reverse=True): out=out[:a]+out[e:]
    log['junctions removed']+=len(jk)
    # a kept pin (one wired to a capacitor, say) whose label sits further out along a straight wire than the standard
    # stub, with nothing joining beyond the stub: the wire becomes the standard stub and the label moves to its end
    S4=Sch.__new__(Sch);S4.path=path;S4.t=out;S4.parse();pp4=S4.all_pin_points();edits=[]
    for P,d,L,ref,num in pulled:
        Q=(R(P[0]+d[0]*L),R(P[1]+d[1]*L))
        along=lambda q:abs((q[0]-P[0])*d[1]-(q[1]-P[1])*d[0])<1e-6 and (q[0]-P[0])*d[0]+(q[1]-P[1])*d[1]>-1e-6
        dist=lambda q:(q[0]-P[0])*d[0]+(q[1]-P[1])*d[1]
        chain=[];cur=P
        while True:
            nxt=[w for w in S4.wires if w not in chain and cur in(w['p'][0],w['p'][-1]) and along(w['p'][0]) and along(w['p'][-1])]
            nxt=[w for w in nxt if dist(w['p'][-1] if w['p'][0]==cur else w['p'][0])>dist(cur)+1e-6]
            if len(nxt)!=1: break
            w=nxt[0];chain.append(w);cur=w['p'][-1] if w['p'][0]==cur else w['p'][0]
        if not chain: continue
        F=cur
        if dist(F)<=L+1e-6: continue
        labs=[l for l in S4.labels if l['p']==F]
        if len(labs)!=1: continue
        # anything joining the ray strictly beyond Q?
        others=[w for w in S4.wires if w not in chain]
        join=any(Q!=e and dist(e)>L+1e-6 and dist(e)<=dist(F)+1e-6 and along(e) for w in others for e in(w['p'][0],w['p'][-1]))
        join=join or any(q!=P and along(q) and L+1e-6<dist(q)<=dist(F)+1e-6 for q in pp4)
        join=join or any(l is not labs[0] and along(l['p']) and L+1e-6<dist(l['p'])<=dist(F)+1e-6 for l in S4.labels)
        if join: continue
        for w in chain: edits.append((w['a'],w['e'],''))
        l=labs[0];b=out[l['a']:l['e']]
        b=re.sub(r'\(at [-\d.]+ [-\d.]+ ([-\d.]+)\)',lambda m:f'(at {fmt(Q[0])} {fmt(Q[1])} {m.group(1)})',b)
        edits.append((l['a'],l['e'],b))
        edits.append((len(out),len(out),wire_item(P,Q,f'pull{ref}.{num}')))
        log['label pulled in']+=1
    ins=[e for e in edits if e[0]==len(out)];edits=[e for e in edits if e[0]!=len(out)]
    for a,e,b2 in sorted(edits,reverse=True): out=out[:a]+b2+out[e:]
    if ins:
        m=re.search(r'\n\t\(sheet_instances',out) or re.search(r'\n\t\(embedded_fonts',out)
        pos=m.start() if m else out.rstrip().rfind(')');out=out[:pos]+''.join(x[2] for x in ins)+out[pos:]
    # every label made here faces away from the wire it ends
    S3=Sch.__new__(Sch);S3.path=path;S3.t=out;S3.parse();edits=[]
    for l in S3.labels:
        if l['kind']!='global_label' or l['uuid'] not in made: continue
        ends=[w for w in S3.wires if l['p'] in(w['p'][0],w['p'][-1])]
        if len(ends)!=1: continue
        w=ends[0];o=w['p'][-1] if w['p'][0]==l['p'] else w['p'][0];dx,dy=l['p'][0]-o[0],l['p'][1]-o[1]
        rot=0 if dx>0 else 180 if dx<0 else 270 if dy>0 else 90
        if rot==l['rot']: continue
        b=out[l['a']:l['e']];x,y=fmt(l['p'][0]),fmt(l['p'][1])
        b2=re.sub(r'\(at [-\d.]+ [-\d.]+ [-\d.]+\)',f'(at {x} {y} {rot})',b)
        b2=re.sub(r'\(justify (left|right)\)',f'(justify {"right" if rot in(180,270) else "left"})',b2,count=1)
        edits.append((l['a'],l['e'],b2))
    for a,e,b2 in sorted(edits,reverse=True): out=out[:a]+b2+out[e:]
    log['labels turned']+=len(edits)
    # Label shapes are never rewritten here: a shape follows the signal's flow at its own pin (KICAD.md K25), which
    # a signal's name can't tell. K21's one-shape-per-name pass turned every address label into an output.
    out2=out
    if not dry: open(path,'w',encoding='utf-8',newline='').write(out2)
    return dict(log)
GL='''
	(global_label "X"
		(shape passive)
		(at 0 0 0)
		(effects
			(font
				(size 1.27 1.27)
			)
			(justify left)
		)
		(uuid "00000000-0000-0000-0000-000000000000")
		(property "Intersheetrefs" "${INTERSHEET_REFS}"
			(at 0 0 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
	)'''
NC='''
	(no_connect
		(at 0 0)
		(uuid "00000000-0000-0000-0000-000000000000")
	)'''
