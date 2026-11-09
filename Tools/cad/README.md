# CAD: the flat parts

The base plates, the top panels and the helper enclosures' tops are laser-cut from clear acrylic. These tools read
how a machine is put together from its assembly file, `CAD/Assembly.json`, and place every board on the plate from
its own PCB, so a plate, its mounting drawing and its tops can be generated and checked instead of drawn by hand.

**Status (2026-11-07).** The KIM's plate, its mounting drawing, its STL and its boards' tops are generated from its
assembly file (`CAD.md` C4, C5). The KIM Board's new top is a draft until the owner approves it (C6). The other machines get their assembly files when their parts are generated
(C7); until then their plates are Fusion's and their mounting drawings come from an older script kept outside the
repositories.

## What's here

| File | What it does |
|---|---|
| `make.py` | Writes `CAD/Bases/Plate.svg`, `Plate Mounting Drawing.svg` and `.png`, and `Plate.stl`. `--check` writes nothing and fails if any is out of date; `derived-check.py` runs it. `--compare` lists how the generated plate differs from the one in git. |
| `plate.py` | The plate from the assembly file: its outline, its holes and what uses each one in each build, and `Plate.svg`. |
| `drawing.py` | The mounting drawing: both builds, the numbered holes, the boards, the hardware each build needs, counted from each hole's kind, and how a hole goes together. |
| `bodies.py` | Reads the parts' 3D bodies from a board's STEP model: each part's box, a profile of it in 1 mm bands above the standoffs, and any round feature at its top. Slow, so cached by the STEP's bytes. |
| `tops.py` | A board's top, from its PCB, its STEP model and the assembly file: the openings below, merged and kept clear of the mounting holes. `--report` lists every opening and why it's there; `--compare OLD.svg` lists how a top differs from another, such as Fusion's. Needs build123d. |
| `solid.py` | `Plate.stl`, one layer of the plate as a 3D model, from `Plate.svg`. Needs build123d. |
| `setup.sh` | Makes `Tools/work/venv`, the Python with build123d that `solid.py` (and the tops, to come) needs. Run it once. |
| `assembly.py` | Reads `CAD/Assembly.json`, places each board from its PCB, and checks it: every board hole on a plate hole or a listed position, every plate hole used, the margin and gaps kept, every listed top present. `-v` lists every plate hole and what uses it. |
| `standards.json` | The family's standards, below, as numbers. An assembly file can override one for its own machine, and says why. |
| `board_dump.py` | Writes one PCB's outline, mounting holes and parts as JSON. It runs with KiCad's Python, which has `pcbnew`; `assembly.py` calls it and caches the result in `Tools/work/cache.json`. |
| `fusion.py` | Reads the plates and tops drawn in Fusion 360 and exported with the Shaper Origin add-in, in millimetres. |

```sh
zsh Tools/cad/setup.sh                # once: the Python that reads the STEP models and writes the STL
python3 Tools/cad/make.py             # write this repository's plate, drawing, STL and tops from CAD/Assembly.json
python3 Tools/cad/make.py --check     # are they current? derived-check.py runs this
python3 Tools/cad/assembly.py -v      # check the assembly file, and list every plate hole and what uses it
```

Add `--all` to any of them for every repository. When `Plate.svg` changes, `make.py` says so: remake `Plate.lbrn2` in
LightBurn from the new SVG; the same goes for a top. `Plate.stl`'s header names the `Plate.svg` it was made from, and
a generated top names the sha1 of everything it was made from, so the check needs no 3D tools.

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
  `"generated": true` marks a top these tools draw, and `"draft": true` one waiting for the owner's approval, which
  `make.py` leaves alone. A generated top lists what no rule gives: `openings`, each round parts (`refs`), a named
  rule area (`zone`), a block (`block`, at and size from the board's back-left corner in its PCB file) or a lever's
  swing (`lever`: the part, the height its knob stands above, the length and which way it swings), of a kind from
  `standards.json`, with its own `margin` if it needs one; and round `holes` over a part, centred on the round feature
  at the top of its 3D model. `also` lists the other revisions of the board that get the same top in their folders.
- **`gap`, `gap_y`**: a build's own gaps between boards side by side and one behind the other, when it doesn't keep
  the family's 10 mm.
- **`positions`**: a board hole with no plate hole under it, named as the mounting drawing names it (S1, S2): for each
  build that uses it, its kind, `resting` (a standoff stands on the plate) or `on_part` (the board screws to the
  printed part `part` names).
- **`printed_parts`**: the printed parts that screw to the plate, with their holes (`"corners"` for the Corners),
  the builds they're in, and a note for the drawing.
- **`plate.added`**: a hole added to the plate after plates were made, with the note the drawing shows for it.
- **`hardware`**, **`notes`**: what the drawing's hardware table and notes need beyond the stacks, which are in
  `standards.json`.
- **Drawing hints**, which only place text: `drawing` (title, subtitle), a build's `short` (its table column) and
  `phrase` ("the four-board build"), and a board's `label` (where its name goes) and `features` (parts and named rule
  areas outlined on the drawing).

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

