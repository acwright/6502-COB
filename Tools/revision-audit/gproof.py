#!/usr/bin/env python3
"""gproof.py REPO "Board" OLD NEW: export Gerbers and drill from both PCBs with today's kicad-cli; list layers that differ, headers stripped."""
import sys,os,re,subprocess,tempfile,hashlib
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))));from common import K
repo,board,a,b=sys.argv[1:5];KC='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def ex(rev):
    d=tempfile.mkdtemp();f=f'{K}6502-{repo}/Hardware/{board}/Rev {rev}/{board}.kicad_pcb'
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
    print('geometry',n,'lines/flashes same' if ga==gb else f'lines/flashes differ {len(ga^gb)}','regions same' if sa==sb else f'regions differ {len(set(sa)^set(sb))}')
for n in sorted(set(A)&set(B)):
    if A[n]!=B[n]:
        print('sorted-lines',n,'same' if sorted(A[n].split('\n'))==sorted(B[n].split('\n')) else 'differ')
