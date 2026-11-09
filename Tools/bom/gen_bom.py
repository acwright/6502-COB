#!/usr/bin/env python3
"""Generates BOM.md and the Digi-Key and Mouser cart files for one repo or all five, from the PCB files, assignment.json and catalogue.json.
Usage: gen_bom.py [--readme]. --readme also swaps the README's old BOM tables for links."""
import re,os,sys,glob,json,csv,io,math,collections,urllib.parse
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','revision-audit'));import labels
from apply import footprints,props,fp_ref,silk_value,FIT,DNP_REF,H,K,C,O,status
from common import load,SCOPE
A=load('assignment.json');AUD={(r['repo'],r['board'],r['rev']):r for r in load('audit.json')}
TEST=O.get('tested',{});REP=json.load(open(H+'/known-values.json')) if os.path.exists(H+'/known-values.json') else []
JAM={'43318':'https://www.jameco.com/z/R6551AP-Rockwell-IC-6551-Asynchronous-Communication-Interface-Adapter-DIP-28-pin_43318.html','44564':'https://www.jameco.com/z/74C922-Major-Brands-IC-74C922-16-20-Key-Encoder-DIP-18-pin_44564.html'}
def nat(s): return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)',s)]
def ranges(R):
    R=sorted(set(R),key=nat);out=[];i=0
    while i<len(R):
        m=re.fullmatch(r'([A-Za-z_]+)(\d+)',R[i]);j=i
        if m:
            while j+1<len(R):
                n=re.fullmatch(r'([A-Za-z_]+)(\d+)',R[j+1])
                if n and n.group(1)==m.group(1) and int(n.group(2))==int(m.group(2))+(j+1-i): j+=1
                else: break
        out.append(R[i] if j==i else (f'{R[i]}, {R[j]}' if j==i+1 else f'{R[i]}–{R[j]}'));i=j+1
    return ', '.join(out)
def L_dk(p): return f"[{p}](https://www.digikey.com/en/products/filter?keywords={urllib.parse.quote(p,safe='')})" if p else ''
def L_mo(p): return f"[{p}](https://www.mouser.com/ProductDetail/{urllib.parse.quote(p,safe='-')})" if p else ''
def L_lc(p): return f"[{p}](https://www.lcsc.com/search?q={p})" if p else ''
def L_ot(o):
    if not o: return ''
    if not o.startswith('http'): return o
    h=urllib.parse.urlparse(o).netloc.replace('www.','');n={'amazon.com':'Amazon','tindie.com':'Tindie','sparkfun.com':'SparkFun','adafruit.com':'Adafruit','pjrc.com':'PJRC','retrocomp.cz':'Retrocomp'}.get(h,h)
    return f'[{n}]({o})'
def other_cell(e):
    c=[]
    if e.get('jameco'): c.append(f"[Jameco {e['jameco']}]({JAM.get(e['jameco'],'https://www.jameco.com/z/'+e['jameco'])})")
    if e.get('lcsc'): c.append('LCSC '+L_lc(e['lcsc']))
    if e.get('other'): c.append(L_ot(e['other']))
    return '; '.join(c)
def part_name(e,fb=None):
    if e.get('mpn'):
        m=e.get('mfr') or '';m={'Vishay General Semiconductor - Diodes Division':'Vishay','TE Connectivity AMP Connectors':'TE Connectivity','Panasonic Industry':'Panasonic','Sullins Connector Solutions':'Sullins','Amphenol ICC (FCI)':'Amphenol','Analog Devices Inc./Maxim Integrated':'Maxim','Alliance Memory, Inc.':'Alliance Memory','CTS-Frequency Controls':'CTS'}.get(m,m)
        return (m+' '+e['mpn']).strip()
    return (e.get('desc') or e['id']).split('|')[0]
