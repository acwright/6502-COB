#!/usr/bin/env python3
"""Delete the tracks and vias KiCad's own DRC calls dangling, on the named nets only, until none are left.
  drcprune.py PCB NET [NET...]"""
import sys,re,json,subprocess,tempfile
KC='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
pcb,nets=sys.argv[1],set(sys.argv[2:])
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
total=0
for rnd in range(30):
    o=tempfile.mktemp(suffix='.json');subprocess.run([KC,'pcb','drc','--severity-all','--format','json','-o',o,pcb],capture_output=True)
    d=json.load(open(o));uu=[]
    for v in d['violations']:
        if v['type'] not in('track_dangling','via_dangling'): continue
        for i in v['items']:
            m=re.search(r'\[([^\]]*)\]',i['description'])
            if m and m.group(1) in nets: uu.append(i['uuid'])
    if not uu: break
    t=open(pcb,encoding='utf-8',newline='').read();spans=[]
    for u in set(uu):
        k=t.find(f'(uuid "{u}")')
        if k<0: continue
        s=t.rfind('\n\t(',0,k);head=t[s+3:s+12]
        if not head.startswith(('segment','via','arc')): raise SystemExit(f'{u} is a {head}')
        spans.append((s,blk(t,s+2)))
    for s,e in sorted(spans,reverse=True): t=t[:s]+t[e:]
    open(pcb,'w',encoding='utf-8',newline='').write(t);total+=len(spans);print('round',rnd+1,'removed',len(spans))
print('removed',total)
