#!/usr/bin/env python3
"""Global label shapes by signal flow (KICAD.md K25).

  flow.py SCHEMATIC... [--apply]     list (or set) the labels whose shape is off the rule
  flow.py --all [--apply]            every schematic in the five repos
  flow.py --check                    exit 1 if any label in the five repos is off the rule (run by derived-check.py)

A label's shape shows which way the signal flows at the pins on the label's own wire:
  a pin that drives the signal -> output;  one that only receives it -> input;  one that does both -> bidirectional;
  VCC, GND -> passive;  a pull-up alone on the wire -> output (it sets the idle level).

Each pin's role comes from, in order:
  1. the board's own rules in BOARDS (reference pattern, net pattern, role);
  2. a part rule by pin name (PARTS), because library pin types are often wrong (the 65C02 symbol types its data pins
     as outputs, the RAM symbols type everything bidirectional);
  3. a 6502 bus connector: by the board's side. 'cpu': the board drives the bus, so the addresses, RWB, SYNC, PHI2 and
     RESB flow into the connector (input) and IRQB, NMIB, RDY, BE and HRDB come out of it (output). 'card': the reverse.
  4. a two-pin part the signal passes through (series resistor, diode, LED, solder jumper, switch, capacitor): the pin
     on the side that has a source is an input, the other an output. A resistor or a jumper to VCC or GND is a
     pull-up/down: it sets a level and is no source. A switch to a rail (a reset button) drives the line.
  5. any other connector or header: bidirectional if a bidirectional pin shares its net, input if something on the
     board drives the net, output if nothing does (the signal comes from whatever is plugged in);
  6. the library pin type.
A pin none of these decides (a microcontroller's port pin, whose direction is the firmware's) keeps the owner's
pre-K21 shape, or the present one if the label is newer; the report lists these as 'kept' for review.
"""
import sys, os, re, glob, json, subprocess, tempfile, collections
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from labelpins import analyse
KC = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
sys.path.insert(0, os.path.dirname(H)); import common; from common import K, files, load
K21 = {'ACE': '909629f', 'COB': 'f6838dff', 'DEV': '340cf97', 'KIM': '465d707', 'VCS': 'a12f5eb'}  # the connector redraw
POWER = re.compile(r'VCC|GND|5V|\+5V|3V3|\+3V3|VDD|VSS')
SUPPLY = re.compile(r'VBAUX|VBAT|VBATT|VDD|VEE')   # supplies other than the rails: the drawing says

# ---- the 6502 bus, by who drives each signal
FROM_CPU = re.compile(r'A\d+|RWB|SYNC|PHI2|RESB')
TO_CPU = re.compile(r'IRQB|NMIB|RDY|BE|HRDB')
BOTH = re.compile(r'D\d|EXP\d')
def bus_role(net, side):
    if BOTH.fullmatch(net): return 'bid'
    if FROM_CPU.fullmatch(net): return 'rcv' if side == 'cpu' else 'drv'
    if TO_CPU.fullmatch(net): return 'drv' if side == 'cpu' else 'rcv'
def is_bus_conn(lib, ref): return ref.startswith('J') and (lib == '6502 Parts:6502 Card Edge' or 'Conn_02x20' in lib)