STRIP=re.compile(r'pinheader-([12])x(\d+)-2\.54-vertical')
SOCK=re.compile(r'^DIP-(\d+)_W([\d.]+)mm_Socket');ZIF=re.compile(r'^DIP_Socket-(\d+)_')
EXTRA={('KIM','KIM Board','1.0'):[('Female header 1×20, 2.54 mm','S7018-ND','',2,'J6',''),('Female header 1×10, 2.54 mm','S7008-ND','',1,'J6',''),('Shunt, 2.54 mm','S9337-ND','',2,'J1, J3',''),('Female header 1×16, 2.54 mm','S7014-ND','',1,'U13',''),('BusBoard BB830 breadboard','4526-BB830-ND','854-BB830',2,'The breadboards',''),('Clear two-piece keycap for Cherry MX switches','','',24,'SW1–SW24','https://www.amazon.com/dp/B0G2WJBLBC'),('5 V DC power supply, centre positive','','',1,'J7',''),('Straight-through DB-9 serial cable','','',1,'J2','')]}
SKIP={('ACE','ACE Board','1.0'):{'U12','U13'}}
EXTRA[('ACE','ACE Board','1.0')]=[('Panasonic EEA-GA1C100, 10 µF, on the underside across J19','P14482-ND','667-EEA-GA1C100',1,'Added',''),('Vishay BAT85S-TR, for the video card /INT','BAT85SCT-ND','78-BAT85S',1,'Added','')]
EXTRA_NOTE={('ACE','ACE Board','1.0'):'U12 and U13 are not listed: fit the ACE RAM Patch Rev 1.1 in their sockets. See the build notes.',('KIM','KIM Board','1.0'):'J6 is one footprint, built from three strips of header. U13 also takes a 1×16 pin header, cut from the strip above.'}
EXTRA_STRIP={('KIM','KIM Board','1.0'):16}
# The KIM Board Rev 1.1 is built as Rev 1.0 is
for _d in(EXTRA,EXTRA_NOTE,EXTRA_STRIP): _d[('KIM','KIM Board','1.1')]=_d[('KIM','KIM Board','1.0')]
# Shunts, from Tools/data/jumpers.json: one row per revision, for every header a builder fits a shunt on
def _shunts():
    import json as _j
    acc=collections.OrderedDict()
    for e in load('jumpers.json'):
        if not e.get('shunts'): continue
        ref=[r for r in e['refs'] if r.startswith('J') and not r.startswith('JP')][0]
        for rev in e['revs']:
            n,refs=acc.get((e['repo'],e['board'],rev),(0,[]));acc[(e['repo'],e['board'],rev)]=(n+e['shunts'],refs+[ref])
    for k,(n,refs) in acc.items():
        EXTRA[k]=[x for x in EXTRA.get(k,[]) if not x[0].startswith('Shunt')]+[('Shunt, 2.54 mm','S9337-ND','',n,', '.join(sorted(refs,key=nat)),'')]
_shunts()
def rev_rows(repo,board,rev,path):
    t=open(path,encoding='utf-8',newline='').read();rows=collections.OrderedDict();socks=collections.defaultdict(list);dnp=[];pins=collections.Counter()
    for s,e in footprints(t):
        b=t[s:e];ref=fp_ref(b);i=A.get(f'{repo}|{board}|{rev}|{ref}')
        if not i: continue
        P={n:v.replace('\\"','"') for n,v,_,_ in props(b,'\t\t')};at=re.search(r'\n\t\t\(attr ([^)]*)\)',b);a=at.group(1).split() if at else [];name=re.match(r'\n\t\(footprint "([^"]*)"',b).group(1).split(':')[-1]
        if 'dnp' in a: dnp.append((ref,P.get('Value','')));continue
        skip=ref in SKIP.get((repo,board,rev),())
        m=SOCK.match(name);z=ZIF.match(name)
        if m:
            n,w=m.group(1),float(m.group(2));sid=f"socket-dip-{n}"+(('-w7' if w<8 else '-w15') if n in('24','28','32','40') else '')
            socks[(sid,f"IC socket, {n}-pin, {'0.3' if w<8 else '0.6'} in")].append(ref)
        elif z: socks[(f'socket-zif-{z.group(1)}',f'{z.group(1)}-pin ZIF socket, or an ordinary {z.group(1)}-pin socket')].append(ref)
        if skip: dnp.append((ref,'SKIP'));continue
        st=STRIP.fullmatch(i)
        if st: pins[st.group(1)]+=int(st.group(2))
        val='Keyswitch' if i=='keyswitch-mx' else P.get('Value','')
        k=f'{repo}|{board}|{rev}|{ref}'
        if k in FIT and silk_value(b): val=f"10k (the silk says {P.get('Value','')})"
        presold='smd' in a and bool(P.get('LCSC'))
        rows.setdefault((i,val),dict(id=i,val=val,refs=[],presold=presold))['refs'].append(ref)
    R=sorted(rows.values(),key=lambda r:nat(sorted(r['refs'],key=nat)[0]))
    return R,socks,dnp,pins
