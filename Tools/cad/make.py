#!/usr/bin/env python3
"""Generates a machine's flat parts from CAD/Assembly.json, the boards' PCBs and the standards.

  make.py             write this repository's files (or every repository's with --all)
  make.py --check     write nothing: exit 1 if any file differs from what would be generated. derived-check.py runs it
  make.py --compare   how the generated plate differs from the plate as it is in git (HEAD), hole by hole

What it writes, in CAD/Bases/:
  Plate.svg                     the plate's cut file: one layer, cut three times
  Plate Mounting Drawing.svg    the drawing for builders, and its .png
  Plate.stl                     one layer as a 3D model (needs Tools/work/venv: run Tools/cad/setup.sh once)
and in CAD/Tops/<board>/Rev X/, the top of each of this repository's boards whose top the assembly file marks
generated (tops.py, which needs the venv too). A top marked draft is left alone until the owner approves it.

When Plate.svg changes, the owner remakes Plate.lbrn2 in LightBurn from the new SVG.
"""
import hashlib, os, subprocess, sys, tempfile
CAD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CAD)
import assembly, plate, drawing  # noqa: E402
from common import SCOPE, repo_dir  # noqa: E402

VENV = os.path.join(os.path.dirname(CAD), 'work', 'venv', 'bin', 'python')
BASES = 'CAD/Bases'


def png(svg_path, out):
    subprocess.run(['rsvg-convert', '-w', '3200', '-b', 'white', svg_path, '-o', out], check=True)


def stl_source(path):
    """The sha1 of the Plate.svg an STL was made from, from its header; None for an STL not made here."""
    try:
        head = open(path, 'rb').read(80).decode('ascii', 'replace')
    except OSError:
        return None
    return head.split('sha1 ')[1].split()[0] if 'Tools/cad/solid.py' in head and 'sha1 ' in head else None


def files(a):
    """{path in the repository: generated text}"""
    return {f'{BASES}/Plate.svg': plate.svg(a), f'{BASES}/Plate Mounting Drawing.svg': drawing.svg(a)}


def make(a):
    root = repo_dir(a['_repo'])
    for rel, text in files(a).items():
        p = f'{root}/{rel}'
        old = open(p).read() if os.path.exists(p) else None
        if old != text:
            open(p, 'w').write(text)
            print(a['_repo'], 'wrote', rel)
            if rel.endswith('Plate.svg'):
                print(a['_repo'], '  the plate changed: remake CAD/Bases/Plate.lbrn2 in LightBurn from the new Plate.svg')
    d = f'{root}/{BASES}/Plate Mounting Drawing'
    with tempfile.TemporaryDirectory() as t:
        png(d + '.svg', t + '/d.png')
        if not os.path.exists(d + '.png') or open(t + '/d.png', 'rb').read() != open(d + '.png', 'rb').read():
            os.replace(t + '/d.png', d + '.png')
            print(a['_repo'], 'wrote', f'{BASES}/Plate Mounting Drawing.png')
    svg = f'{root}/{BASES}/Plate.svg'
    stl = f'{root}/{BASES}/Plate.stl'
    if stl_source(stl) != hashlib.sha1(open(svg, 'rb').read()).hexdigest():
        if not os.path.exists(VENV):
            raise SystemExit('Plate.stl needs build123d: run zsh Tools/cad/setup.sh once, then make.py again')
        subprocess.run([VENV, os.path.join(CAD, 'solid.py'), svg, stl], check=True)
        print(a['_repo'], 'wrote', f'{BASES}/Plate.stl')


def top_digest(path):
    """The inputs sha1 a generated top carries; None for a top not made here."""
    try:
        head = open(path).read(600)
    except OSError:
        return None
    return head.split('inputs sha1 ')[1].split()[0] if 'inputs sha1 ' in head else None


def make_tops(a):
    for q, path in assembly.generated_tops(a):
        if top_digest(path) == assembly.top_inputs(a, q):
            continue
        if not os.path.exists(VENV):
            raise SystemExit('the tops need build123d: run zsh Tools/cad/setup.sh once, then make.py again')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run([VENV, os.path.join(CAD, 'tops.py'), a['_repo'], q.name, q.rev, path], check=True)
        print(a['_repo'], 'wrote', os.path.relpath(path, repo_dir(a['_repo'])))
        print(a['_repo'], f'  remake its .lbrn2 in LightBurn from the new SVG')


def check(a):
    root = repo_dir(a['_repo'])
    bad = []
    for rel, text in files(a).items():
        p = f'{root}/{rel}'
        if not os.path.exists(p) or open(p).read() != text:
            bad.append(f"{a['_repo']}: {rel} is out of date: run Tools/cad/make.py")
    d = f'{root}/{BASES}/Plate Mounting Drawing'
    if os.path.exists(d + '.svg'):
        with tempfile.TemporaryDirectory() as t:
            png(d + '.svg', t + '/d.png')
            if not os.path.exists(d + '.png') or open(t + '/d.png', 'rb').read() != open(d + '.png', 'rb').read():
                bad.append(f"{a['_repo']}: {BASES}/Plate Mounting Drawing.png is out of date: run Tools/cad/make.py")
    svg = f'{root}/{BASES}/Plate.svg'
    if os.path.exists(svg) and stl_source(f'{root}/{BASES}/Plate.stl') != hashlib.sha1(open(svg, 'rb').read()).hexdigest():
        bad.append(f"{a['_repo']}: {BASES}/Plate.stl wasn't made from today's Plate.svg: run Tools/cad/make.py")
    for q, path in assembly.generated_tops(a):
        if top_digest(path) != assembly.top_inputs(a, q):
            bad.append(f"{a['_repo']}: {os.path.relpath(path, root)} is out of date: run Tools/cad/make.py")
    return bad


def compare_head(a):
    """The generated plate against Plate.svg as committed (HEAD), which may still be Fusion's."""
    root = repo_dir(a['_repo'])
    old = subprocess.run(['git', 'show', f'HEAD:{BASES}/Plate.svg'], cwd=root, capture_output=True, text=True)
    if old.returncode:
        print(a['_repo'], 'no Plate.svg in HEAD')
        return
    p = f'{root}/{BASES}/Plate.svg'
    cur = open(p).read()
    try:
        open(p, 'w').write(old.stdout)
        turned, diffs = plate.compare(a)
    finally:
        open(p, 'w').write(cur)
    print(f"{a['_repo']}: Plate.svg in HEAD is drawn turned {turned}° from the view as used; {len(diffs)} differences"
          + (' beyond 0.05 mm' if diffs else ': every hole and the outline within 0.05 mm'))
    for kind, text in diffs:
        print(f'  {kind}: {text}')


if __name__ == '__main__':
    bad = []
    for r in SCOPE:
        a = assembly.load(r)
        if a is None:
            continue
        if '--check' in sys.argv:
            bad += check(a)
        elif '--compare' in sys.argv:
            compare_head(a)
        else:
            make(a)
            make_tops(a)
    assembly.save_cache()
    for b in bad:
        print(b)
    sys.exit(1 if bad else 0)
