"""The plate's mounting drawing, for builders: every build on the plate, every hole numbered with what uses it, the
boards, the hardware each build needs and how a hole goes together. Generated from the assembly file, the boards'
PCBs and the standards; only the drawing hints in the assembly file (where a board's name sits, which parts are
outlined) are typed in.

  svg(a) -> the drawing's SVG text
"""
import collections
from assembly import plate_size, repo_dir
from plate import holes, positions

INK, BLUE, GRN, RED, GREY, PUR = '#16202c', '#1f5fbf', '#17803d', '#c0392b', '#7b8794', '#7b3fbf'
GUT, TOP, MARGIN, RH = 62, 62, 34, 5.05
WORDS = {1: 'one', 2: 'two', 3: 'three', 4: 'four'}


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;')


def turned(r):
    return 'turned 90° anticlockwise' if r == 270 else ('turned 90° clockwise' if r == 90 else f'turned {r}°')


def wrap(s, width):
    lines, ln = [], ''
    for w in s.split():
        if ln and len(ln) + len(w) + 1 > width:
            lines.append(ln)
            ln = w
        else:
            ln = (ln + ' ' + w).strip()
    return lines + ([ln] if ln else [])


def hardware(a):
    """{build name: Counter(part: count)} and the stack sentences, from each hole's kind."""
    st = a['_std']['stacks']
    counts = {b['name']: collections.Counter() for b in a['builds']}
    optional = {b['name']: collections.Counter() for b in a['builds']}
    W, H = plate_size(a)
    for h in holes(a) + positions(a):
        for build, uses in h.uses.items():
            for what, kind in uses:
                if kind == 'part':
                    part = next(p for p in a['printed_parts'] if what.startswith(p['name']))
                    c = optional[build] if part.get('optional') else counts[build]
                    for item, n in st['part']['each']:
                        c[(part['name'] if part.get('optional') else '', item)] += n
                    continue
                for item, n in st[kind]['below'] + st['above']:
                    counts[build][('', item)] += n
    for b in a['builds']:
        for q in b['_placed']:
            for item, n in a.get('hardware', {}).get(q.name, []):
                counts[b['name']][('', item)] += n
        feet = sum(4 if p['holes'] == 'corners' else 1 for p in a.get('printed_parts', [])
                   if p['name'] in st['feet']['under'] and b['name'] in p['builds'])
        if feet:
            counts[b['name']][('', st['feet']['row'])] = feet
    order = a['_std']['hardware_order']
    keys = []
    for b in a['builds']:
        for k in counts[b['name']]:
            if k not in keys:
                keys.append(k)
    keys.sort(key=lambda k: (order.index(k[1]) if k[1] in order else len(order) + (k[1].startswith('Rubber')), ))
    rows = [[k[1]] + [str(counts[b['name']][k]) for b in a['builds']] for k in keys]
    okeys = []
    for b in a['builds']:
        for k in optional[b['name']]:
            if k not in okeys:
                okeys.append(k)
    rows += [[f'Optional {k[0]}: {k[1]}'] + [str(optional[b['name']][k]) for b in a['builds']] for k in okeys]
    # how a hole goes together
    stack = [st['screwed']['text']]
    groups = {}
    for p in positions(a):
        for build, kind in p.spec['builds'].items():
            groups.setdefault((build, kind, p.spec.get('part', '')), []).append(p.name)
    for (build, kind, part), names in groups.items():
        phrase = next(b.get('phrase', 'the ' + b['name']) for b in a['builds'] if b['name'] == build)
        stack.append(st[kind]['text'].format(name=' and '.join(names), build=phrase, part=part).replace('on the the ', 'on the '))
    parts = [('Corners' if p['name'] == 'Corner' else 'the ' + p['name']) for p in a.get('printed_parts', [])]
    if parts:
        listed = parts[0] if len(parts) == 1 else ', '.join(parts[:-1]) + ' and ' + parts[-1]
        stack.append(st['part']['text'].format(parts=listed[0].upper() + listed[1:]))
    stack += a.get('notes', [])
    under = [p['name'] for p in a.get('printed_parts', []) if p['name'] in st['feet']['under']]
    if under:
        stack.append(st['feet']['text'].format(parts=' and '.join(under)))
    return rows, stack