def cart_lines(repo,board,rev,R,socks,pins,sup,through):
    key=sup;tot=collections.OrderedDict()
    def add(n,mpn,q,ref):
        if not n: return
        x=tot.setdefault(n,[mpn,0,[]]);x[1]+=q;x[2].append(ref)
    for r in R:
        if through and r['presold']: continue
        if r['id'] not in C: continue
        e=C[r['id']]
        if r['id'].startswith('BREADBOARD HEADERS'): continue
        if STRIP.fullmatch(r['id']): continue
        add(e.get(key),e.get('mpn') or '',len(r['refs']),ranges(r['refs']))
    extra_pins=EXTRA_STRIP.get((repo,board,rev),0)
    for rows_,cols in pins.items():
        cols=cols+(extra_pins if rows_=='1' else 0)
        sid='pinheader-1x02-2.54-vertical' if rows_=='1' else 'pinheader-2x02-2.54-vertical';e=C[sid]
        per={('digikey','1'):40,('digikey','2'):40,('mouser','1'):40,('mouser','2'):20}[(key,rows_)]
        add(e.get(key),e.get('mpn') or '',math.ceil(cols/per),'header strip, cut to size')
    if '1' not in pins and extra_pins:
        e=C['pinheader-1x02-2.54-vertical'];add(e.get(key),e.get('mpn') or '',math.ceil(extra_pins/40),'header strip, cut to size')
    for (sid,txt),refs in socks.items():
        e=C[sid]
        add(e.get(key),e.get('mpn') or '',len(refs),'socket '+ranges(refs))
    for part,dk,mo,q,ref,ot in EXTRA.get((repo,board,rev),[]):
        add(dk if key=='digikey' else mo,'',q,ref)
    return tot
def write_cart(path,head,tot):
    o=io.StringIO(newline='');w=csv.writer(o);w.writerow(head)
    for n,(mpn,q,refs) in tot.items():
        ref=', '.join(refs).replace('–','-');ref=ref if len(ref)<=40 else ref[:37]+'...'
        w.writerow([n,mpn,q,ref])
    os.makedirs(os.path.dirname(path),exist_ok=True);open(path,'w',encoding='utf-8',newline='').write(o.getvalue())
BS='<!-- Build notes: hand-written. Tools/bom/gen_bom.py keeps everything between these two markers. -->'
BS_OLD=BS.replace('Tools/','tools/')   # the marker before the tools moved into the repositories
BE='<!-- End of build notes. -->'
def build_notes(repo):
    """The build notes are hand-written in BOM.md, between BS and BE. They moved there from the README on 2026-11-05."""
    f=f'{K}6502-{repo}/BOM.md'
    t=open(f,encoding='utf-8').read() if os.path.exists(f) else ''
    t=t.replace(BS_OLD,BS)
    if BS not in t: return ''
    return t[t.index(BS)+len(BS):t.index(BE)].strip('\n')
