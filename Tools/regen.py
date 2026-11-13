#!/usr/bin/env python3
"""Regenerates what one board revision derives, after a schematic or PCB edit.

  python3 regen.py [REPO] "Board" REV [--no-production | --production-only]   REPO defaults to this repository

Writes, in the repo:
  Production/<Board>/Rev X/  the zip, bom.csv, positions.csv, designators.csv and netlist.ipc, from the Fabrication
                             Toolkit run headlessly on a scratch copy (Tools/production/toolkit.py), with the same
                             settings and plugin as its window, so both give the same files (Tools/production/README.md).
                             The plugin names the zip from the title block, as the window does. For a revision that was
                             made or ordered, only bom.csv: its zip is what JLCPCB received and never changes.
  Schematics/<Board>/Rev X/<Board>.pdf
  CAD/Models/<Board>/Rev X/<Board>.step
  CAD/Images/<Board>/Rev X/  through Tools/board-images/render.py

Then run Tools/bom/gen_bom.py, Tools/revision-audit/register.py and Tools/derived-check.py.
"""
import os,sys,glob,shutil,subprocess,tempfile
H=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,H+'/bom');sys.path.insert(0,H)
from common import repo_dir,THIS
from apply import status
KC='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
KPY='/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3'
MODELS='/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels'
a=[x for x in sys.argv[1:] if not x.startswith('--')];repo,board,rev=a if len(a)==3 else [THIS,*a];R=repo_dir(repo)
src=f'{R}/Hardware/{board}/Rev {rev}';pcb=f'{src}/{board}.kicad_pcb';sch=f'{src}/{board}.kicad_sch'
env=dict(os.environ,KICAD10_3DMODEL_DIR=MODELS,KICAD9_3DMODEL_DIR=MODELS)
def run(*c,**k):
    x=subprocess.run(c,capture_output=True,text=True,**k)
    if x.returncode: raise SystemExit(f'failed: {" ".join(c)}\n{x.stdout[-800:]}\n{x.stderr[-800:]}')
    return x
st=status(repo,board,rev)
if st=='drawn' and '--no-production' not in sys.argv:
    tmp=tempfile.mkdtemp();t=f'{tmp}/Hardware/{board}/Rev {rev}';shutil.copytree(src,t)
    for d in ('Libraries','Models'):
        if os.path.exists(f'{R}/{d}'): os.symlink(f'{R}/{d}',f'{tmp}/{d}')
    pd=f'{R}/Production/{board}/Rev {rev}';old=glob.glob(f'{pd}/*.zip')
    run(KPY,H+'/production/toolkit.py',f'{t}/{board}.kicad_pcb',env=env)
    out=f'{t}/production'
    made=sorted(os.listdir(out));zips=[n for n in made if n.endswith('.zip')];need=['bom.csv','positions.csv','designators.csv','netlist.ipc']
    if len(zips)!=1 or any(n not in made for n in need): raise SystemExit(f'toolkit wrote {made}')
    os.makedirs(pd,exist_ok=True)
    for z in old:
        if os.path.basename(z)!=zips[0]: os.remove(z);print('production zip renamed from',os.path.basename(z))
    for n in zips+need: shutil.copy2(f'{out}/{n}',f'{pd}/{n}')
    shutil.rmtree(tmp);print('production',pd)
elif st!='drawn':
    # the zip is what JLCPCB received and never changes; bom.csv is BOM data, so it follows the PCB
    from apply import gen_bom
    pd=f'{R}/Production/{board}/Rev {rev}/bom.csv'
    if os.path.exists(pd):
        t=open(pcb,encoding='utf-8',newline='').read();new=gen_bom(t)
        if open(pd,encoding='utf-8',newline='').read()!=new: open(pd,'w',encoding='utf-8',newline='').write(new);print('bom.csv')
    print(f'production zip: left as it is ({st})')
if '--production-only' in sys.argv: raise SystemExit(0)   # the production files alone (KICAD.md K38's regeneration)
os.makedirs(f'{R}/Schematics/{board}/Rev {rev}',exist_ok=True)
run(KC,'sch','export','pdf','-o',f'{R}/Schematics/{board}/Rev {rev}/{board}.pdf',sch,env=env);print('schematic pdf')
os.makedirs(f'{R}/CAD/Models/{board}/Rev {rev}',exist_ok=True)
run(KC,'pcb','export','step','--subst-models','--force','-o',f'{R}/CAD/Models/{board}/Rev {rev}/{board}.step',pcb,env=env);print('step')
run('python3',H+'/board-images/render.py',repo,board,rev);print('images')
