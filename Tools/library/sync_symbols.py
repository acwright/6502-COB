#!/usr/bin/env python3
"""Gives every repo's "6502 Parts" symbol library every symbol its schematics use, each one the same in every repo.

A symbol's canonical definition comes from a library (ACE, then KIM, VCS, DEV, COB), or from PICK where the
copies disagree for a reason, or, for a symbol no library had, from the cached copy in the newest revision that
uses it. A schematic keeps its own cached copy: KiCad reports a difference as lib_symbol_mismatch in ERC, and a
board that was made is never changed.
"""
import os,re,glob,collections,sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))));import common;from common import K,SCOPE,files,load,save
REPOS=common.scope(['--all']);ORDER=('ACE','KIM','VCS','DEV','COB')
# Where the libraries disagree. W65C02S VPB is an output; the 65C22's D0-D7 are bidirectional (both as in ACE's).
# VCS's PS2 Jack names its footprint. KIM's 6502 Card Edge is the one most boards have cached.
PICK={'65C02':'ACE','65C22':'ACE','PS2 Jack':'VCS','6502 Card Edge':'KIM','PIA 6521':'cache','CompactFlash Socket Plated Pegs':'cache'}
# The PIA's two old symbols (65C21 and W65C21N) became one; the KIM Board's W65C21N has the right pin types.
CACHE_FROM={'PIA 6521':'6502-KIM/Hardware/KIM Board/Rev 1.0/KIM Board.kicad_sch','CompactFlash Socket Plated Pegs':'6502-COB/Hardware/Storage Card/Rev 1.0/Storage Card.kicad_sch'}
def blocks(t,indent):
    out=collections.OrderedDict()
    for m in re.finditer(r'\n'+indent+r'\(symbol "([^"]+)"',t):
        a=m.start()+1;d=0;j=a;q=False
        while True:
            c=t[j]
            if c=='"' and t[j-1]!='\\': q=not q
            elif not q:
                if c=='(':d+=1
                elif c==')':
                    d-=1
                    if d==0:break
            j+=1
        out.setdefault(m.group(1),t[a:j+1].lstrip('\t'))
    return out
def nat(s): return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)',s)]
lib={r:blocks(open(K+f'6502-{r}/Libraries/6502 Parts.kicad_sym',encoding='utf-8').read(),'\t') for r in REPOS}
used=collections.defaultdict(set);cache={}
for f in sorted(files('Hardware/*/Rev */*.kicad_sch',REPOS),key=lambda f:nat(f.split('/Rev ')[1])):
    r=f.split('/6502-')[1].split('/')[0];t=open(f,encoding='utf-8').read()
    used[r]|={x for x in re.findall(r'\(lib_id "6502 Parts:([^"]+)"\)',t)}
    ls=t[t.find('(lib_symbols'):]
    for n,b in blocks(ls,'\t\t').items():
        if n.startswith('6502 Parts:'):
            x=n[11:];used[r].add(x)
            cache[x]=re.sub(r'\n\t','\n',b).replace(f'(symbol "6502 Parts:{x}"',f'(symbol "{x}"',1)   # the newest revision wins
cache_of={}
for x,f in CACHE_FROM.items():
    t=open(K+f,encoding='utf-8').read();b=blocks(t[t.find('(lib_symbols'):],'\t\t')['6502 Parts:'+x]
    cache_of[x]=re.sub(r'\n\t','\n',b).replace(f'(symbol "6502 Parts:{x}"',f'(symbol "{x}"',1)
canon={}
for x in set().union(*used.values())|{n for r in REPOS for n in lib[r]}:
    src=PICK.get(x)
    if src=='cache': canon[x]=cache_of[x];continue
    if src: canon[x]=lib[src][x];continue
    for r in ORDER:
        if x in lib[r]: canon[x]=lib[r][x];break
    else: canon[x]=cache[x]
head=open(K+'6502-KIM/Libraries/6502 Parts.kicad_sym',encoding='utf-8').read();head=head[:head.find('\n\t(symbol')]
for r in REPOS:
    names=sorted(used[r]|set(lib[r]),key=str.lower)
    t=head+''.join('\n\t'+canon[x] for x in names)+'\n)\n'
    p=K+f'6502-{r}/Libraries/6502 Parts.kicad_sym';old=open(p,encoding='utf-8').read()
    if t!=old: open(p,'w',encoding='utf-8').write(t)
    print(r,len(names),'symbols;',len(set(names)-set(lib[r])),'added')