ISS={'22pF|disc-p2.5':'The silk says 22 pF; fit 20 pF. A board built with 22 pF is fine.','6551|DIP-28_W15.24mm':'The silk says 6551; fit an R6551AP.','65C51|DIP-28_W15.24mm':'The silk says 65C51; fit an R6551AP.','6581|DIP-28_W15.24mm':'The silk says 6581; fit an ARMSID.','6581|DIP_Socket-28_W11.9mm_W12.7mm_W15.24mm_W17.78mm_W18.5mm_3M_228-1277-00-0602J':'The silk says 6581; fit an ARMSID.'}
def known(repo):
    Iss=[];S=collections.OrderedDict()
    for f in sorted(glob.glob(f'{K}6502-{repo}/Hardware/*/Rev */*.kicad_pcb')):
        p=f.split('/');board,rev=p[-3],p[-2][4:];t=open(f,encoding='utf-8',newline='').read();bad=collections.defaultdict(list)
        for s,e in footprints(t):
            b=t[s:e];ref=fp_ref(b);i=A.get(f'{repo}|{board}|{rev}|{ref}')
            if not i: continue
            P={n:v for n,v,_,_ in props(b,'\t\t')};sv=re.search(r'\(property "Value"[^)]*\)\s*(?:\(unlocked yes\)\s*)?\(layer "[FB]\.SilkS"\)(?!\s*\(hide yes\))',b)
            if i in ISS and status(repo,board,rev)!='drawn' and sv: bad[ISS[i]].append(ref)
            if i in('CR2032|BAT_BAT-HLD-001-THM','BAT-HLD-001-THM|BAT_BAT-HLD-001-THM'): bad['`BAT-HLD-001-THM`, on the tested boards, is obsolete. `BAT-HLD-001-THM-TR` is its listed continuation, with no stock today and no board built with it yet.'].append(ref)
            if i=='TMS9918A|DIP-40_W15.24mm': bad['The TMS9918A is out of production, and eBay is the likely source. The VGA Card is the recommended alternative to this board.'].append(ref)
            if i=='MT8808|DIP-28_W15.24mm': bad['The MT8808 is out of production, and eBay is the likely source. The Keyboard Encoder Helper is the recommended way to handle a keyboard instead.'].append(ref)
            if i=='32pF|disc-p2.5' : bad['Fit 32 or 33 pF. 33 pF is the standard value, and it is what the tested card has.'].append(ref)
            k=f'{repo}|{board}|{rev}|{ref}'
            if k in FIT: bad['Fit 10k, not 1k. If your board came with 1k soldered here, replace it. See the build notes.' if 'smd' in (re.search(r'\n\t\t\(attr ([^)]*)\)',b) or [0,''])[1] else 'Fit 10k, not the 1k in the original files. See the build notes.'].append(ref)
            if (repo,board,rev,ref) in(('ACE','ACE Board','1.0','J5'),('COB','Sound Card','1.0','J2'),('VCS','Output Board','1.0','J1')): bad['`VDD` is the supply for a real SID at pin 28: 12 V for a 6581, 9 V for an 8580. The standard build does not provide it, and it has never been tested. Leave it unconnected with an ARMSID.'].append(ref)
            if (repo,board,rev,ref)==('KIM','Keypad Card','1.0','U3'): bad['The silk says 65C21; fit the W65C21N listed here.'].append(ref)
            if (repo,board,rev,ref)==('VCS','Input Board','1.0','U2'): bad['The silk says ATmega1284-P; fit the ATmega1284 listed here.'].append(ref)
            if k in DNP_REF: bad['Do not fit this. If your board came with it soldered, remove it. See the build notes.'].append(ref)
            if (repo,board,rev,ref) in(('COB','Backplane Pro','1.0','J10'),('VCS','Main Board','1.0','J10'),('COB','Breadboard Helper','1.0','J1')): bad['Fit a box header for a ribbon cable. The silk shows a plain header, but the holes are the same. Pin 1 is the square pad, and the notch faces the even-numbered pins.'].append(ref)
        for msg,refs in bad.items(): Iss.append((board,rev,ranges(refs),msg))
    if repo=='ACE': Iss.append(('ACE RAM Patch','1.0','','Boards were made, and testing showed the decode is wrong. Do not fit one: use Rev 1.1.'))
    return Iss
INTRO="""Every part for every board in this repository, by revision, with supplier numbers.

## How to use this

1. **Find your board and revision** in [Which revision do I have?](#which-revision-do-i-have)
2. **Read the [known issues](#known-issues)** for that revision, because they change what you buy or fit.
3. **Order from the table for your revision.** Each revision links to files you can upload to Digi-Key and Mouser. Those files are for one board, so multiply the quantities if you're building more. If a site asks which column is which, the first column is its part number and the third is the quantity. A cart only holds what that supplier sells, so check the table for anything else, such as chips from Jameco.
4. **Set the jumpers** before the first power-up. The README's [Jumpers](README.md#jumpers) section says which ones each board needs, and the table for your revision lists the shunts.

**Pre-soldered parts.** Some boards on Tindie come with their surface-mount parts already soldered. Parts marked **Yes** under Pre-soldered are the ones soldered on those boards. Check your listing, because others are sold as a bare PCB. Each revision that has such parts also has a `through-hole` cart that leaves them out. To solder a bare board yourself, use the full cart.

**Suppliers.** Every part has one set of numbers, so the same resistor is the same order line on every board. The numbers were read from Digi-Key and Mouser on 2026-11-04, and stock changes. A blank supplier cell means that supplier doesn't sell the part, or only sells it in bulk.

**The `bom.csv` files** under `Production/` are for JLCPCB assembly. They list the same parts. A blank LCSC cell there means JLCPCB doesn't place that part, and JLCPCB's "missing parts" warning about it is expected.
"""
def stat_text(repo,board,rev):
    k=f'{repo}|{board}|{rev}';st=status(repo,board,rev);t=TEST.get(k)
    if st=='made': return 'Made, tested' if t=='Yes' else ('Made, not tested yet' if t=='Not yet' else (f'Made. {t}' if t else 'Made'))
    if st=='ordered': return 'Ordered, not tested yet'
    if k in O.get('never',{}): return 'Never made'
    return 'Drawn, not made yet'
