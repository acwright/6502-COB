"""The parts' 3D bodies, read from a board's STEP model with build123d: kept apart from tops.py so that the slow read
is cached by the STEP's bytes and this file's, and survives changes to the rules in tops.py."""
import math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assembly  # noqa: E402


def norm(s):
    return re.sub(r'[^A-Za-z0-9]', '', os.path.splitext(os.path.basename(s))[0]).lower()


def bodies(step, sheet_z0, sheet_z1):
    """Each STEP child: its label, its box in the PCB's frame (y down) with its height above the board's top, the box
    of a round feature at its top (or None), and, for a part taller than sheet_z0, its profile from sheet_z0 up: the
    box of each 1 mm band of it, [[z, box], ...]. Cached by the STEP's bytes."""
    cache = assembly.Cache('cad-step', os.path.abspath(__file__))
    key = f'bodies {assembly.digest(step)} {sheet_z0} {sheet_z1}'

    def run():
        from build123d import import_step, Box, GeomType, Pos
        a = import_step(step)
        pcb = [c for c in a.children if c.label.endswith('_PCB')]
        ztop = max(c.bounding_box().max.Z for c in pcb) if pcb else 1.6
        out = []
        for c in a.children:
            if c.label.endswith('_PCB'):
                continue
            bb = c.bounding_box()
            # a round feature at the part's top, which a hole over it is centred on: a trimmer's rotor. The upright
            # cylindrical faces within 2.5 mm of the top, at least 1 mm across
            tb = None
            for f in c.faces():
                if f.geom_type != GeomType.CYLINDER:
                    continue
                fb = f.bounding_box()
                if fb.max.Z < bb.max.Z - 2.5 or abs(f.normal_at(f.center()).Z) > 0.01 or max(fb.max.X - fb.min.X, fb.max.Y - fb.min.Y) < 1:
                    continue
                n_ = [fb.min.X, -fb.max.Y, fb.max.X, -fb.min.Y]
                tb = n_ if tb is None else [min(tb[0], n_[0]), min(tb[1], n_[1]), max(tb[2], n_[2]), max(tb[3], n_[3])]
            prof = []
            z = math.floor(sheet_z0)
            while ztop + z < bb.max.Z:
                cut = c & (Pos(0, 0, ztop + z + 0.5) * Box(5000, 5000, 1))
                if cut is not None and cut.solids():
                    cb = cut.bounding_box()
                    prof.append([z, [cb.min.X, -cb.max.Y, cb.max.X, -cb.min.Y]])
                z += 1
            out.append([c.label, [bb.min.X, -bb.max.Y, bb.max.X, -bb.min.Y, bb.max.Z - ztop], prof, tb])
        return out
    v = cache.get(key, run)
    cache.save()
    return v