def board_drawing(q):
    """A placed board's outline, its outlined parts and areas, on the plate."""
    d = q.data
    outline = [q.place(x, y) for x, y in d['outlines'][0]] if d['outlines'] else None
    feats = []
    for ft in q.spec.get('features', []):
        if 'zone' in ft:
            z = next(z for z in d['zones'] if z['name'] == ft['zone'])
            (x0, y0), (x1, y1) = q.place(z['box'][0], z['box'][1]), q.place(z['box'][2], z['box'][3])
            x0, x1, y0, y1 = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
            n = ft.get('rows', 1)
            for i in range(n):
                feats.append(('area', ft['label'], x0, y0 + (y1 - y0) * i / n, x1, y0 + (y1 - y0) * (i + 1) / n))
            continue
        xs, ys = [], []
        for p in d['parts']:
            if p['ref'] not in ft['refs']:
                continue
            for bx in (p['pads'], p['courtyard'], p['drawn']):
                if bx:
                    for x, y in ((bx[0], bx[1]), (bx[2], bx[3])):
                        u, v = q.place(x, y)
                        xs.append(u)
                        ys.append(v)
        feats.append(('part', ft['label'], min(xs), min(ys), max(xs), max(ys)))
    return outline, feats


def svg(a):
    W, H = plate_size(a)
    PR = a['plate']['radius']
    builds = a['builds']
    hs, ps = holes(a), positions(a)
    dr = a.get('drawing', {})
    o = []
    A = o.append

    def t(x, y, s, size=3.4, anchor='start', fill=INK, weight='normal', rot=None):
        tr = f' transform="rotate({rot} {x:g} {y:g})"' if rot is not None else ''
        A(f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}"{tr}>{esc(s)}</text>')

    def line(x0, y0, x1, y1, c=INK, w=0.25, extra=''):
        A(f'<line x1="{x0:g}" y1="{y0:g}" x2="{x1:g}" y2="{y1:g}" stroke="{c}" stroke-width="{w:g}"{extra}/>')

    def rect(x, y, w, h, r=0, fill='none', c=INK, sw=0.4, dash=None):
        dd = f' stroke-dasharray="{dash}"' if dash else ''
        A(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{r:g}" fill="{fill}" stroke="{c}" stroke-width="{sw:g}"{dd}/>')

    def circ(x, y, r, fill='#fff', c=INK, sw=0.4, dash=None):
        dd = f' stroke-dasharray="{dash}"' if dash else ''
        A(f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="{fill}" stroke="{c}" stroke-width="{sw:g}"{dd}/>')
    ARW = ' marker-start="url(#a)" marker-end="url(#a)"'

    def hdim(x0, x1, y, yref, s):
        line(x0, yref, x0, y - 1.5, BLUE, 0.15)
        line(x1, yref, x1, y - 1.5, BLUE, 0.15)
        line(x0, y, x1, y, BLUE, 0.22, ARW)
        t((x0 + x1) / 2, y - 1.3, s, 3.2, 'middle', BLUE)

    def vdim(y0, y1, x, xref, s):
        line(xref, y0, x - 1.5, y0, BLUE, 0.15)
        line(xref, y1, x - 1.5, y1, BLUE, 0.15)
        line(x, y0, x, y1, BLUE, 0.22, ARW)
        t(x - 1.3, (y0 + y1) / 2, s, 3.2, 'middle', BLUE, rot=-90)

    one = len(builds) == 1
    SW = MARGIN * 2 + W * len(builds) + GUT * (len(builds) - 1) + 8 + (26 + 196 if one else 0)
    vy = TOP
    for vi, b in enumerate(builds):
        name = b['name']
        ox = MARGIN + 8 + vi * (W + GUT)
        t(ox, vy - 18, name, 5, weight='bold')
        A(f'<g transform="translate({ox} {vy})">')
        rect(0, 0, W, H, PR, '#f4f5f7', INK, 0.5)
        drawn = [(q, *board_drawing(q)) for q in b['_placed']]
        for q, outline, feats in drawn:
            A('<polygon points="' + ' '.join(f'{x:.3f},{y:.3f}' for x, y in outline) + '" fill="#e4f1e6" stroke="#2c6e49" stroke-width="0.45"/>')
        for q, outline, feats in drawn:
            for kind, lab, x0, y0, x1, y1 in feats:
                if kind == 'area':
                    rect(x0, y0, x1 - x0, y1 - y0, 0.8, '#fbf7ec', '#9a7b2f', 0.3)
                    t((x0 + x1) / 2, (y0 + y1) / 2 + 1.2, lab, 3.4, 'middle', '#7a6020')
                else:
                    rect(x0, y0, x1 - x0, y1 - y0, 0.6, '#cfe3d3', '#6d9a7c', 0.2)
                    t((x0 + x1) / 2, (y0 + y1) / 2 + 1.2, lab, 3.4, 'middle', '#2c6e49')
            bx = q.box
            lp = q.spec.get('label', [(bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2])
            t(lp[0], lp[1], q.name, 3.8, 'middle', '#1d5236', 'bold')
            t(lp[0], lp[1] + 4.3, f"{bx[2] - bx[0]:g} × {bx[3] - bx[1]:g}" + (f", {turned(q.rot)}" if q.rot else ''), 2.9, 'middle', '#2c6e49')
        for sp in b.get('space', []):
            t(sp['at'][0] + sp['size'][0] / 2, sp['at'][1] + sp['size'][1] / 2, sp['text'], 3.4, 'middle', GREY)
        for p in a.get('printed_parts', []):
            ol = p.get('outline')
            if ol and name in p['builds']:
                (x, y), (w, h) = ol['at'], ol['size']
                rect(x, y, w, h, 0.6, 'none', PUR, 0.3, '1.6 1')
                lab = p['name'] + (' (optional)' if p.get('optional') else '')
                if h > w:
                    t(x - 2, y + h + 3, lab, 2.9, 'end', PUR)
                else:
                    t(x + w / 2, y + h + 4, lab, 2.9, 'middle', PUR)
        for h in hs:
            uses = h.uses.get(name, [])
            kinds = {k for _, k in uses}
            if 'screwed' in kinds:
                circ(h.x, h.y, h.d / 2 + 0.25, '#fff', BLUE, 0.55)
                circ(h.x, h.y, 0.45, BLUE, BLUE, 0)
                col = BLUE
            elif 'part' in kinds:
                circ(h.x, h.y, h.d / 2, '#fff', PUR, 0.5)
                col = PUR
            else:
                circ(h.x, h.y, h.d / 2, '#fff', GREY, 0.3)
                col = GREY
            if h.added:
                circ(h.x, h.y, h.d / 2 + 1.5, 'none', RED, 0.4)
                col = RED
            left = h.x > W - 30
            t(h.x + (-2.7 if left else 2.7), h.y - 1.5, h.name, 2.8, 'end' if left else 'start', col, 'bold' if uses else 'normal')
        for p in ps:
            kind = p.spec['builds'].get(name)
            if not kind or not p.uses.get(name):
                continue
            c = PUR if kind == 'on_part' else GRN
            circ(p.x, p.y, 1.85, '#fff', c, 0.55)
            circ(p.x, p.y, 0.45, c, c, 0)
            t(p.x + 2.7, p.y - 1.5, p.name, 2.8, 'start', c, 'bold')
        hdim(0, W, -7, -0.5, f'{W:g}')
        vdim(0, H, -7, -0.5, f'{H:g}')
        if len(b['_placed']) == 1:
            q = b['_placed'][0]
            bx = q.box
            hdim(bx[0], bx[2], -2.5, bx[1], f'{bx[2] - bx[0]:g}')
            vdim(bx[1], bx[3], -2.5, bx[0], f'{bx[3] - bx[1]:g}')
        A('</g>')

    # the plate holes' table
    ty = vy + H + 16
    tx = MARGIN + 8
    cols = [(0, 'Hole'), (13, 'x'), (27, 'y'), (41, 'Ø')] + [(52 + 62 * i, b.get('short', b['name'])) for i, b in enumerate(builds)]
    pcol = 52 + 62 * len(builds) - 6
    t(tx, ty, 'Plate holes', 4.2, weight='bold')
    t(tx + 42, ty, "x and y in mm from the plate's back-left corner, as the computer is used", 3, fill=GREY)
    y = ty + 7
    for c, s in cols:
        t(tx + c, y, s, 3.1, weight='bold')
    line(tx, y + 1.4, tx + pcol, y + 1.4)
    y += 6

    def cell(h, name):
        uses = h.uses.get(name)
        if not uses:
            return '—'
        out = []
        for what, kind in uses:
            if kind == 'resting':
                out.append(f'{what} (resting)')
            elif kind == 'on_part':
                out.append(f"{what}, to the {h.spec.get('part', 'printed part')}")
            else:
                out.append(what)
        return '; '.join(out)
    for h in hs + ps:
        col = RED if h.added else (INK if h.d else GRN)
        t(tx, y, h.name, 3, fill=col, weight='bold')
        t(tx + 13, y, f'{h.x:g}', 3, fill=col)
        t(tx + 27, y, f'{h.y:g}', 3, fill=col)
        t(tx + 41, y, f'{h.d:g}' if h.d else 'none', 3, fill=col)
        for i, b in enumerate(builds):
            t(tx + 52 + 62 * i, y, cell(h, b['name']), 3)
        y += RH
    tbl_bottom = y

    # boards, key and notes
    rx, ry = tx + pcol + 12, ty
    if one:
        rx, ry = MARGIN + 8 + W + 26, vy - 18
    t(rx, ry, 'Boards', 4.2, weight='bold')
    ry += 7
    for c, s in [(0, 'Board'), (62, 'Size'), (84, 'Back-left on plate'), (116, 'As mounted')]:
        t(rx + c, ry, s, 3.1, weight='bold')
    line(rx, ry + 1.4, rx + 142, ry + 1.4)
    ry += 6
    for b in builds:
        for q in b['_placed']:
            bx = q.box
            t(rx, ry, f'{q.name} Rev {q.rev}', 3)
            t(rx + 62, ry, f'{bx[2] - bx[0]:g} × {bx[3] - bx[1]:g}', 3)
            t(rx + 84, ry, f'({bx[0]:g}, {bx[1]:g})', 3)
            t(rx + 116, ry, turned(q.rot) if q.rot else 'as drawn', 3)
            ry += RH
    ry += 6
    t(rx, ry, 'Key', 4.2, weight='bold')
    ry += 6.5
    kinds = {k for h in hs + ps for us in h.uses.values() for _, k in us}
    key = [('used', 'Plate hole used by this build: a screw through the board into a standoff.'),
           ('part', 'Plate hole for a printed part.'),
           ('free', "Plate hole this build doesn't use.")]
    for p in ps:
        if 'on_part' in p.spec['builds'].values() and not any(k == 'onpart' for k, _ in key):
            key.append(('onpart', f"On the {p.spec['part']}: the board has a hole here and the plate doesn't. The board screws to the {p.spec['part']}, not the plate."))
    if 'resting' in kinds:
        key.append(('rest', "Resting: the board has a hole here and the plate doesn't. The standoff stands on the plate."))
    for h in hs:
        if h.added:
            key.append(('new', h.added))
    for kind, s in key:
        cx, cy = rx + 3, ry - 1
        if kind == 'used':
            circ(cx, cy, 1.85, '#fff', BLUE, 0.55)
            circ(cx, cy, 0.45, BLUE, BLUE, 0)
        elif kind == 'part':
            circ(cx, cy, 1.6, '#fff', PUR, 0.5)
        elif kind == 'onpart':
            circ(cx, cy, 1.85, '#fff', PUR, 0.55)
            circ(cx, cy, 0.45, PUR, PUR, 0)
        elif kind == 'free':
            circ(cx, cy, 1.6, '#fff', GREY, 0.3)
        elif kind == 'rest':
            circ(cx, cy, 1.85, '#fff', GRN, 0.55)
            circ(cx, cy, 0.45, GRN, GRN, 0)
        else:
            circ(cx, cy, 1.6, '#fff', GREY, 0.3)
            circ(cx, cy, 3, 'none', RED, 0.4)
        ls = wrap(s, 100)
        for i, ln in enumerate(ls):
            t(rx + 9, ry + i * 3.9, ln, 3)
        ry += len(ls) * 3.9 + 2.2
    ry += 3
    notes = [p['note'] for p in a.get('printed_parts', []) if p.get('note')]
    notes += [f"The plate is a stack of {WORDS[a['plate']['layers']]} {a['_std']['sheet']:g} mm {a['_std']['material']} layers, each cut from Plate.svg.",
              'The SVG is drawn 1:1, so it can be printed at full size to check a plate.']
    t(rx, ry, 'Notes', 4.2, weight='bold')
    ry += 6.5
    for s in notes:
        ls = wrap(s, 108)
        for i, ln in enumerate(ls):
            t(rx, ry + i * 3.9, ln, 3)
        ry += len(ls) * 3.9 + 1.8

    # hardware and the stack
    rows, stack = hardware(a)
    hx, hy = rx + 172, ty
    if one:
        hx, hy = rx, ry + 4
    t(hx, hy, 'Hardware', 4.2, weight='bold')
    hy += 7
    t(hx, hy, 'Part', 3.1, weight='bold')
    for i, b in enumerate(builds):
        t(hx + 92 + 28 * i, hy, b.get('short', b['name']), 3.1, weight='bold')
    line(hx, hy + 1.4, SW - MARGIN, hy + 1.4)
    hy += 6
    for row in rows:
        t(hx, hy, row[0], 3)
        for i, s in enumerate(row[1:]):
            t(hx + 92 + 28 * i, hy, s, 3)
        hy += RH
    hy += 6
    t(hx, hy, 'How a hole goes together', 4.2, weight='bold')
    hy += 6.5
    for s in stack:
        ls = wrap(s, 104)
        for i, ln in enumerate(ls):
            t(hx, hy + i * 3.9, ln, 3)
        hy += len(ls) * 3.9 + 1.8
    SH = max(tbl_bottom, ry, hy) + 16
    t(MARGIN + 8, 15, dr.get('title', f"{a['machine']} base plate: mounting drawing"), 7.2, weight='bold')
    t(MARGIN + 8, 23, dr.get('subtitle', 'Looking down on the plate, as the computer is used. All dimensions in mm.'), 3.6, fill=GREY)
    line(MARGIN, SH - 11, SW - MARGIN, SH - 11)
    t(MARGIN, SH - 6, f"6502-{a['_repo']} · CAD/Bases/Plate.svg, generated from CAD/Assembly.json · {WORDS[a['plate']['layers']]} layers of {a['_std']['sheet']:g} mm {a['_std']['material']}", 3, fill=GREY)
    t(SW - MARGIN, SH - 6, '© ' + dr.get('year', '2026') + ' A.C. Wright Design', 3, 'end', GREY)
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SW:g} {SH:g}" width="{SW:g}mm" height="{SH:g}mm" '
            f'font-family="Helvetica, Arial, sans-serif">'
            '<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
            f'<path d="M0,1 L9,5 L0,9z" fill="{BLUE}"/></marker></defs>'
            f'<rect width="{SW:g}" height="{SH:g}" fill="#fff"/>')
    return head + '\n'.join(o) + '</svg>\n'
