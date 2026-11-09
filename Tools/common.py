"""Where things are, for every tool in Tools/.

Tools/ is the same in all five AC6502 KiCad repositories (6502-ACE, -COB, -DEV, -KIM and -VCS), apart from
Tools/data/, which holds this repository's own records, and any folder listed in sync.py as belonging to one
repository. The five repositories sit side by side in one folder, as GitHub clones them.

A tool acts on this repository by default. With --all it acts on all five, which must then be checked out beside this
one.

  ROOT    this repository                       K      the folder that holds the five, ending in '/'
  THIS    'COB' for 6502-COB                    ALL    the five short names
  SCOPE   the repositories this run acts on: (THIS,), or ALL with --all

Data. Each repository's records live in its own Tools/data/*.json, keyed by repository ('COB|Board|1.0' or an
entry's "repo"), so a change to one board's records commits only that repository. load() merges every repository
checked out beside this one; save() writes each repository's share back, touching only files whose content changed.
Generated files go to Tools/work/, which git ignores.
"""
import os,sys,json,glob
TOOLS=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(TOOLS)
K=os.path.dirname(ROOT)+'/'
ALL=('ACE','COB','DEV','KIM','VCS')
THIS=os.path.basename(ROOT).split('-')[-1]
if THIS not in ALL: raise SystemExit(f'Tools/ must sit in one of 6502-{"/".join(ALL)}, not in {ROOT}')
WORK=os.path.join(TOOLS,'work')
KC='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
KPY='/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3'
def present():
    """The five that are checked out beside this one, in the usual order."""
    return tuple(r for r in ALL if os.path.isdir(f'{K}6502-{r}/Hardware'))
def scope(argv=None):
    argv=sys.argv if argv is None else argv
    if '--all' in argv:
        missing=[r for r in ALL if r not in present()]
        if missing: raise SystemExit(f'--all needs every repository beside this one; missing: {", ".join("6502-"+r for r in missing)}')
        return ALL
    return (THIS,)
SCOPE=scope()
ALLFLAG=['--all'] if SCOPE==ALL else []   # pass on to a tool run as a subprocess
def repo_dir(r): return f'{K}6502-{r}'
def files(pattern,repos=None):
    """glob(pattern) inside each repository of the scope, sorted: files('Hardware/*/Rev */*.kicad_pcb')."""
    out=[]
    for r in (repos or SCOPE): out+=glob.glob(f'{K}6502-{r}/{pattern}')
    return sorted(out)
def repo_of(path):
    """'COB' for any path inside 6502-COB."""
    p=os.path.abspath(path)
    for r in ALL:
        if p.startswith(f'{K}6502-{r}/'): return r
    return None

# --- data -----------------------------------------------------------------------------------------------------------
# How each data file splits by repository. 'sections': a dict of sections, each a dict or list keyed by repository
# (orders.json). 'flat': a dict keyed by repository. 'list': a list of entries, each with a "repo". Keys that start
# with '_' are notes about the file, kept in every copy.
DATA={'orders.json':'sections','offboard.json':'sections','assignment.json':'flat','rendered.json':'flat',
      'tindie.json':'flat','jumpers.json':'list','audit.json':'list','cardedge.json':'sections'}
GENERATED={'audit.json'}   # written by a tool into Tools/work/, never committed
def _path(r,name): return f'{K}6502-{r}/Tools/{"work" if name in GENERATED else "data"}/{name}'
def _key_repo(k): return k.split('|',1)[0]
def _share(obj,r,kind):
    if kind=='list': return [e for e in obj if e.get('repo')==r]
    if kind=='flat': return {k:v for k,v in obj.items() if k.startswith('_') or _key_repo(k)==r}
    out={}
    for s,v in obj.items():
        if s.startswith('_'): out[s]=v
        elif isinstance(v,dict): out[s]={k:x for k,x in v.items() if _key_repo(k)==r}
        elif isinstance(v,list): out[s]=[k for k in v if _key_repo(k)==r]
        else: out[s]=v
    return out
def load(name,repos=None):
    """One data file, merged across the repositories checked out here (or the ones named)."""
    kind=DATA[name];out=[] if kind=='list' else {}
    for r in (repos or present()):
        p=_path(r,name)
        if not os.path.exists(p):
            if name in GENERATED and r in SCOPE: raise SystemExit(f'{p} is missing: run Tools/revision-audit/audit.py{" --all" if len(SCOPE)>1 else ""} first')
            continue
        d=json.load(open(p,encoding='utf-8'))
        if kind=='list': out+=d
        elif kind=='flat': out.update(d)
        else:
            for s,v in d.items():
                if s.startswith('_') or not isinstance(v,(dict,list)): out.setdefault(s,v)
                elif isinstance(v,dict): out.setdefault(s,{}).update(v)
                else: out.setdefault(s,[]).extend(x for x in v if x not in out.get(s,[]))
    return out
def dumps(obj): return json.dumps(obj,indent=1,ensure_ascii=False)+'\n'
def save(name,obj,repos=None):
    """Write each repository's share of obj into its own file, where that changed. Returns the files written."""
    kind=DATA[name];wrote=[]
    for r in (repos or present()):
        p=_path(r,name);new=dumps(_share(obj,r,kind))
        old=open(p,encoding='utf-8').read() if os.path.exists(p) else None
        if old!=new:
            os.makedirs(os.path.dirname(p),exist_ok=True);open(p,'w',encoding='utf-8').write(new);wrote.append(p)
    return wrote
