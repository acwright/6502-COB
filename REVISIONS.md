# Revisions

Every revision of every board in this repository, and what is known about each. The dates of the checks are at the end.

**Status** says what has happened to a revision:

- **Made, matches order:** JLCPCB's own copy of the order is byte-identical to the production zip here, and the PCB file regenerates the same copper, mask, outline and holes. This compares files with the order. It says nothing about whether the board works: that's the **Label**.
- **Made, not compared:** the board exists, but its files haven't been compared with an order.
- **Ordered:** placed, and not yet arrived.
- **Drawn:** the files are complete, and the board hasn't been ordered.
- **Never made**, or **To confirm** where nothing on record says either way.

**Label** says whether a builder can rely on a revision. Make the newest revision of a board, and check its label first:

- **Tested:** This revision was built and tested.
- **Proven design:** Not built at this revision, but its circuit is a tested revision's. The only changes are silkscreen text, part values, mounting holes, outline clean-up, capacitor pitch, socket outlines, a footprint swap with the same holes, a solder jumper's default, or tracks rerouted with DRC and the netlist check passing. A builder can treat it as tested.
- **Untested:** The circuit, the power path or the layout changed in a way that only a built board proves, or the board has never been built at all.

**Holes** is how far the corner mounting holes sit from the board's edges. The standard is 6 mm, and 5 mm on the ACE Board, the CF Adapter and the Keyboard Helper. A dash means a card or cart, which has no corner holes.