def gen(repo,readme=False):
    d=f'{K}6502-{repo}';F=sorted(glob.glob(d+'/Hardware/*/Rev */*.kicad_pcb'));B=collections.OrderedDict()
    for f in F:
        p=f.split('/');B.setdefault(p[-3],[]).append((p[-2][4:],f))
    Notes=build_notes(repo);Iss=known(repo)
    o=[f'# Bill of materials: 6502-{repo}\n',INTRO]
    o.append('## Which revision do I have?\n\nLook on the board: the silk prints the revision next to the copyright line. [REVISIONS.md](REVISIONS.md) has the facts for each one, and its history lists what changed between them.\n\n**To make a new board, make the newest revision**, and check its label first. The README\'s [Which revision to make](README.md#which-revision-to-make) explains the three labels: **Tested**, **Proven design** and **Untested**.\n\n| Board | Revision | What the silk says | Status | Label |\n|---|---|---|---|---|')
    for b,rs in B.items():
        for rev,f in rs:
            a=AUD.get((repo,b,rev),{});sl=a.get('silk_label') or '';m=re.search(r'Rev\s*\S+',sl);say=m.group(0) if m else '—'
            if b=='ROM Cart' and rev in ('1.0a','1.0b'): say=f"Rev 1.0. U1's label tells them apart: {'AT27C256 is Rev 1.0b' if rev=='1.0b' else 'AT28C256 is Rev 1.0a'}"
            o.append(f'| [{b}](#{re.sub(r"[^a-z0-9 -]","",b.lower()).replace(" ","-")}) | {rev} | {say} | {stat_text(repo,b,rev)} | {labels.cell(repo,b,rev)} |')
    o.append('\n## Known issues\n\nThese change what you buy or fit. The boards themselves stay as they were made.\n')
    if Iss:
        o.append('| Board | Revision | Parts | Issue |\n|---|---|---|---|')
        for b,r,refs,msg in Iss: o.append(f'| {b} | {r} | {refs} | {msg} |')
    else: o.append('None for parts.')
    if Notes:
        o.append('\n### Build notes\n\nHow to build each board, where it needs more than its parts list.\n')
        o.append(BS+'\n\n'+Notes+'\n\n'+BE)
    for b,rs in B.items():
        o.append(f'\n## {b}\n')
        for rev,f in reversed(rs):
            R,socks,dnp,pins=rev_rows(repo,b,rev,f);cd=f'BOM/{b}/Rev {rev}';has=any(r['presold'] for r in R)
            o.append(f'### {b} Rev {rev}\n\n{stat_text(repo,b,rev)}. {labels.cell(repo,b,rev)}.\n')
            tD=cart_lines(repo,b,rev,R,socks,pins,'digikey',False);tM=cart_lines(repo,b,rev,R,socks,pins,'mouser',False)
            write_cart(f'{d}/{cd}/digikey.csv',['Digi-Key Part Number','Manufacturer Part Number','Quantity','Customer Reference'],tD)
            write_cart(f'{d}/{cd}/mouser.csv',['Mouser Part Number','Manufacturer Part Number','Quantity','Reference'],tM)
            enc=lambda s:urllib.parse.quote(s)
            links=f'[digikey.csv]({enc(cd)}/digikey.csv), [mouser.csv]({enc(cd)}/mouser.csv)'
            if has:
                write_cart(f'{d}/{cd}/digikey-through-hole.csv',['Digi-Key Part Number','Manufacturer Part Number','Quantity','Customer Reference'],cart_lines(repo,b,rev,R,socks,pins,'digikey',True))
                write_cart(f'{d}/{cd}/mouser-through-hole.csv',['Mouser Part Number','Manufacturer Part Number','Quantity','Reference'],cart_lines(repo,b,rev,R,socks,pins,'mouser',True))
                links+=f', [digikey-through-hole.csv]({enc(cd)}/digikey-through-hole.csv), [mouser-through-hole.csv]({enc(cd)}/mouser-through-hole.csv)'
            o.append(f'Cart files: {links}\n')
            pre=' Pre-soldered |' if has else '';preb='---|' if has else ''
            o.append(f'| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |{pre}\n|---|---|---|---|---|---|---|{preb}')
            notes=collections.OrderedDict()
            for r in R:
                e=C.get(r['id'],{})
                if r['id'].startswith('BREADBOARD HEADERS'): continue
                st=STRIP.fullmatch(r['id']);name=part_name(e)
                if st: name=f"Pin header {st.group(1)}×{int(st.group(2))}, 2.54 mm, cut from a strip"
                dk,mo=e.get('digikey'),e.get('mouser')
                o.append(f"| {ranges(r['refs'])} | {len(r['refs'])} | {r['val'].replace('|','/')} | {name} | {L_dk(dk)} | {L_mo(mo)} | {other_cell(e)} |"+((' Yes |' if r['presold'] else ' |') if has else ''))
                if e.get('note') and not st: notes.setdefault(e['note'],[]).extend(r['refs'])
            for (sid,txt),refs in socks.items():
                e=C[sid];o.append(f"| {ranges(refs)} | {len(refs)} | Socket | {txt} | {L_dk(e.get('digikey'))} | {L_mo(e.get('mouser'))} | |"+(' |' if has else ''))
            for part,dk,mo,q,ref,ot in EXTRA.get((repo,b,rev),[]):
                o.append(f"| {ref} | {q} | | {part} | {L_dk(dk)} | {L_mo(mo)} | {L_ot(ot)} |"+(' |' if has else ''))
            o.append('')
            if pins: o.append('Pin headers are cut from strips, and the cart files count whole strips.\n')
            if (repo,b,rev) in EXTRA_NOTE: o.append(EXTRA_NOTE[(repo,b,rev)]+'\n')
            real=[x for x in dnp if x[1]!='SKIP']
            if real:
                why=real[0][1].replace('DNP: ','') if real[0][1].startswith('DNP') else 'see the build notes'
                o.append('**Do not fit** '+ranges([x[0] for x in real])+': '+why+'.\n')
            for n,refs in notes.items():
                if n.startswith('Do not fit'): continue
                o.append(f'- **{ranges(refs)}:** {n}')
            if notes: o.append('')
    open(d+'/BOM.md','w',encoding='utf-8').write('\n'.join(o).rstrip()+'\n')
    if readme: swap_readme(repo,set(B))
    return len(F)
