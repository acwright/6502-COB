#!/usr/bin/env python3
"""Board logos, generated from the font (KICAD.md K32). The design is design.json, beside this file.

  generate.py "Board" H [--png]     write the footprint "6502 <Board> Logo <H>mm" into this repository's
                                    Libraries/6502 Logos.pretty/, and with --png its picture into CAD/Logos/<Board>/
  generate.py --check [--all]       generate every logo in the 6502 Logos libraries and compare it with the
                                    library's footprint by geometry; exit 1 on a difference that isn't in
                                    Tools/data/logos.json "differences". derived-check.py runs it.
  generate.py --report [--all]      the same, printing every logo's measures
  generate.py --rewrite [--all]     draw every logo in the 6502 Logos libraries afresh, in place, with its picture
                                    in CAD/Logos/<Board>/6502 <Board>.png (any other picture there is removed)

A logo reads "6502", then the board's name in capitals, in Bebas Neue (BebasNeue-Regular.woff2, under the SIL Open
Font License in OFL.txt). It is drawn from the font's own outlines, so it is vector, not a traced bitmap.

  H        the logo's height: "6502" from the top of its 6 and 0 to their bottom, overshoots included (720 of the
           font's 1000 units), so a 5 mm logo is 5 mm tall on the board
  name     half the scale of "6502", its capitals centred on the digits' centre line
  gap      from the end of the 2 (its advance) to the start of the name's first letter (its origin)
  spacing  the font's advances and its kerning (GPOS kern), within a word only; a word space is the font's space

The numbers were measured from the 50 footprints the Image Converter traced from the PNGs (2026-11-14), which agree to
the pixel: see design.json.

The footprint's origin is the centre of its printed shapes. Each letter is one filled polygon on F.SilkS, its holes
joined to its outline by KiCad's own SHAPE_POLY_SET.Fracture(), run in KiCad's Python (kicad_poly.py, beside this
file). The reference (G***) and value (LOGO) are hidden, as a board shows them, and the footprint is board only, out
of the BOM and the placement file.

The check: each library footprint is matched to the logo generated from its name and height, letter by letter. Its
size must agree to design.json "size_tolerance" and each letter's outline to "outline_tolerance" times H (the furthest any
point of either outline is from the other's, after the two logos' printed shapes are centred on each other). A difference that the owner has ruled on is listed in Tools/data/logos.json "differences", with the ruling.
"""
import os, re, sys, json, glob, math, subprocess
H_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(H_DIR))
import common
from common import K, SCOPE, KPY

D = json.load(open(os.path.join(H_DIR, 'design.json')))
FONT = os.path.join(H_DIR, D['font'])
UPM_HEIGHT = D['height_units']          # 720: the digits from overshoot to overshoot
CENTRE = D['centre_units']              # 350: the font height that falls on the logo's centre line
LIB = 'Libraries/6502 Logos.pretty'
NAME_RE = re.compile(r'^6502 (.+?)(?: Logo)? (\d+(?:\.\d+)?)mm$')

_font = None
def font():
    global _font
    if _font is None:
        try:
            from fontTools.ttLib import TTFont
        except ImportError:
            raise SystemExit('generate.py needs fontTools and brotli: pip3 install --user fonttools brotli')
        f = TTFont(FONT)
        _font = (f, f.getGlyphSet(), f.getBestCmap(), f['hmtx'], kerning(f))
    return _font

def kerning(f):
    """{(left glyph, right glyph): advance adjustment} from the GPOS kern feature's pair lookups."""
    gpos = f['GPOS'].table
    lookups = set()
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == 'kern': lookups.update(fr.Feature.LookupListIndex)
    out, order = {}, f.getGlyphOrder()
    for li in sorted(lookups):
        lk = gpos.LookupList.Lookup[li]
        for st in lk.SubTable:
            if lk.LookupType == 9: st = st.ExtSubTable
            if st.LookupType != 2: continue
            if st.Format == 1:
                for i, g1 in enumerate(st.Coverage.glyphs):
                    for pvr in st.PairSet[i].PairValueRecord:
                        out.setdefault((g1, pvr.SecondGlyph), getattr(pvr.Value1, 'XAdvance', 0) or 0)
            else:
                c1, c2 = st.ClassDef1.classDefs, st.ClassDef2.classDefs
                for g1 in st.Coverage.glyphs:
                    rec = st.Class1Record[c1.get(g1, 0)]
                    for g2 in order:
                        v = getattr(rec.Class2Record[c2.get(g2, 0)].Value1, 'XAdvance', 0) or 0
                        if v: out.setdefault((g1, g2), v)
    return out