| Board | Rev | Status | Label | Order | Ordered | Made from | Tindie stock | Size (mm) | Holes | Top panel | Enclosure | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Backplane | 1.0 | Made, matches order | **Tested** | Y50 | 2024-07-03 | `3e494e3` | 3 | 100×100 | 6 mm | yes | — |  |
| Backplane Helper | 1.0 | Made, matches order | **Tested** | Y77 | 2025-12-02 | `4115600` | 3 | 50×100 | 6 mm | yes | — |  |
| Backplane Pro | 1.0 | Made, matches order | **Tested** | Y30 | 2024-04-30 | `305dab8` | 4 | 100×100 | 6 mm | yes | — | symbol has pins the footprint lacks: J2 shield pin; the board's silk says 6502 BACKPLANE, its name when ordered |
| Backplane Pro | 1.1 | Made, matches order | **Tested** | Y93 | 2026-06-21 | `7486bd6` | 4 | 100×100 | 6 mm | yes | — |  |
| Backplane Pro | 1.2 | Drawn | **Untested**: a 1N5819 in the power path (`VCC` near 4.6 V), and R5 removed |  |  |  | — | 100×100 | 6 mm | yes | — |  |
| Blinkenlights Card | 1.0 | Made, matches order | **Tested** | Y40 | 2024-06-08 | `7d050b0` | 4 | 100×57.62 | — | — | — |  |
| Blinkenlights Card | 1.1 | Drawn | **Untested**: decoupling capacitors added, with tracks rerouted to reach them |  |  |  | — | 100×57.62 | — | — | — |  |
| Breadboard Helper | 1.0 | Made, matches order | **Tested** | Y39 | 2024-06-08 | `7d050b0` | 3 | 75×55 | — | — | — |  |
| Breadboard Helper | 1.1 | Drawn | **Proven design**: J1 takes the box header's footprint, with the same holes |  |  |  | — | 75×55 | — | — | — |  |
| CPU Card | 1.0 | Made, matches order | **Tested** | Y18 | 2024-04-03 | `da975a6` | 4 | 100×57.62 | — | — | — |  |
| CPU Card | 1.1 | Drawn | **Proven design**: 10k pull-ups, some tracks rerouted, silkscreen |  |  |  | — | 100×57.62 | — | — | — |  |
| CPU Card Pro | 1.0 | Never made | **Untested**: never made |  |  |  | — | 100×57.62 | — | — | — | title block credits bahamutkotd, who contributed |
| Clock Card | 1.0 | Ordered | **Untested**: a new board, ordered and not tested yet |  |  |  | — | 100×57.62 | — | — | — | Order 1, placed 2026-11-02 |
| Clock Helper | 1.0 | Made, matches order | **Tested** | Y74 | 2025-11-21 | `65a5e49` | 4 | 50×50 | 5.32–5.68 mm | yes | yes |  |
| Clock Helper | 1.1 | Drawn | **Proven design**: mounting holes moved to the standard, silkscreen |  |  |  | — | 50×50 | 6 mm | yes | yes |  |
| DB25 Helper | 1.0 | Made, matches order | **Tested** | Y65 | 2025-10-06 | `013b131` | — | 100×50 | 5.32–6.25 mm | yes | yes |  |
| DB25 Helper | 1.1 | Drawn | **Proven design**: mounting holes moved to the standard, silkscreen |  |  |  | — | 100×50 | 6 mm | yes | yes |  |
| GPIO Breadboard Helper | 1.0 | Made, matches order | **Tested** | Y57 | 2025-10-06 | `0dd90c8` | 4 | 58.83×55 | — | — | — |  |
| GPIO Card | 1.0 | Made, matches order | **Tested** | Y45 | 2024-06-19 | `390cb17` | 3 | 100×57.62 | — | — | — |  |
| GPIO Helper | 1.0 | Made, matches order | **Tested** | Y66 | 2025-10-06 | `013b131` | 4 | 100×50 | 5.32–6.25 mm | yes | yes |  |
| GPIO Helper | 1.1 | Drawn | **Proven design**: mounting holes moved to the standard, silkscreen |  |  |  | — | 100×50 | 6 mm | yes | yes |  |
| Joystick Helper | 1.0 | Made, matches order | **Tested** | Y73 | 2025-11-16 | `4f73288` | 4 | 50×50 | 5.32–5.68 mm | yes | yes |  |
| Joystick Helper | 1.1 | Drawn | **Proven design**: mounting holes moved to the standard, silkscreen |  |  |  | — | 50×50 | 6 mm | yes | yes |  |
| Keyboard Encoder Helper | 1.0 | Made, matches order | **Tested** | Y72 | 2025-11-14 | `4470a4f` | 4 | 100×50 | 5.32–6.25 mm | yes | yes | to fit the COB plate, drill plate holes 9 and 21 out to 5 mm: see the README |
| Keyboard Encoder Helper | 1.1 | Drawn | **Proven design**: mounting holes, silkscreen |  |  |  | — | 100×50 | 6 mm | yes | yes |  |
| Keyboard Helper | 1.0 | Made, matches order | **Tested** | Y70 | 2025-10-27 | `3b654ed` | 4 | 335×125 | 5 mm | — | yes |  |
| LCD Board | 1.0 | Made, matches order | **Tested** | Y80 | 2026-01-13 | `2a232e3` | — | 100×100 | 6 mm | yes | — |  |
| LCD Card | 1.0 | Made, matches order | **Tested** | Y27 | 2024-04-22 | `f77fc20` | 4 | 100×57.62 | — | — | — |  |
| LCD Card | 1.1 | Drawn | **Proven design**: JP1, a solder jumper, ships open, where Rev 1.0's is bridged |  |  |  | — | 100×57.62 | — | — | — |  |
| Mega Helper | 1.0 | Made, matches order | **Tested** | Y81 | 2026-01-10 | `affcc47` | 3 | in footprint | — | — | — | symbol has pins the footprint lacks: Arduino header pins |
| Memory Card | 1.0 | Made, matches order | **Tested** | Y20 | 2024-04-03 | `da975a6` | 4 | 100×57.62 | — | — | — |  |
| PS2 Helper | 1.0 | Made, matches order | **Tested** | Y61 | 2025-10-06 | `0969243` | 4 | 100×50 | 5.32–6.25 mm | yes | yes |  |
| PS2 Helper | 1.1 | Drawn | **Proven design**: resistors moved and tracks rerouted, mounting holes, silkscreen |  |  |  | — | 100×50 | 6 mm | yes | yes |  |
| Prototype Card | 1.0 | Made, matches order | **Tested** | Y22 | 2024-04-03 | `da975a6` | 4 | 100×57.62 | — | — | — |  |
| RAM Card | 1.0 | Made, matches order | **Tested** | Y69 | 2025-10-28 | `9b9e95d` | 4 | 100×57.62 | — | — | — |  |
| RTC Card | 1.0 | Made, matches order | **Tested** | Y62 | 2025-10-06 | `0969243` | 4 | 100×57.62 | — | — | — |  |
| Serial Card | 1.0 | Made, matches order | **Tested** | Y67 | 2025-10-06 | `013b131` | 3 | 100×57.62 | — | — | — |  |
| Serial Card | 1.1 | Drawn | **Proven design**: silkscreen text only |  |  |  | — | 100×57.62 | — | — | — |  |
| Serial Card Pro | 1.0 | Made, matches order | **Tested** | Y36 | 2024-05-20 | `ffafeba` | 4 | 100×57.62 | — | — | — |  |
| Serial Card Pro | 1.1 | Drawn | **Proven design**: the DB-9 moved to KiCad's standard footprint (the same connector), tracks rerouted, silkscreen |  |  |  | — | 100×57.62 | — | — | — |  |
| Sound Card | 1.0 | Made, matches order | **Tested** | Y84 | 2026-01-13 | `3b4c7bb` | 4 | 100×57.62 | — | — | — |  |
| Sound Card | 1.1 | Drawn | **Proven design**: silkscreen text only |  |  |  | — | 100×57.62 | — | — | — |  |
| Storage Card | 1.0 | Made, matches order | **Tested** | Y47 | 2024-06-22 | `b8f89eb` | 4 | 100×57.62 | — | — | — | copper drawn differently by today's KiCad, as recorded in audit.py |
| Storage Card Pro | 1.0 | Made, matches order | **Untested**: made, and not tested yet: the BIOS has no driver for it | Y78 | 2025-12-11 | `b89a4a4` | — | 100×57.62 | — | — | — |  |
| Storage Card Pro | 1.1 | Drawn | **Untested**: silkscreen text only, but Rev 1.0 hasn't been tested |  |  |  | — | 100×57.62 | — | — | — |  |
| VERA Helper | 1.0 | Made, matches order | **Tested** | Y71 | 2025-11-04 | `e74f44e` | 4 | 100×80 | 5.32–6.25 mm | — | — |  |
| VERA Helper | 1.1 | Drawn | **Proven design**: mounting holes, capacitor pitch |  |  |  | — | 100×80 | 6 mm | — | — |  |
| VGA Card | 1.0 | Made, matches order | **Tested** | Y64 | 2025-10-06 | `0dd90c8` | 4 | 100×57.62 | — | — | — |  |
| VGA Card | 1.1 | Drawn | **Untested**: the pico9918 turned around, a new outline and jack mount, and A1 wired to `MODE1` |  |  |  | — | 100×57.62 | — | — | — |  |
| VGA Card Pro | 1.0 | Never made | **Untested**: never made |  |  |  | — | 100×57.62 | — | — | — | symbol has pins the footprint lacks: Pico pins 41-43 |
| Video Card | 1.0 | Made, matches order | **Tested** | Y53 | 2024-07-09 | `f890f21` | 2 | 100×57.62 | — | — | — |  |
| Video Card | 1.1 | Drawn | **Proven design**: JP7, a solder jumper, ships bridged (fine with a real TMS9918A's open-drain `/INT`), sockets, silkscreen |  |  |  | — | 100×57.62 | — | — | — |  |
| Video Card Pro | 1.0 | Never made | **Untested**: never made |  |  |  | — | 100×57.62 | — | — | — |  |

JLCPCB's orders were checked on 2026-11-04: each production zip marked *Made, matches order* was compared byte for byte with JLCPCB's copy, and its PCB regenerated to the same copper, mask, outline and holes. Each time this table is written, every PCB is checked again against its production zip, for copper and drill holes. Tindie stock is from the listings as saved on 2026-10-23.

<!-- History: hand-written. Tools/revision-audit/register.py keeps everything from here to the end. -->

## History

What changed in each revision of each board, newest first. The table above has the facts about each one.

**Schematic drawing, 2026-11-06.** Every schematic's 6502 bus, cart and card connectors are drawn one way, made revisions included: a short wire and a global label on each used pin, a no-connect flag on each unused one, and GND and VCC as global labels. Bus lines, bus entries and local labels for the bus are gone. Each label's name matches the board's silk. Where pins 4 and 6 carry `EXP1` and `EXP0`, or a cartridge grounds them, a note on the schematic says what `HRDB` does with them (see the README's *Extra pins*). No netlist changed, so no board did: the schematic PDFs are regenerated, and a few PCB files carry the new net names, as text only.