# ---- part rules by library and pin name: (lib pattern, pin-name pattern, role); first match wins
MEM = r'6502 Parts:(AS6C\w+|AT28C\w+|AT27C\w+|SST39SF\w*(-TSOP)?)'
PARTS = [
    (r'6502 Parts:65C02', r'A\d+|RWB|SYNC|VPB|MLB|PHI1O|PHI2O', 'drv'),
    (r'6502 Parts:65C02', r'D\d', 'bid'),
    (r'6502 Parts:65C02', r'.*', 'rcv'),                      # PHI2, RDY, BE, SOB, IRQB, NMIB, RESB
    (r'6502 Parts:65C816', r'A\d+|RWB|E|MX|VDA|VPA|VPB|MLB', 'drv'),
    (r'6502 Parts:65C816', r'D\d.*', 'bid'),
    (r'6502 Parts:65C816', r'.*', 'rcv'),
    (MEM, r'(D|DQ|I/O)\d', 'mem-data'),                       # bidirectional, or output where /WE is tied high
    (MEM, r'.*', 'rcv'),
    (r'6502 Parts:DS1511Y', r'IRQB|RSTB|SQW|PWRB', 'drv'),
    (r'6502 Parts:DS1511Y', r'VBAUX', 'fw'),                  # a supply: the drawing says
    (r'6502 Parts:DS1511Y', r'D\d', 'bid'),
    (r'6502 Parts:DS1511Y', r'.*', 'rcv'),
    # 65xx peripherals: by pin name, because older cached copies of their symbols type the data pins as outputs
    (r'6502 Parts:(65C22|ACIA 6551|PIA 6521)', r'D\d', 'bid'),
    (r'6502 Parts:(65C22|PIA 6521)', r'PA\d|PB\d|CA2|CB2', 'fw'),   # port pins: the firmware sets their direction
    (r'6502 Parts:65C22', r'CB1', 'fw'),
    (r'6502 Parts:(65C22|ACIA 6551|PIA 6521)', r'IRQ.*|TXD|RTSB|DTRB|XTALO', 'drv'),
    (r'6502 Parts:(65C22|ACIA 6551|PIA 6521)', r'.*', 'rcv'),   # CA1 is an input only; the selects, RWB, PHI2, RESB
    (r'74xx:74HC245', r'A\d', '245-A'), (r'74xx:74HC245', r'B\d', '245-B'),   # by DIR: one way when it's tied
    (r'6502 Parts:(LCD-16X2|Adafruit 2.8 TFT LCD)', r'CS|C/D|RD|WR|E|RS|R/W|RST|~\{.*\}', 'rcv'),   # display control
    (r'6502 Parts:(LCD-16X2|Adafruit 2.8 TFT LCD)', r'D\d|DB\d', 'fw'),   # written only, or read too: the drawing says
    (r'6502 Parts:microSD Socket', r'DAT0|CD|WP', 'drv'),        # SPI mode: DAT0 is MISO; CD, WP are switches
    (r'6502 Parts:microSD Socket', r'CMD|CLK|DAT3/CD|DAT\d', 'rcv'),
    (r'Memory_Flash:W25Q\w+', r'DO/.*', 'drv'),
    (r'Memory_Flash:W25Q\w+', r'DI/.*|CLK|~\{CS\}', 'rcv'),
    (r'Logic_LevelTranslator:TXS0108\w*', r'[AB]\d', 'fw'),   # either way electrically; the drawing gives the flow
    (r'6502 Parts:MT8808', r'[XY]\d', 'fw'),                    # a crosspoint switch: either way
    (r'Device:Battery\w*|6502 Parts:CR2032 Holder', r'.*', 'fw'),
    # a signal diode passes a low from its cathode to its anode: an IRQ's isolation diode, a wired-AND, KIMB to HRDB
    (r'Device:D_Schottky|Device:D|Diode:.*', r'K', 'rcv'), (r'Device:D_Schottky|Device:D|Diode:.*', r'A', 'drv'),
    (r'.*(Q_NPN|2N3904|2N4401|Simulation_SPICE:NPN).*', r'C', 'drv'),   # an open collector pulls the line
    (r'.*(Q_NPN|2N3904|2N4401|Simulation_SPICE:NPN).*', r'B', 'rcv'),
]
THROUGH = re.compile(r'Device:(R|D_Schottky|LED|C)$|Diode:|Jumper:|Switch:SW_Push|Switch:SW_DIP|BSS138')
MCU = re.compile(r'MCU_|Teensy|Raspberry Pi Pico|Arduino')