- **Tall parts.** Today's tops have an opening for every part that reaches into the sheet. The opening goes round
  the part as it is at the top's height, so a tab or pin at board level doesn't pull it off centre, and grows only if
  something of the part above the top (a ZIF socket's lever, standing up) wouldn't pass through. The connectors at the
  edges (DB9, DB25, PS/2, audio, the power jack, RJ45) stand taller than 10 mm only past the board's edge, so the
  outline clears them. Two that reach in without an opening, the Backplane Pro 1.1 and 1.2's power jack and the DB9
  under the Joystick Helper's enclosure top, get openings (owner).
- **Short parts to reach**, on every top: every pin header and JST XH header, so every jumper
  (`Tools/data/jumpers.json`) and off-board header (`Tools/data/offboard.json`); every box header for a ribbon
  cable, bus or GPIO, whose plug comes up through the top (owner, 2026-11-07: the Fusion tops of the Keypad Helper
  and Keypad LCD Helper had none, and needed them); and the reset button.
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
| Card slots, DIP switches, ZIF and swapped-chip sockets, box headers for ribbon cables | 1.5 mm | 1.0 mm | 29 openings, each 1.50 on all four sides |
| An HC-49 crystal | 0.5 mm, as a slot with round ends | half the slot's width | 0.35–0.48 on 8 tops; 0.5 was meant (owner) |
| An LCD window | 1.0 mm | 1.0 mm | KIM Keypad LCD Helper |
| A keyboard window, round all its keys | 1.9 mm across, 1.6 mm front to back | 1.0 mm | ACE, COB Keyboard Helper (owner: to be tried on the KIM Board) |

**Openings close together become one** (owner): where two openings would leave less than 3 mm of acrylic between
them, that acrylic is cut away; each keeps its own shape elsewhere. Keys that sit together become one rectangular
window.

**Mounting holes keep their acrylic:** no opening comes within 3.5 mm of a mounting hole's centre, so the screw head
and the standoff have something to bear on. Where that costs an opening less than a quarter of itself, its side is
pulled straight back; otherwise a round bite is cut from it.

**A lever needs room to swing:** a ZIF socket's lever gets a window along its swing, from the centre of its knob, as
long as the assembly file says, with 2 mm round it so it can be worked with fingers, pliers or tweezers (owner).

**A part at the board's edge** that reaches into the top gets a notch in the outline, as the ACE's DB9s and power jack
have.

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
  180° and sometimes not; `assembly.py` finds which way round a Fusion `Plate.svg` is by its holes.
- **Plate holes to 0.01 mm.** A board's edge can sit a few micrometres off its holes (the COB Backplane Helper's
  does), and that shouldn't reach the plate.
- **`Plate.stl`** is one layer, in the frame Fusion exported the KIM's in: centred, x to the right, z towards the
  front, y up, from y 6 to 9.
- **In millimetres**, at 1:1, in the Shaper export's style (a black outline, white holes), so LightBurn imports them
  as it does today. LightBurn files are the owner's, and git doesn't track them (`.lbrn2`, with the slicer's `.3mf`
  and `.bgcode`, are in `.gitignore`): when a cut file changes, say which `.lbrn2` needs remaking.