### Backplane

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Backplane/Rev 1.0/` and `Production/Backplane/Rev 1.0/` match the boards JLCPCB made (order Y50). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Backplane Helper

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/Backplane Helper/Rev 1.0/` and `Production/Backplane Helper/Rev 1.0/` match the boards JLCPCB made (order Y77). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Backplane Pro

#### Rev 1.2

Drawn, not yet made. Two changes from Rev 1.1:

- **R5 is removed.** It was a 1kΩ pull-up on `RESB`, in parallel with the CPU Card's. The CPU Card's pull-up is the only one a COB needs, and the reset circuit only pulls `RESB` low, through Q1. Without a CPU Card on the bus, `RESB` has no pull-up, so whatever drives the bus instead (a [Mega Helper](#mega-helper), for example) must hold `RESB` high itself.
- **D2, a 1N5819, is added** in series between the barrel jack (J1) and the power switch (SW1), anode at the jack, so a reversed supply can't reach VCC. It drops about 0.3–0.4 V, so VCC sits near 4.6 V.

The backplane carries no decoupling capacitors, as on the other backplanes: every card that plugs in has 100nF on each of its own chips.

#### Rev 1.1

- Built and tested. `Hardware/Backplane Pro/Rev 1.1/` and `Production/Backplane Pro/Rev 1.1/` match the boards JLCPCB made (order Y93). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

#### Rev 1.0

- Initial release, and the board on sale. Built and tested. `Hardware/Backplane Pro/Rev 1.0/` and `Production/Backplane Pro/Rev 1.0/` match the boards JLCPCB made (order Y30). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- This board was called the Backplane when it was ordered, so its silkscreen says `6502 BACKPLANE`. Today's [Backplane](#backplane) is a different board, order Y50.
- The PCB file was restored to that layout on 2026-11-04. A later edit only moved C8, C14, D1 and TP1 slightly, and Rev 1.1 is a full redesign, so that edit has no revision of its own. The schematic and BOM are today's, and they match this copper.

### Blinkenlights Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Adds `C1`–`C4`, 100nF decoupling capacitors, one beside each chip, with tracks rerouted to reach them. Rev 1.0 has no pads for them.
- The silkscreen spells out `RESB`. Rev 1.0's says `RSB`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Blinkenlights Card/Rev 1.0/` and `Production/Blinkenlights Card/Rev 1.0/` match the boards JLCPCB made (order Y40). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Breadboard Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- J1 uses the `6502 Bus Connector` footprint, the box header that is fitted, in place of Rev 1.0's plain 2×20 pin header. The pads are in the same places, so the copper, mask, holes and outline are Rev 1.0's. Only the silkscreen outline changes. The box header is longer than the board's edge, as on Rev 1.0 boards built with one, so its outline is cut off there.

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/Breadboard Helper/Rev 1.0/` and `Production/Breadboard Helper/Rev 1.0/` match the boards JLCPCB made (order Y39). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- The PCB file was restored to that layout on 2026-11-04. Later edits only changed pad shapes, when footprints were refreshed, so they don't make a Rev 1.1. The schematic and BOM are today's, and they match this copper.
- This is a different board from the [GPIO Breadboard Helper](#gpio-breadboard-helper): this one breaks out the full 6502 bus, and that one breaks out a VIA's PORT A and PORT B.

### Clock Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the standard position, 6 mm from each edge. The spacing goes from 39 × 39 mm to 38 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/Clock Helper/` and `CAD/Tops/Clock Helper/`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Clock Helper/Rev 1.0/` and `Production/Clock Helper/Rev 1.0/` match the boards JLCPCB made (order Y74). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Clock Card

Rev 1.0 has been ordered. No card has been built or tested yet. The card takes a 1 MHz DIP-14 can, the AC6502's standard `PHI2`. It has no power switch, and no `RESB` pull-up: the CPU Card's is the only one a COB needs. JP1 is open as made, so the clock reaches `PHI2` only through J3: fit a switch or a jumper there, or bridge JP1 if the clock never needs to stop.

### CPU Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Pull-up resistors changed from 1kΩ to 10kΩ.
- Some tracks are rerouted.
- The silkscreen labels U1 `65C02` and J3 `EXP`, and adds a `6502` label. It drops Rev 1.0's "Jumper J2 for original 6502" note.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/CPU Card/Rev 1.0/` and `Production/CPU Card/Rev 1.0/` match the boards JLCPCB made (order Y18). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### DB25 Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the standard position, 6 mm from each edge. The spacing goes from 88 × 39 mm to 88 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/DB25 Helper/` and `CAD/Tops/DB25 Helper/`.
- The project's name is `DB25 Helper`. The order's Gerbers carry its old name, `GPIO DB25 Helper`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/DB25 Helper/Rev 1.0/` and `Production/DB25 Helper/Rev 1.0/` match the boards JLCPCB made (order Y65). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### GPIO Breadboard Helper

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/GPIO Breadboard Helper/Rev 1.0/` and `Production/GPIO Breadboard Helper/Rev 1.0/` match the boards JLCPCB made (order Y57). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### GPIO Card

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/GPIO Card/Rev 1.0/` and `Production/GPIO Card/Rev 1.0/` match the boards JLCPCB made (order Y45). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### GPIO Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the standard position, 6 mm from each edge. The spacing goes from 88 × 39 mm to 88 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/GPIO Helper/` and `CAD/Tops/GPIO Helper/`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/GPIO Helper/Rev 1.0/` and `Production/GPIO Helper/Rev 1.0/` match the boards JLCPCB made (order Y66). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Joystick Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the standard position, 6 mm from each edge. The spacing goes from 39 × 39 mm to 38 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/Joystick Helper/` and `CAD/Tops/Joystick Helper/`. The holes' courtyards now overlap the courtyard of J2, the DB9 connector. That has been reviewed and is fine, so the project excludes it from DRC.
- The silkscreen says `JOYSTICK` at `J2`. Rev 1.0's says `DB9 MALE`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Joystick Helper/Rev 1.0/` and `Production/Joystick Helper/Rev 1.0/` match the boards JLCPCB made (order Y73). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Keyboard Encoder Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the standard position, 6 mm from each edge. The spacing goes from 88 × 39 mm to 88 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/Keyboard Encoder Helper/` and `CAD/Tops/Keyboard Encoder Helper/`.
- The silkscreen says `20pF` at `C2` and `C3`, the value to fit with the 16 MHz crystal, and `ATmega1284` at `U1`. Rev 1.0's say `22pF` and `ATmega1284-P`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Keyboard Encoder Helper/Rev 1.0/` and `Production/Keyboard Encoder Helper/Rev 1.0/` match the boards JLCPCB made (order Y72). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- To mount it on the COB's base plate, two plate holes have to be drilled wider: see [CAD](README.md#cad).

### Keyboard Helper

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Keyboard Helper/Rev 1.0/` and `Production/Keyboard Helper/Rev 1.0/` match the boards JLCPCB made (order Y70). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### LCD Board

**Rev 1.0**

- Initial release. Built and tested. `Hardware/LCD Board/Rev 1.0/` and `Production/LCD Board/Rev 1.0/` match the boards JLCPCB made (order Y80). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- The PCB file was restored to that layout on 2026-11-04. Later edits only changed pad shapes, when footprints were refreshed, so they don't make a Rev 1.1. The schematic and BOM are today's, and they match this copper.

### LCD Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- `JP1` is open as made. On Rev 1.0 it is bridged.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/LCD Card/Rev 1.0/` and `Production/LCD Card/Rev 1.0/` match the boards JLCPCB made (order Y27). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Mega Helper

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/Mega Helper/Rev 1.0/` and `Production/Mega Helper/Rev 1.0/` match the boards JLCPCB made (order Y81). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Memory Card

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/Memory Card/Rev 1.0/` and `Production/Memory Card/Rev 1.0/` match the boards JLCPCB made (order Y20). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- The PCB file was restored to that layout on 2026-11-04. Later edits only changed pad shapes, when footprints were refreshed, so they don't make a Rev 1.1. The schematic and BOM are today's, and they match this copper.

### Prototype Card

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Prototype Card/Rev 1.0/` and `Production/Prototype Card/Rev 1.0/` match the boards JLCPCB made (order Y22). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### PS2 Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the resistors `R2`–`R9` and reroutes the tracks around them.
- Moves the four mounting holes (`H1`–`H4`) to the standard position, 6 mm from each edge. The spacing goes from 88 × 39 mm to 88 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/PS2 Helper/` and `CAD/Tops/PS2 Helper/`.
- Drops the `R2-R9` silkscreen label.
- The silkscreen says `20pF` at `C4` and `C5`, the value to fit with the 16 MHz crystal. Rev 1.0's says `22pF`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/PS2 Helper/Rev 1.0/` and `Production/PS2 Helper/Rev 1.0/` match the boards JLCPCB made (order Y61). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### RAM Card

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/RAM Card/Rev 1.0/` and `Production/RAM Card/Rev 1.0/` match the boards JLCPCB made (order Y69). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

A Rev 1.1, with a latch per window and window selects that read as not selected when a jumper is missing, is planned.

### RTC Card

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/RTC Card/Rev 1.0/` and `Production/RTC Card/Rev 1.0/` match the boards JLCPCB made (order Y62). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Serial Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- The silkscreen says `SERIAL (DCE)` at J2 and `R6551AP` at U3. Rev 1.0's says `DB9 FEMALE (DCE)` and `6551`. Nothing else changed: the copper, mask, holes and outline are Rev 1.0's.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Serial Card/Rev 1.0/` and `Production/Serial Card/Rev 1.0/` match the boards JLCPCB made (order Y67). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Serial Card Pro

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- `J2` uses KiCad's standard DB-9 footprint, in a new position, in place of Rev 1.0's own. Its pin spacing and mounting lugs are the same, so the same connector fits both revisions.
- The silkscreen says `SERIAL (DTE)` and `R6551AP`. Rev 1.0's says `DB9 Male (DTE)` and `6551`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Serial Card Pro/Rev 1.0/` and `Production/Serial Card Pro/Rev 1.0/` match the boards JLCPCB made (order Y36). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Sound Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- The silkscreen says `ARMSID` at U1 and `SID VDD` at J2. Rev 1.0's says `6581` and `VDD`. Every tested build uses an ARMSID, and J2 is only for a real SID's supply, so the labels now say so. J2 stays: the COB is the experimenter's machine. Nothing else changed: the copper, mask, holes and outline are Rev 1.0's.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Sound Card/Rev 1.0/` and `Production/Sound Card/Rev 1.0/` match the boards JLCPCB made (order Y84). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Storage Card

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/Storage Card/Rev 1.0/` and `Production/Storage Card/Rev 1.0/` match the boards JLCPCB made (order Y47). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- The PCB file was restored to that layout on 2026-11-04. Later edits only changed pad shapes, when footprints were refreshed, so they don't make a Rev 1.1. The schematic and BOM are today's, and they match this copper.

### Storage Card Pro

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- The silkscreen says `20pF` at C5 and C6, the value the BOM lists. Rev 1.0's says `22pF`. Nothing else changed: the copper, mask, holes and outline are Rev 1.0's. No Storage Card Pro has been tested yet, at either revision.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Storage Card Pro/Rev 1.0/` and `Production/Storage Card Pro/Rev 1.0/` match the boards JLCPCB made (order Y78). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### VERA Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the standard position, 6 mm from each edge. The spacing goes from 88 × 69 mm to 88 × 68 mm.
- `C1` and `C2` use the 2.5 mm capacitor footprint in place of Rev 1.0's 5 mm one, matching the family's other through-hole boards. Pad 1 of each stays where it was.

**Rev 1.0**

- Initial release, and the board on sale. Its mounting holes are off the standard: 5.75 and 6.25 mm from the long sides' ends, and 5.32 and 5.68 mm from the top and bottom.
- Built and tested. `Hardware/VERA Helper/Rev 1.0/` and `Production/VERA Helper/Rev 1.0/` match the boards JLCPCB made (order Y71). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### VGA Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- `A1` reaches U1 pin 11, the pico9918's `MODE1`, as on the ACE Rev 1.1. A PICO9918 PRO takes it through a header pin soldered into its `MDE1` pad.
- JP1 is open as made, so the pico9918's `/INT` reaches `IRQB` (or `NMIB`, through J2) only through D1.
- D1 is named in its value field: a BAT85, cathode toward the pico9918.
- U1, the pico9918, is turned around, and the board's outline around its VGA jack changes. The two mounting holes move, and the tracks are rerouted to suit.
- U1 uses a socket footprint (`Socket_LongPads`) in place of Rev 1.0's `LongPads`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/VGA Card/Rev 1.0/` and `Production/VGA Card/Rev 1.0/` match the boards JLCPCB made (order Y64). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Video Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- `JP7` is bridged as made, which shorts across D1. On Rev 1.0 it is open, so `/INT` reaches `IRQB` or `NMIB` through D1. Both work, because a real TMS9918A's `/INT` is open-drain.
- U1 and U7 use socket footprints (`Socket_LongPads`) in place of Rev 1.0's `LongPads`.
- Adds the OSHW and A.C. Wright logos to the silkscreen.
- The silkscreen labels `J4` as `VIDEO`. Rev 1.0's says `Video Out`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Video Card/Rev 1.0/` and `Production/Video Card/Rev 1.0/` match the boards JLCPCB made (order Y53). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Video Card Pro

**Rev 1.0**

- Drawn, and never ordered.