# ---- per board: the bus side and the rules for pins nothing above decides. Keyed (repo, board) or (repo, board, rev).
def keyboard(mcu=None, via=None, ports=(), keyboard=None, end='encoder', joysticks=(), switches=r'SW\d+'):
    """The keyboard circuit, drawn as on the ACE (owner, 2026-11-07) wherever it appears. The ATmega strobes the matrix on
    PB and reads it on PA, interrupts the VIA on CA1/CB1 and reads CA2/CB2. The VIA's port pins and the headers that
    carry its port are bidirectional. A KEYBOARD header at the encoder takes PB in and gives PA out; at the keyboard's
    end of the ribbon (the Keyboard Helper) the reverse. A joystick pulls its lines."""
    r = []
    if mcu: r += [(mcu, r'RESB|NMIB|CA1|CB1|PB\d', 'drv'), (mcu, 'PS2DATA', 'bid'),
                  (mcu, r'PA\d|CA2|CB2|PS2CLK|SQW|PHI2_16MHZ', 'rcv')]
    if via: r += [(via, r'PA\d|PB\d|CA2|CB1|CB2', 'bid')]
    for p in ports: r += [(p, r'P[AB]\d|C[AB]\d', 'bid')]
    if keyboard:
        a, b = ('drv', 'rcv') if end == 'encoder' else ('rcv', 'drv')
        r += [(keyboard, r'PA\d', a), (keyboard, r'PB\d', b), (keyboard, r'C[AB]\d', 'bid')]
    for j in joysticks: r += [(j, '.*', 'drv')]
    if switches: r += [(switches, r'PA\d', 'drv'), (switches, r'PB\d', 'rcv')]
    return r

BOARDS = {
    ('ACE', 'ACE Board', '1.0'): dict(side='cpu', rules=[
        ('J21', 'RDY', 'drv'),                                   # STORAGE (CF Adapter): RDY reserved for a device
        ('J1', 'PHI2', 'drv'), ('J1', '.*', 'rcv'),             # PHI2 SELECT jumper: the middle pin is PHI2
    ] + keyboard('U6', 'U2', ('J9', 'J10'), 'J22', joysticks=('J6', 'J8'))),
    ('ACE', 'ACE Board', '1.1'): dict(side='cpu', rules=[      # Rev 1.0's designators (re-annotated back, 2026-11-11)
        ('J21', 'RDY', 'drv'),                                   # STORAGE
        ('J1', 'PHI2', 'drv'), ('J1', '.*', 'rcv'),             # PHI2 SELECT jumper: the middle pin is PHI2
    ] + keyboard('U6', 'U2', ('J9', 'J10'), 'J22', joysticks=('J6', 'J8'))),
    ('COB', 'Keyboard Encoder Helper'): dict(side='card', rules=keyboard('U1', None, ('J1', 'J2'), 'J4')),
    ('COB', 'Keyboard Helper'): dict(side='card', rules=keyboard(None, None, ('J5', 'J6'), 'J7', end='keyboard',
                                                                 joysticks=('J1', 'J2', 'J3', 'J4'))),
    ('VCS', 'Input Board'): dict(side='card', rules=keyboard('U2', 'U1', ('J1', 'J2'), 'J5')),
    ('COB', 'Serial Card'): dict(side='card', rules=[]),
    # A programmer: its microcontroller drives the cartridge's bus, so the connector is read like any header
    ('VCS', 'Flash Helper'): dict(side='header', rules=[]),
    ('DEV', 'DEV Board'): dict(side='card', rules=[('J3', '.*_SW', 'drv')]),   # PANEL: the case's switches
    ('COB', 'Storage Card Pro'): dict(side='card', rules=[('J3', 'MISO.*', 'drv')]),   # SPI port for another device
    # The Arduino drives the bus and the CPU's control inputs, shares the data bus and reads SYNC (owner's drawing)
    ('COB', 'Mega Helper'): dict(side='cpu', rules=[
        ('A1', 'SYNC', 'rcv'), ('A1', r'D\d|EXP\d', 'bid'), ('A1', '.*', 'drv'),
        ('J1', 'SYNC', 'drv'), ('J1', r'D\d|EXP\d', 'bid'), ('J1', '.*', 'rcv'),
    ]),
    # Backplanes have no CPU; they carry the CPU board's bus to the slots, as the Backplane Pro's own RESB driver (Q1)
    # does, so they take the cpu side (owner, 2026-11-07).
    ('COB', 'Backplane'): dict(side='cpu', rules=[]),
    ('COB', 'Backplane Pro'): dict(side='cpu', rules=[]),
    ('COB', 'Backplane Helper'): dict(side='cpu', rules=[]),
}

