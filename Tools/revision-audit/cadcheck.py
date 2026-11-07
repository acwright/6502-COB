#!/usr/bin/env python3
"""Every top and enclosure top sits under a revision of its board, and fits it. Read-only."""
import os,glob,sys,re
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'cadfit.py')).read().split("if __name__=='__main__':")[0])
bad=0;n=0
for repo in REPOS:
    os.chdir(BASE+repo)
    for kind,pat in(('Tops','CAD/Tops/*/Rev */*Top.svg'),('Enclosures','CAD/Enclosures/*/Rev */Top.svg')):
        for f in sorted(glob.glob(pat)):
            p=f.split('/');b,rev=p[2],p[3];pcb=f'Hardware/{b}/{rev}/{b}.kicad_pcb';n+=1
            if not os.path.exists(pcb): print('NO PCB',repo,f);bad+=1;continue
            c=pcb_holes(pcb);h=svg_holes(open(f,errors='replace').read());ok=fits(h,c)
            # DB25 Helper's old enclosure top has only two screw holes, both on the board's holes.
            if f=='CAD/Enclosures/DB25 Helper/Rev 1.0/Top.svg': ok=len(h)==2
            if ok is False: print('DOES NOT FIT',repo,f);bad+=1
    for f in glob.glob('CAD/Tops/*.svg')+glob.glob('CAD/Tops/*.lbrn2')+glob.glob('CAD/Enclosures/*/*.svg'):
        print('UNVERSIONED',repo,f);bad+=1
print(f'{n} checked, {bad} problems')
