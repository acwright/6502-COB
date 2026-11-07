#!/usr/bin/env python3
"""Writes Plate.stl, one layer of the plate as a 3D model, from Plate.svg. Needs build123d: run it with the venv that
setup.sh makes (make.py does).

  solid.py PLATE.svg OUT.stl

The model is in the frame Fusion exported the KIM's plate in: centred on the plate, x to the right as the computer is
used, z towards the front, y up, and the layer from y 6 to 9, the top of the three. The STL's header names the sha1 of
the Plate.svg it was made from, so make.py --check can tell a stale STL without build123d.
"""
import hashlib, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fusion  # noqa: E402
from build123d import Axis, BuildPart, BuildSketch, Circle, Locations, Mode, RectangleRounded, extrude  # noqa: E402


def main(src, out):
    p = fusion.read(src)
    W, H = p.w, p.h
    r = max(fusion.corner_radii(p.outline))
    with BuildPart() as part:
        with BuildSketch():
            RectangleRounded(W, H, r)
            # the sketch's y is up; the plate's y (towards the front) goes to -y here and becomes +z below
            for h in p.holes:
                with Locations((h.x - W / 2, -(h.y - H / 2))):
                    Circle(h.d / 2, mode=Mode.SUBTRACT)
        extrude(amount=3)
    solid = part.part.rotate(Axis.X, -90).translate((0, 6, 0))
    verts, tris = solid.tessellate(0.05, 0.2)
    digest = hashlib.sha1(open(src, 'rb').read()).hexdigest()
    head = f'Tools/cad/solid.py from Plate.svg sha1 {digest}'.encode().ljust(80, b' ')
    body = bytearray()
    for a, b, c in tris:
        A, B, C = verts[a], verts[b], verts[c]
        n = (B - A).cross(C - A)
        n = n.normalized() if n.length > 0 else n
        body += struct.pack('<12fH', n.X, n.Y, n.Z, A.X, A.Y, A.Z, B.X, B.Y, B.Z, C.X, C.Y, C.Z, 0)
    open(out, 'wb').write(head + struct.pack('<I', len(tris)) + bytes(body))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
