# CAD: the flat parts

The base plates, the top panels and the helper enclosures' tops are laser-cut from clear acrylic. These tools read
how a machine is put together from its assembly file, `CAD/Assembly.json`, and place every board on the plate from
its own PCB, so a plate, its mounting drawing and its tops can be generated and checked instead of drawn by hand.

**Status (2026-11-07).** The assembly file and its check are written, starting with the KIM. Generating the mounting
drawing and `Plate.svg` (`CAD.md` C4) and the tops (C5) come next. The other machines get their assembly files when
their parts are generated (C7). Until then each plate's mounting drawing comes from an older script kept outside
the repositories.

## What's here

| File | What it does |
|---|---|
| `assembly.py` | Reads `CAD/Assembly.json`, places each board from its PCB, and checks it: every board hole on a plate hole or a listed position, every plate hole used, the margin and gaps kept, every listed top present. `-v` lists every plate hole and what uses it. |
| `standards.json` | The family's standards, below, as numbers. An assembly file can override one for its own machine, and says why. |
| `board_dump.py` | Writes one PCB's outline, mounting holes and parts as JSON. It runs with KiCad's Python, which has `pcbnew`; `assembly.py` calls it and caches the result in `Tools/work/cache.json`. |
| `fusion.py` | Reads the plates and tops drawn in Fusion 360 and exported with the Shaper Origin add-in, in millimetres. |

```sh
python3 Tools/cad/assembly.py         # this repository's assembly file, if it has one
python3 Tools/cad/assembly.py --all   # every repository's
```

## The assembly file

`CAD/Assembly.json` in each machine's repository. Positions are millimetres, looking down on the plate as the
computer is used: x to the right and y towards the front, from the plate's back-left corner.

- **`builds`**: each way the machine can be built on the one plate (the KIM has two). A build lists its boards.
- **A board**: `board`, `rev`, and `repo` when it comes from another repository (the KIM's four-board build uses the
  COB's Backplane Helper and the VCS's Main Board). `at` is the board's own back-left corner as it sits on the plate.
  `rot` turns the board from its PCB file: 0, 90 (clockwise, looking down), 180 or 270. Most boards are drawn upside
  down in KiCad, so they sit at 180: as the computer is used, the reset button and the 6502 graphic face the user,
  the bus connector is on the left, and the card slot is toward the front.
- **`top`**: the board has a top, at `CAD/Tops/<board>/Rev <rev>/<board> Top.svg` in its own repository.
  `"generated": true` marks a top these tools draw.
- **`gap`, `gap_y`**: a build's own gaps between boards side by side and one behind the other, when it doesn't keep
  the family's 10 mm.
- **`positions`**: a board hole with no plate hole under it, named as the mounting drawing names it (S1, S2), with the
  builds that use it and how each is stacked.
- **`printed_parts`**: the printed parts that screw to the plate, with their holes (`"corners"` for the Corners),
  the builds they're in, and a note for the drawing.
- **`hardware`**, **`notes`**: what the drawing's hardware table and notes need beyond the normal stack.

Keys that start with `_` are notes for the reader, such as why a build keeps its own gap.

## The standards

Measured on 2026-11-07 from the 54 files drawn in Fusion (the 5 plates, 34 board tops, 13 enclosure tops and 2 stray
copies since removed), each top placed on its board by the mounting holes and measured against the board's STEP
model, and confirmed by the owner the same day (`CAD.md` C2). The owner's rulings on the differences are marked.

### Material and stack

- **Clear acrylic, 3 mm**, for every plate and every top.
- **A plate is three layers**, each cut from the same `Plate.svg`.
- **Tops sit on 10 mm standoffs** above the board. M3 throughout, M2.5 for an LCD.
- **A normal mounting hole**, from the bottom up: an M3 × 12 pan head through the back of the plate, a female-male
  standoff, the board, a female-female standoff, the top, and an M3 × 6 pan head.

### Plates

- **The boards' area with a 10 mm margin** on every side, measured on all five plates.
- **10 mm between neighbouring boards** (COB, DEV and VCS). The COB's Keyboard Encoder Helper, 10.07 mm from its
  neighbour, is corrected to 10 and its plate fixed (owner). The KIM's four-board build keeps its own gaps, 15 mm and
  5 mm, because its plate is already made (owner).