JUMPERS = {}
for j in load('jumpers.json'):
    for rev in j['revs']: JUMPERS.setdefault((j['repo'], j['board'], rev), set()).update(j['refs'])

def board_cfg(key, parts):
    cfg = BOARDS.get(key) or BOARDS.get(key[:2])
    if cfg: return cfg
    side = 'cpu' if any(re.search(r'65C02|65C816', l) for l in parts.values()) else 'card'
    return dict(side=side, rules=[], auto=True)

def netlist(sch):
    o = tempfile.mktemp(suffix='.net'); subprocess.run([KC, 'sch', 'export', 'netlist', '-o', o, sch], capture_output=True)
    t = open(o).read(); os.remove(o)
    from sch import Sch
    parts = {sym['ref']: sym['lib'] for sym in Sch(sch).symbols}
    t = t[t.index('(nets'):]; nets = {}; pinnet = {}
    for part in re.split(r'\n\t\t\(net\n', t)[1:]:
        name = re.search(r'\(name "([^"]*)"', part).group(1).lstrip('/')
        nodes = re.findall(r'\(ref "([^"]*)"\)\s*\(pin "([^"]*)"\)(?:\s*\(pinfunction "([^"]*)"\))?\s*\(pintype "([^"]*)"\)', part)
        nets[name] = [(r, p, re.sub(r'_[^_]*$', '', f) if f else '', ty) for r, p, f, ty in nodes]
        for r, p, f, ty in nodes: pinnet[(r, p)] = name
    return parts, nets, pinnet

OWNER = set()   # (schematic, (ref, pin)) whose role comes from the owner's drawing
THRU = {}       # schematic -> the references of parts a signal passes through
def owner_roles(sch, repo):
    pre = pre_shapes(sch, repo); out = {}
    for l in analyse(sch):
        k = (l['name'], tuple(sorted((q['ref'], q['pin']) for q in l['pins'])))
        sh = pre.get(k, l['shape']); r = {'output': 'drv', 'input': 'rcv', 'bidirectional': 'bid'}.get(sh)
        if r and len(l['pins']) == 1:
            q = l['pins'][0]; ref = re.sub(r'(?<=\d)[A-H]$', '', q['ref']); out.setdefault((ref, q['pin']), r)
    return out