def outline(glyph, scale, ox, tol):
    """A glyph's contours as lists of (x, y) in mm, y down, flattened to within tol mm."""
    from fontTools.pens.basePen import BasePen
    class Pen(BasePen):
        def __init__(s, gs): super().__init__(gs); s.c = []; s.cur = None
        def P(s, p): return (ox + p[0] * scale, (CENTRE - p[1]) * scale)
        def _moveTo(s, p): s.cur = [s.P(p)]; s.last = p
        def _lineTo(s, p): s.cur.append(s.P(p)); s.last = p
        def _qCurveToOne(s, p1, p2):
            p0 = s.last
            dev = math.hypot(p0[0] - 2 * p1[0] + p2[0], p0[1] - 2 * p1[1] + p2[1]) / 4 * scale
            n = max(1, math.ceil(math.sqrt(dev / tol)))
            for i in range(1, n + 1):
                t = i / n
                s.cur.append(s.P(tuple((1 - t) ** 2 * p0[k] + 2 * (1 - t) * t * p1[k] + t * t * p2[k] for k in (0, 1))))
            s.last = p2
        def _curveToOne(s, p1, p2, p3):
            p0 = s.last
            n = 16
            for i in range(1, n + 1):
                t = i / n
                s.cur.append(s.P(tuple((1 - t) ** 3 * p0[k] + 3 * (1 - t) ** 2 * t * p1[k] + 3 * (1 - t) * t * t * p2[k]
                                       + t ** 3 * p3[k] for k in (0, 1))))
            s.last = p3
        def _closePath(s):
            if len(s.cur) > 1 and s.cur[-1] == s.cur[0]: s.cur.pop()
            s.c.append(s.cur); s.cur = None
        _endPath = _closePath
    f, gs, cm, hm, kern = font()
    pen = Pen(gs); gs[glyph].draw(pen)
    return pen.c

def layout(name, height):
    """The logo's letters: [(character, [contour, ...]), ...] in mm, the origin at the centre of the printed shapes."""
    f, gs, cm, hm, kern = font()
    s = height / UPM_HEIGHT
    tol = D['flatten_tolerance']
    letters = []
    def line(text, scale, x):
        prev = None
        for ch in text:
            g = cm.get(ord(ch))
            if g is None: raise SystemExit(f'Bebas Neue has no "{ch}"')
            if prev: x += kern.get((prev, g), 0) * scale
            if ch != ' ': letters.append((ch, outline(g, scale, x, tol)))
            x += hm[g][0] * scale
            prev = g
        return x
    x = line('6502', s, 0.0)
    line(name.upper(), s * D['name_scale'], x + D['gap'] * height)
    pts = [p for _, cs in letters for c in cs for p in c]
    cx = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2
    cy = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2
    return [(ch, [[(round(px - cx, 6), round(py - cy, 6)) for px, py in c] for c in cs]) for ch, cs in letters]

def fp_name(name, height):
    h = ('%g' % height)
    return f'6502 {name} Logo {h}mm'

def kicad(job):
    """Run kicad_poly.py in KiCad's Python with a JSON job; returns its JSON answer."""
    r = subprocess.run([KPY, os.path.join(H_DIR, 'kicad_poly.py')], input=json.dumps(job), capture_output=True,
                       text=True)
    out = [l for l in r.stdout.splitlines() if l.startswith('{')]
    if r.returncode or not out: raise SystemExit('kicad_poly.py failed:\n' + r.stdout[-2000:] + r.stderr[-2000:])
    return json.loads(out[-1])

def write(repo, name, height, png=False):
    root = f'{K}6502-{repo}'
    path = f'{root}/{LIB}/{fp_name(name, height)}.kicad_mod'
    letters = layout(name, height)
    kicad({'do': 'write', 'path': path, 'name': fp_name(name, height), 'letters': letters})
    print('wrote', os.path.relpath(path, K))
    if png:
        p = picture(letters, height, f'{root}/CAD/Logos/{name}/6502 {name}.png')
        print('wrote', os.path.relpath(p, K))
    return path

def picture(letters, height, path):
    """Black on white at the source PNGs' scale: the logo's height is png_height pixels."""
    from PIL import Image, ImageDraw
    px = D['png_height'] / height
    pts = [p for _, cs in letters for c in cs for p in c]
    x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
    w = math.ceil((max(p[0] for p in pts) - x0) * px)
    big = 4
    im = Image.new('L', (w * big, D['png_height'] * big), 255)
    from PIL import ImageChops
    for _, cs in letters:   # even-odd within a letter: a hole is a contour drawn over its outline
        acc = Image.new('1', im.size, 0)
        for c in cs:
            one = Image.new('1', im.size, 0)
            ImageDraw.Draw(one).polygon([((x - x0) * px * big, (y - y0) * px * big) for x, y in c], fill=1)
            acc = ImageChops.logical_xor(acc, one)
        im.paste(0, mask=acc)
    im = im.resize((w, D['png_height']), Image.LANCZOS)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, dpi=(300, 300))
    return path