- **Corner radius 5 mm.**
- **Every M3 hole Ø3.2**, the standard clearance for M3: one under each board hole, and the printed parts' holes. The
  KIM's Cable Bridge holes were Ø3.4, a loose clearance chosen by accident in Fusion, and become Ø3.2 (owner).
- **A printed Corner at each corner**, its hole 5 mm in from both edges.
- **A Center Support**, where a plate needs one: four holes on a 15 mm square, centred on the plate (COB, VCS).
- **Rubber feet**, Ø10, in the recess under each Corner and Center Support.
- A machine's own holes are in its assembly file: the KIM's Hanger and Cable Bridge, the ACE's two spare M2 holes
  (Ø2.2) under the keyboard.

### Board tops

- **The top's outline is the board's outline**, corner radius and all, exactly. Four older tops are off by 0.26–0.51
  mm; generated tops are exact (owner).
- **An M3 hole, Ø3.2, at every mounting hole under the top.** The ACE's VGA Adapter holes have none: the adapter
  bolts there.
- **Drawn seen from above**, never mirrored.

### Openings in a top

A top needs an opening wherever a part **reaches into the top's sheet**, higher than the 10 mm standoffs and inside
the top's outline, and wherever the builder **needs to reach a short part**.

- **Tall parts.** Today's tops have an opening for every part that reaches into the sheet. The connectors at the
  edges (DB9, DB25, PS/2, audio, the power jack, RJ45) stand taller than 10 mm only past the board's edge, so the
  outline clears them. Two that reach in without an opening, the Backplane Pro 1.1 and 1.2's power jack and the DB9
  under the Joystick Helper's enclosure top, get openings (owner).
- **Short parts to reach**, on every top: every pin header and JST XH header, so every jumper
  (`Tools/data/jumpers.json`) and off-board header (`Tools/data/offboard.json`), and the reset button.
- **Short parts never reached:** plain IC sockets, the oscillator can, the power switch at the board's edge.
- **The owner's own choices**, named in the assembly file because no rule gives them: the sockets of chips a builder
  swaps, LCDs and keyboards.

**Margins are nominal, and round outward (owner).** A little extra room round a part is a good thing, and measuring
too precisely causes problems. Each margin below is the least clearance round the part's 3D body. The opening's sides
then move outward to whole 0.5 mm, centred on the part, so a margin comes out at the figure or a little more and
every opening has round-number sizes.

| Kind of opening | Margin round the 3D body | Corner radius | Measured |
|---|---|---|---|
| Pin headers, JST XH headers, LCD headers | 1.0 mm | 0.5 mm | 46 openings, each 1.00 on all four sides |
| Card slots, DIP switches, ZIF and swapped-chip sockets, the bus box header | 1.5 mm | 1.0 mm | 29 openings, each 1.50 on all four sides |
| An HC-49 crystal | 0.5 mm, as a slot with round ends | half the slot's width | 0.35–0.48 on 8 tops; 0.5 was meant (owner) |
| An LCD window | 1.0 mm | 1.0 mm | KIM Keypad LCD Helper |
| A keyboard window, round all its keys | 1.9 mm across, 1.6 mm front to back | 1.0 mm | ACE, COB Keyboard Helper (owner: to be tried on the KIM Board) |

**Openings close together become one** (owner): two openings that would leave less than 3 mm of acrylic between them
are merged.

**Round holes:**

| Hole | Over |
|---|---|
| Ø3.3 | a reset button, under the ACE's printed Reset Button. The family's standard (owner): the COB's printed Button, over a Ø2.5 hole, had a stem too thin |
| Ø5.5 | an LCD's contrast trimmer |
| Ø8 | the COB Clock Helper's 5.8 mm push switches, which stand through the top |
| Ø11 | the COB GPIO Helper's 6 mm push switches, under printed Buttons |
| Ø3.0 | the COB LCD Board's TFT mounting screws |

### Enclosure tops

The COB's helper enclosures: **the board's outline grown by 2 mm on every side, corner radius 7 mm** (5 + 2), with
the same holes and openings as the board's own top.

### The generated files

- **Drawn as the computer is used, seen from above**, front edge at the bottom. Fusion's exports are sometimes turned
  180° and sometimes not; `assembly.py` finds which way round today's `Plate.svg` is by its holes.
- **In millimetres**, at 1:1, in the Shaper export's style (a black outline, white holes), so LightBurn imports them
  as it does today. LightBurn files are the owner's: when a cut file changes, say which `.lbrn2` needs remaking.
