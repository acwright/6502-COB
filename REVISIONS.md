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
- **Proven design:** Not built at this revision, but its circuit is a tested revision's. The only changes are silkscreen text, part values, mounting holes, outline clean-up, parts moved a fraction of a millimetre onto their grid, capacitor pitch, socket outlines, a footprint swap with the same holes, a solder jumper's default, the solder mask or paste at a card edge, or tracks rerouted or pours refilled with DRC and the netlist check passing. A builder can treat it as tested.
- **Untested:** The circuit, the power path or the layout changed in a way that only a built board proves, or the board has never been built at all.

**Holes** is how far the corner mounting holes sit from the board's edges. The standard is 6 mm, and 5 mm on the ACE Board, the CF Adapter and the Keyboard Helper. A dash means a card or cart, which has no corner holes.

| Board | Rev | Status | Label | Order | Ordered | Made from | Tindie stock | Size (mm) | Holes | Top panel | Enclosure | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Backplane | 1.0 | Made, matches order | **Tested** | Y50 | 2024-07-03 | `3e494e3` | 3 | 100×100 | 6 mm | yes | — |  |
| Backplane | 1.1 | Drawn | **Proven design**: JLCPCB's marker removed and the logo moved; silkscreen only |  |  |  | — | 100×100 | 6 mm | yes | — |  |
| Backplane Helper | 1.0 | Made, matches order | **Tested** | Y77 | 2025-12-02 | `4115600` | 3 | 50×100 | 6 mm | yes | — |  |
| Backplane Helper | 1.1 | Drawn | **Proven design**: JLCPCB's marker removed and the logo moved; silkscreen only |  |  |  | — | 50×100 | 6 mm | yes | — |  |
| Backplane Pro | 1.0 | Made, matches order | **Tested** | Y30 | 2024-04-30 | `305dab8` | 4 | 100×100 | 6 mm | yes | — | symbol has pins the footprint lacks: J2 shield pin; the board's silk says 6502 BACKPLANE, its name when ordered |
| Backplane Pro | 1.1 | Drawn | **Untested**: the made Rev 1.1 with R5 removed |  |  |  | 4 | 100×100 | 6 mm | yes | — | replaces the boards made as Rev 1.1 (order Y93, 2026-06-21, made from `7486bd6`; their files are in `1b94d135`) |
| Blinkenlights Card | 1.0 | Made, matches order | **Tested** | Y40 | 2024-06-08 | `7d050b0` | 4 | 100×57.62 | — | — | — |  |
| Blinkenlights Card | 1.1 | Drawn | **Untested**: decoupling capacitors added, the RESB, IRQB and NMIB LEDs driven through inverters, every inverter a 74HC3G04, tracks rerouted, and the bare card edge |  |  |  | — | 100×57.62 | — | — | — |  |
| Breadboard Helper | 1.0 | Made, matches order | **Tested** | Y39 | 2024-06-08 | `7d050b0` | 3 | 75×55 | — | — | — |  |
| Breadboard Helper | 1.1 | Drawn | **Proven design**: J1 takes the box header's footprint, with the same holes, and the outline grows to hold it |  |  |  | — | 75×60 | — | — | — |  |
| CPU Card | 1.0 | Made, matches order | **Tested** | Y18 | 2024-04-03 | `da975a6` | 4 | 100×57.62 | — | — | — |  |
| CPU Card | 1.1 | Drawn | **Proven design**: 10k pull-ups, some tracks rerouted, silkscreen, the bare card edge |  |  |  | — | 100×57.62 | — | — | — |  |
| CPU Card Pro | 1.1 | Never made | **Untested**: never made |  |  |  | — | 100×57.62 | — | — | — | title block credits bahamutkotd, who contributed |
| Clock Card | 1.0 | Made, matches order | **Tested** | Y101 | 2026-11-02 | `ca9de28` | — | 100×57.62 | — | — | — |  |
| Clock Card | 1.1 | Drawn | **Proven design**: the bare card edge only |  |  |  | — | 100×57.62 | — | — | — |  |
| Clock Helper | 1.0 | Made, matches order | **Tested** | Y74 | 2025-11-21 | `65a5e49` | 4 | 50×50 | 5.32–5.68 mm | yes | yes |  |
| Clock Helper | 1.1 | Drawn | **Proven design**: mounting holes moved to the standard, silkscreen |  |  |  | — | 50×50 | 6 mm | yes | yes |  |
| DB25 Helper | 1.0 | Made, matches order | **Tested** | Y65 | 2025-10-06 | `013b131` | — | 100×50 | 5.32–6.25 mm | yes | yes |  |
| DB25 Helper | 1.1 | Drawn | **Proven design**: mounting holes moved to the standard, silkscreen |  |  |  | — | 100×50 | 6 mm | yes | yes |  |
| GPIO Breadboard Helper | 1.0 | Made, matches order | **Tested** | Y57 | 2025-10-06 | `0dd90c8` | 4 | 58.83×55 | — | — | — |  |
| GPIO Breadboard Helper | 1.1 | Drawn | **Proven design**: outline clean-up |  |  |  | — | 59×55 | — | — | — |  |
| GPIO Card | 1.0 | Made, matches order | **Tested** | Y45 | 2024-06-19 | `390cb17` | 3 | 100×57.62 | — | — | — |  |
| GPIO Card | 1.1 | Drawn | **Proven design**: the bare card edge only |  |  |  | — | 100×57.62 | — | — | — |  |
| GPIO Helper | 1.0 | Made, matches order | **Tested** | Y66 | 2025-10-06 | `013b131` | 4 | 100×50 | 5.32–6.25 mm | yes | yes |  |
| GPIO Helper | 1.1 | Drawn | **Proven design**: mounting holes moved to the standard, silkscreen |  |  |  | — | 100×50 | 6 mm | yes | yes |  |
| Joystick Helper | 1.0 | Made, matches order | **Tested** | Y73 | 2025-11-16 | `4f73288` | 4 | 50×50 | 5.32–5.68 mm | yes | yes |  |
| Joystick Helper | 1.1 | Drawn | **Proven design**: mounting holes moved to the standard, silkscreen |  |  |  | — | 50×50 | 6 mm | yes | yes |  |
| Keyboard Encoder Helper | 1.0 | Made, matches order | **Tested** | Y72 | 2025-11-14 | `4470a4f` | 4 | 100×50 | 5.32–6.25 mm | yes | yes | to fit the COB plate, drill plate holes 9 and 21 out to 5 mm: see the README |
| Keyboard Encoder Helper | 1.1 | Drawn | **Proven design**: mounting holes, silkscreen |  |  |  | — | 100×50 | 6 mm | yes | yes |  |
| Keyboard Helper | 1.0 | Made, matches order | **Tested** | Y70 | 2025-10-27 | `3b654ed` | 4 | 335×125 | 5 mm | — | yes |  |
| Keyboard Helper | 1.1 | Drawn | **Proven design**: JLCPCB's marker removed and the logo moved; silkscreen only |  |  |  | — | 335×125 | 5 mm | — | — |  |
| LCD Card | 1.0 | Made, matches order | **Tested** | Y27 | 2024-04-22 | `f77fc20` | 4 | 100×57.62 | — | — | — |  |
| LCD Card | 1.1 | Drawn | **Proven design**: the bare card edge only |  |  |  | — | 100×57.62 | — | — | — |  |
| Mega Helper | 1.0 | Made, matches order | **Tested** | Y81 | 2026-01-10 | `affcc47` | 3 | in footprint | — | — | — | symbol has pins the footprint lacks: Arduino header pins |
| Mega Helper | 1.1 | Drawn | **Proven design**: JLCPCB's marker removed, J1's reference resized and the logo moved; silkscreen only |  |  |  | — | in footprint | — | — | — | symbol has pins the footprint lacks: Arduino header pins |
| Memory Card | 1.0 | Made, matches order | **Tested** | Y20 | 2024-04-03 | `da975a6` | 4 | 100×57.62 | — | — | — |  |
| Memory Card | 1.1 | Drawn | **Proven design**: the bare card edge, and a 74HCT00 at U5 |  |  |  | — | 100×57.62 | — | — | — |  |
| PS2 Helper | 1.0 | Made, matches order | **Tested** | Y61 | 2025-10-06 | `0969243` | 4 | 100×50 | 5.32–6.25 mm | yes | yes |  |
| PS2 Helper | 1.1 | Drawn | **Proven design**: resistors moved and tracks rerouted, mounting holes, silkscreen |  |  |  | — | 100×50 | 6 mm | yes | yes |  |
| Prototype Card | 1.0 | Made, matches order | **Tested** | Y22 | 2024-04-03 | `da975a6` | 4 | 100×57.62 | — | — | — |  |
| Prototype Card | 1.1 | Drawn | **Proven design**: the bare card edge only |  |  |  | — | 100×57.62 | — | — | — |  |
| RAM Card | 1.0 | Made, matches order | **Tested** | Y69 | 2025-10-28 | `9b9e95d` | 4 | 100×57.62 | — | — | — |  |
| RAM Card | 1.1 | Drawn | **Untested**: the ACE 1.1's banked-RAM circuit: a bank latch for each window, a diode chip select, a 74HCT00 for `RB` and `WB`, and no `LATCH EN` or `BANK ADDR` header. |  |  |  | — | 100×57.62 | — | — | — |  |
| RTC Card | 1.0 | Made, matches order | **Tested** | Y62 | 2025-10-06 | `0969243` | 4 | 100×57.62 | — | — | — |  |
| RTC Card | 1.1 | Drawn | **Proven design**: the bare card edge, and JP2 and JP3 removed, wired as Rev 1.0 ships them |  |  |  | — | 100×57.62 | — | — | — |  |
| Serial Card | 1.0 | Made, matches order | **Tested** | Y67 | 2025-10-06 | `013b131` | 3 | 100×57.62 | — | — | — |  |
| Serial Card | 1.1 | Drawn | **Proven design**: silkscreen text and the bare card edge |  |  |  | — | 100×57.62 | — | — | — |  |
| Serial Card Pro | 1.0 | Made, matches order | **Tested** | Y36 | 2024-05-20 | `ffafeba` | 4 | 100×57.62 | — | — | — |  |
| Serial Card Pro | 1.1 | Drawn | **Proven design**: the DB-9 moved to KiCad's standard footprint (the same connector), tracks rerouted, silkscreen, the bare card edge |  |  |  | — | 100×57.62 | — | — | — |  |
| Sound Card | 1.0 | Made, matches order | **Tested** | Y84 | 2026-01-13 | `3b4c7bb` | 4 | 100×57.62 | — | — | — |  |
| Sound Card | 1.1 | Drawn | **Proven design**: silkscreen text, the bare card edge, and a second RCA jack on the same signal, as on the ACE |  |  |  | — | 100×57.62 | — | — | — |  |
| Storage Card | 1.0 | Made, matches order | **Tested** | Y47 | 2024-06-22 | `b8f89eb` | 4 | 100×57.62 | — | — | — | copper drawn differently by today's KiCad, as recorded in audit.py |
| Storage Card | 1.1 | Drawn | **Proven design**: the bare card edge only |  |  |  | — | 100×57.62 | — | — | — |  |
| Storage Card Pro | 1.1 | Drawn | **Untested**: redesigned in K33: an SD card the stock BIOS takes for CompactFlash, with a built-in drive. Being drawn; parts not yet placed or routed |  |  |  | — | 100×57.62 | — | — | — | 182 unconnected; DRC errors: starved_thermal 4 |
| VERA Helper | 1.0 | Made, matches order | **Tested** | Y71 | 2025-11-04 | `e74f44e` | 4 | 100×80 | 5.32–6.25 mm | — | — |  |
| VERA Helper | 1.1 | Drawn | **Proven design**: mounting holes, capacitor pitch, JP2 ships open, JP1 and JP3 removed and wired as Rev 1.0 ships them |  |  |  | — | 100×80 | 6 mm | — | — |  |
| VGA Card | 1.0 | Made, matches order | **Tested** | Y64 | 2025-10-06 | `0dd90c8` | 4 | 100×57.62 | — | — | — |  |
| VGA Card | 1.1 | Drawn | **Untested**: the pico9918 turned around, a new outline and jack mount, A1 wired to `MODE1`, the bare card edge, and JP2 and JP3 removed |  |  |  | — | 100×57.62 | — | — | — |  |
| Video Card | 1.0 | Made, matches order | **Tested** | Y53 | 2024-07-09 | `f890f21` | 2 | 100×57.62 | — | — | — |  |
| Video Card | 1.1 | Drawn | **Proven design**: JP7, a solder jumper, ships bridged (fine with a real TMS9918A's open-drain `/INT`), JP1–JP6 removed and wired as Rev 1.0 ships them, sockets, silkscreen, the bare card edge |  |  |  | — | 100×57.62 | — | — | — |  |

JLCPCB's orders were checked on 2026-11-04: each production zip marked *Made, matches order* was compared byte for byte with JLCPCB's copy, and its PCB regenerated to the same copper, mask, outline and holes. Each time this table is written, every PCB is checked again against its production zip, for copper and drill holes. Tindie stock is from the listings as saved on 2026-10-23.

<!-- History: hand-written. Tools/revision-audit/register.py keeps everything from here to the end. -->

## History

What changed in each revision of each board, newest first. The table above has the facts about each one.

**The Video Card Pro retired, 2026-11-16.** The Video Card Pro is gone from this repository too (owner, 2026-11-16). It was drawn, like the VGA Card Pro, as a possible VDP before the family settled on the pico9918, and was never made. Its video circuit follows the [Amethyst](https://github.com/74hc595/Amethyst), an ATmega1284 home computer whose own program makes the picture through two 74HC157s and two 74HC166s, but its bus interface was new: the ATmega1284 sat straight on the 6502 bus with no latch, and the Amethyst's video code leaves it no time to answer a bus cycle while it draws a line. No firmware was written. Don't build it. Its last files are in git at commit `6bbc0238`.

**The VGA Card Pro retired, 2026-11-16.** The VGA Card Pro is gone from this repository (owner, 2026-11-16). It was an experimental VGA card, a Raspberry Pi Pico with firmware the builder writes, designed as a possible VDP for the COB before the pico9918 became the family's. No firmware was ever written for it, and the stock BIOS never used it. Neither revision is a sound design. Rev 1.0 was made as the "VGA Card" (order Y24, 2024-04-03, its silkscreen says `6502 VGA CARD`), built and never tried: its TXS0108E level shifters are unsuited to the 6502 bus, as they were on the DEV Board. Rev 1.1, a redesign never made, gives the Pico no read strobe, so the card can't answer reads, and feeds the Pico through `VBUS`, which ties its USB port to the machine's 5 V. Don't build either. Its last files, both revisions complete and Rev 1.0 proven against JLCPCB's order, are in git at commit `b2d30214`. Today's [VGA Card](#vga-card) is the pico9918 card, a different board.

**The LCD Board moved to 6502-DEV, 2026-11-14.** The LCD Board is a DEV board, so it moved to [6502-DEV](https://github.com/acwright/6502-DEV) as the DEV LCD Board, with its made Rev 1.0, its history and a new Rev 1.1. Its files' history in this repository ends at the commit that removed them.

**The generated logos on the boards, 2026-11-14.** Every revision not yet made now prints its logo exactly as `Tools/logos/generate.py` draws it. KiCad keeps a copy of each footprint in the PCB, so when the library's logos were redrawn from Bebas Neue the boards still carried the older traced copies. `Tools/logos/embed.py` put the library's logo into each of the 33 revisions here (Backplane 1.1, Backplane Helper 1.1, Backplane Pro 1.1, Blinkenlights Card 1.1, Breadboard Helper 1.1, CPU Card 1.1, CPU Card Pro 1.1, Clock Card 1.1, Clock Helper 1.1, DB25 Helper 1.1, GPIO Breadboard Helper 1.1, GPIO Card 1.1, GPIO Helper 1.1, Joystick Helper 1.1, Keyboard Encoder Helper 1.1, Keyboard Helper 1.1, LCD Card 1.1, Mega Helper 1.1, Memory Card 1.1, PS2 Helper 1.1, Prototype Card 1.1, RAM Card 1.1, RTC Card 1.1, Serial Card 1.1, Serial Card Pro 1.1, Sound Card 1.1, Storage Card 1.1, Storage Card Pro 1.1, VERA Helper 1.1, VGA Card 1.1, VGA Card Pro 1.1, Video Card 1.1, Video Card Pro 1.1), keeping the centre of the print where it was, and its check in `derived-check.py` keeps them in step. The logos the owner ruled onto the design change visibly: on Backplane 1.1, CPU Card 1.1, Memory Card 1.1, Serial Card 1.1 and Prototype Card 1.1 the name sits up to 0.11 mm closer to "6502" (the Backplane's logo moved 0.07 mm to keep its end in place); on every other board the difference is under 0.02 mm. `Tools/revision-audit/gproof.py` shows only the front silkscreen changed on each. Made revisions keep the logo they were made with.

**Every board has a Rev 1.1, 2026-11-14.** The family's boards end as one set of Rev 1.1s under one set of rules (owner, 2026-11-13). The Backplane, Backplane Helper, Keyboard Helper and Mega Helper had only a made Rev 1.0, so each gets a Rev 1.1: Rev 1.0's circuit and copper, without JLCPCB's order-number marker, with its logo in its place and, on the Mega Helper, J1's reference at the family's size. Each is **Proven design**, its Rev 1.0 being tested. The CPU Card Pro, VGA Card Pro and Video Card Pro, drawn as Rev 1.0 and thought never made, are renumbered Rev 1.1 in place; the notes that name them as 1.0 were written before. The VGA Card Pro's first revision was in fact made, in 2024, as the VGA Card of order Y24, so the 2026-11-13 notes call its renumbered design "VGA Card Pro 1.1 (then numbered 1.0)". The VGA Card Pro is retired since 2026-11-16 (see above). The Backplane Pro's drawn Rev 1.2 takes the number 1.1 and replaces the design of the boards made as Rev 1.1, by the owner's ruling; those boards' files are in git at `1b94d135` (see [Backplane Pro](#backplane-pro)). `Tools/revision-audit/gproof.py` shows that only the silkscreen differs from Rev 1.0 on each new revision.

**Title blocks, 2026-11-14.** Every schematic's and PCB's title block names the family as it is: `AC6502 <Board>`, not `6502 <Board>`, on all 61 revisions, the made ones included. The title block is drawing-sheet text, which no Gerber layer carries: every PCB plots exactly as before (`Tools/revision-audit/gproof.py`), so no board and no label changed, and the made revisions' production zips are as JLCPCB received them. The schematic PDFs are regenerated. The production zip of each revision not yet made (29) is named from the title, so it is now `AC6502_<Board>_<Rev>.zip`, its contents unchanged. The board logos still read "6502". `Tools/revision-audit/audit.py` checks the titles.

**Reference text size, 2026-11-14.** Every reference printed on the silkscreen of a revision not yet made is 1.0 mm high and wide, with a 0.15 mm stroke, as 970 of the family's 991 already were. `Tools/revision-audit/audit.py` checks it. Resized: the Joystick Helper 1.1's J2 (from a 0.127 mm stroke), the Memory Card 1.1's TP1–TP5 (from 0.7 mm) and the RTC Card 1.1's BT1 (from 1.4 mm). The Video Card 1.1's and Video Card Pro 1.0's Y1 (from 0.8 mm) followed on the same day, with the owner's placement of their U3 and U6. Each grew or shrank about its own centre, clear of pads and other silk. Silk only: no copper moved, and no label changed. The made revisions keep their silk as made.

**IC designators and values, 2026-11-13.** On every revision not yet made, each IC's designator sits centred at one short end of its footprint, the text running along that end, and a through-hole IC's value sits at the other end. Where the centre is taken, the text is aligned to the end's left or right edge. A surface-mount IC's value is hidden, because a small package leaves no room for it, and a module whose outline names it keeps its silk as it is. A ZIF socket's texts sit on its silk outline, not its lever. `Tools/revision-audit/audit.py` checks the values. Moved: CPU Card 1.1, CPU Card Pro 1.0, GPIO Card 1.1, LCD Card 1.1 (U1's texts at its ends, under the LCD module), Memory Card 1.1, PS2 Helper 1.1, Prototype Card 1.1, RTC Card 1.1, Serial Card 1.1, Serial Card Pro 1.1, Sound Card 1.1, Storage Card 1.1, VGA Card Pro 1.1 (then numbered 1.0), Video Card 1.1 and Video Card Pro 1.0. Values shown: the Memory Card 1.1's U3 and U4. Values hidden: the Blinkenlights Card 1.1's six. Placed by the owner, on 2026-11-14: the Video Card 1.1's U3 and the Video Card Pro 1.0's U6, which have a capacitor at one end and the bus header at the other, and the RAM Card 1.1's, with its routing, its surface-mount values hidden. Silk only: no copper moved, and no label changed. The made revisions keep their silk as made.

**The board logo's place, 2026-11-13.** Every board logo on a revision not yet made sits in one place for its kind of board. A card's or cart's logo reads bottom to top on the left, 2.5 mm from the edge and centred on the body; any other board's runs along its edge on the line of that edge's corner holes, centred or with its end 11.5 mm from the corner (`Tools/logos/standard.json`, checked by `Tools/logos/placement.py`). Moved, each by at most 2.5 mm: Backplane Pro 1.2, Blinkenlights Card 1.1, CPU Card Pro 1.0, CPU Card 1.1, Clock Card 1.1, Clock Helper 1.1, DB25 Helper 1.1, GPIO Card 1.1, Joystick Helper 1.1, Keyboard Encoder Helper 1.1, PS2 Helper 1.1, RTC Card 1.1, Serial Card Pro 1.1, Serial Card 1.1, Sound Card 1.1, Storage Card Pro 1.1, Storage Card 1.1, VERA Helper 1.1, VGA Card Pro 1.1 (then numbered 1.0), VGA Card 1.1, Video Card Pro 1.0 and Video Card 1.1. The RAM Card 1.1's moved with its redesign (see its History). The GPIO Helper 1.1, LCD Card 1.1, Memory Card 1.1 and Prototype Card 1.1 keep theirs where they are: parts fill the place the rule gives, and the owner ruled each an exception (`Tools/data/logos.json`). The two breadboard helpers have a rule of their own, added the same day: the logo lies flat under the pin rows, centred on them, as on the GPIO Breadboard Helper 1.1. The Breadboard Helper 1.1's logo moved there from the strip beside J1, and the GPIO Breadboard Helper 1.1's moved 0.07 mm to centre it (see their History). Silk only: no copper moved, DRC is unchanged, and no label changed. The made revisions keep their logos where they are.

**JLCPCB's order-number marker, 2026-11-13.** The `JLCJLCJLCJLC` text is gone from the silkscreen of every revision not yet made: Backplane Pro 1.2, Blinkenlights Card 1.1, Breadboard Helper 1.1, CPU Card Pro 1.0, CPU Card 1.1, Clock Card 1.1, Clock Helper 1.1, DB25 Helper 1.1, GPIO Breadboard Helper 1.1, GPIO Card 1.1, GPIO Helper 1.1, Joystick Helper 1.1, Keyboard Encoder Helper 1.1, LCD Card 1.1, Memory Card 1.1, PS2 Helper 1.1, Prototype Card 1.1, RAM Card 1.1, RTC Card 1.1, Serial Card Pro 1.1, Serial Card 1.1, Sound Card 1.1, Storage Card Pro 1.1, Storage Card 1.1, VERA Helper 1.1, VGA Card Pro 1.1 (then numbered 1.0), VGA Card 1.1, Video Card Pro 1.0 and Video Card 1.1. It told JLCPCB where to print its order number. JLCPCB stopped printing order numbers in May 2026, and its help page now asks for the text not to be there. Only the front silkscreen changed, so no label did. The made revisions keep the text, which JLCPCB ignores.

**Schematic drawing, 2026-11-06.** Every schematic's 6502 bus, cart and card connectors are drawn one way, made revisions included: a short wire and a global label on each used pin, a no-connect flag on each unused one, and GND and VCC as global labels. Bus lines, bus entries and local labels for the bus are gone. Each label's name matches the board's silk. Where pins 4 and 6 carry `EXP1` and `EXP0`, or a cartridge grounds them, a note on the schematic says what `HRDB` does with them (see the README's *Extra pins*). No netlist changed, so no board did: the schematic PDFs are regenerated, and a few PCB files carry the new net names, as text only.

### Backplane

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Drawn so the family's boards end as one set of Rev 1.1s under one set of rules (owner, 2026-11-13). The circuit, parts, copper, holes and outline are Rev 1.0's.
- JLCPCB's order-number marker, `JLCJLCJLCJLC`, is gone from the silkscreen, as from every revision not yet made: JLCPCB stopped printing order numbers in May 2026 and asks for the text not to be there.
- The board logo moves 0.39 mm across and 0.12 mm down, to its place on the top corner holes' line, as every logo on a revision not yet made sits.
- The silkscreen's revision reads Rev 1.1.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Backplane/Rev 1.0/` and `Production/Backplane/Rev 1.0/` match the boards JLCPCB made (order Y50). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Backplane Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Drawn so the family's boards end as one set of Rev 1.1s under one set of rules (owner, 2026-11-13). The circuit, parts, copper, holes and outline are Rev 1.0's.
- JLCPCB's order-number marker, `JLCJLCJLCJLC`, is gone from the silkscreen, as from every revision not yet made: JLCPCB stopped printing order numbers in May 2026 and asks for the text not to be there.
- The board logo moves −0.64 mm across and 0.04 mm down, to its place on the top corner holes' line, as every logo on a revision not yet made sits.
- The silkscreen's revision reads Rev 1.1.

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/Backplane Helper/Rev 1.0/` and `Production/Backplane Helper/Rev 1.0/` match the boards JLCPCB made (order Y77). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Backplane Pro

#### Rev 1.1

Drawn, not yet made. It replaces the design of the boards made as Rev 1.1 (owner, 2026-11-13). It was drawn as Rev 1.2 and took the number on 2026-11-14, so the family's boards end as one set of Rev 1.1s; a Rev 1.2 opens only when there are meaningful changes. One change from the boards made as Rev 1.1:

- **R5 is removed.** It was a 1kΩ pull-up on `RESB`, in parallel with the CPU Card's. The CPU Card's pull-up is the only one a COB needs, and the reset circuit only pulls `RESB` low, through Q1. Without a CPU Card on the bus, `RESB` has no pull-up, so whatever drives the bus instead (a [Mega Helper](#mega-helper), for example) must hold `RESB` high itself.

The barrel jack (J1) goes straight to the power switch (SW1), as on the boards made as Rev 1.1, so `VCC` gets the supply's full 5 V. This revision was drawn with a 1N5819 (D2) between them, against a reversed supply, but it dropped `VCC` to about 4.6 V, and it came out on 2026-11-16 (owner). Use a centre-positive 5 V supply.

The backplane carries no decoupling capacitors, as on the other backplanes: every card that plugs in has 100nF on each of its own chips.

**The boards made as Rev 1.1** (order Y93, 2026-06-21) were built and tested, and are the boards on sale. Their files left `Hardware/Backplane Pro/Rev 1.1/` when the new design took the number: they are in git at commit `1b94d135`, with the production zip that is byte for byte what JLCPCB received (made from `7486bd6`). To build one, follow *Building a board made as Rev 1.1* in [BOM.md](BOM.md#build-notes).

#### Rev 1.0

- Initial release, and the board on sale. Built and tested. `Hardware/Backplane Pro/Rev 1.0/` and `Production/Backplane Pro/Rev 1.0/` match the boards JLCPCB made (order Y30). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- This board was called the Backplane when it was ordered, so its silkscreen says `6502 BACKPLANE`. Today's [Backplane](#backplane) is a different board, order Y50.
- The PCB file was restored to that layout on 2026-11-04. A later edit only moved C8, C14, D1 and TP1 slightly, and Rev 1.1 is a full redesign, so that edit has no revision of its own. The schematic and BOM are today's, and they match this copper.

### Blinkenlights Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Adds `C1`–`C4`, 100nF decoupling capacitors, one beside each chip, with tracks rerouted to reach them. Every other chip in the family has one: it supplies the current the chip draws as its outputs switch, so the switching doesn't disturb the supply the other chips share. Rev 1.0 has no pads for them.
- The silkscreen spells out `RESB`. Rev 1.0's says `RSB`.
- The `RESB`, `IRQB` and `NMIB` LEDs (D25–D27) are driven from inverters, as the `RDY` and `BE` LEDs already are, and light while their line is low. On Rev 1.0 they hang straight on those lines through R25–R27, so whatever pulls a line low also sinks about 9 mA of LED current, nearly three times the 3.2 mA that a W65C22's or W65C21's IRQ output is rated for. Each line now carries only a CMOS input.
- Every inverter is a 74HC3G04 (U3, U5 and U6), three inverters in an 8-pin TSSOP. Rev 1.0 has one 74HC04 (U3), and all six of its gates are in use, two each for the `RDY` and `BE` LEDs and for the delayed `PHI2` that latches U4. The nine gates are those six, as before, and one each for the three new LED drivers. The smaller packages fit where a second 74HC04 couldn't. C5 and C6 decouple U5 and U6.
- The schematic is drawn on a US Legal sheet, wider than Rev 1.0's US Letter, to fit the new gates.
- Routed by the owner: U3, U5 and U6 sit side by side where Rev 1.0's U3 was, each with its decoupling capacitor just below it, and the tracks round them are rerouted. The card edge's opening is unchanged. DRC, the netlist check and connectivity are clean.
- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. Rev 1.0 has mask between the fingers. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved up to 0.05 mm from Rev 1.0's, and no track, pad or hole moved. The ground pours are refilled to suit.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Blinkenlights Card/Rev 1.0/` and `Production/Blinkenlights Card/Rev 1.0/` match the boards JLCPCB made (order Y40). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Breadboard Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- J1 uses the `6502 Bus Connector` footprint, the box header that is fitted, in place of Rev 1.0's plain 2×20 pin header. The pads are in the same places, so the copper, mask and holes are Rev 1.0's.
- The T's stem is 60 mm long, 5 mm longer than Rev 1.0's, and centred on J1, so the box header sits inside the board with 0.95 mm to spare at each end. On a Rev 1.0 built with one, the header runs 1.3 mm past the top of the board and 1.8 mm past the bottom, and its silkscreen outline is cut off at the edge. The corners keep their 5 mm radii, and the ground pours reach the new ends. No hole, pad or track moved.
- The board logo lies flat under the pin rows, centred on them, as on the GPIO Breadboard Helper 1.1. On Rev 1.0 it reads up the narrow strip beside J1, where it is hard to see.

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/Breadboard Helper/Rev 1.0/` and `Production/Breadboard Helper/Rev 1.0/` match the boards JLCPCB made (order Y39). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- The PCB file was restored to that layout on 2026-11-04. Later edits only changed pad shapes, when footprints were refreshed, so they don't make a Rev 1.1. The schematic and BOM are today's, and they match this copper.
- This is a different board from the [GPIO Breadboard Helper](#gpio-breadboard-helper): this one breaks out the full 6502 bus, and that one breaks out a VIA's PORT A and PORT B.

### Clock Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the family's standard position, 6 mm from each edge (see *Holes* above), so its plate holes, enclosure and top panel follow the same rule as the other boards'. The spacing goes from 39 × 39 mm to 38 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/Clock Helper/` and `CAD/Tops/Clock Helper/`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Clock Helper/Rev 1.0/` and `Production/Clock Helper/Rev 1.0/` match the boards JLCPCB made (order Y74). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Clock Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is built first)

- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. Rev 1.0 has mask between the fingers. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved 0.11 mm from Rev 1.0's, and no track, pad or hole moved. The ground pours are refilled to suit.
- D2, Rev 1.0's 1N5819 between the barrel jack (J2) and `VCC`, is gone (owner, 2026-11-16): the jack goes straight to `VCC`, by one new track, so the card gives the supply's full 5 V. The diode guarded against a reversed supply but dropped `VCC` to about 4.6 V. Use a centre-positive 5 V supply.
- The silkscreen's revision reads Rev 1.1. Nothing else changed: the rest of the circuit, parts, tracks and pads are Rev 1.0's.
- Rev 1.1 was labelled **Untested** until Rev 1.0 was tested. It became **Proven design** when Rev 1.0 passed, on 2026-11-15.

**Rev 1.0**

- Initial release, ordered on 2026-11-02 with the KIM Board Rev 1.0. `Hardware/Clock Card/Rev 1.0/` and `Production/Clock Card/Rev 1.0/` match the boards JLCPCB made (order Y101). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- Built and tested on 2026-11-15, in a KIM built on the VCS Main Board: the 1 MHz oscillator can moved from the Main Board to the Clock Card, the card went into the Main Board's slot, and the KIM was powered through the card's barrel jack. The KIM ran on the card's clock and power, and the card's reset button reset it. The card is **Tested**.
- The card takes a 1 MHz DIP-14 can, the AC6502's standard `PHI2`. It has no power switch, and no `RESB` pull-up: the CPU Card's is the only one a COB needs. JP1 is open as made, so the clock reaches `PHI2` only through J3: fit a switch or a jumper there, or bridge JP1 if the clock never needs to stop.
- D2 is marked do-not-fit in Rev 1.0's files, with a note on the schematic to fit a wire link in its place (owner, 2026-11-16). The board as made has its pads; the 1N5819 there dropped `VCC` to about 4.6 V.

### CPU Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Pull-up resistors R1–R6 changed from 1kΩ to 10kΩ. With a 1kΩ pull-up, a device that pulls `IRQB` low sinks 5 mA, more than the 3.2 mA that the W65C22's and W65C21's IRQ outputs are rated for; every CPU board in the family uses 10kΩ.
- Some tracks are rerouted, as a tidy-up: no part moved, and the circuit is Rev 1.0's.
- The silkscreen labels U1 `65C02`, the part fitted, and J3 `EXP`, the bus pins it joins, and adds a `6502` label. It drops Rev 1.0's "Jumper J2 for original 6502" note: J2 stays, and the README's *Jumpers* table says what it is for.
- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. Rev 1.0 has mask between the fingers. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved up to 0.1 mm from Rev 1.0's, and no track, pad or hole moved. The ground pours are refilled to suit.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/CPU Card/Rev 1.0/` and `Production/CPU Card/Rev 1.0/` match the boards JLCPCB made (order Y18). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### CPU Card Pro

**Rev 1.1**

- Drawn, and never ordered. It was drawn as Rev 1.0, and renumbered 1.1 on 2026-11-14, so the family's boards end as one set of Rev 1.1s (owner, 2026-11-13). Nothing but the number changed: its files moved from `Rev 1.0` to `Rev 1.1`, and its title blocks and silkscreen say Rev 1.1.
- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved up to 0.1 mm from its outline as first drawn, and no track, pad or hole moved. The ground pours are refilled to suit.

### DB25 Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the family's standard position, 6 mm from each edge (see *Holes* above), so its plate holes, enclosure and top panel follow the same rule as the other boards'. The spacing goes from 88 × 39 mm to 88 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/DB25 Helper/` and `CAD/Tops/DB25 Helper/`.
- The project's name is `DB25 Helper`. The order's Gerbers carry its old name, `GPIO DB25 Helper`.
- The holes were trued on 2026-11-12, before any Rev 1.1 was made. As first drawn, they sat 0.071 mm too near the top edge and 0.004 mm too near the right edge, and each moved by that much to sit exactly 6 mm from its two edges. No track or pad moved, and the ground pours are refilled around the holes' new places.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/DB25 Helper/Rev 1.0/` and `Production/DB25 Helper/Rev 1.0/` match the boards JLCPCB made (order Y65). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### GPIO Breadboard Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- The outline is redrawn true: 59 × 55 mm, with a 5 mm radius at every corner, so the board's size and corners are round numbers like the other helpers'. Rev 1.0's outline is 58.83 mm wide, its two right-hand corners have radii of 5.006 mm and 4.996 mm, and a 0.007 mm sliver of edge joins the lower one to the bottom edge. The right edge moves 0.17 mm outward. No track, pad or hole moved, and the ground pour is refilled to the new edge.
- The board logo moved 0.07 mm right, so it is centred on the pin rows. That is the rule for both breadboard helpers (`Tools/logos/standard.json`), and the Breadboard Helper 1.1 follows it too.
- The silkscreen's revision reads Rev 1.1. Nothing else changed: the circuit, parts, tracks and pads are Rev 1.0's.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/GPIO Breadboard Helper/Rev 1.0/` and `Production/GPIO Breadboard Helper/Rev 1.0/` match the boards JLCPCB made (order Y57). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### GPIO Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. Rev 1.0 has mask between the fingers. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved 0.05 mm from Rev 1.0's, and no track, pad or hole moved. The ground pours are refilled to suit.
- The silkscreen's revision reads Rev 1.1. Nothing else changed: the circuit, parts, tracks and pads are Rev 1.0's.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/GPIO Card/Rev 1.0/` and `Production/GPIO Card/Rev 1.0/` match the boards JLCPCB made (order Y45). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### GPIO Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the family's standard position, 6 mm from each edge (see *Holes* above), so its plate holes, enclosure and top panel follow the same rule as the other boards'. The spacing goes from 88 × 39 mm to 88 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/GPIO Helper/` and `CAD/Tops/GPIO Helper/`.
- The holes were trued on 2026-11-12, before any Rev 1.1 was made. As first drawn, the four corner holes sat 0.071 mm too near the top edge and 0.021 mm too near the left edge, and each moved by that much to sit exactly 6 mm from its two edges. The fifth hole, `H5`, moved 0.07 mm to sit exactly 19 mm from the left edge and 31.5 mm from the top edge; Rev 1.0 has it at 19.004 mm and 31.43 mm, which makes no difference to a screw in a plate hole. No track or pad moved, and the ground pours are refilled around the holes' new places.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/GPIO Helper/Rev 1.0/` and `Production/GPIO Helper/Rev 1.0/` match the boards JLCPCB made (order Y66). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Joystick Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the family's standard position, 6 mm from each edge (see *Holes* above), so its plate holes, enclosure and top panel follow the same rule as the other boards'. The spacing goes from 39 × 39 mm to 38 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/Joystick Helper/` and `CAD/Tops/Joystick Helper/`. The holes' courtyards now overlap the courtyard of J2, the DB9 connector. That has been reviewed and is fine, so the project excludes it from DRC.
- The silkscreen says `JOYSTICK` at `J2`, what the connector is for, where Rev 1.0's says `DB9 MALE`, what it is (owner, 2026-11-06).
- The holes were trued on 2026-11-12, before any Rev 1.1 was made. As first drawn, they sat 0.071 mm too near the top edge and 0.084 mm too near the left edge, and each moved by that much to sit exactly 6 mm from its two edges. The DRC exclusions for the holes' courtyards over `J2` are recorded again at the holes' new places. No track or pad moved, and the ground pours are refilled around the holes' new places.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Joystick Helper/Rev 1.0/` and `Production/Joystick Helper/Rev 1.0/` match the boards JLCPCB made (order Y73). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Keyboard Encoder Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the family's standard position, 6 mm from each edge (see *Holes* above), so its plate holes, enclosure and top panel follow the same rule as the other boards'. The spacing goes from 88 × 39 mm to 88 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/Keyboard Encoder Helper/` and `CAD/Tops/Keyboard Encoder Helper/`.
- The silkscreen says `ATmega1284` at `U1`, the part the parts list orders (ATMEGA1284-PU). Rev 1.0's says `ATmega1284-P`.
- `C2` and `C3`, the 16 MHz crystal's capacitors, stay 22 pF as on Rev 1.0, the value every made board was built and tested with (2026-11-11). Rev 1.1 was drawn with 20 pF from 2026-11-04 to 2026-11-11, and never made that way.
- The holes were trued on 2026-11-12, before any Rev 1.1 was made. As first drawn, they sat 0.071 mm too near the top edge and 0.004 mm too near the right edge, and each moved by that much to sit exactly 6 mm from its two edges. No track or pad moved, and the ground pours are refilled around the holes' new places.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Keyboard Encoder Helper/Rev 1.0/` and `Production/Keyboard Encoder Helper/Rev 1.0/` match the boards JLCPCB made (order Y72). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- To mount it on the COB's base plate, two plate holes have to be drilled wider: see [CAD](README.md#cad).

### Keyboard Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Drawn so the family's boards end as one set of Rev 1.1s under one set of rules (owner, 2026-11-13). The circuit, parts, copper, holes and outline are Rev 1.0's.
- JLCPCB's order-number marker, `JLCJLCJLCJLC`, is gone from the silkscreen, as from every revision not yet made: JLCPCB stopped printing order numbers in May 2026 and asks for the text not to be there.
- The board logo moves 0.00 mm across and 3.51 mm down, to its place on the left corner holes' line, 11.5 mm from the corner, as every logo on a revision not yet made sits.
- The silkscreen's revision reads Rev 1.1.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Keyboard Helper/Rev 1.0/` and `Production/Keyboard Helper/Rev 1.0/` match the boards JLCPCB made (order Y70). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### LCD Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- The silkscreen's revision reads Rev 1.1. The circuit is Rev 1.0's, with `JP1` bridged as made: the W65C22N's interrupt output is open-drain, so the card works as shipped.
- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. Rev 1.0 has mask between the fingers. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved up to 0.05 mm from Rev 1.0's, and no track, pad or hole moved. The ground pours are refilled to suit.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/LCD Card/Rev 1.0/` and `Production/LCD Card/Rev 1.0/` match the boards JLCPCB made (order Y27). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Mega Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Drawn so the family's boards end as one set of Rev 1.1s under one set of rules (owner, 2026-11-13). The circuit, parts, copper, holes and outline are Rev 1.0's.
- JLCPCB's order-number marker, `JLCJLCJLCJLC`, is gone from the silkscreen, as from every revision not yet made: JLCPCB stopped printing order numbers in May 2026 and asks for the text not to be there.
- J1's reference is 1.0 mm high, with a 0.15 mm stroke, as every reference on a revision not yet made is. Rev 1.0's is 0.8 mm.
- The board logo moves 1.00 mm across and 1.13 mm down, to its place 2.5 mm from the left edge and centred on the board's height, the rule for a board with no corner holes by its logo, as every logo on a revision not yet made sits.
- The silkscreen's revision reads Rev 1.1.

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/Mega Helper/Rev 1.0/` and `Production/Mega Helper/Rev 1.0/` match the boards JLCPCB made (order Y81). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Memory Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. Rev 1.0 has mask between the fingers. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved 0.04 mm from Rev 1.0's, and no track, pad or hole moved. The ground pours are refilled to suit.
- The silkscreen's revision reads Rev 1.1.
- U5, the 74HC00 that makes the RAM's and ROM's `RB` and `WB` from `PHI2` and `RWB`, is a 74HCT00 (SN74HCT00DR, LCSC C6764, 2026-11-11). Its TTL input threshold ends `RB` and `WB` a few nanoseconds later after `PHI2` falls. An Alliance AS6C62256 with a fast-releasing 74HC00 lot in this gate misread at 2 MHz; a 74HCT00 there cured it in the ACE, writes included. Rev 1.0 keeps its 74HC00. Same footprint, so no track moved.
- Nothing else changed: the circuit, tracks and pads are Rev 1.0's.

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/Memory Card/Rev 1.0/` and `Production/Memory Card/Rev 1.0/` match the boards JLCPCB made (order Y20). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- The PCB file was restored to that layout on 2026-11-04. Later edits only changed pad shapes, when footprints were refreshed, so they don't make a Rev 1.1. The schematic and BOM are today's, and they match this copper.

### Prototype Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. Rev 1.0 has mask between the fingers. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved 0.06 mm from Rev 1.0's, and no track, pad or hole moved. The ground pours are refilled to suit.
- The silkscreen's revision reads Rev 1.1. Nothing else changed: the circuit, parts, tracks and pads are Rev 1.0's.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Prototype Card/Rev 1.0/` and `Production/Prototype Card/Rev 1.0/` match the boards JLCPCB made (order Y22). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### PS2 Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Stands the resistors `R2`–`R9` upright and moves them, with the tracks around them rerouted, for a tidier layout. The parts, their values and the circuit are Rev 1.0's.
- Moves the four mounting holes (`H1`–`H4`) to the family's standard position, 6 mm from each edge (see *Holes* above), so its plate holes, enclosure and top panel follow the same rule as the other boards'. The spacing goes from 88 × 39 mm to 88 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/PS2 Helper/` and `CAD/Tops/PS2 Helper/`.
- Drops the `R2-R9` silkscreen label, which the new layout has no place for; each resistor keeps its own reference.
- `C4` and `C5`, the 16 MHz crystal's capacitors, stay 22 pF as on Rev 1.0, the value every made board was built and tested with (2026-11-11). Rev 1.1 was drawn with 20 pF from 2026-11-04 to 2026-11-11, and never made that way.
- The holes were trued on 2026-11-12, before any Rev 1.1 was made. As first drawn, they sat 0.071 mm too near the top edge and 0.004 mm too near the right edge, and each moved by that much to sit exactly 6 mm from its two edges. No track or pad moved, and the ground pours are refilled around the holes' new places.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/PS2 Helper/Rev 1.0/` and `Production/PS2 Helper/Rev 1.0/` match the boards JLCPCB made (order Y61). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### RAM Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. Rev 1.0 has mask between the fingers. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved 0.04 mm from Rev 1.0's, and no track, pad or hole moved. The ground pours are refilled to suit.
- The ACE Board 1.1's banked-RAM circuit replaces Rev 1.0's. Rev 1.0 has one bank latch for both windows, so both always show the same bank. Rev 1.1 has two 74HC573s, U2 for window 0 and U9 for window 1, each with its outputs on only while its own window is selected, so each window has its own bank. Each latch loads only on a write to `$x3FF` of its own window while `PHI2` is high, decoded by U3 (74HC00) and U8 (74HC02) as on the ACE's U12 and U13. The RAM's chip select is D1 and D2 (BAT54) with R3 (10k), as the ACE's D2, D3 and R27, and its A18 is window 1's select, inverted. U6, the `RB`/`WB` gate, is a 74HCT00, as on every board where that gate drives a RAM.
- Removed: U4 (74HC21); R1 and R2, the pull-downs that made a window without its shunt answer at every address; JP1 and J2 (`LATCH EN`); and J4 (`BANK ADDR`). The window selects have no pull-ups, as on every other card: fit one shunt per window.
- The schematic sheet is US Legal, to fit the second latch. `Tests/check-schematics.mjs` checks all 16 settings of one shunt per window.
- The board is placed afresh and routed (2026-11-14): every part except J1 is new in its place, and only the card edge, the A.C. Wright and open hardware logos and the copyright line are Rev 1.0's. The board logo moved 0.5 mm right and 0.8 mm down, to the family's place for it: 2.5 mm from the left edge and centred on the body.

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/RAM Card/Rev 1.0/` and `Production/RAM Card/Rev 1.0/` match the boards JLCPCB made (order Y69). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### RTC Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. Rev 1.0 has mask between the fingers. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved 0.06 mm from Rev 1.0's, its corners are 5 mm (Rev 1.0's are 5.011 mm), and no track, pad or hole moved. The ground pours are refilled to suit.
- The silkscreen's revision reads Rev 1.1.
- `JP2` and `JP3` are removed. They chose whether `PHI2` or the supply drives E2, an enable of U3, the 74HC138 that makes the card's read and write strobes. With `PHI2` there, as Rev 1.0 ships, the strobes last only while `PHI2` is high, when the 6502's address and data are valid; tied high, they would run through the whole cycle and glitch while the address settles. So Rev 1.1 wires `PHI2` straight to E2. JP3's copper strip is a short track now, and JP2 goes with its feed from the supply.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/RTC Card/Rev 1.0/` and `Production/RTC Card/Rev 1.0/` match the boards JLCPCB made (order Y62). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Serial Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- The silkscreen says `SERIAL (DCE)` at J2, the family's name for a serial port with its role, and `R6551AP` at U3, the ACIA the parts list orders and every serial port is tested with. Rev 1.0's says `DB9 FEMALE (DCE)` and `6551`. Nothing else changed: the tracks, pads and holes are Rev 1.0's.
- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. Rev 1.0 has mask between the fingers. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved up to 0.05 mm from Rev 1.0's, and no track, pad or hole moved. The ground pours are refilled to suit.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Serial Card/Rev 1.0/` and `Production/Serial Card/Rev 1.0/` match the boards JLCPCB made (order Y67). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Serial Card Pro

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- `J2` uses KiCad's standard DB-9 footprint in place of Rev 1.0's own, so the board uses the library's standard part rather than a home-made one. The footprint's origin and rotation differ, but its pads sit where Rev 1.0's do, to within 0.02 mm, so the same connector fits both revisions. Its mounting lugs join `GND`, where Rev 1.0's join nothing.
- The silkscreen says `SERIAL (DTE)`, the family's name for a serial port with its role, and `R6551AP`, the ACIA the parts list orders and every serial port is tested with. Rev 1.0's says `DB9 Male (DTE)` and `6551`.
- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. Rev 1.0 has mask between the fingers. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved up to 0.05 mm from Rev 1.0's, and no track, pad or hole moved. The ground pours are refilled to suit.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Serial Card Pro/Rev 1.0/` and `Production/Serial Card Pro/Rev 1.0/` match the boards JLCPCB made (order Y36). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Sound Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- A second RCA jack, J4 (`AUDIO R`, a red Switchcraft PJRAN1X1U03X), beside J3, now `AUDIO L` (white, PJRAN1X1U02X), as on the ACE and the VCS Output Board 1.1, so a stereo amplifier's two inputs each get the SID's sound (owner, 2026-11-15). Both carry the same signal, from C4, wired together on the schematic. Like J3, J4 has the signal on its tip and ground on its sleeve, which is right: Switchcraft's drawing for the PJRAN1X1U jacks puts the sleeve, ground, on the centred slot nearest the board edge (pad 1 of the `RCA Jack White` footprint) and the tip, the signal, on the two holes behind it (pads 2, the tip and its shunt). Placed and routed by the owner (2026-11-15).
- The silkscreen says `ARMSID` at U1 and `SID VDD` at J2. Rev 1.0's says `6581` and `VDD`. Every tested build uses an ARMSID, and J2 is only for a real SID's supply, so the labels now say so. J2 stays: the COB is the experimenter's machine. Nothing else changed: the tracks, pads and holes are Rev 1.0's.
- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. Rev 1.0 has mask between the fingers. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved up to 0.05 mm from Rev 1.0's, and no track, pad or hole moved. The ground pours are refilled to suit.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Sound Card/Rev 1.0/` and `Production/Sound Card/Rev 1.0/` match the boards JLCPCB made (order Y84). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Storage Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. Rev 1.0 has mask between the fingers. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved 0.05 mm from Rev 1.0's, and no track, pad or hole moved. The ground pours are refilled to suit.
- The silkscreen's revision reads Rev 1.1. Nothing else changed: the circuit, parts, tracks and pads are Rev 1.0's.

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/Storage Card/Rev 1.0/` and `Production/Storage Card/Rev 1.0/` match the boards JLCPCB made (order Y47). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- The PCB file was restored to that layout on 2026-11-04. Later edits only changed pad shapes, when footprints were refreshed, so they don't make a Rev 1.1. The schematic and BOM are today's, and they match this copper.

### Storage Card Pro

**Rev 1.1** (drawn, not yet made)

- Redesigned (K33, 2026-11-15): the stock BIOS sees an SD card in this card as the Storage Card's CompactFlash card at `$8C00`, with no BIOS change. An RP2350A answers the eight CompactFlash registers through a 74LVC4245A (data, at 5 V on the bus) and a 74LVC541 (controls), with a full-size SD socket and a 16 MB built-in drive (W25Q128JVFIQ) that answers when no card is in. The circuit is the ACE SD Adapter 1.1's, part for part. The card adds the Storage Card's front end: the 74HC138 and the window jumper over A10–A15, a 74HCT00 making `RB` and `WB` from `PHI2` and `RWB`, and the off-board ACT header. Rev 1.0's ATmega328P, TXS0108E, external SPI header and 16 MHz crystal are gone. Drawn; the parts are not yet placed or routed.
- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. Rev 1.0 has mask between the fingers. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved up to 0.05 mm from Rev 1.0's, and no track, pad or hole moved. The ground pours are refilled to suit.

**Rev 1.0** (retired)

- Made by JLCPCB (order Y78, 2025-12-11) and never shown to work, then retired on 2026-11-16 (owner): it is not offered, and Rev 1.1 replaces its design. An ATmega328P sat straight on the 6502 bus and answered two SPI registers in IO 4, with a TXS0108E between it and the SD card, a 16 MB SPI flash and an external SPI header. The stock BIOS has no driver for it, and its firmware, the STP Controller, could not serve the bus: it ran from an Arduino interrupt on `PHI2`, on a pin that has no such interrupt, and even attached it would answer microseconds after a cycle that lasts one. Its files and the STP Controller are in git at commit `a300b196`, the last that holds them.

### VERA Helper

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the family's standard position, 6 mm from each edge (see *Holes* above), so its holes follow the same rule as the other boards'. Rev 1.0's were off the standard, at 5.32 to 6.25 mm from the edges. The spacing goes from 88 × 69 mm to 88 × 68 mm.
- `C1` and `C2` use the 2.5 mm capacitor footprint in place of Rev 1.0's 5 mm one, matching the family's other through-hole boards. Pad 1 of each stays where it was.
- `JP1` and `JP3` are removed. They chose whether `PHI2` or the supply drives E2, an enable of U2, the 74HC138 that makes the card's read and write strobes. With `PHI2` there, as Rev 1.0 ships, the strobes last only while `PHI2` is high, when the 6502's address and data are valid; tied high, they would run through the whole cycle and glitch while the address settles. So Rev 1.1 wires `PHI2` straight to E2. JP3's copper strip is a short track now, and JP1 goes with its feed from the supply.
- `JP2` is open as made, so D1 stays in the VERA module's interrupt line. The VERA drives its interrupt high as well as low, so with JP2 bridged, as on Rev 1.0, and a shunt on J5, it holds `IRQB` (or `NMIB`) high against every other interrupt source. D1 lets it only pull the line low.

**Rev 1.0**

- Initial release, and the board on sale. Its mounting holes are off the standard: 5.75 and 6.25 mm from the long sides' ends, and 5.32 and 5.68 mm from the top and bottom.
- Built and tested. `Hardware/VERA Helper/Rev 1.0/` and `Production/VERA Helper/Rev 1.0/` match the boards JLCPCB made (order Y71). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### VGA Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- `A1` reaches U1 pin 11, the pico9918's `MODE1`, as on the ACE. With `MODE1` on `A1`, the pico9918 answers on its extended register ports as well as its two standard ones. A PICO9918 PRO takes it through a header pin soldered into its `MDE1` pad. On Rev 1.0, pin 11 connects to nothing and no track carries `A1`.
- JP1 is open as made, so the pico9918's `/INT` reaches `IRQB` (or `NMIB`, through J2) only through D1. The pico9918 drives `/INT` high as well as low, and with JP1 bridged, as on Rev 1.0, it holds `IRQB` high against every other interrupt source.
- D1 is named in its value field: a BAT85, cathode toward the pico9918, so the schematic says which diode to fit. Rev 1.0's parts list orders the same BAT85.
- U1, the pico9918, is turned around. On Rev 1.0 its pin 1 faces the wrong way, so the flat cable (FFC) to the VGA adapter that comes with the pico9918 has to leave its left side, run under the card, twist, and come back to the adapter. Turned round, a shorter cable runs straight to the jack with no twist. The outline around the VGA jack changes, the two mounting holes move to fit the VGA adapter better, and the tracks are rerouted to suit. The notch for the adapter is 32.5 mm wide, with its two M3 holes 25.0 mm apart and 2.5 mm in from the notch's inner edge, the same as the VCS Output Board 1.1's, so one 3D-printed adapter fits both. Notch and holes are centred on the pico9918's socket (2026-11-15: they had sat 0.43 and 0.38 mm off its centreline); the outline at the notch's mouth is redrawn clean, with a 1 mm fillet into the card's right edge.
- U1 uses a socket footprint (`Socket_LongPads`) in place of Rev 1.0's `LongPads`, so the silkscreen shows the sockets the pico9918 sits in. The holes are the same.
- `JP2` and `JP3` are removed. They chose whether `PHI2` or the supply drives E2, an enable of U3, the 74HC138 that makes the card's read and write strobes. With `PHI2` there, as Rev 1.0 ships, the strobes last only while `PHI2` is high, when the 6502's address and data are valid; tied high, they would run through the whole cycle and glitch while the address settles. So Rev 1.1 wires `PHI2` straight to E2. JP3's copper strip is a short track now, and JP2 goes with its feed from the supply.
- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. Rev 1.0 has mask between the fingers. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved up to 0.05 mm from Rev 1.0's, and no track, pad or hole moved. Only the notch for the VGA jack stays as it was, where the jack needs it. The ground pours are refilled to suit.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/VGA Card/Rev 1.0/` and `Production/VGA Card/Rev 1.0/` match the boards JLCPCB made (order Y64). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Video Card

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- `JP7` is bridged as made, which shorts across D1. On Rev 1.0 it is open, so `/INT` reaches `IRQB` or `NMIB` through D1. Both work, because a real TMS9918A's `/INT` is open-drain. Rev 1.1 follows the family's interrupt rule (`KICAD.md` K24b): a board whose interrupt source is open-drain ships its diode's jumper bridged, so the card works as shipped even without D1.
- U1 and U7 use socket footprints (`Socket_LongPads`) in place of Rev 1.0's `LongPads`, so the silkscreen shows the sockets they sit in, as every socketed chip in the family has. The holes are the same.
- `JP1`–`JP6` are removed. They were for testing the first cards: JP1 and JP2 chose whether `PHI2` or VCC enables U4, and JP3–JP6 chose whether the column latch, U6, is clocked by `/CAS` through one of U8's inverters or three. The tested cards run as Rev 1.0 ships them, so Rev 1.1 is wired that way, with nothing for a builder to set: `PHI2` goes straight to U4's enable, and `/CAS` reaches U6 through three inverters. The three jumpers that shipped bridged are short tracks now; the open ones' stubs, and a via that served only JP5, are gone.
- Adds the OSHW and A.C. Wright logos to the silkscreen, which the family's other boards carry.
- The silkscreen labels `J4` as `VIDEO`, in capitals like the family's other connector labels. Rev 1.0's says `Video Out`.
- The card edge is bare: no solder mask on the tab, front or back, from where its fillets end, so the fingers seat better in the slot and make better contact. Rev 1.0 has mask between the fingers. The fingers carry no solder paste, so no stencil prints paste onto them. The outline is redrawn to the one card shape every card shares, placed by the fingers: it moved up to 0.05 mm from Rev 1.0's, and no track, pad or hole moved. The ground pours are refilled to suit.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Video Card/Rev 1.0/` and `Production/Video Card/Rev 1.0/` match the boards JLCPCB made (order Y53). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
