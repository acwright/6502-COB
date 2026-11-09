#!/usr/bin/env python3
"""Front and back images of a board revision, all made the same way.

  python3 render.py [--all]             every revision in this repository, or in all five
  python3 render.py COB "Serial Card"   every revision of one board
  python3 render.py COB "Serial Card" 1.0 [--out DIR]

Writes Front.png and Back.png (white background) and Front Transparent.png and Back Transparent.png
to CAD/Images/<Board>/Rev X/. Each render uses a temporary copy of the project: the copy gets a stackup with
black solder mask and white silk, as every board is made, over FR4 in its own pale colour, which shows wherever
there is no mask, such as a card's tab. The real KiCad files aren't touched.
"""
import argparse,glob,os,re,shutil,subprocess,sys,tempfile
from PIL import Image
KC='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))));import common;from common import K as BASE,load,save
CANVAS=(2400,1600)     # every image is this size
MARGIN=0.06            # empty space around the board, as a fraction of the canvas
RENDER=(4800,3200)     # rendered larger, then scaled down for clean edges
FINISH=os.environ.get('BOARD_FINISH','HAL lead-free')
MASK='#0C0C0CF4'       # just under opaque: black, with the traces faintly visible, as on the real boards
STACKUP='''(stackup
\t\t\t(layer "F.SilkS" (type "Top Silk Screen") (color "White"))
\t\t\t(layer "F.Paste" (type "Top Solder Paste"))
\t\t\t(layer "F.Mask" (type "Top Solder Mask") (color "%s") (thickness 0.01))
\t\t\t(layer "F.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 1" (type "core") (thickness 1.51) (material "FR4") (color "FR4 natural") (epsilon_r 4.5) (loss_tangent 0.02))
\t\t\t(layer "B.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "B.Mask" (type "Bottom Solder Mask") (color "%s") (thickness 0.01))
\t\t\t(layer "B.Paste" (type "Bottom Solder Paste"))
\t\t\t(layer "B.SilkS" (type "Bottom Silk Screen") (color "White"))
\t\t\t(copper_finish "%s")
\t\t\t(dielectric_constraints no)
\t\t)
\t''' % (MASK,MASK,FINISH)
def block_end(t,i):
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
def with_stackup(t):
    m=re.search(r'\(stackup\b',t)
    if m: return t[:m.start()]+STACKUP.rstrip()+t[block_end(t,m.start()):]
    m=re.search(r'\(setup\b\s*',t)
    if not m: raise SystemExit('no setup block')
    return t[:m.end()]+STACKUP+t[m.end():]
def fit(img):
    box=img.getchannel('A').getbbox()
    if not box: raise SystemExit('empty render')
    b=img.crop(box);W,H=CANVAS;mw=int(W*MARGIN);s=min((W-2*mw)/b.width,(H-2*mw)/b.height)
    b=b.resize((max(1,round(b.width*s)),max(1,round(b.height*s))),Image.LANCZOS)
    o=Image.new('RGBA',CANVAS,(0,0,0,0));o.paste(b,((W-b.width)//2,(H-b.height)//2));return o
def one(repo,board,rev,out=None):
    root=BASE+'6502-'+repo;src=f'{root}/Hardware/{board}/Rev {rev}';d=tempfile.mkdtemp(prefix='render-')
    try:
        h=f'{d}/Hardware/x/y';os.makedirs(d+'/Hardware/x');shutil.copytree(src,h,ignore=shutil.ignore_patterns('*-backups','production','*.step'))
        for l in('Libraries','Models'):
            if os.path.exists(f'{root}/{l}'): os.symlink(f'{root}/{l}',f'{d}/{l}')
        if os.path.exists(f'{root}/CAD'): os.symlink(f'{root}/CAD',f'{d}/CAD')
        p=f'{h}/{board}.kicad_pcb';t=open(p,encoding='utf8',errors='surrogateescape',newline='').read();open(p,'w',encoding='utf8',errors='surrogateescape',newline='').write(with_stackup(t))
        dest=out or f'{root}/CAD/Images/{board}/Rev {rev}';os.makedirs(dest,exist_ok=True)
        for side,name in(('top','Front'),('bottom','Back')):
            raw=f'{d}/{name}.png'
            r=subprocess.run([KC,'pcb','render','--side',side,'--width',str(RENDER[0]),'--height',str(RENDER[1]),'--quality','basic','--background','transparent','--use-board-stackup-colors','--zoom','1.0','-o',raw,p],capture_output=True,text=True)
            if not os.path.exists(raw): raise SystemExit(f'{board} {rev} {side}: {r.stdout[-200:]} {r.stderr[-200:]}')
            im=fit(Image.open(raw).convert('RGBA'))
            im.save(f'{dest}/{name} Transparent.png',optimize=True)
            w=Image.new('RGBA',CANVAS,'white');w.alpha_composite(im);w.convert('RGB').save(f'{dest}/{name}.png',optimize=True)
    finally: shutil.rmtree(d,ignore_errors=True)
    if not out: stamp(repo,board,rev)
def visible(t):
    """What an image shows: the PCB without UUIDs and supplier fields. derived-check.py compares this with
    Tools/data/rendered.json."""
    import hashlib
    return hashlib.sha1(re.sub(r'\(uuid "[^"]*"\)|\(property "(?:Digikey|Mouser|Jameco|LCSC|Other)"[\s\S]*?\n\t\t\)','',t).encode()).hexdigest()
def stamp(repo,board,rev):
    R=load('rendered.json')
    t=open(f'{BASE}6502-{repo}/Hardware/{board}/Rev {rev}/{board}.kicad_pcb',encoding='utf-8',newline='').read()
    R[f'{repo}|{board}|{rev}']=visible(t);save('rendered.json',dict(sorted(R.items())),repos=(repo,))
def revisions(repos):
    for repo in repos:
        for f in sorted(glob.glob(f'{BASE}6502-{repo}/Hardware/*/Rev */*.kicad_pcb')):
            yield repo,f.split('/')[-3],f.split('/')[-2][4:]
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('repo',nargs='?');a.add_argument('board',nargs='?');a.add_argument('rev',nargs='?');a.add_argument('--out');a.add_argument('--all',action='store_true');x=a.parse_args()
    n=0
    for repo,board,rev in revisions((x.repo,) if x.repo else common.SCOPE):
        if (x.repo and repo!=x.repo) or (x.board and board!=x.board) or (x.rev and rev!=x.rev): continue
        one(repo,board,rev,x.out);n+=1;print(repo,board,rev,flush=True)
    print(n,'revisions')