def roles(key, sch):
    """(ref, pin) -> drv | rcv | bid | weak | None, for every pin on a named net"""
    parts, nets, pinnet = netlist(sch); cfg = board_cfg(key, parts); R = {}
    jumpers = JUMPERS.get(key, set())
    def through(ref): return bool(THROUGH.search(parts.get(ref, ''))) or ref in jumpers   # a jumper header too
    def first(table, a, b):
        for pa, pb, r in table:
            if re.fullmatch(pa, a) and re.fullmatch(pb, b): return r
    later = []
    for net, nodes in nets.items():
        if POWER.fullmatch(net): continue
        for ref, pin, fn, ty in nodes:
            lib = parts.get(ref, ''); base = re.match(r'[A-Z]+\d+', ref).group(0)
            r = first(cfg['rules'], base, net)
            if not r: r = first(PARTS, lib, fn)
            if r == 'mem-data':
                we = [n for n, nodes in nets.items() for r2, p2, f2, t2 in nodes if r2 == ref and re.fullmatch(r'~\{WE\}|WE', f2)]
                r = 'drv' if all(POWER.fullmatch(n) for n in we) else 'bid'   # /WE on VCC: a ROM that only drives
            if r in ('245-A', '245-B'):
                d = [n for n, nodes in nets.items() for r2, p2, f2, t2 in nodes if r2 == ref and f2 in ('A->B', 'DIR')]
                d = d[0] if d else ''
                r = 'bid' if not POWER.fullmatch(d) else ('rcv' if (r == '245-A') == (d != 'GND') else 'drv')
            if r == 'fw': R[(ref, pin)] = None; continue
            if not r and is_bus_conn(lib, ref) and cfg['side'] == 'header': later.append((ref, pin, net)); continue
            if not r and is_bus_conn(lib, ref):
                if cfg['side'] == 'card' and not BOTH.fullmatch(net) and bus_role(net, 'card'): later.append((ref, pin, net)); continue
                r = bus_role(net, cfg['side'])
            if not r and through(ref): later.append((ref, pin, net)); continue
            if not r and ref[0] in 'JP' and not MCU.search(lib) and ty == 'passive':
                later.append((ref, pin, net)); continue
            if not r and not MCU.search(lib):
                r = {'output': 'drv', 'tri_state': 'drv', 'open_collector': 'drv', 'open_emitter': 'drv',
                     'input': 'rcv', 'bidirectional': 'bid'}.get(ty)
            R[(ref, pin)] = r
    # A pin no rule decides (a microcontroller's, a VIA port's) takes its direction from the owner's label on it, the
    # pre-K21 one where K21 changed it, so the parts beyond it resolve too.
    drawn = owner_roles(sch, key[0])
    for k, v in drawn.items():
        if k in R and R[k] is None: R[k] = v; OWNER.add((sch, k))
        # parts the signal passes through, then headers; repeat while anything resolves
    thr = [(ref, pin, net) for ref, pin, net in later if through(ref)]
    hdr = [(ref, pin, net) for ref, pin, net in later if not through(ref)]
    links = []
    for ref, pin, net in thr:
        mine = {p: n for (r, p), n in pinnet.items() if r == ref}
        part = [n for n in partners(parts.get(ref, ''), pin, mine) if n != net]
        lib = parts.get(ref, '')
        if not part: R[(ref, pin)] = None
        elif all(POWER.fullmatch(n) for n in part):   # to a rail: a pull-up or -down (a resistor or jumper), a switch that drives
            # A jumper to a rail only sets a level, as a pull-up does, whether it ships open or bridged: it is no
            # source. A switch to a rail (a reset button) drives the line.
            R[(ref, pin)] = ('weak' if lib == 'Device:R' or re.search(r'Jumper:', lib) or ref in jumpers
                             else None if lib == 'Device:C' else 'drv' if re.search(r'Switch:', lib) else 'rcv')
        else: links.append((ref, pin, net, [n for n in part if not POWER.fullmatch(n)]))
    edges = [(ref, pin, net) for ref, pin, net in hdr if is_bus_conn(parts.get(ref, ''), ref) and cfg['side'] != 'header']
    far = {(ref, pin): b for ref, pin, a, b in links}   # b: the partner nets
    linked = set(far)                                   # pins whose role the flow decides; they are not sources
    hdr = [x for x in hdr if x not in edges]
    def spread(depth):
        for _ in range(len(links) + 1):
            for ref, pin, a, bs in links:
                for b in bs:
                    if a in depth and depth.get(b, 99) > depth[a] + 1: depth[b] = depth[a] + 1
    for _ in range(8):
        # how many pass-through parts lie between each net and a real source
        depth = {n: 0 for n, nodes in nets.items()
                 if any(R.get((r, p)) in ('drv', 'bid') and (r, p) not in linked for r, p, f, t in nodes)}
        spread(depth)
        # a card's edge: a signal flows into it if the card drives it (a clock, a reset, an IRQ), out of it otherwise
        for ref, pin, net in edges:
            if net in depth and not (depth[net] == 0 and R.get((ref, pin)) == 'drv'): R[(ref, pin)] = 'rcv'
            else: R[(ref, pin)] = 'drv'; depth[net] = 0
        spread(depth)
        for ref, pin, a, bs in links:
            da = depth.get(a); ds = [depth[b] for b in bs if b in depth]; db = min(ds) if ds else None
            if da is not None and (db is None or da < db): R[(ref, pin)] = 'rcv'
            elif db is not None and (da is None or db < da): R[(ref, pin)] = 'drv'
        for ref, pin, net in hdr:
            if R.get((ref, pin)): continue
            others = [R.get((r, p), 'x') for r, p, f, t in nets[net] if r != ref]
            # a pass-through part whose far side reaches no source can't drive this net
            dead = lambda bs: not set(bs) & set(depth) and all(R.get((r2, p2)) is not None or through(r2)
                                                                for b in bs for r2, p2, f2, t2 in nets[b])
            others = ['rcv' if o in (None, 'x') and far.get((r, p)) is not None and dead(far[(r, p)]) else o
                      for o, (r, p, f, t) in zip(others, [x for x in nets[net] if x[0] != ref])]
            if 'bid' in others: R[(ref, pin)] = 'bid'
            elif 'drv' in others: R[(ref, pin)] = 'rcv'
            elif all(o not in (None, 'x') for o in others) or not others: R[(ref, pin)] = 'drv'
    later = hdr + edges + [(r, p, n) for r, p, n, o in links]
    for ref, pin, net in later: R.setdefault((ref, pin), None)
    THRU[sch] = {r for r in parts if through(r)}
    return R, cfg, nets

