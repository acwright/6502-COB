"""Run in KiCad's own Python: resave.py LIB.pretty '{"old": "new", ...}'
Loads every footprint in the library and saves it again in KiCad's current format, under its new name where the
mapping gives one. Merged names (two old names, one new) keep the first one in sorted order.
The caller says which survives by listing it first in its mapping's merge order."""
import sys,os,json,pcbnew
lib,m=sys.argv[1],json.loads(sys.argv[2])
names=sorted(f[:-10] for f in os.listdir(lib) if f.endswith('.kicad_mod'))
done=set()
for n in names:
    new=m.get(n,n)
    if new in done and new==n: continue   # already written, from a part merged into it
    if new in done:
        os.remove(f'{lib}/{n}.kicad_mod');print('renamed',n,'->',new,'(merged)');continue
    fp=pcbnew.FootprintLoad(lib,n)
    if fp is None: raise SystemExit(f'cannot load {n}')
    fp.SetFPID(pcbnew.LIB_ID('',new))
    if new!=n:
        if os.path.exists(f'{lib}/{new}.kicad_mod') and new not in names: raise SystemExit(f'{new} exists')
        os.remove(f'{lib}/{n}.kicad_mod');print('renamed',n,'->',new)
    pcbnew.FootprintSave(lib,fp);done.add(new)
