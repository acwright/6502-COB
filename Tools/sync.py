#!/usr/bin/env python3
"""Keeps Tools/ the same in all five repositories.

  sync.py           copy this repository's shared files into every repository beside it, and remove shared files
                    they have that this one doesn't
  sync.py --check   exit 1 if any shared file differs, or exists in only some of the repositories

Shared means every file in Tools/ except Tools/data/ (each repository's own records), Tools/work/ (generated, ignored
by git), .env, and the folders in ONE_REPO, which belong to one repository. Edit a shared tool in any repository, run
sync.py there, and commit all five."""
import os,sys,hashlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import K,THIS,present
ONE_REPO={'build-notes':'ACE'}   # Tools/<folder> that lives in one repository only
SKIP_DIRS={'data','work','__pycache__'}
SKIP_FILES={'.env','.DS_Store'}
def shared(r):
    """{path inside Tools/: sha1} for one repository."""
    top=f'{K}6502-{r}/Tools';out={}
    for d,dirs,fs in os.walk(top):
        rel=os.path.relpath(d,top)
        if rel=='.': dirs[:]=[x for x in dirs if x not in SKIP_DIRS and x not in ONE_REPO]
        else: dirs[:]=[x for x in dirs if x!='__pycache__']
        for f in fs:
            if f in SKIP_FILES or f.endswith('.pyc'): continue
            p=os.path.normpath(os.path.join(rel,f));out[p]=hashlib.sha1(open(os.path.join(d,f),'rb').read()).hexdigest()
    return out
def check():
    R=present();S={r:shared(r) for r in R};bad=[]
    for p in sorted(set().union(*S.values())):
        have={r:S[r].get(p) for r in R}
        if len(set(have.values()))>1:
            missing=[r for r,h in have.items() if h is None]
            bad.append(f'Tools/{p}: '+(f'missing in {", ".join(missing)}' if missing else 'differs: '+', '.join(f'{r} {h[:7]}' for r,h in have.items())))
    for b in bad: print(b)
    print(f'Tools/: {len(S[THIS])} shared files in {len(R)} repositories, {len(bad)} differences');return not bad
def copy():
    import shutil
    mine=shared(THIS);n=0
    for r in present():
        if r==THIS: continue
        theirs=shared(r)
        for p,h in mine.items():
            if theirs.get(p)!=h:
                dst=f'{K}6502-{r}/Tools/{p}';os.makedirs(os.path.dirname(dst),exist_ok=True)
                shutil.copy2(f'{K}6502-{THIS}/Tools/{p}',dst);print(r,'copied',p);n+=1
        for p in set(theirs)-set(mine):
            os.remove(f'{K}6502-{r}/Tools/{p}');print(r,'removed',p);n+=1
    print(n,'changes');return True
if __name__=='__main__':
    sys.exit(0 if (check() if '--check' in sys.argv else copy()) else 1)
