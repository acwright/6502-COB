"""Reads a .kicad_pcb as text, keeping every node's place in the file, so a tool can change one node and leave every
other byte as it was. No KiCad needed.

  parse(text)       the file as a tree of Node
  Node.name         the node's first word: 'footprint', 'gr_line', 'pad' …
  Node.kids         its child nodes; Node.atoms its bare words and strings, in order
  Node.span         (start, end) in the text, end exclusive
  Node.get(name)    its first child of that name, or None; Node.all(name) every one
"""
import math, re

TOKEN = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')


class Node:
    __slots__ = ('name', 'kids', 'atoms', 'span', 'parent')

    def __init__(self, start, parent):
        self.name, self.kids, self.atoms, self.span, self.parent = None, [], [], (start, None), parent

    def get(self, name):
        return next((k for k in self.kids if k.name == name), None)

    def all(self, name):
        return [k for k in self.kids if k.name == name]

    def nums(self):
        return [float(a) for a in self.atoms]

    def text(self, t):
        return t[self.span[0]:self.span[1]]

    def __repr__(self):
        return f'<{self.name} {self.atoms[:3]}>'


def unquote(a):
    return a[1:-1].replace('\\"', '"').replace('\\\\', '\\') if a.startswith('"') else a


def parse(t):
    root = cur = None
    for m in TOKEN.finditer(t):
        s = m.group()
        if s == '(':
            n = Node(m.start(), cur)
            if cur is not None:
                cur.kids.append(n)
            else:
                root = n
            cur = n
        elif s == ')':
            cur.span = (cur.span[0], m.end())
            cur = cur.parent
        elif cur.name is None:
            cur.name = s
        else:
            cur.atoms.append(unquote(s))
    return root


def layer(n):
    l = n.get('layer')
    return l.atoms[0] if l else None


def at(n):
    """(x, y, rotation in degrees) of a node's (at …)."""
    a = n.get('at')
    v = a.nums() if a else [0, 0]
    return v[0], v[1], (v[2] if len(v) > 2 else 0.0)


def to_board(fp, x, y):
    """A point in a footprint's own frame, in the board's. KiCad turns footprints counter-clockwise on screen, y down."""
    fx, fy, r = at(fp)
    c, s = math.cos(math.radians(r)), math.sin(math.radians(r))
    return fx + x * c + y * s, fy - x * s + y * c


def lib_id(fp):
    return fp.atoms[0] if fp.atoms else ''


def ref(fp):
    for p in fp.all('property'):
        if p.atoms and p.atoms[0] == 'Reference':
            return p.atoms[1]
    return '?'


def footprints(root):
    return root.all('footprint')


def pad_box(fp, pad):
    """The copper box round a rectangular pad, in the board's frame: (x0, y0, x1, y1)."""
    px, py, pr = at(pad)
    w, h = pad.get('size').nums()
    if round(pr) % 90 or round(at(fp)[2]) % 90:
        raise ValueError('a pad that is not square to the board')
    if round(pr / 90) % 2:   # a pad's (at) holds its angle on the board, the footprint's turn included
        w, h = h, w
    cx, cy = to_board(fp, px, py)
    return cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