def swap_readme(repo,boards):
    f=f'{K}6502-{repo}/README.md';L=open(f,encoding='utf-8').read().split('\n');o=[];i=0;inb=False;cur=None;n=0
    while i<len(L):
        l=L[i]
        if l.startswith('## '):
            inb=l.startswith('## Bill of Materials')
            o.append(l)
            if inb and not (i+2<len(L) and 'BOM.md' in L[i+2]): o+= ['','Every part for every board, by revision, is in **[BOM.md](BOM.md)**, with supplier numbers, known issues and files to upload to Digi-Key and Mouser.']
            i+=1;continue
        if inb and l.startswith('#'):
            m=re.match(r'#{3,4} (.+)',l)
            if l.startswith('### '): cur=re.sub(r' \(Rev.*\)','',m.group(1)).strip()
        if inb and (re.match(r'\| *(Reference|Part) *\|',l)):
            j=i
            while j<len(L) and L[j].startswith('|'): j+=1
            if cur in boards and not any(f'BOM.md#' in x for x in o[-12:]):
                o.append(f"Parts list: [BOM.md](BOM.md#{re.sub(r'[^a-z0-9 -]','',cur.lower()).replace(' ','-')}).")
            elif cur not in boards and cur: print('  no board for',cur)
            n+=1;i=j
            continue
        if inb and re.match(r"(This table is Rev|Rev 1\.1's designators\.|R19 is not fitted|Also needed, and not on the schematic)",l):
            i+=1;continue
        o.append(l);i+=1
    t=re.sub(r'\n{3,}','\n\n','\n'.join(o))
    if 'Building one?' not in t:
        m=re.search(r'\n## ',t);head=t[:m.start()].rstrip()
        t=head+'\n\n**Building one? Every part you need, with supplier numbers and known issues, is in [BOM.md](BOM.md).**\n'+t[m.start():]
    open(f,'w',encoding='utf-8').write(t);print(repo,'README tables replaced',n)
if __name__=='__main__':
    for r in SCOPE:
        print(r,gen(r,'--readme' in sys.argv))
