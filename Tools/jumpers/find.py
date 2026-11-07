"""Every jumper on every revision, read from the schematics' netlists: solder jumpers, and pin headers that take a
shunt. Used by check.py; prints them when run."""
import os,re,glob,subprocess,tempfile,collections,sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))));import common;from common import K,SCOPE,files,load,save
KC='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
# pin headers that are connectors, not jumpers
NOT_JUMPER=re.compile(r'^(VCC|AUDIO|POWER LED|RESET SW|RESET_SW|VDD|SID VDD|BANK ADDR|PANEL|ETHERNET|VBAT|ACT LED|SPEAKER|KEYBOARD|PADDLES|STORAGE|6502 Bus|Conn_01x20|IO|PORT A|PORT B|HVSYNC|GPIO|AUX|SPI|VERA Module|SERIAL|USB HOST)$')
NOT_JUMPER_REF={('COB','Prototype Card','J3')}   # the decoder's outputs, for wires
def netlist(sch):
    o=tempfile.mktemp(suffix='.net');subprocess.run([KC,'sch','export','netlist','-o',o,sch],capture_output=True)
    t=open(o).read();os.remove(o);comps={}
    for blk in re.split(r'\n\t\t\(comp\n',t[:t.index('(libparts')])[1:]:
        r=re.search(r'\(ref "([^"]*)"',blk).group(1);v=re.search(r'\(value "([^"]*)"',blk).group(1);fp=re.search(r'\(footprint "([^"]*)"',blk)
        comps[r]=(v,fp.group(1) if fp else '')
    return comps
def jumpers(repo,board,rev,comps):
    out={}
    for r,(v,fp) in comps.items():
        if r.startswith('JP') or 'SolderJumper' in fp:
            out[r]=('open' if 'Open' in fp else 'bridged' if 'Bridged' in fp else '?',v)
        elif r.startswith('J') and 'PinHeader' in fp and not NOT_JUMPER.match(v) and (repo,board,r) not in NOT_JUMPER_REF:
            out[r]=('header',v)
    return out
def all_jumpers():
    res={}
    for f in files('Hardware/*/Rev */*.kicad_sch'):
        p=f.split('/');repo,board,rev=p[-5].split('-')[-1],p[-3],p[-2][4:]
        j=jumpers(repo,board,rev,netlist(f))
        if j: res[(repo,board,rev)]=j
    return res
if __name__=='__main__':
    for k,v in all_jumpers().items(): print('|'.join(k),sorted((r,s,val) for r,(s,val) in v.items()))