def library(repo):
    return sorted(glob.glob(f'{K}6502-{repo}/{LIB}/*.kicad_mod'))

def check(report=False):
    rulings = {}
    for repo in common.present():
        try: rulings.update(json.load(open(f'{K}6502-{repo}/Tools/data/logos.json')).get('differences', {}))
        except FileNotFoundError: pass
    jobs = []
    for repo in SCOPE:
        for path in library(repo):
            fp = os.path.basename(path)[:-10]
            m = NAME_RE.match(fp)
            if not m:
                jobs.append({'repo': repo, 'fp': fp, 'error': 'name is not "6502 <Board> Logo <H>mm"'}); continue
            name, height = m.group(1), float(m.group(2))
            jobs.append({'repo': repo, 'fp': fp, 'path': path, 'letters': layout(name, height), 'height': height})
    res = kicad({'do': 'compare', 'jobs': [j for j in jobs if 'error' not in j]})['results']
    by = {(r['repo'], r['fp']): r for r in res}
    faults, n = [], 0
    for j in jobs:
        key = f"{j['repo']}|{j['fp']}"
        if 'error' in j: found = [j['error']]
        else:
            r = by[(j['repo'], j['fp'])]; n += 1
            found = []
            if fp_name(NAME_RE.match(j['fp']).group(1), j['height']) != j['fp']:
                found.append(f'name is not "{fp_name(NAME_RE.match(j["fp"]).group(1), j["height"])}"')
            if r['letters'] != r['want']: found.append(f"{r['letters']} shapes, {r['want']} letters")
            dw, dh = r['size'][0] - r['gen_size'][0], r['size'][1] - r['gen_size'][1]
            if abs(dw) > D['size_tolerance'] or abs(dh) > D['size_tolerance']:
                found.append(f"size {r['size'][0]:.3f} x {r['size'][1]:.3f} mm, generated "
                             f"{r['gen_size'][0]:.3f} x {r['gen_size'][1]:.3f} ({dw:+.3f}, {dh:+.3f})")
            tol = D['outline_tolerance'] * j['height']
            off = [(ch, d) for ch, d in r['per_letter'] if d > tol]
            if off: found.append('outline off by more than %.3f mm: ' % tol +
                                 ', '.join(f'{ch} {d:.3f}' for ch, d in off))
            if report:
                print(f"{key:48} {r['size'][0]:7.3f} x {r['size'][1]:6.3f}  generated {r['gen_size'][0]:7.3f} x "
                      f"{r['gen_size'][1]:6.3f}  worst letter {max(d for _, d in r['per_letter']):.4f} mm"
                      + ('' if not found else '  ← ' + '; '.join(found)))
        if found and key not in rulings: faults.append(f'{key}: ' + '; '.join(found))
        if not found and key in rulings: faults.append(f'{key}: listed in logos.json "differences" but matches now')
    print(f'logos generated: {n} footprints, {len(faults)} faults')
    for f in faults: print('  ' + f)
    return faults

def rewrite():
    for repo in SCOPE:
        root = f'{K}6502-{repo}'
        for path in library(repo):
            fp = os.path.basename(path)[:-10]
            m = NAME_RE.match(fp)
            if not m or fp_name(m.group(1), float(m.group(2))) != fp:
                raise SystemExit(f'{repo}: "{fp}" is not named "6502 <Board> Logo <H>mm": run Tools/library/rename.py --logos')
            write(repo, m.group(1), float(m.group(2)), png=True)
            keep = f'6502 {m.group(1)}.png'
            for other in glob.glob(f'{root}/CAD/Logos/{m.group(1)}/*.png'):
                if os.path.basename(other) != keep:
                    subprocess.run(['git', '-C', root, 'rm', '-q', '--', os.path.relpath(other, root)], check=True)
                    print('removed', os.path.relpath(other, K))

if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if x != '--all']
    if a[:1] == ['--check']: sys.exit(1 if check() else 0)
    if a[:1] == ['--report']: check(report=True); sys.exit(0)
    if a[:1] == ['--rewrite']: rewrite(); sys.exit(0)
    if len(a) >= 2 and not a[0].startswith('-'):
        write(common.THIS, a[0], float(a[1]), png='--png' in a); sys.exit(0)
    print(__doc__); sys.exit(2)