def fn_of(nets, ref, pin):
    for n, nodes in nets.items():
        for r, p, f, t in nodes:
            if r == ref and p == pin: return f
def partners(lib, pin, mine):
    """the nets a pass-through part connects this pin to: mine is pin -> net for every pin of the part"""
    if 'SW_DIP' in lib and pin.isdigit(): return [mine[q] for q in [str(17 - int(pin))] if q in mine]
    if re.search(r'Conn_02x\d+_Odd_Even|Conn_02x01', lib) and pin.isdigit():    # a 2-row jumper: across the row
        n = int(pin); return [mine[q] for q in [str(n + 1 if n % 2 else n - 1)] if q in mine]
    if 'BSS138' in lib:                                                       # a level shifter: source to drain
        return [mine[q] for q in {'2': ['3'], '3': ['2']}.get(pin, []) if q in mine]
    if len(mine) == 3 and set(mine) >= {'1', '2', '3'}:                       # a 3-pin jumper: the middle and an end
        return [mine['2']] if pin in ('1', '3') else [mine['1'], mine['3']]
    return list({n for p, n in mine.items() if p != pin})
def pre_shapes(sch, repo):
    rel = os.path.relpath(sch, K + f'6502-{repo}')
    g = subprocess.run(['git', '-C', K + f'6502-{repo}', 'show', f'{K21[repo]}^:{rel}'], capture_output=True, text=True)
    if g.returncode: return {}
    f = tempfile.mktemp(suffix='.kicad_sch'); open(f, 'w').write(g.stdout)
    try: return {(l['name'], tuple(sorted((q['ref'], q['pin']) for q in l['pins']))): l['shape'] for l in analyse(f)}
    finally: os.remove(f)

