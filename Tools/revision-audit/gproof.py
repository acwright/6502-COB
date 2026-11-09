#!/usr/bin/env python3
"""gproof.py REPO "Board" OLD NEW [--no-fill]: export Gerbers and drill from both PCBs with today's kicad-cli; list layers that differ, headers stripped.
A revision may be REV@COMMIT, read from git: "1.1@HEAD 1.1" proves a revision fixed in place against its last commit.
--no-fill leaves the pours' fills out of both, for a change that refills them (KICAD.md K28: the outline moved, so the
pours were refilled): the copper layers then show whether any track, pad or via moved."""
import sys,os,re,subprocess,tempfile,hashlib,shutil,glob
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))));from common import K
NOFILL='--no-fill' in sys.argv;sys.argv=[x for x in sys.argv if x!='--no-fill']
repo,board,a,b=sys.argv[1:5];KC='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def at_commit(f,ref):
    """The PCB and its project as they were at a git commit, in a scratch folder."""
    d=tempfile.mkdtemp();out=f'{d}/{board}.kicad_pcb';top=f'{K}6502-{repo}'
    for src,dst in ((f,out),(f[:-len('.kicad_pcb')]+'.kicad_pro',out[:-len('.kicad_pcb')]+'.kicad_pro')):
        x=subprocess.run(['git','show',f'{ref}:{os.path.relpath(src,top)}'],cwd=top,capture_output=True)
        if x.returncode: raise SystemExit(f'git show {ref}:{os.path.relpath(src,top)} failed')
        open(dst,'wb').write(x.stdout)
    return out
def unfilled(f):
    """A copy of the PCB, with its project, whose pours have no fill."""
    sys.path.insert(0,os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'cardedge'));import kpcb
    t=open(f,encoding='utf-8',newline='').read();sp=[]
    def walk(n):
        for k in n.kids:
            if k.name=='filled_polygon': sp.append(k.span)
            else: walk(k)
    walk(kpcb.parse(t))
    for s,e in sorted(sp,reverse=True): t=t[:s]+t[e:]
    d=tempfile.mkdtemp();out=f'{d}/{board}.kicad_pcb';open(out,'w',encoding='utf-8',newline='').write(t)
    for x in glob.glob(f[:-len('.kicad_pcb')]+'.kicad_pro'): shutil.copy(x,d)
    return out
def ex(rev):
    rev,_,ref=rev.partition('@')
    d=tempfile.mkdtemp();f=f'{K}6502-{repo}/Hardware/{board}/Rev {rev}/{board}.kicad_pcb'
    if ref: f=at_commit(f,ref)
    if NOFILL: f=unfilled(f)
    subprocess.run([KC,'pcb','export','gerbers','-o',d+'/',f],capture_output=True);subprocess.run([KC,'pcb','export','drill','-o',d+'/',f],capture_output=True)
    out={}
    for n in os.listdir(d):
        if n.endswith('.gbrjob'): continue
        t=open(f'{d}/{n}',encoding='latin-1').read()
        t=re.sub(r'[^\n]*(CreationDate|Created by|TF\.ProjectId|TF\.GenerationSoftware|DRILL file|Date)[^\n]*\n','',t)
        out[n.replace(board+'-','')]=t
    return out
A,B=ex(a),ex(b)
for n in sorted(set(A)|set(B)):
    if A.get(n)!=B.get(n): print('DIFF',n)
print('same:',' '.join(n for n in sorted(A) if A.get(n)==B.get(n)))
# geometry: the audit's parser, lines and flashes as sets, and filled regions
src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'audit.py')).read()
ns={};exec(src[src.index('def gerb('):src.index('def drill(')],{'re':re,'collections':__import__('collections'),'__builtins__':__builtins__},ns)
for n in sorted(set(A)&set(B)):
    if A[n]==B[n] or not n.endswith(('gtl','gbl','gm1','gts','gbs','gtp','gbp')): continue
    pa,pb=tempfile.mktemp(),tempfile.mktemp();open(pa,'w',encoding='latin-1').write(A[n]);open(pb,'w',encoding='latin-1').write(B[n])
    ga,gb=ns['gerb'](pa),ns['gerb'](pb);ra,rb=ns['regions'](pa),ns['regions'](pb)
    sa=sorted(tuple((round(x,3),round(y,3)) for x,y in p) for p in ra);sb=sorted(tuple((round(x,3),round(y,3)) for x,y in p) for p in rb)
    pts=[q for e in ga^gb for q in ([e[1:]] if e[0]=='c' else e[1:])]+[q for p in set(sa)^set(sb) for q in p]
    where=f', all within x {min(x for x,_ in pts):.2f}–{max(x for x,_ in pts):.2f}, y {min(-y for _,y in pts):.2f}–{max(-y for _,y in pts):.2f} (the PCB\'s frame)' if pts else ''
    print('geometry',n,'lines/flashes same' if ga==gb else f'lines/flashes differ {len(ga^gb)}','regions same' if sa==sb else f'regions differ {len(set(sa)^set(sb))}',where)
for n in sorted(set(A)&set(B)):
    if A[n]!=B[n]:
        print('sorted-lines',n,'same' if sorted(A[n].split('\n'))==sorted(B[n].split('\n')) else 'differ')
