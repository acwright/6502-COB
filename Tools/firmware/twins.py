#!/usr/bin/env python3
"""Checks firmware kept as copies in more than one repository (twins.json).

  twins.py [--all]    exit 1 if a copy differs from its twin anywhere but the files it may differ in, or a tracked
                      .uf2 wasn't built from the sources beside it

A pair is checked when one of its copies is in this run's scope (this repository, or all five with --all) and every
copy's repository is cloned beside this one; otherwise it's reported as skipped. derived-check.py runs it.

The .uf2 check reads the source hash the build stamps in ("AC6502-SRC:" and 64 hex digits) and compares it with the
hash of the files beside it, worked out as the firmware's cmake/source_hash.cmake does: product.h, CMakeLists.txt,
CMakePresets.json and everything under cmake/, core/ and rp2350/ but .DS_Store, sorted by path; one line per file,
"<sha256>  <path>\\n"; the SHA-256 of those lines. The two must stay the same."""
import os,re,sys,json,struct,hashlib
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import K,SCOPE,present

HERE=os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS={'build','__pycache__','.vscode'}
SKIP_FILES={'.DS_Store'}
HASHED_FILES=('product.h','CMakeLists.txt','CMakePresets.json')
HASHED_DIRS=('cmake','core','rp2350')
MARKER=re.compile(rb'AC6502-SRC:([0-9a-f]{64})')

def sha256(path): return hashlib.sha256(open(path,'rb').read()).hexdigest()

def listing(folder):
    """{relative path: sha256} of every file in a copy, but the build folder and the editor's leavings."""
    out={}
    for d,dirs,fs in os.walk(folder):
        dirs[:]=[x for x in dirs if x not in SKIP_DIRS]
        for f in fs:
            if f in SKIP_FILES: continue
            p=os.path.join(d,f);out[os.path.relpath(p,folder).replace(os.sep,'/')]=sha256(p)
    return out

def source_hash(folder):
    """The hash cmake/source_hash.cmake stamps into a build of this folder."""
    files=[f for f in HASHED_FILES]
    for top in HASHED_DIRS:
        for d,dirs,fs in os.walk(os.path.join(folder,top)):
            files+=[os.path.relpath(os.path.join(d,f),folder).replace(os.sep,'/') for f in fs if f not in SKIP_FILES]
    lines=''.join(f'{sha256(os.path.join(folder,f))}  {f}\n' for f in sorted(files))
    return hashlib.sha256(lines.encode()).hexdigest()

def uf2_hash(path):
    """The source hash stamped into a .uf2, or None. The payloads are put back in address order first, so a marker
    split across two blocks is still found."""
    data=open(path,'rb').read();blocks=[]
    for i in range(0,len(data)-511,512):
        m0,m1,_flags,addr,size=struct.unpack_from('<5I',data,i)
        if m0!=0x0A324655 or m1!=0x9E5D5157: raise ValueError(f'{path}: not a UF2 file (block {i//512})')
        blocks.append((addr,data[i+32:i+32+size]))
    m=MARKER.search(b''.join(b for _,b in sorted(blocks,key=lambda x:x[0])))
    return m.group(1).decode() if m else None

def check_pair(pair):
    faults=[];copies=pair['copies'];have=present()
    missing=[r for r in copies if r not in have]
    if missing:
        print(f'{pair["name"]}: skipped, needs 6502-{", 6502-".join(missing)} beside this repository');return faults
    folders={r:f'{K}6502-{r}/{p}' for r,p in copies.items()}
    for r,f in folders.items():
        if not os.path.isdir(f): faults.append(f'{r}: {copies[r]} is missing')
    if faults: return faults
    own={r:pair.get('uf2',{}).get(r) for r in copies}
    L={r:{p:h for p,h in listing(f).items() if p!=own[r]} for r,f in folders.items()}
    allowed=set(pair.get('differ',[]))
    first=next(iter(copies))
    for r in copies:
        if r==first: continue
        for p in sorted(set(L[first])|set(L[r])):
            a,b=L[first].get(p),L[r].get(p)
            if p in allowed:
                if a is None or b is None: faults.append(f'{p}: must exist in both copies (missing in {r if b is None else first})')
            elif a is None or b is None:
                faults.append(f'{p}: only in {first if b is None else r} ({copies[first] if b is None else copies[r]})')
            elif a!=b:
                faults.append(f'{p}: differs between {first} and {r}')
    for r,f in folders.items():
        name=own[r]
        if not name: continue
        path=os.path.join(f,name)
        if not os.path.exists(path):
            if pair.get('uf2_required'): faults.append(f'{r}: {copies[r]}/{name} is missing')
            continue
        stamped,want=uf2_hash(path),source_hash(f)
        if stamped is None: faults.append(f'{r}: {name} has no source hash')
        elif stamped!=want: faults.append(f'{r}: {name} was built from other sources ({stamped[:12]}, the files give {want[:12]}); rebuild it')
    print(f'{pair["name"]}: {len(L[first])} files in each copy, {len(faults)} faults')
    return faults

def main():
    pairs=json.load(open(os.path.join(HERE,'twins.json')))['pairs'];faults=[]
    for pair in pairs:
        if not set(pair['copies'])&set(SCOPE): continue
        faults+=[f'{pair["name"]}: {x}' for x in check_pair(pair)]
    for x in faults: print(x)
    return not faults

if __name__=='__main__':
    sys.exit(0 if main() else 1)