def shapes(sch):
    p = sch.split('/'); repo, board, rev = p[-5].split('-')[-1], p[-3], p[-2][4:]; key = (repo, board, rev)
    R, cfg, nets = roles(key, sch); pre = None; out = []
    for l in analyse(sch):
        if POWER.fullmatch(l['name']): out.append((l, 'passive', 'rule')); continue
        ks = [(re.sub(r'(?<=\d)[A-H]$', '', q['ref']), q['pin']) for q in l['pins']]
        rs = [R.get(k) for k in ks]
        # a chip's pin on the wire decides the label; a part the signal passes through decides only on its own
        # (a 74C922's Y input beside its diode's anode is an input)
        chip = [(r, k) for r, k in zip(rs, ks) if k[0] not in THRU[sch] and r is not None]
        use = chip if chip else list(zip(rs, ks))
        dec = set(r for r, k in use if (sch, k) not in OWNER) - {None}
        if SUPPLY.fullmatch(l['name']): dec = set()
        if 'bid' in dec: w = 'bidirectional'
        elif 'drv' in dec: w = 'output'
        elif 'rcv' in dec: w = 'input'
        elif 'weak' in dec: w = 'output'
        else:
            if pre is None: pre = pre_shapes(sch, repo)
            k = (l['name'], tuple(sorted((q['ref'], q['pin']) for q in l['pins'])))
            out.append((l, pre.get(k, l['shape']), 'kept')); continue
        out.append((l, w, 'rule'))
    return out, cfg

def apply(sch, want):
    from sch import Sch
    S = Sch(sch); t = S.t; edits = []
    for l in S.labels:
        if l['kind'] == 'global_label' and l['uuid'] in want and want[l['uuid']] != l['shape']: edits.append((l['a'], l['e'], want[l['uuid']]))
    for a, e, w in sorted(edits, reverse=True):
        t = t[:a] + re.sub(r'\(shape \w+\)', f'(shape {w})', t[a:e], count=1) + t[e:]
    open(sch, 'w', encoding='utf-8', newline='').write(t); return len(edits)

def check():
    """derived-check.py's label shape check: every schematic on the rule. Cached by the bytes of each schematic and
    of these tools."""
    sys.path.insert(0, os.path.dirname(H)); from cache import Cache, digest
    C = Cache('label-shapes', os.path.abspath(__file__))
    tools = [os.path.join(H, f) for f in ('flow.py', 'labelpins.py', 'sch.py')] + [f'{K}6502-{r}/Tools/data/jumpers.json' for r in common.present()]
    bad = 0
    for sch in files('Hardware/*/Rev */*.kicad_sch'):
        off = C.get('flow ' + digest(sch, *tools), lambda sch=sch: [f"{l['name']} {l['shape']} -> {w} at {','.join(q['ref'] for q in l['pins'])}"
                                                               for l, w, how in shapes(sch)[0] if l['shape'] != w])
        for o in off: print(sch.split('/Hardware/')[-1], '|', o); bad += 1
    C.save(); print(f'{bad} labels off the rule'); sys.exit(1 if bad else 0)

if __name__ == '__main__':
    if '--check' in sys.argv: check()
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--all' in sys.argv or not args: args = files('Hardware/*/Rev */*.kicad_sch')
    for sch in map(os.path.abspath, args):
        out, cfg = shapes(sch); off = [(l, w, how) for l, w, how in out if l['shape'] != w]
        kept = collections.Counter(l['name'] for l, w, how in out if how == 'kept')
        print(f"{sch.split('/Hardware/')[-1]}: {len(out)} labels, {len(off)} off the rule, side {cfg['side']}{' (guessed)' if cfg.get('auto') else ''}")
        for l, w, how in sorted(off, key=lambda x: x[0]['name']):
            print(f"  {l['name']:12} {l['shape']:>13} -> {w:13} at {','.join(q['ref'] for q in l['pins'])}{'  (pre-K21)' if how == 'kept' else ''}")
        if kept: print('  kept, no rule decides:', ' '.join(sorted(kept)))
        if '--apply' in sys.argv and off: print('  set', apply(sch, {l['uuid']: w for l, w, how in out}))
