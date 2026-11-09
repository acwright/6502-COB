# Bill of materials: 6502-COB

Every part for every board in this repository, by revision, with supplier numbers.

## How to use this

1. **Find your board and revision** in [Which revision do I have?](#which-revision-do-i-have)
2. **Read the [known issues](#known-issues)** for that revision, because they change what you buy or fit.
3. **Order from the table for your revision.** Each revision links to files you can upload to Digi-Key and Mouser. Those files are for one board, so multiply the quantities if you're building more. If a site asks which column is which, the first column is its part number and the third is the quantity. A cart only holds what that supplier sells, so check the table for anything else, such as chips from Jameco.
4. **Set the jumpers** before the first power-up. The README's [Jumpers](README.md#jumpers) section says which ones each board needs, and the table for your revision lists the shunts.

**Pre-soldered parts.** Some boards on Tindie come with their surface-mount parts already soldered. Parts marked **Yes** under Pre-soldered are the ones soldered on those boards. Check your listing, because others are sold as a bare PCB. Each revision that has such parts also has a `through-hole` cart that leaves them out. To solder a bare board yourself, use the full cart.

**Suppliers.** Every part has one set of numbers, so the same resistor is the same order line on every board. The numbers were read from Digi-Key and Mouser on 2026-11-04, and stock changes. A blank supplier cell means that supplier doesn't sell the part, or only sells it in bulk.

**The `bom.csv` files** under `Production/` are for JLCPCB assembly. They list the same parts. A blank LCSC cell there means JLCPCB doesn't place that part, and JLCPCB's "missing parts" warning about it is expected.

## Which revision do I have?

Look on the board: the silk prints the revision next to the copyright line. [REVISIONS.md](REVISIONS.md) has the facts for each one, and its history lists what changed between them.

**To make a new board, make the newest revision**, and check its label first. The README's [Which revision to make](README.md#which-revision-to-make) explains the three labels: **Tested**, **Proven design** and **Untested**.

| Board | Revision | What the silk says | Status | Label |
|---|---|---|---|---|
| [Backplane Helper](#backplane-helper) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [Backplane Pro](#backplane-pro) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [Backplane Pro](#backplane-pro) | 1.1 | Rev 1.1 | Made, tested | **Tested** |
| [Backplane Pro](#backplane-pro) | 1.2 | Rev 1.2 | Drawn, not made yet | **Untested**: a 1N5819 in the power path (`VCC` near 4.6 V), and R5 removed |
| [Backplane](#backplane) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [Blinkenlights Card](#blinkenlights-card) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [Blinkenlights Card](#blinkenlights-card) | 1.1 | Rev 1.1 | Drawn, not made yet | **Untested**: decoupling capacitors added, with tracks rerouted to reach them, and the bare card edge |
| [Breadboard Helper](#breadboard-helper) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [Breadboard Helper](#breadboard-helper) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: J1 takes the box header's footprint, with the same holes |
| [CPU Card Pro](#cpu-card-pro) | 1.0 | Rev 1.0 | Never made | **Untested**: never made |
| [CPU Card](#cpu-card) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [CPU Card](#cpu-card) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: 10k pull-ups, some tracks rerouted, silkscreen, the bare card edge |
| [Clock Card](#clock-card) | 1.0 | Rev 1.0 | Ordered, not tested yet | **Untested**: a new board, ordered and not tested yet |
| [Clock Card](#clock-card) | 1.1 | Rev 1.1 | Drawn, not made yet | **Untested**: the bare card edge only, but Rev 1.0 hasn't been tested yet |
| [Clock Helper](#clock-helper) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [Clock Helper](#clock-helper) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: mounting holes moved to the standard, silkscreen |
| [DB25 Helper](#db25-helper) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [DB25 Helper](#db25-helper) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: mounting holes moved to the standard, silkscreen |
| [GPIO Breadboard Helper](#gpio-breadboard-helper) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [GPIO Card](#gpio-card) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [GPIO Card](#gpio-card) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: the bare card edge only |
| [GPIO Helper](#gpio-helper) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [GPIO Helper](#gpio-helper) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: mounting holes moved to the standard, silkscreen |
| [Joystick Helper](#joystick-helper) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [Joystick Helper](#joystick-helper) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: mounting holes moved to the standard, silkscreen |
| [Keyboard Encoder Helper](#keyboard-encoder-helper) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [Keyboard Encoder Helper](#keyboard-encoder-helper) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: mounting holes, silkscreen |
| [Keyboard Helper](#keyboard-helper) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [LCD Board](#lcd-board) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [LCD Card](#lcd-card) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [LCD Card](#lcd-card) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: the bare card edge only |
| [Mega Helper](#mega-helper) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [Memory Card](#memory-card) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [Memory Card](#memory-card) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: the bare card edge only |
| [PS2 Helper](#ps2-helper) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [PS2 Helper](#ps2-helper) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: resistors moved and tracks rerouted, mounting holes, silkscreen |
| [Prototype Card](#prototype-card) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [Prototype Card](#prototype-card) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: the bare card edge only |
| [RAM Card](#ram-card) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [RAM Card](#ram-card) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: the bare card edge only, so far: it keeps Rev 1.0's one bank latch, which the build notes describe |
| [RTC Card](#rtc-card) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [RTC Card](#rtc-card) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: the bare card edge only |
| [Serial Card Pro](#serial-card-pro) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [Serial Card Pro](#serial-card-pro) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: the DB-9 moved to KiCad's standard footprint (the same connector), tracks rerouted, silkscreen, the bare card edge |
| [Serial Card](#serial-card) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [Serial Card](#serial-card) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: silkscreen text and the bare card edge |
| [Sound Card](#sound-card) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [Sound Card](#sound-card) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: silkscreen text and the bare card edge |
| [Storage Card Pro](#storage-card-pro) | 1.0 | Rev 1.0 | Made, not tested yet | **Untested**: made, and not tested yet: the BIOS has no driver for it |
| [Storage Card Pro](#storage-card-pro) | 1.1 | Rev 1.1 | Drawn, not made yet | **Untested**: silkscreen text and the bare card edge, but Rev 1.0 hasn't been tested |
| [Storage Card](#storage-card) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [Storage Card](#storage-card) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: the bare card edge only |
| [VERA Helper](#vera-helper) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [VERA Helper](#vera-helper) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: mounting holes, capacitor pitch, JP2 ships open |
| [VGA Card Pro](#vga-card-pro) | 1.0 | Rev 1.0 | Never made | **Untested**: never made |
| [VGA Card](#vga-card) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [VGA Card](#vga-card) | 1.1 | Rev 1.1 | Drawn, not made yet | **Untested**: the pico9918 turned around, a new outline and jack mount, A1 wired to `MODE1`, and the bare card edge |
| [Video Card Pro](#video-card-pro) | 1.0 | Rev 1.0 | Never made | **Untested**: never made |
| [Video Card](#video-card) | 1.0 | Rev 1.0 | Made, tested | **Tested** |
| [Video Card](#video-card) | 1.1 | Rev 1.1 | Drawn, not made yet | **Proven design**: JP7, a solder jumper, ships bridged (fine with a real TMS9918A's open-drain `/INT`), sockets, silkscreen, the bare card edge |

## Known issues

These change what you buy or fit. The boards themselves stay as they were made.

| Board | Revision | Parts | Issue |
|---|---|---|---|
| Backplane Pro | 1.0 | J10 | Fit a box header for a ribbon cable. The silk shows a plain header, but the holes are the same. Pin 1 is the square pad, and the notch faces the even-numbered pins. |
| Backplane Pro | 1.0 | R3 | Do not fit this. If your board came with it soldered, remove it. See the build notes. |
| Backplane Pro | 1.1 | R5 | Do not fit this. If your board came with it soldered, remove it. See the build notes. |
| Breadboard Helper | 1.0 | J1 | Fit a box header for a ribbon cable. The silk shows a plain header, but the holes are the same. Pin 1 is the square pad, and the notch faces the even-numbered pins. |
| CPU Card | 1.0 | R1–R6 | Fit 10k, not 1k. If your board came with 1k soldered here, replace it. See the build notes. |
| Keyboard Encoder Helper | 1.0 | C2, C3 | The silk says 22 pF; fit 20 pF. A board built with 22 pF is fine. |
| PS2 Helper | 1.0 | C4, C5 | The silk says 22 pF; fit 20 pF. A board built with 22 pF is fine. |
| PS2 Helper | 1.0 | U1 | The MT8808 is out of production, and eBay is the likely source. The Keyboard Encoder Helper is the recommended way to handle a keyboard instead. |
| PS2 Helper | 1.1 | U1 | The MT8808 is out of production, and eBay is the likely source. The Keyboard Encoder Helper is the recommended way to handle a keyboard instead. |
| RTC Card | 1.0 | BT1 | `BAT-HLD-001-THM`, on the tested boards, is obsolete. `BAT-HLD-001-THM-TR` is its listed continuation, with no stock today and no board built with it yet. |
| RTC Card | 1.1 | BT1 | `BAT-HLD-001-THM`, on the tested boards, is obsolete. `BAT-HLD-001-THM-TR` is its listed continuation, with no stock today and no board built with it yet. |
| Serial Card Pro | 1.0 | U4 | The silk says 6551; fit an R6551AP. |
| Serial Card | 1.0 | U3 | The silk says 6551; fit an R6551AP. |
| Sound Card | 1.0 | J2 | `VDD` is the supply for a real SID at pin 28: 12 V for a 6581, 9 V for an 8580. The standard build does not provide it, and it has never been tested. Leave it unconnected with an ARMSID. |
| Sound Card | 1.0 | U1 | The silk says 6581; fit an ARMSID. |
| Storage Card Pro | 1.0 | C5, C6 | The silk says 22 pF; fit 20 pF. A board built with 22 pF is fine. |
| Video Card | 1.0 | C1, C2 | Fit 32 or 33 pF. 33 pF is the standard value, and it is what the tested card has. |
| Video Card | 1.0 | U1 | The TMS9918A is out of production, and eBay is the likely source. The VGA Card is the recommended alternative to this board. |
| Video Card | 1.1 | C1, C2 | Fit 32 or 33 pF. 33 pF is the standard value, and it is what the tested card has. |
| Video Card | 1.1 | U1 | The TMS9918A is out of production, and eBay is the likely source. The VGA Card is the recommended alternative to this board. |

### Build notes

How to build each board, where it needs more than its parts list.

<!-- Build notes: hand-written. Tools/bom/gen_bom.py keeps everything between these two markers. -->

**Backplane Pro**

**Building a Rev 1.1:**
- **Leave R5 unfitted.** R5 is a 1kΩ pull-up on `RESB`, in parallel with the CPU Card's. The CPU Card's pull-up is the only one a COB needs, and the Backplane Pro's reset circuit only pulls `RESB` low, through Q1. Without a CPU Card on the bus, `RESB` then has no pull-up, so whatever drives the bus instead (a [Mega Helper](#mega-helper), for example) must hold `RESB` high itself.
- **Use a centre-positive 5 V supply only.** Rev 1.1 has no reverse-polarity protection on the barrel jack.

**Building a Rev 1.0:** leave R3 unfitted, or remove it from a built board. R3 is a 1kΩ pull-up on `RESB`, in parallel with the CPU Card's, and the CPU Card's pull-up is the only one a COB needs. The Rev 1.1 notes above explain what that means for a machine without a CPU Card.

**Blinkenlights Card**

**Both revisions:** the `IRQB`, `NMIB` and `RESB` LEDs (D25–D27, through R25–R27) hang straight on those lines. While a line is asserted, whatever pulls it low also sinks about 9 mA of LED current, nearly three times the 3.2 mA that the W65C22's and W65C21's IRQ outputs are rated for. The 65C02 may still read the line as low, but nothing guarantees it. Fit the card to watch the bus, not in a machine that relies on its interrupts. A later revision will buffer those three LEDs through the 74HC04's spare gates, as `RDY` and `BE` already are.

**CPU Card**

**Building a Rev 1.0:** fit 10kΩ (0805) for R1–R6, not the 1kΩ in Rev 1.0's files; Rev 1.1 has 10kΩ. With a 1kΩ pull-up, a device that pulls `IRQB` low sinks 5 mA, more than the 3.2 mA that the W65C22's and W65C21's IRQ outputs are rated for. Rev 1.1's other changes, its rerouted tracks, its silkscreen and its bare card edge, need nothing on a built board.

**Clock Card**

**Building a Rev 1.0:** nothing to do. Rev 1.1 changes only the card edge, which has no solder mask on its tab; a Rev 1.0's masked edge works in the slot.

**GPIO Card**

**Building a Rev 1.0:** nothing to do. Rev 1.1 changes only the card edge, which has no solder mask on its tab; a Rev 1.0's masked edge works in the slot.

**LCD Card**

**Building a Rev 1.0:** nothing to do. Rev 1.1 changes only the card edge, which has no solder mask on its tab; a Rev 1.0's masked edge works in the slot. Both revisions ship JP1 bridged for the W65C22N.

**Mega Helper**

**Writing firmware for it:** the Mega's D2, D3, D4, D9 and D10 connect straight to `IRQB`, `NMIB`, `RESB`, `RDY` and `BE`, which every other device on the bus shares. Drive those pins open-drain. To assert a line, call `digitalWrite(pin, LOW)` and then `pinMode(pin, OUTPUT)`, in that order: after `INPUT_PULLUP` the pin's output latch is high, so switching to `OUTPUT` first would drive the line high for a moment. To release a line, call `pinMode(pin, INPUT)`. Never drive one of these pins high, because a pin driven high holds its line high against every other device that pulls it low. The pull-ups are on the CPU Card; in a machine without a CPU Card, release `RESB` with `pinMode(pin, INPUT_PULLUP)` so that it rises.

**Memory Card**

**Building a Rev 1.0:** nothing to do. Rev 1.1 changes only the card edge, which has no solder mask on its tab; a Rev 1.0's masked edge works in the slot.

**Prototype Card**

**Building a Rev 1.0:** nothing to do. Rev 1.1 changes only the card edge, which has no solder mask on its tab; a Rev 1.0's masked edge works in the slot.

**RAM Card**

**Rev 1.0 is deprecated, and still works with the BIOS and BASIC.** Rev 1.1 as drawn today has the same circuit, so all of this applies to it too; it is to get a bank latch for each window, and window selects that read as not selected when a jumper is missing, before it is made. Before fitting either:
- **Jumper both windows on J3, and nothing else:** 1–2 for IO 1 (`$8000`) and 3–4 for IO 2 (`$8400`), the setting the BIOS expects. R1 and R2 pull the window selects low, and the selects are active low, so a window left without a jumper is selected at every address: the card then drives the data bus on every read, against the system RAM and ROM. J3's other positions connect the same two windows to other addresses, so a third jumper puts two 74HC138 outputs on one window's select and ties them together.
- **One bank latch serves both windows.** A write to `$83FF` and a write to `$87FF` load the same 74HC573, so both windows always show the same bank number, each in its own half of the AS6C4008. A program can't point one window at one bank and the other window at another, so copying between banks through the two windows doesn't work on this card.
- **The data bus reaches the latch bit-reversed** (`D0` drives the latch's `D7`). That only renumbers the banks, and no program can tell.

**Building a Rev 1.0:** as above. Rev 1.1's other change, its bare card edge, needs nothing on a built board: a Rev 1.0's masked edge works in the slot.

**RTC Card**

**Building a Rev 1.0:** nothing to do. Rev 1.1 changes only the card edge, which has no solder mask on its tab; a Rev 1.0's masked edge works in the slot.

**Storage Card**

**Building a Rev 1.0:** nothing to do. Rev 1.1 changes only the card edge, which has no solder mask on its tab; a Rev 1.0's masked edge works in the slot.

**VERA Helper**

**Building a Rev 1.0: cut JP2 before fitting a shunt on J5.** The VERA module drives its interrupt high as well as low. JP2, bridged on the board as made, shorts across D1, so with a shunt on J5 the module holds `IRQB` (or `NMIB`) high against every other interrupt source. Cut the trace between JP2's pads, and check with a meter that they no longer connect; Rev 1.1 ships JP2 open. Without a shunt on J5 the interrupt reaches neither line, and JP2 doesn't matter. Rev 1.1's other changes, its mounting holes and capacitor pitch, need nothing on a built board.

**VGA Card**

**Building a Rev 1.0: cut JP1.** The pico9918 drives its `/INT` (U1 pin 16) high as well as low. D1 is meant to let it only pull `IRQB` (or `NMIB`, through J2) low, but JP1, a solder jumper bridged on the board as made, shorts across D1. With JP1 bridged, the pico9918 holds `IRQB` high against every other interrupt source, and the keyboard and serial input stop working. Cut the trace between JP1's pads, and check with a meter that they no longer connect. The COB Video Card's JP7 is a different case: a real TMS9918A's `/INT` is open-drain, so it doesn't matter whether JP7 is open or bridged.

Rev 1.1's bare card edge, with no mask on its tab, needs nothing on a built board: a Rev 1.0's masked edge works in the slot.

<!-- End of build notes. -->

## Backplane Helper

### Backplane Helper Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Backplane%20Helper/Rev%201.0/digikey.csv), [mouser.csv](BOM/Backplane%20Helper/Rev%201.0/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| J1, J2 | 2 | 6502 Card Connector | TE Connectivity 5-5530843-4 | [A31723-ND](https://www.digikey.com/en/products/filter?keywords=A31723-ND) | [571-5-5530843-4](https://www.mouser.com/ProductDetail/571-5-5530843-4) |  |
| J3 | 1 | 6502 Bus | Würth Elektronik 61204021621 | [732-5401-ND](https://www.digikey.com/en/products/filter?keywords=732-5401-ND) | [710-61204021621](https://www.mouser.com/ProductDetail/710-61204021621) |  |

- **J3:** Male box header with a keying notch, for a 40-way ribbon cable.


## Backplane Pro

### Backplane Pro Rev 1.2

Drawn, not made yet. **Untested**: a 1N5819 in the power path (`VCC` near 4.6 V), and R5 removed.

Cart files: [digikey.csv](BOM/Backplane%20Pro/Rev%201.2/digikey.csv), [mouser.csv](BOM/Backplane%20Pro/Rev%201.2/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| C1, C3 | 2 | 10uF | Panasonic EEA-GA1C100 | [P14482-ND](https://www.digikey.com/en/products/filter?keywords=P14482-ND) | [667-EEA-GA1C100](https://www.mouser.com/ProductDetail/667-EEA-GA1C100) |  |
| C2 | 1 | 100nF | KYOCERA AVX SR205C104KAR | [478-3187-ND](https://www.digikey.com/en/products/filter?keywords=478-3187-ND) | [581-SR205C104KAR](https://www.mouser.com/ProductDetail/581-SR205C104KAR) |  |
| D1 | 1 | POWER LED | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D2 | 1 | 1N5819 | Vishay 1N5819-E3/54 | [1N5819-E3/54GICT-ND](https://www.digikey.com/en/products/filter?keywords=1N5819-E3%2F54GICT-ND) | [625-1N5819-E3](https://www.mouser.com/ProductDetail/625-1N5819-E3) |  |
| J1 | 1 | 5V DC | Same Sky PJ-102AH | [CP-102AH-ND](https://www.digikey.com/en/products/filter?keywords=CP-102AH-ND) | [490-PJ-102AH](https://www.mouser.com/ProductDetail/490-PJ-102AH) |  |
| J2–J4, J7, J8 | 5 | 6502 Card Connector | TE Connectivity 5-5530843-4 | [A31723-ND](https://www.digikey.com/en/products/filter?keywords=A31723-ND) | [571-5-5530843-4](https://www.mouser.com/ProductDetail/571-5-5530843-4) |  |
| J5 | 1 | CLOCK ENBL SW | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  |
| J6 | 1 | RESET SW | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  |
| J9 | 1 | 6502 Bus | Würth Elektronik 61204021621 | [732-5401-ND](https://www.digikey.com/en/products/filter?keywords=732-5401-ND) | [710-61204021621](https://www.mouser.com/ProductDetail/710-61204021621) |  |
| Q1 | 1 | 2N3904 | onsemi 2N3904BU | [2N3904FS-ND](https://www.digikey.com/en/products/filter?keywords=2N3904FS-ND) | [512-2N3904BU](https://www.mouser.com/ProductDetail/512-2N3904BU) |  |
| R1 | 1 | 330 | YAGEO MFR-12FTF52-330R | [13-MFR-12FTF52-330RCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-330RCT-ND) | [603-MFR-12FTF52-330R](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-330R) |  |
| R2 | 1 | 1M | YAGEO MFR-12FTF52-1M | [13-MFR-12FTF52-1MCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1MCT-ND) | [603-MFR-12FTF52-1M](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1M) |  |
| R3 | 1 | 47k | YAGEO MFR-12FTF52-47K | [13-MFR-12FTF52-47KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-47KCT-ND) | [603-MFR-12FTF52-47K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-47K) |  |
| R4 | 1 | 10k | YAGEO MFR-12FTF52-10K | [13-MFR-12FTF52-10KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-10KCT-ND) | [603-MFR-12FTF52-10K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-10K) |  |
| SW1 | 1 | POWER | E-Switch 400MSP1R6BLKM6QE | [EG4326-ND](https://www.digikey.com/en/products/filter?keywords=EG4326-ND) | [612-400MSP1R6BLKM6QE](https://www.mouser.com/ProductDetail/612-400MSP1R6BLKM6QE) |  |
| SW2 | 1 | RESET | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| U1 | 1 | LM555 | Texas Instruments LM555CN/NOPB | [LM555CNNS/NOPB-ND](https://www.digikey.com/en/products/filter?keywords=LM555CNNS%2FNOPB-ND) | [926-LM555CN/NOPB](https://www.mouser.com/ProductDetail/926-LM555CN%2FNOPB) |  |
| X1 | 1 | 1 MHz | ECS Inc. ECS-100AX-010 | [X937-ND](https://www.digikey.com/en/products/filter?keywords=X937-ND) | [520-TCF100-X](https://www.mouser.com/ProductDetail/520-TCF100-X) |  |
| U1 | 1 | Socket | IC socket, 8-pin, 0.3 in | [3M5473-ND](https://www.digikey.com/en/products/filter?keywords=3M5473-ND) | [517-4808-3004-CP](https://www.mouser.com/ProductDetail/517-4808-3004-CP) | |

- **D1:** Green shown. The colour is the builder's choice.
- **J1:** Replaces GCT DCJ200-10-A-K1-K, now obsolete, which older builds used. Its pads and body match this footprint on the datasheet. No board has been built with it yet.
- **J9:** Male box header with a keying notch, for a 40-way ribbon cable.

### Backplane Pro Rev 1.1

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Backplane%20Pro/Rev%201.1/digikey.csv), [mouser.csv](BOM/Backplane%20Pro/Rev%201.1/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| C1, C3 | 2 | 10uF | Panasonic EEA-GA1C100 | [P14482-ND](https://www.digikey.com/en/products/filter?keywords=P14482-ND) | [667-EEA-GA1C100](https://www.mouser.com/ProductDetail/667-EEA-GA1C100) |  |
| C2 | 1 | 100nF | KYOCERA AVX SR205C104KAR | [478-3187-ND](https://www.digikey.com/en/products/filter?keywords=478-3187-ND) | [581-SR205C104KAR](https://www.mouser.com/ProductDetail/581-SR205C104KAR) |  |
| D1 | 1 | POWER LED | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| J1 | 1 | 5V DC | Same Sky PJ-102AH | [CP-102AH-ND](https://www.digikey.com/en/products/filter?keywords=CP-102AH-ND) | [490-PJ-102AH](https://www.mouser.com/ProductDetail/490-PJ-102AH) |  |
| J2–J4, J7, J8 | 5 | 6502 Card Connector | TE Connectivity 5-5530843-4 | [A31723-ND](https://www.digikey.com/en/products/filter?keywords=A31723-ND) | [571-5-5530843-4](https://www.mouser.com/ProductDetail/571-5-5530843-4) |  |
| J5 | 1 | CLOCK ENBL SW | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  |
| J6 | 1 | RESET SW | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  |
| J9 | 1 | 6502 Bus | Würth Elektronik 61204021621 | [732-5401-ND](https://www.digikey.com/en/products/filter?keywords=732-5401-ND) | [710-61204021621](https://www.mouser.com/ProductDetail/710-61204021621) |  |
| Q1 | 1 | 2N3904 | onsemi 2N3904BU | [2N3904FS-ND](https://www.digikey.com/en/products/filter?keywords=2N3904FS-ND) | [512-2N3904BU](https://www.mouser.com/ProductDetail/512-2N3904BU) |  |
| R1 | 1 | 330 | YAGEO MFR-12FTF52-330R | [13-MFR-12FTF52-330RCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-330RCT-ND) | [603-MFR-12FTF52-330R](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-330R) |  |
| R2 | 1 | 1M | YAGEO MFR-12FTF52-1M | [13-MFR-12FTF52-1MCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1MCT-ND) | [603-MFR-12FTF52-1M](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1M) |  |
| R3 | 1 | 47k | YAGEO MFR-12FTF52-47K | [13-MFR-12FTF52-47KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-47KCT-ND) | [603-MFR-12FTF52-47K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-47K) |  |
| R4 | 1 | 10k | YAGEO MFR-12FTF52-10K | [13-MFR-12FTF52-10KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-10KCT-ND) | [603-MFR-12FTF52-10K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-10K) |  |
| SW1 | 1 | POWER | E-Switch 400MSP1R6BLKM6QE | [EG4326-ND](https://www.digikey.com/en/products/filter?keywords=EG4326-ND) | [612-400MSP1R6BLKM6QE](https://www.mouser.com/ProductDetail/612-400MSP1R6BLKM6QE) |  |
| SW2 | 1 | RESET | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| U1 | 1 | LM555 | Texas Instruments LM555CN/NOPB | [LM555CNNS/NOPB-ND](https://www.digikey.com/en/products/filter?keywords=LM555CNNS%2FNOPB-ND) | [926-LM555CN/NOPB](https://www.mouser.com/ProductDetail/926-LM555CN%2FNOPB) |  |
| X1 | 1 | 1 MHz | ECS Inc. ECS-100AX-010 | [X937-ND](https://www.digikey.com/en/products/filter?keywords=X937-ND) | [520-TCF100-X](https://www.mouser.com/ProductDetail/520-TCF100-X) |  |
| U1 | 1 | Socket | IC socket, 8-pin, 0.3 in | [3M5473-ND](https://www.digikey.com/en/products/filter?keywords=3M5473-ND) | [517-4808-3004-CP](https://www.mouser.com/ProductDetail/517-4808-3004-CP) | |

**Do not fit** R5: see the build notes.

- **D1:** Green shown. The colour is the builder's choice.
- **J1:** Replaces GCT DCJ200-10-A-K1-K, now obsolete, which older builds used. Its pads and body match this footprint on the datasheet. No board has been built with it yet.
- **J9:** Male box header with a keying notch, for a 40-way ribbon cable.

### Backplane Pro Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Backplane%20Pro/Rev%201.0/digikey.csv), [mouser.csv](BOM/Backplane%20Pro/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/Backplane%20Pro/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Backplane%20Pro/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C3–C14 | 13 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| C2 | 1 | 10uF | KYOCERA AVX TAJA106K016RNJ | [478-1655-1-ND](https://www.digikey.com/en/products/filter?keywords=478-1655-1-ND) | [581-TAJA106K016R](https://www.mouser.com/ProductDetail/581-TAJA106K016R) | LCSC [C7171](https://www.lcsc.com/search?q=C7171) | Yes |
| D1 | 1 | 1N5819 | MCC (Micro Commercial Components) B5819WS-TP | [B5819WS-TPMSCT-ND](https://www.digikey.com/en/products/filter?keywords=B5819WS-TPMSCT-ND) |  | LCSC [C191023](https://www.lcsc.com/search?q=C191023) | Yes |
| D2 | 1 | LED | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| J1 | 1 | PWR_SW | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  | |
| J2 | 1 | USB_C_Receptacle_USB2.0 | G-Switch GT-USB-7010ASV |  |  | LCSC [C2988369](https://www.lcsc.com/search?q=C2988369) | Yes |
| J3 | 1 | RESET_SW | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  | |
| J4 | 1 | CLOCK_ENBL_SW | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  | |
| J5–J9 | 5 | 6502 Card Connector | TE Connectivity 5-5530843-4 | [A31723-ND](https://www.digikey.com/en/products/filter?keywords=A31723-ND) | [571-5-5530843-4](https://www.mouser.com/ProductDetail/571-5-5530843-4) |  | |
| J10 | 1 | 6502 Bus | Pin header 2×20, 2.54 mm, cut from a strip | [732-5401-ND](https://www.digikey.com/en/products/filter?keywords=732-5401-ND) | [710-61204021621](https://www.mouser.com/ProductDetail/710-61204021621) |  | |
| Q1 | 1 | SS8050 | Comchip Technology SS8050-G | [641-1790-1-ND](https://www.digikey.com/en/products/filter?keywords=641-1790-1-ND) | [750-SS8050-G](https://www.mouser.com/ProductDetail/750-SS8050-G) | LCSC [C2150](https://www.lcsc.com/search?q=C2150) | Yes |
| R1 | 1 | 1M | YAGEO RC0805FR-071ML | [311-1.00MCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-1.00MCRCT-ND) | [603-RC0805FR-071ML](https://www.mouser.com/ProductDetail/603-RC0805FR-071ML) | LCSC [C17514](https://www.lcsc.com/search?q=C17514) | Yes |
| R2 | 1 | 47k | YAGEO RC0805FR-0747KL | [311-47.0KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-47.0KCRCT-ND) | [603-RC0805FR-0747KL](https://www.mouser.com/ProductDetail/603-RC0805FR-0747KL) | LCSC [C17713](https://www.lcsc.com/search?q=C17713) | Yes |
| R4 | 1 | 10k | YAGEO RC0805FR-0710KL | [311-10.0KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-10.0KCRCT-ND) | [603-RC0805FR-0710KL](https://www.mouser.com/ProductDetail/603-RC0805FR-0710KL) | LCSC [C17414](https://www.lcsc.com/search?q=C17414) | Yes |
| R5, R6 | 2 | 5.1k | YAGEO RC0805FR-075K1L | [311-5.10KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-5.10KCRCT-ND) | [603-RC0805FR-075K1L](https://www.mouser.com/ProductDetail/603-RC0805FR-075K1L) | LCSC [C27834](https://www.lcsc.com/search?q=C27834) | Yes |
| R7 | 1 | 330 | YAGEO RC0805FR-07330RL | [311-330CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-330CRCT-ND) | [603-RC0805FR-07330RL](https://www.mouser.com/ProductDetail/603-RC0805FR-07330RL) | LCSC [C17630](https://www.lcsc.com/search?q=C17630) | Yes |
| SW1 | 1 | Reset | TS-1187A-B-A-B |  |  | LCSC [C318884](https://www.lcsc.com/search?q=C318884) | |
| U1 | 1 | NE555 | Texas Instruments NE555DR | [296-6501-1-ND](https://www.digikey.com/en/products/filter?keywords=296-6501-1-ND) | [595-NE555DR](https://www.mouser.com/ProductDetail/595-NE555DR) | LCSC [C7593](https://www.lcsc.com/search?q=C7593) | Yes |
| X1 | 1 | 1 MHz | ECS Inc. ECS-100AX-010 | [X937-ND](https://www.digikey.com/en/products/filter?keywords=X937-ND) | [520-TCF100-X](https://www.mouser.com/ProductDetail/520-TCF100-X) |  | |

Pin headers are cut from strips, and the cart files count whole strips.

**Do not fit** R3: the RESB pull-up is on the CPU Card.

- **J2:** What LCSC C2988369 is. The footprint is HRO TYPE-C-31-M-12, and JLCPCB placed this part on the made boards.


## Backplane

### Backplane Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Backplane/Rev%201.0/digikey.csv), [mouser.csv](BOM/Backplane/Rev%201.0/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| J1–J5 | 5 | 6502 Card Connector | TE Connectivity 5-5530843-4 | [A31723-ND](https://www.digikey.com/en/products/filter?keywords=A31723-ND) | [571-5-5530843-4](https://www.mouser.com/ProductDetail/571-5-5530843-4) |  |
| J6, J7 | 2 | 6502 Bus | Würth Elektronik 61204021621 | [732-5401-ND](https://www.digikey.com/en/products/filter?keywords=732-5401-ND) | [710-61204021621](https://www.mouser.com/ProductDetail/710-61204021621) |  |

- **J6, J7:** Male box header with a keying notch, for a 40-way ribbon cable.


## Blinkenlights Card

### Blinkenlights Card Rev 1.1

Drawn, not made yet. **Untested**: decoupling capacitors added, with tracks rerouted to reach them, and the bare card edge.

Cart files: [digikey.csv](BOM/Blinkenlights%20Card/Rev%201.1/digikey.csv), [mouser.csv](BOM/Blinkenlights%20Card/Rev%201.1/mouser.csv), [digikey-through-hole.csv](BOM/Blinkenlights%20Card/Rev%201.1/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Blinkenlights%20Card/Rev%201.1/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1–C4 | 4 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| D1 | 1 | A15 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D2 | 1 | A14 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D3 | 1 | A13 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D4 | 1 | A12 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D5 | 1 | A11 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D6 | 1 | A10 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D7 | 1 | A9 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D8 | 1 | A8 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D9 | 1 | A7 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D10 | 1 | A6 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D11 | 1 | A5 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D12 | 1 | A4 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D13 | 1 | A3 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D14 | 1 | A2 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D15 | 1 | A1 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D16 | 1 | A0 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D17 | 1 | D7 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D18 | 1 | D6 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D19 | 1 | D5 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D20 | 1 | D4 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D21 | 1 | D3 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D22 | 1 | D2 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D23 | 1 | D1 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D24 | 1 | D0 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D25 | 1 | RESB | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D26 | 1 | IRQB | Lite-On Inc. LTST-C170KRKT | [160-1415-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1415-1-ND) | [859-LTST-C170KRKT](https://www.mouser.com/ProductDetail/859-LTST-C170KRKT) | LCSC [C2295](https://www.lcsc.com/search?q=C2295) | Yes |
| D27 | 1 | NMIB | Lite-On Inc. LTST-C170KRKT | [160-1415-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1415-1-ND) | [859-LTST-C170KRKT](https://www.mouser.com/ProductDetail/859-LTST-C170KRKT) | LCSC [C2295](https://www.lcsc.com/search?q=C2295) | Yes |
| D28 | 1 | RDY | Lite-On Inc. LTST-C170KSKT | [160-1416-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1416-1-ND) | [859-LTST-C170KSKT](https://www.mouser.com/ProductDetail/859-LTST-C170KSKT) | LCSC [C2296](https://www.lcsc.com/search?q=C2296) | Yes |
| D29 | 1 | BE | Lite-On Inc. LTST-C170KSKT | [160-1416-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1416-1-ND) | [859-LTST-C170KSKT](https://www.mouser.com/ProductDetail/859-LTST-C170KSKT) | LCSC [C2296](https://www.lcsc.com/search?q=C2296) | Yes |
| D30 | 1 | RWB | Lite-On Inc. LTST-C170KSKT | [160-1416-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1416-1-ND) | [859-LTST-C170KSKT](https://www.mouser.com/ProductDetail/859-LTST-C170KSKT) | LCSC [C2296](https://www.lcsc.com/search?q=C2296) | Yes |
| D31 | 1 | SYNC | Lite-On Inc. LTST-C170TBKT | [160-1579-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1579-1-ND) | [859-LTST-C170TBKT](https://www.mouser.com/ProductDetail/859-LTST-C170TBKT) | LCSC [C2293](https://www.lcsc.com/search?q=C2293) | Yes |
| D32 | 1 | PHI2 | Lite-On Inc. LTST-C170TBKT | [160-1579-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1579-1-ND) | [859-LTST-C170TBKT](https://www.mouser.com/ProductDetail/859-LTST-C170TBKT) | LCSC [C2293](https://www.lcsc.com/search?q=C2293) | Yes |
| R1–R32 | 32 | 330 | YAGEO RC0805FR-07330RL | [311-330CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-330CRCT-ND) | [603-RC0805FR-07330RL](https://www.mouser.com/ProductDetail/603-RC0805FR-07330RL) | LCSC [C17630](https://www.lcsc.com/search?q=C17630) | Yes |
| U1, U2, U4 | 3 | 74HC573 | Nexperia USA Inc. 74HC573D,653 | [1727-2818-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2818-1-ND) | [771-74HC573D-T](https://www.mouser.com/ProductDetail/771-74HC573D-T) | LCSC [C5608](https://www.lcsc.com/search?q=C5608) | Yes |
| U3 | 1 | 74HC04 | Nexperia USA Inc. 74HC04D,653 | [1727-2776-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2776-1-ND) | [771-74HC04D-T](https://www.mouser.com/ProductDetail/771-74HC04D-T) | LCSC [C5590](https://www.lcsc.com/search?q=C5590) | Yes |

### Blinkenlights Card Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Blinkenlights%20Card/Rev%201.0/digikey.csv), [mouser.csv](BOM/Blinkenlights%20Card/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/Blinkenlights%20Card/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Blinkenlights%20Card/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| D1 | 1 | A15 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D2 | 1 | A14 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D3 | 1 | A13 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D4 | 1 | A12 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D5 | 1 | A11 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D6 | 1 | A10 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D7 | 1 | A9 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D8 | 1 | A8 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D9 | 1 | A7 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D10 | 1 | A6 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D11 | 1 | A5 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D12 | 1 | A4 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D13 | 1 | A3 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D14 | 1 | A2 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D15 | 1 | A1 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D16 | 1 | A0 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D17 | 1 | D7 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D18 | 1 | D6 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D19 | 1 | D5 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D20 | 1 | D4 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D21 | 1 | D3 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D22 | 1 | D2 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D23 | 1 | D1 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D24 | 1 | D0 | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D25 | 1 | RESB | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| D26 | 1 | IRQB | Lite-On Inc. LTST-C170KRKT | [160-1415-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1415-1-ND) | [859-LTST-C170KRKT](https://www.mouser.com/ProductDetail/859-LTST-C170KRKT) | LCSC [C2295](https://www.lcsc.com/search?q=C2295) | Yes |
| D27 | 1 | NMIB | Lite-On Inc. LTST-C170KRKT | [160-1415-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1415-1-ND) | [859-LTST-C170KRKT](https://www.mouser.com/ProductDetail/859-LTST-C170KRKT) | LCSC [C2295](https://www.lcsc.com/search?q=C2295) | Yes |
| D28 | 1 | RDY | Lite-On Inc. LTST-C170KSKT | [160-1416-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1416-1-ND) | [859-LTST-C170KSKT](https://www.mouser.com/ProductDetail/859-LTST-C170KSKT) | LCSC [C2296](https://www.lcsc.com/search?q=C2296) | Yes |
| D29 | 1 | BE | Lite-On Inc. LTST-C170KSKT | [160-1416-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1416-1-ND) | [859-LTST-C170KSKT](https://www.mouser.com/ProductDetail/859-LTST-C170KSKT) | LCSC [C2296](https://www.lcsc.com/search?q=C2296) | Yes |
| D30 | 1 | RWB | Lite-On Inc. LTST-C170KSKT | [160-1416-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1416-1-ND) | [859-LTST-C170KSKT](https://www.mouser.com/ProductDetail/859-LTST-C170KSKT) | LCSC [C2296](https://www.lcsc.com/search?q=C2296) | Yes |
| D31 | 1 | SYNC | Lite-On Inc. LTST-C170TBKT | [160-1579-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1579-1-ND) | [859-LTST-C170TBKT](https://www.mouser.com/ProductDetail/859-LTST-C170TBKT) | LCSC [C2293](https://www.lcsc.com/search?q=C2293) | Yes |
| D32 | 1 | PHI2 | Lite-On Inc. LTST-C170TBKT | [160-1579-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1579-1-ND) | [859-LTST-C170TBKT](https://www.mouser.com/ProductDetail/859-LTST-C170TBKT) | LCSC [C2293](https://www.lcsc.com/search?q=C2293) | Yes |
| R1–R32 | 32 | 330 | YAGEO RC0805FR-07330RL | [311-330CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-330CRCT-ND) | [603-RC0805FR-07330RL](https://www.mouser.com/ProductDetail/603-RC0805FR-07330RL) | LCSC [C17630](https://www.lcsc.com/search?q=C17630) | Yes |
| U1, U2, U4 | 3 | 74HC573 | Nexperia USA Inc. 74HC573D,653 | [1727-2818-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2818-1-ND) | [771-74HC573D-T](https://www.mouser.com/ProductDetail/771-74HC573D-T) | LCSC [C5608](https://www.lcsc.com/search?q=C5608) | Yes |
| U3 | 1 | 74HC04 | Nexperia USA Inc. 74HC04D,653 | [1727-2776-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2776-1-ND) | [771-74HC04D-T](https://www.mouser.com/ProductDetail/771-74HC04D-T) | LCSC [C5590](https://www.lcsc.com/search?q=C5590) | Yes |


## Breadboard Helper

### Breadboard Helper Rev 1.1

Drawn, not made yet. **Proven design**: J1 takes the box header's footprint, with the same holes.

Cart files: [digikey.csv](BOM/Breadboard%20Helper/Rev%201.1/digikey.csv), [mouser.csv](BOM/Breadboard%20Helper/Rev%201.1/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| J1 | 1 | 6502 Bus | Würth Elektronik 61204021621 | [732-5401-ND](https://www.digikey.com/en/products/filter?keywords=732-5401-ND) | [710-61204021621](https://www.mouser.com/ProductDetail/710-61204021621) |  |
| J2, J3 | 2 | Conn_01x20 | Pin header 1×20, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  |

Pin headers are cut from strips, and the cart files count whole strips.

- **J1:** Male box header with a keying notch, for a 40-way ribbon cable.

### Breadboard Helper Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Breadboard%20Helper/Rev%201.0/digikey.csv), [mouser.csv](BOM/Breadboard%20Helper/Rev%201.0/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| J1 | 1 | 6502 Bus | Pin header 2×20, 2.54 mm, cut from a strip | [732-5401-ND](https://www.digikey.com/en/products/filter?keywords=732-5401-ND) | [710-61204021621](https://www.mouser.com/ProductDetail/710-61204021621) |  |
| J2, J3 | 2 | Conn_01x20 | Pin header 1×20, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  |

Pin headers are cut from strips, and the cart files count whole strips.


## CPU Card Pro

### CPU Card Pro Rev 1.0

Never made. **Untested**: never made.

Cart files: [digikey.csv](BOM/CPU%20Card%20Pro/Rev%201.0/digikey.csv), [mouser.csv](BOM/CPU%20Card%20Pro/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/CPU%20Card%20Pro/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/CPU%20Card%20Pro/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1–C4 | 4 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| J2 | 1 | BANK ADDR | Pin header 2×5, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| J3 | 1 | EXP | Pin header 2×4, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| R1–R6 | 6 | 10k | YAGEO RC0805FR-0710KL | [311-10.0KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-10.0KCRCT-ND) | [603-RC0805FR-0710KL](https://www.mouser.com/ProductDetail/603-RC0805FR-0710KL) | LCSC [C17414](https://www.lcsc.com/search?q=C17414) | Yes |
| U1 | 1 | 65C816 | Western Design Center (WDC) W65C816S6PG-14 |  | [955-W65C816S6PG-14](https://www.mouser.com/ProductDetail/955-W65C816S6PG-14) |  | |
| U2 | 1 | 74HC00 | Nexperia USA Inc. 74HC00D,653 | [1727-2773-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2773-1-ND) | [771-74HC00D-T](https://www.mouser.com/ProductDetail/771-74HC00D-T) | LCSC [C5586](https://www.lcsc.com/search?q=C5586) | Yes |
| U3 | 1 | 74HC245 | Nexperia USA Inc. 74HC245PW,118 | [1727-4296-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-4296-1-ND) | [771-HC245PW118](https://www.mouser.com/ProductDetail/771-HC245PW118) | LCSC [C5626](https://www.lcsc.com/search?q=C5626) | Yes |
| U4 | 1 | 74HC573 | Nexperia USA Inc. 74HC573D,653 | [1727-2818-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2818-1-ND) | [771-74HC573D-T](https://www.mouser.com/ProductDetail/771-74HC573D-T) | LCSC [C5608](https://www.lcsc.com/search?q=C5608) | Yes |
| U1 | 1 | Socket | IC socket, 40-pin, 0.6 in | [3M5471-ND](https://www.digikey.com/en/products/filter?keywords=3M5471-ND) | [517-4840-6000-CP](https://www.mouser.com/ProductDetail/517-4840-6000-CP) | | |

Pin headers are cut from strips, and the cart files count whole strips.


## CPU Card

### CPU Card Rev 1.1

Drawn, not made yet. **Proven design**: 10k pull-ups, some tracks rerouted, silkscreen, the bare card edge.

Cart files: [digikey.csv](BOM/CPU%20Card/Rev%201.1/digikey.csv), [mouser.csv](BOM/CPU%20Card/Rev%201.1/mouser.csv), [digikey-through-hole.csv](BOM/CPU%20Card/Rev%201.1/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/CPU%20Card/Rev%201.1/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1 | 1 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| J2 | 1 | Conn_01x02 | Pin header 1×2, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| J3 | 1 | EXP | Pin header 2×5, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| R1–R6 | 6 | 10k | YAGEO RC0805FR-0710KL | [311-10.0KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-10.0KCRCT-ND) | [603-RC0805FR-0710KL](https://www.mouser.com/ProductDetail/603-RC0805FR-0710KL) | LCSC [C17414](https://www.lcsc.com/search?q=C17414) | Yes |
| U1 | 1 | 65C02 | Western Design Center (WDC) W65C02S6TPG-14 |  | [955-W65C02S6TPG-14](https://www.mouser.com/ProductDetail/955-W65C02S6TPG-14) |  | |
| U1 | 1 | Socket | IC socket, 40-pin, 0.6 in | [3M5471-ND](https://www.digikey.com/en/products/filter?keywords=3M5471-ND) | [517-4840-6000-CP](https://www.mouser.com/ProductDetail/517-4840-6000-CP) | | |

Pin headers are cut from strips, and the cart files count whole strips.

### CPU Card Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/CPU%20Card/Rev%201.0/digikey.csv), [mouser.csv](BOM/CPU%20Card/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/CPU%20Card/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/CPU%20Card/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1 | 1 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| J2 | 1 | Conn_01x02 | Pin header 1×2, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| J3 | 1 | EXP | Pin header 2×5, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| R1–R6 | 6 | 10k | YAGEO RC0805FR-0710KL | [311-10.0KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-10.0KCRCT-ND) | [603-RC0805FR-0710KL](https://www.mouser.com/ProductDetail/603-RC0805FR-0710KL) | LCSC [C17414](https://www.lcsc.com/search?q=C17414) | Yes |
| U1 | 1 | 65C02 | Western Design Center (WDC) W65C02S6TPG-14 |  | [955-W65C02S6TPG-14](https://www.mouser.com/ProductDetail/955-W65C02S6TPG-14) |  | |
| U1 | 1 | Socket | IC socket, 40-pin, 0.6 in | [3M5471-ND](https://www.digikey.com/en/products/filter?keywords=3M5471-ND) | [517-4840-6000-CP](https://www.mouser.com/ProductDetail/517-4840-6000-CP) | | |

Pin headers are cut from strips, and the cart files count whole strips.


## Clock Card

### Clock Card Rev 1.1

Drawn, not made yet. **Untested**: the bare card edge only, but Rev 1.0 hasn't been tested yet.

Cart files: [digikey.csv](BOM/Clock%20Card/Rev%201.1/digikey.csv), [mouser.csv](BOM/Clock%20Card/Rev%201.1/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| C1, C3 | 2 | 10uF | Panasonic EEA-GA1C100 | [P14482-ND](https://www.digikey.com/en/products/filter?keywords=P14482-ND) | [667-EEA-GA1C100](https://www.mouser.com/ProductDetail/667-EEA-GA1C100) |  |
| C2, C4, C5 | 3 | 100nF | KYOCERA AVX SR205C104KAR | [478-3187-ND](https://www.digikey.com/en/products/filter?keywords=478-3187-ND) | [581-SR205C104KAR](https://www.mouser.com/ProductDetail/581-SR205C104KAR) |  |
| D1 | 1 | POWER LED | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D2 | 1 | 1N5819 | Vishay 1N5819-E3/54 | [1N5819-E3/54GICT-ND](https://www.digikey.com/en/products/filter?keywords=1N5819-E3%2F54GICT-ND) | [625-1N5819-E3](https://www.mouser.com/ProductDetail/625-1N5819-E3) |  |
| J2 | 1 | 5V DC | Same Sky PJ-102AH | [CP-102AH-ND](https://www.digikey.com/en/products/filter?keywords=CP-102AH-ND) | [490-PJ-102AH](https://www.mouser.com/ProductDetail/490-PJ-102AH) |  |
| J3 | 1 | CLOCK ENBL SW | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  |
| J4 | 1 | RESET SW | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  |
| Q1 | 1 | 2N3904 | onsemi 2N3904BU | [2N3904FS-ND](https://www.digikey.com/en/products/filter?keywords=2N3904FS-ND) | [512-2N3904BU](https://www.mouser.com/ProductDetail/512-2N3904BU) |  |
| R1 | 1 | 330 | YAGEO MFR-12FTF52-330R | [13-MFR-12FTF52-330RCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-330RCT-ND) | [603-MFR-12FTF52-330R](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-330R) |  |
| R2 | 1 | 1M | YAGEO MFR-12FTF52-1M | [13-MFR-12FTF52-1MCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1MCT-ND) | [603-MFR-12FTF52-1M](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1M) |  |
| R3 | 1 | 47k | YAGEO MFR-12FTF52-47K | [13-MFR-12FTF52-47KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-47KCT-ND) | [603-MFR-12FTF52-47K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-47K) |  |
| R4 | 1 | 10k | YAGEO MFR-12FTF52-10K | [13-MFR-12FTF52-10KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-10KCT-ND) | [603-MFR-12FTF52-10K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-10K) |  |
| SW1 | 1 | RESET | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| U1 | 1 | LM555 | Texas Instruments LM555CN/NOPB | [LM555CNNS/NOPB-ND](https://www.digikey.com/en/products/filter?keywords=LM555CNNS%2FNOPB-ND) | [926-LM555CN/NOPB](https://www.mouser.com/ProductDetail/926-LM555CN%2FNOPB) |  |
| X1 | 1 | 1 MHz | ECS Inc. ECS-100AX-010 | [X937-ND](https://www.digikey.com/en/products/filter?keywords=X937-ND) | [520-TCF100-X](https://www.mouser.com/ProductDetail/520-TCF100-X) |  |
| U1 | 1 | Socket | IC socket, 8-pin, 0.3 in | [3M5473-ND](https://www.digikey.com/en/products/filter?keywords=3M5473-ND) | [517-4808-3004-CP](https://www.mouser.com/ProductDetail/517-4808-3004-CP) | |

- **D1:** Green shown. The colour is the builder's choice.
- **J2:** Replaces GCT DCJ200-10-A-K1-K, now obsolete, which older builds used. Its pads and body match this footprint on the datasheet. No board has been built with it yet.

### Clock Card Rev 1.0

Ordered, not tested yet. **Untested**: a new board, ordered and not tested yet.

Cart files: [digikey.csv](BOM/Clock%20Card/Rev%201.0/digikey.csv), [mouser.csv](BOM/Clock%20Card/Rev%201.0/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| C1, C3 | 2 | 10uF | Panasonic EEA-GA1C100 | [P14482-ND](https://www.digikey.com/en/products/filter?keywords=P14482-ND) | [667-EEA-GA1C100](https://www.mouser.com/ProductDetail/667-EEA-GA1C100) |  |
| C2, C4, C5 | 3 | 100nF | KYOCERA AVX SR205C104KAR | [478-3187-ND](https://www.digikey.com/en/products/filter?keywords=478-3187-ND) | [581-SR205C104KAR](https://www.mouser.com/ProductDetail/581-SR205C104KAR) |  |
| D1 | 1 | POWER LED | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D2 | 1 | 1N5819 | Vishay 1N5819-E3/54 | [1N5819-E3/54GICT-ND](https://www.digikey.com/en/products/filter?keywords=1N5819-E3%2F54GICT-ND) | [625-1N5819-E3](https://www.mouser.com/ProductDetail/625-1N5819-E3) |  |
| J2 | 1 | 5V DC | Same Sky PJ-102AH | [CP-102AH-ND](https://www.digikey.com/en/products/filter?keywords=CP-102AH-ND) | [490-PJ-102AH](https://www.mouser.com/ProductDetail/490-PJ-102AH) |  |
| J3 | 1 | CLOCK ENBL SW | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  |
| J4 | 1 | RESET SW | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  |
| Q1 | 1 | 2N3904 | onsemi 2N3904BU | [2N3904FS-ND](https://www.digikey.com/en/products/filter?keywords=2N3904FS-ND) | [512-2N3904BU](https://www.mouser.com/ProductDetail/512-2N3904BU) |  |
| R1 | 1 | 330 | YAGEO MFR-12FTF52-330R | [13-MFR-12FTF52-330RCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-330RCT-ND) | [603-MFR-12FTF52-330R](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-330R) |  |
| R2 | 1 | 1M | YAGEO MFR-12FTF52-1M | [13-MFR-12FTF52-1MCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1MCT-ND) | [603-MFR-12FTF52-1M](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1M) |  |
| R3 | 1 | 47k | YAGEO MFR-12FTF52-47K | [13-MFR-12FTF52-47KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-47KCT-ND) | [603-MFR-12FTF52-47K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-47K) |  |
| R4 | 1 | 10k | YAGEO MFR-12FTF52-10K | [13-MFR-12FTF52-10KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-10KCT-ND) | [603-MFR-12FTF52-10K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-10K) |  |
| SW1 | 1 | RESET | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| U1 | 1 | LM555 | Texas Instruments LM555CN/NOPB | [LM555CNNS/NOPB-ND](https://www.digikey.com/en/products/filter?keywords=LM555CNNS%2FNOPB-ND) | [926-LM555CN/NOPB](https://www.mouser.com/ProductDetail/926-LM555CN%2FNOPB) |  |
| X1 | 1 | 1 MHz | ECS Inc. ECS-100AX-010 | [X937-ND](https://www.digikey.com/en/products/filter?keywords=X937-ND) | [520-TCF100-X](https://www.mouser.com/ProductDetail/520-TCF100-X) |  |
| U1 | 1 | Socket | IC socket, 8-pin, 0.3 in | [3M5473-ND](https://www.digikey.com/en/products/filter?keywords=3M5473-ND) | [517-4808-3004-CP](https://www.mouser.com/ProductDetail/517-4808-3004-CP) | |

- **D1:** Green shown. The colour is the builder's choice.
- **J2:** Replaces GCT DCJ200-10-A-K1-K, now obsolete, which older builds used. Its pads and body match this footprint on the datasheet. No board has been built with it yet.


## Clock Helper

### Clock Helper Rev 1.1

Drawn, not made yet. **Proven design**: mounting holes moved to the standard, silkscreen.

Cart files: [digikey.csv](BOM/Clock%20Helper/Rev%201.1/digikey.csv), [mouser.csv](BOM/Clock%20Helper/Rev%201.1/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| C1 | 1 | 100nF | KYOCERA AVX SR205C104KAR | [478-3187-ND](https://www.digikey.com/en/products/filter?keywords=478-3187-ND) | [581-SR205C104KAR](https://www.mouser.com/ProductDetail/581-SR205C104KAR) |  |
| D1 | 1 | RDY | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D2 | 1 | SYNC | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| J1 | 1 | IO | Pin header 1×5, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  |
| R1–R5 | 5 | 1k | YAGEO MFR-12FTF52-1K | [13-MFR-12FTF52-1KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1KCT-ND) | [603-MFR-12FTF52-1K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1K) |  |
| R6–R8 | 3 | 330 | YAGEO MFR-12FTF52-330R | [13-MFR-12FTF52-330RCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-330RCT-ND) | [603-MFR-12FTF52-330R](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-330R) |  |
| SW1 | 1 | CYCLE/INSTR | XKB Connection XKB5858-Z |  |  | LCSC [C318868](https://www.lcsc.com/search?q=C318868) |
| SW2 | 1 | RUN/STOP | XKB Connection XKB5858-Z |  |  | LCSC [C318868](https://www.lcsc.com/search?q=C318868) |
| SW3 | 1 | STEP | XKB Connection XKB5858-W |  |  | LCSC [C318871](https://www.lcsc.com/search?q=C318871) |
| U1 | 1 | 74HC74 | Texas Instruments SN74HC74N | [296-1602-5-ND](https://www.digikey.com/en/products/filter?keywords=296-1602-5-ND) | [595-SN74HC74N](https://www.mouser.com/ProductDetail/595-SN74HC74N) |  |
| U1 | 1 | Socket | IC socket, 14-pin, 0.3 in | [3M5474-ND](https://www.digikey.com/en/products/filter?keywords=3M5474-ND) | [517-4814-3004-CP](https://www.mouser.com/ProductDetail/517-4814-3004-CP) | |

Pin headers are cut from strips, and the cart files count whole strips.

- **D1, D2:** Green shown. The colour is the builder's choice.
- **SW1, SW2:** Latching. LCSC only.
- **SW3:** Momentary, for STEP. LCSC only.

### Clock Helper Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Clock%20Helper/Rev%201.0/digikey.csv), [mouser.csv](BOM/Clock%20Helper/Rev%201.0/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| C1 | 1 | 100nF | KYOCERA AVX SR205C104KAR | [478-3187-ND](https://www.digikey.com/en/products/filter?keywords=478-3187-ND) | [581-SR205C104KAR](https://www.mouser.com/ProductDetail/581-SR205C104KAR) |  |
| D1 | 1 | RDY | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D2 | 1 | SYNC | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| J1 | 1 | IO | Pin header 1×5, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  |
| R1–R5 | 5 | 1k | YAGEO MFR-12FTF52-1K | [13-MFR-12FTF52-1KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1KCT-ND) | [603-MFR-12FTF52-1K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1K) |  |
| R6–R8 | 3 | 330 | YAGEO MFR-12FTF52-330R | [13-MFR-12FTF52-330RCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-330RCT-ND) | [603-MFR-12FTF52-330R](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-330R) |  |
| SW1 | 1 | CYCLE/INSTR | XKB Connection XKB5858-Z |  |  | LCSC [C318868](https://www.lcsc.com/search?q=C318868) |
| SW2 | 1 | RUN/STOP | XKB Connection XKB5858-Z |  |  | LCSC [C318868](https://www.lcsc.com/search?q=C318868) |
| SW3 | 1 | STEP | XKB Connection XKB5858-W |  |  | LCSC [C318871](https://www.lcsc.com/search?q=C318871) |
| U1 | 1 | 74HC74 | Texas Instruments SN74HC74N | [296-1602-5-ND](https://www.digikey.com/en/products/filter?keywords=296-1602-5-ND) | [595-SN74HC74N](https://www.mouser.com/ProductDetail/595-SN74HC74N) |  |
| U1 | 1 | Socket | IC socket, 14-pin, 0.3 in | [3M5474-ND](https://www.digikey.com/en/products/filter?keywords=3M5474-ND) | [517-4814-3004-CP](https://www.mouser.com/ProductDetail/517-4814-3004-CP) | |

Pin headers are cut from strips, and the cart files count whole strips.

- **D1, D2:** Green shown. The colour is the builder's choice.
- **SW1, SW2:** Latching. LCSC only.
- **SW3:** Momentary, for STEP. LCSC only.


## DB25 Helper

### DB25 Helper Rev 1.1

Drawn, not made yet. **Proven design**: mounting holes moved to the standard, silkscreen.

Cart files: [digikey.csv](BOM/DB25%20Helper/Rev%201.1/digikey.csv), [mouser.csv](BOM/DB25%20Helper/Rev%201.1/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| J1 | 1 | PORT A | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J2 | 1 | PORT B | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J3 | 1 | KEYBOARD | Amphenol D25P33E4GX00LF | [609-1505-ND](https://www.digikey.com/en/products/filter?keywords=609-1505-ND) | [649-D25P33E4GX00LF](https://www.mouser.com/ProductDetail/649-D25P33E4GX00LF) |  |

### DB25 Helper Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/DB25%20Helper/Rev%201.0/digikey.csv), [mouser.csv](BOM/DB25%20Helper/Rev%201.0/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| J1 | 1 | PORT A | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J2 | 1 | PORT B | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J3 | 1 | KEYBOARD | Amphenol D25P33E4GX00LF | [609-1505-ND](https://www.digikey.com/en/products/filter?keywords=609-1505-ND) | [649-D25P33E4GX00LF](https://www.mouser.com/ProductDetail/649-D25P33E4GX00LF) |  |


## GPIO Breadboard Helper

### GPIO Breadboard Helper Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/GPIO%20Breadboard%20Helper/Rev%201.0/digikey.csv), [mouser.csv](BOM/GPIO%20Breadboard%20Helper/Rev%201.0/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| J1 | 1 | PORT A | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J2 | 1 | PORT A | Pin header 1×12, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  |
| J3 | 1 | PORT B | Pin header 1×12, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  |
| J4 | 1 | PORT B | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |

Pin headers are cut from strips, and the cart files count whole strips.


## GPIO Card

### GPIO Card Rev 1.1

Drawn, not made yet. **Proven design**: the bare card edge only.

Cart files: [digikey.csv](BOM/GPIO%20Card/Rev%201.1/digikey.csv), [mouser.csv](BOM/GPIO%20Card/Rev%201.1/mouser.csv), [digikey-through-hole.csv](BOM/GPIO%20Card/Rev%201.1/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/GPIO%20Card/Rev%201.1/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C2 | 2 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  | |
| J2 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| J3 | 1 | PORT A | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND | |
| J4 | 1 | PORT B | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND | |
| U1 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U2 | 1 | 65C22 | Western Design Center (WDC) W65C22N6TPG-14 |  | [955-W65C22N6TPG-14](https://www.mouser.com/ProductDetail/955-W65C22N6TPG-14) |  | |
| U2 | 1 | Socket | IC socket, 40-pin, 0.6 in | [3M5471-ND](https://www.digikey.com/en/products/filter?keywords=3M5471-ND) | [517-4840-6000-CP](https://www.mouser.com/ProductDetail/517-4840-6000-CP) | | |
| J2 | 1 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

- **D1:** A 1N914 also works.

### GPIO Card Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/GPIO%20Card/Rev%201.0/digikey.csv), [mouser.csv](BOM/GPIO%20Card/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/GPIO%20Card/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/GPIO%20Card/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C2 | 2 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  | |
| J2 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| J3 | 1 | PORT A | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND | |
| J4 | 1 | PORT B | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND | |
| U1 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U2 | 1 | 65C22 | Western Design Center (WDC) W65C22N6TPG-14 |  | [955-W65C22N6TPG-14](https://www.mouser.com/ProductDetail/955-W65C22N6TPG-14) |  | |
| U2 | 1 | Socket | IC socket, 40-pin, 0.6 in | [3M5471-ND](https://www.digikey.com/en/products/filter?keywords=3M5471-ND) | [517-4840-6000-CP](https://www.mouser.com/ProductDetail/517-4840-6000-CP) | | |
| J2 | 1 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

- **D1:** A 1N914 also works.


## GPIO Helper

### GPIO Helper Rev 1.1

Drawn, not made yet. **Proven design**: mounting holes moved to the standard, silkscreen.

Cart files: [digikey.csv](BOM/GPIO%20Helper/Rev%201.1/digikey.csv), [mouser.csv](BOM/GPIO%20Helper/Rev%201.1/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| D1 | 1 | PB7 | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D2 | 1 | PB6 | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D3 | 1 | PB5 | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D4 | 1 | PB4 | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D5 | 1 | PB3 | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D6 | 1 | PB2 | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D7 | 1 | PB1 | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D8 | 1 | PB0 | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| J1 | 1 | PORT A | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J2 | 1 | PORT B | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| R1–R8 | 8 | 1K | YAGEO MFR-12FTF52-1K | [13-MFR-12FTF52-1KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1KCT-ND) | [603-MFR-12FTF52-1K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1K) |  |
| R9–R16 | 8 | 330 | YAGEO MFR-12FTF52-330R | [13-MFR-12FTF52-330RCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-330RCT-ND) | [603-MFR-12FTF52-330R](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-330R) |  |
| SW1 | 1 | PA7 | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| SW2 | 1 | PA6 | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| SW3 | 1 | PA5 | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| SW4 | 1 | PA4 | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| SW5 | 1 | PA3 | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| SW6 | 1 | PA2 | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| SW7 | 1 | PA1 | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| SW8 | 1 | PA0 | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |

- **D1–D8:** Green shown. The colour is the builder's choice.

### GPIO Helper Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/GPIO%20Helper/Rev%201.0/digikey.csv), [mouser.csv](BOM/GPIO%20Helper/Rev%201.0/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| D1 | 1 | PB7 | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D2 | 1 | PB6 | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D3 | 1 | PB5 | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D4 | 1 | PB4 | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D5 | 1 | PB3 | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D6 | 1 | PB2 | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D7 | 1 | PB1 | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| D8 | 1 | PB0 | Würth Elektronik 151031VS06000 | [732-5008-ND](https://www.digikey.com/en/products/filter?keywords=732-5008-ND) | [710-151031VS06000](https://www.mouser.com/ProductDetail/710-151031VS06000) |  |
| J1 | 1 | PORT A | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J2 | 1 | PORT B | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| R1–R8 | 8 | 1K | YAGEO MFR-12FTF52-1K | [13-MFR-12FTF52-1KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1KCT-ND) | [603-MFR-12FTF52-1K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1K) |  |
| R9–R16 | 8 | 330 | YAGEO MFR-12FTF52-330R | [13-MFR-12FTF52-330RCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-330RCT-ND) | [603-MFR-12FTF52-330R](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-330R) |  |
| SW1 | 1 | PA7 | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| SW2 | 1 | PA6 | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| SW3 | 1 | PA5 | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| SW4 | 1 | PA4 | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| SW5 | 1 | PA3 | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| SW6 | 1 | PA2 | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| SW7 | 1 | PA1 | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |
| SW8 | 1 | PA0 | Same Sky (Formerly CUI Devices) TS02-66-50-BK-160-LCR-D | [2223-TS02-66-50-BK-160-LCR-D-ND](https://www.digikey.com/en/products/filter?keywords=2223-TS02-66-50-BK-160-LCR-D-ND) | [179-TS026650BK160LCR](https://www.mouser.com/ProductDetail/179-TS026650BK160LCR) |  |

- **D1–D8:** Green shown. The colour is the builder's choice.


## Joystick Helper

### Joystick Helper Rev 1.1

Drawn, not made yet. **Proven design**: mounting holes moved to the standard, silkscreen.

Cart files: [digikey.csv](BOM/Joystick%20Helper/Rev%201.1/digikey.csv), [mouser.csv](BOM/Joystick%20Helper/Rev%201.1/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| J1 | 1 | PORT | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J2 | 1 | JOYSTICK | Amphenol D09P33E4GX00LF | [609-1481-ND](https://www.digikey.com/en/products/filter?keywords=609-1481-ND) | [649-D09P33E4GX00LF](https://www.mouser.com/ProductDetail/649-D09P33E4GX00LF) |  |
| R1–R8 | 8 | 1K | YAGEO MFR-12FTF52-1K | [13-MFR-12FTF52-1KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1KCT-ND) | [603-MFR-12FTF52-1K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1K) |  |

### Joystick Helper Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Joystick%20Helper/Rev%201.0/digikey.csv), [mouser.csv](BOM/Joystick%20Helper/Rev%201.0/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| J1 | 1 | PORT | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J2 | 1 | DB9 MALE | Amphenol D09P33E4GX00LF | [609-1481-ND](https://www.digikey.com/en/products/filter?keywords=609-1481-ND) | [649-D09P33E4GX00LF](https://www.mouser.com/ProductDetail/649-D09P33E4GX00LF) |  |
| R1–R8 | 8 | 1K | YAGEO MFR-12FTF52-1K | [13-MFR-12FTF52-1KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1KCT-ND) | [603-MFR-12FTF52-1K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1K) |  |


## Keyboard Encoder Helper

### Keyboard Encoder Helper Rev 1.1

Drawn, not made yet. **Proven design**: mounting holes, silkscreen.

Cart files: [digikey.csv](BOM/Keyboard%20Encoder%20Helper/Rev%201.1/digikey.csv), [mouser.csv](BOM/Keyboard%20Encoder%20Helper/Rev%201.1/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| C1, C4 | 2 | 100nF | KYOCERA AVX SR205C104KAR | [478-3187-ND](https://www.digikey.com/en/products/filter?keywords=478-3187-ND) | [581-SR205C104KAR](https://www.mouser.com/ProductDetail/581-SR205C104KAR) |  |
| C2, C3 | 2 | 20pF | KYOCERA AVX SR151A200JAR | [478-7724-ND](https://www.digikey.com/en/products/filter?keywords=478-7724-ND) | [581-SR151A200JAR](https://www.mouser.com/ProductDetail/581-SR151A200JAR) |  |
| J1 | 1 | PORT B | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J2 | 1 | PORT A | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J3 | 1 | PS/2 KEYBOARD | Kycon, Inc. KMDGX-6S-BS | [2092-KMDGX-6S-BS-ND](https://www.digikey.com/en/products/filter?keywords=2092-KMDGX-6S-BS-ND) | [806-KMDGX-6S-BS](https://www.mouser.com/ProductDetail/806-KMDGX-6S-BS) |  |
| J4 | 1 | KEYBOARD | Amphenol D25P33E4GX00LF | [609-1505-ND](https://www.digikey.com/en/products/filter?keywords=609-1505-ND) | [649-D25P33E4GX00LF](https://www.mouser.com/ProductDetail/649-D25P33E4GX00LF) |  |
| R1 | 1 | 1K | YAGEO MFR-12FTF52-1K | [13-MFR-12FTF52-1KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1KCT-ND) | [603-MFR-12FTF52-1K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1K) |  |
| U1 | 1 | ATmega1284 | Microchip Technology ATMEGA1284-PU | [ATMEGA1284-PU-ND](https://www.digikey.com/en/products/filter?keywords=ATMEGA1284-PU-ND) | [556-ATMEGA1284-PU](https://www.mouser.com/ProductDetail/556-ATMEGA1284-PU) |  |
| Y1 | 1 | 16 MHz | ECS Inc. ECS-160-20-4X | [X1103-ND](https://www.digikey.com/en/products/filter?keywords=X1103-ND) | [520-HCU1600-20X](https://www.mouser.com/ProductDetail/520-HCU1600-20X) |  |
| U1 | 1 | Socket | IC socket, 40-pin, 0.6 in | [3M5471-ND](https://www.digikey.com/en/products/filter?keywords=3M5471-ND) | [517-4840-6000-CP](https://www.mouser.com/ProductDetail/517-4840-6000-CP) | |

- **C2, C3:** 16 MHz crystal capacitors: fit 20 pF. Made boards whose silk says 22 pF keep it; a board built with 22 pF is fine. Mouser has none in stock today.

### Keyboard Encoder Helper Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Keyboard%20Encoder%20Helper/Rev%201.0/digikey.csv), [mouser.csv](BOM/Keyboard%20Encoder%20Helper/Rev%201.0/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| C1, C4 | 2 | 100nF | KYOCERA AVX SR205C104KAR | [478-3187-ND](https://www.digikey.com/en/products/filter?keywords=478-3187-ND) | [581-SR205C104KAR](https://www.mouser.com/ProductDetail/581-SR205C104KAR) |  |
| C2, C3 | 2 | 22pF | KYOCERA AVX SR151A200JAR | [478-7724-ND](https://www.digikey.com/en/products/filter?keywords=478-7724-ND) | [581-SR151A200JAR](https://www.mouser.com/ProductDetail/581-SR151A200JAR) |  |
| J1 | 1 | PORT B | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J2 | 1 | PORT A | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J3 | 1 | PS/2 KEYBOARD | Kycon, Inc. KMDGX-6S-BS | [2092-KMDGX-6S-BS-ND](https://www.digikey.com/en/products/filter?keywords=2092-KMDGX-6S-BS-ND) | [806-KMDGX-6S-BS](https://www.mouser.com/ProductDetail/806-KMDGX-6S-BS) |  |
| J4 | 1 | KEYBOARD | Amphenol D25P33E4GX00LF | [609-1505-ND](https://www.digikey.com/en/products/filter?keywords=609-1505-ND) | [649-D25P33E4GX00LF](https://www.mouser.com/ProductDetail/649-D25P33E4GX00LF) |  |
| R1 | 1 | 1K | YAGEO MFR-12FTF52-1K | [13-MFR-12FTF52-1KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1KCT-ND) | [603-MFR-12FTF52-1K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1K) |  |
| U1 | 1 | ATmega1284-P | Microchip Technology ATMEGA1284-PU | [ATMEGA1284-PU-ND](https://www.digikey.com/en/products/filter?keywords=ATMEGA1284-PU-ND) | [556-ATMEGA1284-PU](https://www.mouser.com/ProductDetail/556-ATMEGA1284-PU) |  |
| Y1 | 1 | 16 MHz | ECS Inc. ECS-160-20-4X | [X1103-ND](https://www.digikey.com/en/products/filter?keywords=X1103-ND) | [520-HCU1600-20X](https://www.mouser.com/ProductDetail/520-HCU1600-20X) |  |
| U1 | 1 | Socket | IC socket, 40-pin, 0.6 in | [3M5471-ND](https://www.digikey.com/en/products/filter?keywords=3M5471-ND) | [517-4840-6000-CP](https://www.mouser.com/ProductDetail/517-4840-6000-CP) | |

- **C2, C3:** 16 MHz crystal capacitors: fit 20 pF. Made boards whose silk says 22 pF keep it; a board built with 22 pF is fine. Mouser has none in stock today.


## Keyboard Helper

### Keyboard Helper Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Keyboard%20Helper/Rev%201.0/digikey.csv), [mouser.csv](BOM/Keyboard%20Helper/Rev%201.0/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| J1 | 1 | JOYSTICK A | Amphenol D09P33E4GX00LF | [609-1481-ND](https://www.digikey.com/en/products/filter?keywords=609-1481-ND) | [649-D09P33E4GX00LF](https://www.mouser.com/ProductDetail/649-D09P33E4GX00LF) |  |
| J2 | 1 | JOYSTICK B | Amphenol D09P33E4GX00LF | [609-1481-ND](https://www.digikey.com/en/products/filter?keywords=609-1481-ND) | [649-D09P33E4GX00LF](https://www.mouser.com/ProductDetail/649-D09P33E4GX00LF) |  |
| J3 | 1 | JOYSTICK A | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J4 | 1 | JOYSTICK B | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J5 | 1 | PORT A | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J6 | 1 | PORT B | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J7 | 1 | KEYBOARD | Amphenol D25P33E4GX00LF | [609-1505-ND](https://www.digikey.com/en/products/filter?keywords=609-1505-ND) | [649-D25P33E4GX00LF](https://www.mouser.com/ProductDetail/649-D25P33E4GX00LF) |  |
| R1–R16 | 16 | 1K | YAGEO MFR-12FTF52-1K | [13-MFR-12FTF52-1KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1KCT-ND) | [603-MFR-12FTF52-1K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1K) |  |
| SW1–SW67 | 67 | Keyswitch | Cherry Americas LLC MX2A-E1NA | [1644-MX2A-E1NA-ND](https://www.digikey.com/en/products/filter?keywords=1644-MX2A-E1NA-ND) | [540-MX2A-E1NA](https://www.mouser.com/ProductDetail/540-MX2A-E1NA) |  |

- **SW1–SW67:** Cherry MX2A RGB Blue, clear housing, as on the owner's Amazon kit. MX1A-E1NN (black housing) is the deeper-stocked alternative; Digi-Key CH196-ND, Mouser 540-MX1A-E1NN.


## LCD Board

### LCD Board Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/LCD%20Board/Rev%201.0/digikey.csv), [mouser.csv](BOM/LCD%20Board/Rev%201.0/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| C1–C4 | 4 | 100nF | KYOCERA AVX SR205C104KAR | [478-3187-ND](https://www.digikey.com/en/products/filter?keywords=478-3187-ND) | [581-SR205C104KAR](https://www.mouser.com/ProductDetail/581-SR205C104KAR) |  |
| D1, D2 | 2 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  |
| J1 | 1 | 6502 Bus | Würth Elektronik 61204021621 | [732-5401-ND](https://www.digikey.com/en/products/filter?keywords=732-5401-ND) | [710-61204021621](https://www.mouser.com/ProductDetail/710-61204021621) |  |
| J2 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  |
| J3 | 1 | HVSYNC | Pin header 1×1, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  |
| R1 | 1 | 10k | YAGEO MFR-12FTF52-10K | [13-MFR-12FTF52-10KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-10KCT-ND) | [603-MFR-12FTF52-10K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-10K) |  |
| U1 | 1 | 65C22 | Western Design Center (WDC) W65C22N6TPG-14 |  | [955-W65C22N6TPG-14](https://www.mouser.com/ProductDetail/955-W65C22N6TPG-14) |  |
| U2 | 1 | Adafruit 2.8 TFT LCD | Adafruit 2.8 TFT LCD, Adafruit 2.8 TFT LCD |  |  | [Adafruit](https://www.adafruit.com/product/1770) |
| U3 | 1 | 74HC138 | Texas Instruments SN74HC138N | [296-1575-5-ND](https://www.digikey.com/en/products/filter?keywords=296-1575-5-ND) | [595-SN74HC138N](https://www.mouser.com/ProductDetail/595-SN74HC138N) |  |
| U3 | 1 | Socket | IC socket, 16-pin, 0.3 in | [3M5475-ND](https://www.digikey.com/en/products/filter?keywords=3M5475-ND) | [517-4816-3004-CP](https://www.mouser.com/ProductDetail/517-4816-3004-CP) | |
| U1 | 1 | Socket | IC socket, 40-pin, 0.6 in | [3M5471-ND](https://www.digikey.com/en/products/filter?keywords=3M5471-ND) | [517-4840-6000-CP](https://www.mouser.com/ProductDetail/517-4840-6000-CP) | |
| J2 | 1 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  |

Pin headers are cut from strips, and the cart files count whole strips.

- **D1, D2:** A 1N914 also works.
- **J1:** Male box header with a keying notch, for a 40-way ribbon cable.


## LCD Card

### LCD Card Rev 1.1

Drawn, not made yet. **Proven design**: the bare card edge only.

Cart files: [digikey.csv](BOM/LCD%20Card/Rev%201.1/digikey.csv), [mouser.csv](BOM/LCD%20Card/Rev%201.1/mouser.csv), [digikey-through-hole.csv](BOM/LCD%20Card/Rev%201.1/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/LCD%20Card/Rev%201.1/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C2 | 2 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  | |
| J2 | 1 | GPIO | Adam Tech PH1RB-07-UA | [2057-PH1RB-07-UA-ND](https://www.digikey.com/en/products/filter?keywords=2057-PH1RB-07-UA-ND) | [737-PH1RB-07-UA](https://www.mouser.com/ProductDetail/737-PH1RB-07-UA) |  | |
| J3 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| U1 | 1 | 65C22 | Western Design Center (WDC) W65C22N6TPG-14 |  | [955-W65C22N6TPG-14](https://www.mouser.com/ProductDetail/955-W65C22N6TPG-14) |  | |
| U2 | 1 | LCD-16X2 | LCD-16X2, LCD-16X2 |  |  | [Amazon](https://www.amazon.com/dp/B0DSFXK7QK) | |
| U3 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| VR1 | 1 | 10k | Bourns Inc. 3386F-1-103LF | [3386F-103LF-ND](https://www.digikey.com/en/products/filter?keywords=3386F-103LF-ND) | [652-3386F-1-103LF](https://www.mouser.com/ProductDetail/652-3386F-1-103LF) |  | |
| U1 | 1 | Socket | IC socket, 40-pin, 0.6 in | [3M5471-ND](https://www.digikey.com/en/products/filter?keywords=3M5471-ND) | [517-4840-6000-CP](https://www.mouser.com/ProductDetail/517-4840-6000-CP) | | |
| J3 | 1 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

**Do not fit** R1: parallel with VR1 to make ~10 k.

- **D1:** A 1N914 also works.
- **U2:** Common hobby 16×2 LCD; any HD44780-compatible module with the same pinout.

### LCD Card Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/LCD%20Card/Rev%201.0/digikey.csv), [mouser.csv](BOM/LCD%20Card/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/LCD%20Card/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/LCD%20Card/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C2 | 2 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  | |
| J2 | 1 | GPIO | Adam Tech PH1RB-07-UA | [2057-PH1RB-07-UA-ND](https://www.digikey.com/en/products/filter?keywords=2057-PH1RB-07-UA-ND) | [737-PH1RB-07-UA](https://www.mouser.com/ProductDetail/737-PH1RB-07-UA) |  | |
| J3 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| U1 | 1 | 65C22 | Western Design Center (WDC) W65C22N6TPG-14 |  | [955-W65C22N6TPG-14](https://www.mouser.com/ProductDetail/955-W65C22N6TPG-14) |  | |
| U2 | 1 | LCD-16X2 | LCD-16X2, LCD-16X2 |  |  | [Amazon](https://www.amazon.com/dp/B0DSFXK7QK) | |
| U3 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| VR1 | 1 | 10k | Bourns Inc. 3386F-1-103LF | [3386F-103LF-ND](https://www.digikey.com/en/products/filter?keywords=3386F-103LF-ND) | [652-3386F-1-103LF](https://www.mouser.com/ProductDetail/652-3386F-1-103LF) |  | |
| U1 | 1 | Socket | IC socket, 40-pin, 0.6 in | [3M5471-ND](https://www.digikey.com/en/products/filter?keywords=3M5471-ND) | [517-4840-6000-CP](https://www.mouser.com/ProductDetail/517-4840-6000-CP) | | |
| J3 | 1 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

**Do not fit** R1: parallel with VR1 to make ~10 k.

- **D1:** A 1N914 also works.
- **U2:** Common hobby 16×2 LCD; any HD44780-compatible module with the same pinout.
- **U3:** Fit a 74HC138: AC6502 logic is HC, not LS.


## Mega Helper

### Mega Helper Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Mega%20Helper/Rev%201.0/digikey.csv), [mouser.csv](BOM/Mega%20Helper/Rev%201.0/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| A1 | 1 | Arduino Mega2560 R3 Shield | Arduino A000067 | [1050-1018-ND](https://www.digikey.com/en/products/filter?keywords=1050-1018-ND) | [782-A000067](https://www.mouser.com/ProductDetail/782-A000067) |  |
| J1 | 1 | 6502 BUS | Würth Elektronik 61204021621 | [732-5401-ND](https://www.digikey.com/en/products/filter?keywords=732-5401-ND) | [710-61204021621](https://www.mouser.com/ProductDetail/710-61204021621) |  |

- **J1:** Male box header with a keying notch, for a 40-way ribbon cable.


## Memory Card

### Memory Card Rev 1.1

Drawn, not made yet. **Proven design**: the bare card edge only.

Cart files: [digikey.csv](BOM/Memory%20Card/Rev%201.1/digikey.csv), [mouser.csv](BOM/Memory%20Card/Rev%201.1/mouser.csv), [digikey-through-hole.csv](BOM/Memory%20Card/Rev%201.1/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Memory%20Card/Rev%201.1/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1–C5 | 5 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| J2 | 1 | Conn_02x02_Odd_Even | Pin header 2×2, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| J3 | 1 | Conn_02x01 | Pin header 1×2, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| R1, R2 | 2 | 1k | YAGEO RC0805FR-071KL | [311-1.00KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-1.00KCRCT-ND) | [603-RC0805FR-071KL](https://www.mouser.com/ProductDetail/603-RC0805FR-071KL) | LCSC [C17513](https://www.lcsc.com/search?q=C17513) | Yes |
| U1, U2, U5 | 3 | 74HC00 | Nexperia USA Inc. 74HC00D,653 | [1727-2773-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2773-1-ND) | [771-74HC00D-T](https://www.mouser.com/ProductDetail/771-74HC00D-T) | LCSC [C5586](https://www.lcsc.com/search?q=C5586) | Yes |
| U3 | 1 | AS6C62256 | Alliance Memory AS6C62256-55PCN | [1450-1033-ND](https://www.digikey.com/en/products/filter?keywords=1450-1033-ND) | [913-AS6C62256-55PCN](https://www.mouser.com/ProductDetail/913-AS6C62256-55PCN) |  | |
| U4 | 1 | AT28C256 | Microchip Technology AT28C256-15PU | [AT28C256-15PU-ND](https://www.digikey.com/en/products/filter?keywords=AT28C256-15PU-ND) | [556-AT28C25615PU](https://www.mouser.com/ProductDetail/556-AT28C25615PU) |  | |
| U3, U4 | 2 | Socket | IC socket, 28-pin, 0.6 in | [3M5481-ND](https://www.digikey.com/en/products/filter?keywords=3M5481-ND) | [517-4828-6004-CP](https://www.mouser.com/ProductDetail/517-4828-6004-CP) | | |

Pin headers are cut from strips, and the cart files count whole strips.

### Memory Card Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Memory%20Card/Rev%201.0/digikey.csv), [mouser.csv](BOM/Memory%20Card/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/Memory%20Card/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Memory%20Card/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1–C5 | 5 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| J2 | 1 | Conn_02x02_Odd_Even | Pin header 2×2, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| J3 | 1 | Conn_02x01 | Pin header 1×2, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| R1, R2 | 2 | 1k | YAGEO RC0805FR-071KL | [311-1.00KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-1.00KCRCT-ND) | [603-RC0805FR-071KL](https://www.mouser.com/ProductDetail/603-RC0805FR-071KL) | LCSC [C17513](https://www.lcsc.com/search?q=C17513) | Yes |
| U1, U2, U5 | 3 | 74HC00 | Nexperia USA Inc. 74HC00D,653 | [1727-2773-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2773-1-ND) | [771-74HC00D-T](https://www.mouser.com/ProductDetail/771-74HC00D-T) | LCSC [C5586](https://www.lcsc.com/search?q=C5586) | Yes |
| U3 | 1 | AS6C62256 | Alliance Memory AS6C62256-55PCN | [1450-1033-ND](https://www.digikey.com/en/products/filter?keywords=1450-1033-ND) | [913-AS6C62256-55PCN](https://www.mouser.com/ProductDetail/913-AS6C62256-55PCN) |  | |
| U4 | 1 | AT28C256 | Microchip Technology AT28C256-15PU | [AT28C256-15PU-ND](https://www.digikey.com/en/products/filter?keywords=AT28C256-15PU-ND) | [556-AT28C25615PU](https://www.mouser.com/ProductDetail/556-AT28C25615PU) |  | |
| U3, U4 | 2 | Socket | IC socket, 28-pin, 0.6 in | [3M5481-ND](https://www.digikey.com/en/products/filter?keywords=3M5481-ND) | [517-4828-6004-CP](https://www.mouser.com/ProductDetail/517-4828-6004-CP) | | |

Pin headers are cut from strips, and the cart files count whole strips.


## PS2 Helper

### PS2 Helper Rev 1.1

Drawn, not made yet. **Proven design**: resistors moved and tracks rerouted, mounting holes, silkscreen.

Cart files: [digikey.csv](BOM/PS2%20Helper/Rev%201.1/digikey.csv), [mouser.csv](BOM/PS2%20Helper/Rev%201.1/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| C1–C3 | 3 | 100nF | KYOCERA AVX SR205C104KAR | [478-3187-ND](https://www.digikey.com/en/products/filter?keywords=478-3187-ND) | [581-SR205C104KAR](https://www.mouser.com/ProductDetail/581-SR205C104KAR) |  |
| C4, C5 | 2 | 20pF | KYOCERA AVX SR151A200JAR | [478-7724-ND](https://www.digikey.com/en/products/filter?keywords=478-7724-ND) | [581-SR151A200JAR](https://www.mouser.com/ProductDetail/581-SR151A200JAR) |  |
| J1 | 1 | PORT A | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J2 | 1 | PORT B | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J3 | 1 | PS/2 | Kycon, Inc. KMDGX-6S-BS | [2092-KMDGX-6S-BS-ND](https://www.digikey.com/en/products/filter?keywords=2092-KMDGX-6S-BS-ND) | [806-KMDGX-6S-BS](https://www.mouser.com/ProductDetail/806-KMDGX-6S-BS) |  |
| J4 | 1 | JOYSTICK | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| R1 | 1 | 1K | YAGEO MFR-12FTF52-1K | [13-MFR-12FTF52-1KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1KCT-ND) | [603-MFR-12FTF52-1K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1K) |  |
| R2–R9 | 8 | 1k | YAGEO MFR-12FTF52-1K | [13-MFR-12FTF52-1KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1KCT-ND) | [603-MFR-12FTF52-1K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1K) |  |
| U1 | 1 | MT8808 | Microchip (was Mitel, Zarlink) MT8808AE1 |  |  | eBay |
| U2 | 1 | ATmega328 | Microchip Technology ATMEGA328P-PU | [ATMEGA328P-PU-ND](https://www.digikey.com/en/products/filter?keywords=ATMEGA328P-PU-ND) | [556-ATMEGA328P-PU](https://www.mouser.com/ProductDetail/556-ATMEGA328P-PU) |  |
| Y1 | 1 | 16 MHz | ECS Inc. ECS-160-20-4X | [X1103-ND](https://www.digikey.com/en/products/filter?keywords=X1103-ND) | [520-HCU1600-20X](https://www.mouser.com/ProductDetail/520-HCU1600-20X) |  |
| U2 | 1 | Socket | IC socket, 28-pin, 0.3 in | [3M5480-ND](https://www.digikey.com/en/products/filter?keywords=3M5480-ND) | [517-4828-3004-CP](https://www.mouser.com/ProductDetail/517-4828-3004-CP) | |
| U1 | 1 | Socket | IC socket, 28-pin, 0.6 in | [3M5481-ND](https://www.digikey.com/en/products/filter?keywords=3M5481-ND) | [517-4828-6004-CP](https://www.mouser.com/ProductDetail/517-4828-6004-CP) | |

- **C4, C5:** 16 MHz crystal capacitors: fit 20 pF. Made boards whose silk says 22 pF keep it; a board built with 22 pF is fine. Mouser has none in stock today.
- **U1:** Out of production; eBay is the likely source. Prefer the Keyboard Encoder Helper to the PS2 Helper, which needs this chip. The DIP-28 only: MT8808AP1 is PLCC and does not fit.

### PS2 Helper Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/PS2%20Helper/Rev%201.0/digikey.csv), [mouser.csv](BOM/PS2%20Helper/Rev%201.0/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| C1–C3 | 3 | 100nF | KYOCERA AVX SR205C104KAR | [478-3187-ND](https://www.digikey.com/en/products/filter?keywords=478-3187-ND) | [581-SR205C104KAR](https://www.mouser.com/ProductDetail/581-SR205C104KAR) |  |
| C4, C5 | 2 | 22pF | KYOCERA AVX SR151A200JAR | [478-7724-ND](https://www.digikey.com/en/products/filter?keywords=478-7724-ND) | [581-SR151A200JAR](https://www.mouser.com/ProductDetail/581-SR151A200JAR) |  |
| J1 | 1 | PORT A | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J2 | 1 | PORT B | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| J3 | 1 | PS/2 | Kycon, Inc. KMDGX-6S-BS | [2092-KMDGX-6S-BS-ND](https://www.digikey.com/en/products/filter?keywords=2092-KMDGX-6S-BS-ND) | [806-KMDGX-6S-BS](https://www.mouser.com/ProductDetail/806-KMDGX-6S-BS) |  |
| J4 | 1 | JOYSTICK | Adam Tech BHR-12-VUA | [2057-BHR-12-VUA-ND](https://www.digikey.com/en/products/filter?keywords=2057-BHR-12-VUA-ND) | [737-BHR-12-VUA](https://www.mouser.com/ProductDetail/737-BHR-12-VUA) | 2057-BHR-12-VUA-ND |
| R1, R8 | 2 | 1K | YAGEO MFR-12FTF52-1K | [13-MFR-12FTF52-1KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1KCT-ND) | [603-MFR-12FTF52-1K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1K) |  |
| R2–R7, R9 | 7 | 1k | YAGEO MFR-12FTF52-1K | [13-MFR-12FTF52-1KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1KCT-ND) | [603-MFR-12FTF52-1K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1K) |  |
| U1 | 1 | MT8808 | Microchip (was Mitel, Zarlink) MT8808AE1 |  |  | eBay |
| U2 | 1 | ATmega328 | Microchip Technology ATMEGA328P-PU | [ATMEGA328P-PU-ND](https://www.digikey.com/en/products/filter?keywords=ATMEGA328P-PU-ND) | [556-ATMEGA328P-PU](https://www.mouser.com/ProductDetail/556-ATMEGA328P-PU) |  |
| Y1 | 1 | 16 MHz | ECS Inc. ECS-160-20-4X | [X1103-ND](https://www.digikey.com/en/products/filter?keywords=X1103-ND) | [520-HCU1600-20X](https://www.mouser.com/ProductDetail/520-HCU1600-20X) |  |
| U2 | 1 | Socket | IC socket, 28-pin, 0.3 in | [3M5480-ND](https://www.digikey.com/en/products/filter?keywords=3M5480-ND) | [517-4828-3004-CP](https://www.mouser.com/ProductDetail/517-4828-3004-CP) | |
| U1 | 1 | Socket | IC socket, 28-pin, 0.6 in | [3M5481-ND](https://www.digikey.com/en/products/filter?keywords=3M5481-ND) | [517-4828-6004-CP](https://www.mouser.com/ProductDetail/517-4828-6004-CP) | |

- **C4, C5:** 16 MHz crystal capacitors: fit 20 pF. Made boards whose silk says 22 pF keep it; a board built with 22 pF is fine. Mouser has none in stock today.
- **U1:** Out of production; eBay is the likely source. Prefer the Keyboard Encoder Helper to the PS2 Helper, which needs this chip. The DIP-28 only: MT8808AP1 is PLCC and does not fit.


## Prototype Card

### Prototype Card Rev 1.1

Drawn, not made yet. **Proven design**: the bare card edge only.

Cart files: [digikey.csv](BOM/Prototype%20Card/Rev%201.1/digikey.csv), [mouser.csv](BOM/Prototype%20Card/Rev%201.1/mouser.csv), [digikey-through-hole.csv](BOM/Prototype%20Card/Rev%201.1/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Prototype%20Card/Rev%201.1/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| B1, B2 | 2 | BREADBOARDMINI | SparkFun PRT-12047 |  | [474-PRT-12047](https://www.mouser.com/ProductDetail/474-PRT-12047) | [SparkFun](https://www.sparkfun.com/products/12047) | |
| C1–C3 | 3 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| J2 | 1 | 6502 Bus | Sullins PPPC202LFBN-RC | [S7123-ND](https://www.digikey.com/en/products/filter?keywords=S7123-ND) |  |  | |
| J3 | 1 | Conn_02x04_Odd_Even | Pin header 2×4, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| U1 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |

Pin headers are cut from strips, and the cart files count whole strips.

### Prototype Card Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Prototype%20Card/Rev%201.0/digikey.csv), [mouser.csv](BOM/Prototype%20Card/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/Prototype%20Card/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Prototype%20Card/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| B1, B2 | 2 | BREADBOARDMINI | SparkFun PRT-12047 |  | [474-PRT-12047](https://www.mouser.com/ProductDetail/474-PRT-12047) | [SparkFun](https://www.sparkfun.com/products/12047) | |
| C1–C3 | 3 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| J2 | 1 | 6502 Bus | Sullins PPPC202LFBN-RC | [S7123-ND](https://www.digikey.com/en/products/filter?keywords=S7123-ND) |  |  | |
| J3 | 1 | Conn_02x04_Odd_Even | Pin header 2×4, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| U1 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |

Pin headers are cut from strips, and the cart files count whole strips.


## RAM Card

### RAM Card Rev 1.1

Drawn, not made yet. **Proven design**: the bare card edge only, so far: it keeps Rev 1.0's one bank latch, which the build notes describe.

Cart files: [digikey.csv](BOM/RAM%20Card/Rev%201.1/digikey.csv), [mouser.csv](BOM/RAM%20Card/Rev%201.1/mouser.csv), [digikey-through-hole.csv](BOM/RAM%20Card/Rev%201.1/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/RAM%20Card/Rev%201.1/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1–C7 | 7 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| J2 | 1 | LATCH EN | Pin header 1×2, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| J3 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| J4 | 1 | BANK ADDR | Pin header 2×5, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| R1, R2 | 2 | 10k | YAGEO RC0805FR-0710KL | [311-10.0KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-10.0KCRCT-ND) | [603-RC0805FR-0710KL](https://www.mouser.com/ProductDetail/603-RC0805FR-0710KL) | LCSC [C17414](https://www.lcsc.com/search?q=C17414) | Yes |
| U1 | 1 | AS6C4008 | Alliance Memory AS6C4008-55PCN | [1450-1027-ND](https://www.digikey.com/en/products/filter?keywords=1450-1027-ND) | [913-AS6C4008-55PCN](https://www.mouser.com/ProductDetail/913-AS6C4008-55PCN) |  | |
| U2 | 1 | 74HC573 | Nexperia USA Inc. 74HC573D,653 | [1727-2818-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2818-1-ND) | [771-74HC573D-T](https://www.mouser.com/ProductDetail/771-74HC573D-T) | LCSC [C5608](https://www.lcsc.com/search?q=C5608) | Yes |
| U3, U6 | 2 | 74HC00 | Nexperia USA Inc. 74HC00D,653 | [1727-2773-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2773-1-ND) | [771-74HC00D-T](https://www.mouser.com/ProductDetail/771-74HC00D-T) | LCSC [C5586](https://www.lcsc.com/search?q=C5586) | Yes |
| U4 | 1 | 74HC21 | Texas Instruments SN74HC21DR | [296-14842-1-ND](https://www.digikey.com/en/products/filter?keywords=296-14842-1-ND) | [595-SN74HC21DR](https://www.mouser.com/ProductDetail/595-SN74HC21DR) | LCSC [C75398](https://www.lcsc.com/search?q=C75398) | Yes |
| U5 | 1 | 74HC30 | Nexperia USA Inc. 74HC30D,653 | [1727-3066-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-3066-1-ND) | [771-74HC30D-T](https://www.mouser.com/ProductDetail/771-74HC30D-T) | LCSC [C19818870](https://www.lcsc.com/search?q=C19818870) | Yes |
| U7 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U1 | 1 | Socket | IC socket, 32-pin, 0.6 in | [3M5470-ND](https://www.digikey.com/en/products/filter?keywords=3M5470-ND) | [517-4832-6000-CP](https://www.mouser.com/ProductDetail/517-4832-6000-CP) | | |
| J3 | 2 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

### RAM Card Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/RAM%20Card/Rev%201.0/digikey.csv), [mouser.csv](BOM/RAM%20Card/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/RAM%20Card/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/RAM%20Card/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1–C7 | 7 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| J2 | 1 | LATCH EN | Pin header 1×2, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| J3 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| J4 | 1 | BANK ADDR | Pin header 2×5, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| R1, R2 | 2 | 10k | YAGEO RC0805FR-0710KL | [311-10.0KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-10.0KCRCT-ND) | [603-RC0805FR-0710KL](https://www.mouser.com/ProductDetail/603-RC0805FR-0710KL) | LCSC [C17414](https://www.lcsc.com/search?q=C17414) | Yes |
| U1 | 1 | AS6C4008 | Alliance Memory AS6C4008-55PCN | [1450-1027-ND](https://www.digikey.com/en/products/filter?keywords=1450-1027-ND) | [913-AS6C4008-55PCN](https://www.mouser.com/ProductDetail/913-AS6C4008-55PCN) |  | |
| U2 | 1 | 74HC573 | Nexperia USA Inc. 74HC573D,653 | [1727-2818-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2818-1-ND) | [771-74HC573D-T](https://www.mouser.com/ProductDetail/771-74HC573D-T) | LCSC [C5608](https://www.lcsc.com/search?q=C5608) | Yes |
| U3, U6 | 2 | 74HC00 | Nexperia USA Inc. 74HC00D,653 | [1727-2773-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2773-1-ND) | [771-74HC00D-T](https://www.mouser.com/ProductDetail/771-74HC00D-T) | LCSC [C5586](https://www.lcsc.com/search?q=C5586) | Yes |
| U4 | 1 | 74HC21 | Texas Instruments SN74HC21DR | [296-14842-1-ND](https://www.digikey.com/en/products/filter?keywords=296-14842-1-ND) | [595-SN74HC21DR](https://www.mouser.com/ProductDetail/595-SN74HC21DR) | LCSC [C75398](https://www.lcsc.com/search?q=C75398) | Yes |
| U5 | 1 | 74HC30 | Nexperia USA Inc. 74HC30D,653 | [1727-3066-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-3066-1-ND) | [771-74HC30D-T](https://www.mouser.com/ProductDetail/771-74HC30D-T) | LCSC [C19818870](https://www.lcsc.com/search?q=C19818870) | Yes |
| U7 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U1 | 1 | Socket | IC socket, 32-pin, 0.6 in | [3M5470-ND](https://www.digikey.com/en/products/filter?keywords=3M5470-ND) | [517-4832-6000-CP](https://www.mouser.com/ProductDetail/517-4832-6000-CP) | | |
| J3 | 2 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.


## RTC Card

### RTC Card Rev 1.1

Drawn, not made yet. **Proven design**: the bare card edge only.

Cart files: [digikey.csv](BOM/RTC%20Card/Rev%201.1/digikey.csv), [mouser.csv](BOM/RTC%20Card/Rev%201.1/mouser.csv), [digikey-through-hole.csv](BOM/RTC%20Card/Rev%201.1/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/RTC%20Card/Rev%201.1/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| BT1 | 1 | CR2032 | TE Connectivity Linx BAT-HLD-001-THM-TR | [343-BAT-HLD-001-THM-TRCT-ND](https://www.digikey.com/en/products/filter?keywords=343-BAT-HLD-001-THM-TRCT-ND) |  |  | |
| C1–C3 | 3 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  | |
| J2 | 1 | AUX | Pin header 1×6, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| J3 | 1 | INT Select | Pin header 1×3, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| J4 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| R1 | 1 | 1k | YAGEO RC0805FR-071KL | [311-1.00KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-1.00KCRCT-ND) | [603-RC0805FR-071KL](https://www.mouser.com/ProductDetail/603-RC0805FR-071KL) | LCSC [C17513](https://www.lcsc.com/search?q=C17513) | Yes |
| U1 | 1 | DS1511Y | Maxim DS1511Y+ | [DS1511Y+-ND](https://www.digikey.com/en/products/filter?keywords=DS1511Y%2B-ND) | [700-DS1511Y](https://www.mouser.com/ProductDetail/700-DS1511Y) |  | |
| U2, U3 | 2 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U1 | 1 | Socket | IC socket, 28-pin, 0.6 in | [3M5481-ND](https://www.digikey.com/en/products/filter?keywords=3M5481-ND) | [517-4828-6004-CP](https://www.mouser.com/ProductDetail/517-4828-6004-CP) | | |
| J3, J4 | 2 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

- **BT1:** Retainer for a CR2032 cell. BAT-HLD-001-THM, on the tested boards, is obsolete; this is its listed continuation. Digi-Key has none in stock today.
- **D1:** A 1N914 also works.

### RTC Card Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/RTC%20Card/Rev%201.0/digikey.csv), [mouser.csv](BOM/RTC%20Card/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/RTC%20Card/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/RTC%20Card/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| BT1 | 1 | CR2032 | TE Connectivity Linx BAT-HLD-001-THM-TR | [343-BAT-HLD-001-THM-TRCT-ND](https://www.digikey.com/en/products/filter?keywords=343-BAT-HLD-001-THM-TRCT-ND) |  |  | |
| C1–C3 | 3 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  | |
| J2 | 1 | AUX | Pin header 1×6, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| J3 | 1 | INT Select | Pin header 1×3, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| J4 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| R1 | 1 | 1k | YAGEO RC0805FR-071KL | [311-1.00KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-1.00KCRCT-ND) | [603-RC0805FR-071KL](https://www.mouser.com/ProductDetail/603-RC0805FR-071KL) | LCSC [C17513](https://www.lcsc.com/search?q=C17513) | Yes |
| U1 | 1 | DS1511Y | Maxim DS1511Y+ | [DS1511Y+-ND](https://www.digikey.com/en/products/filter?keywords=DS1511Y%2B-ND) | [700-DS1511Y](https://www.mouser.com/ProductDetail/700-DS1511Y) |  | |
| U2, U3 | 2 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U1 | 1 | Socket | IC socket, 28-pin, 0.6 in | [3M5481-ND](https://www.digikey.com/en/products/filter?keywords=3M5481-ND) | [517-4828-6004-CP](https://www.mouser.com/ProductDetail/517-4828-6004-CP) | | |
| J3, J4 | 2 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

- **BT1:** Retainer for a CR2032 cell. BAT-HLD-001-THM, on the tested boards, is obsolete; this is its listed continuation. Digi-Key has none in stock today.
- **D1:** A 1N914 also works.


## Serial Card Pro

### Serial Card Pro Rev 1.1

Drawn, not made yet. **Proven design**: the DB-9 moved to KiCad's standard footprint (the same connector), tracks rerouted, silkscreen, the bare card edge.

Cart files: [digikey.csv](BOM/Serial%20Card%20Pro/Rev%201.1/digikey.csv), [mouser.csv](BOM/Serial%20Card%20Pro/Rev%201.1/mouser.csv), [digikey-through-hole.csv](BOM/Serial%20Card%20Pro/Rev%201.1/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Serial%20Card%20Pro/Rev%201.1/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C2, C11, C13 | 4 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| C3–C10 | 8 | 1uF | YAGEO CC0805KKX7R8BB105 | [311-1456-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1456-1-ND) | [603-CC805KKX7R8BB105](https://www.mouser.com/ProductDetail/603-CC805KKX7R8BB105) | LCSC [C28323](https://www.lcsc.com/search?q=C28323) | Yes |
| C12 | 1 | 22pF | Samsung Electro-Mechanics CL21C220JBANNNC | [1276-1047-1-ND](https://www.digikey.com/en/products/filter?keywords=1276-1047-1-ND) | [187-CL21C220JBANNNC](https://www.mouser.com/ProductDetail/187-CL21C220JBANNNC) | LCSC [C1804](https://www.lcsc.com/search?q=C1804) | Yes |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  | |
| J2 | 1 | SERIAL (DTE) | Amphenol D09P33E4GX00LF | [609-1481-ND](https://www.digikey.com/en/products/filter?keywords=609-1481-ND) | [649-D09P33E4GX00LF](https://www.mouser.com/ProductDetail/649-D09P33E4GX00LF) |  | |
| J3 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| J4 | 1 | DCD Select | Pin header 1×3, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| R1 | 1 | 1M | YAGEO RC0805FR-071ML | [311-1.00MCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-1.00MCRCT-ND) | [603-RC0805FR-071ML](https://www.mouser.com/ProductDetail/603-RC0805FR-071ML) | LCSC [C17514](https://www.lcsc.com/search?q=C17514) | Yes |
| U1, U2 | 2 | MAX232 | Texas Instruments MAX232IDR | [296-26141-1-ND](https://www.digikey.com/en/products/filter?keywords=296-26141-1-ND) | [595-MAX232IDR](https://www.mouser.com/ProductDetail/595-MAX232IDR) | LCSC [C59824](https://www.lcsc.com/search?q=C59824) | Yes |
| U3 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U4 | 1 | R6551AP | Rockwell R6551AP |  |  | [Jameco 43318](https://www.jameco.com/z/R6551AP-Rockwell-IC-6551-Asynchronous-Communication-Interface-Adapter-DIP-28-pin_43318.html) | |
| Y1 | 1 | 1.8432 MHz | Abracon LLC AB-1.8432MHZ-B2 | [535-9009-ND](https://www.digikey.com/en/products/filter?keywords=535-9009-ND) | [815-AB-1.8432-B2](https://www.mouser.com/ProductDetail/815-AB-1.8432-B2) |  | |
| U4 | 1 | Socket | IC socket, 28-pin, 0.6 in | [3M5481-ND](https://www.digikey.com/en/products/filter?keywords=3M5481-ND) | [517-4828-6004-CP](https://www.mouser.com/ProductDetail/517-4828-6004-CP) | | |
| J3, J4 | 2 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

- **D1:** A 1N914 also works.
- **U4:** Rockwell R6551AP, out of production. Do not substitute a W65C51.

### Serial Card Pro Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Serial%20Card%20Pro/Rev%201.0/digikey.csv), [mouser.csv](BOM/Serial%20Card%20Pro/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/Serial%20Card%20Pro/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Serial%20Card%20Pro/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C2, C11, C13 | 4 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| C3–C10 | 8 | 1uF | YAGEO CC0805KKX7R8BB105 | [311-1456-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1456-1-ND) | [603-CC805KKX7R8BB105](https://www.mouser.com/ProductDetail/603-CC805KKX7R8BB105) | LCSC [C28323](https://www.lcsc.com/search?q=C28323) | Yes |
| C12 | 1 | 22pF | Samsung Electro-Mechanics CL21C220JBANNNC | [1276-1047-1-ND](https://www.digikey.com/en/products/filter?keywords=1276-1047-1-ND) | [187-CL21C220JBANNNC](https://www.mouser.com/ProductDetail/187-CL21C220JBANNNC) | LCSC [C1804](https://www.lcsc.com/search?q=C1804) | Yes |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  | |
| J2 | 1 | DB9 Male (DTE) | Amphenol D09P33E4GX00LF | [609-1481-ND](https://www.digikey.com/en/products/filter?keywords=609-1481-ND) | [649-D09P33E4GX00LF](https://www.mouser.com/ProductDetail/649-D09P33E4GX00LF) |  | |
| J3 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| J4 | 1 | DCD Select | Pin header 1×3, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| R1 | 1 | 1M | YAGEO RC0805FR-071ML | [311-1.00MCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-1.00MCRCT-ND) | [603-RC0805FR-071ML](https://www.mouser.com/ProductDetail/603-RC0805FR-071ML) | LCSC [C17514](https://www.lcsc.com/search?q=C17514) | Yes |
| U1, U2 | 2 | MAX232 | Texas Instruments MAX232IDR | [296-26141-1-ND](https://www.digikey.com/en/products/filter?keywords=296-26141-1-ND) | [595-MAX232IDR](https://www.mouser.com/ProductDetail/595-MAX232IDR) | LCSC [C59824](https://www.lcsc.com/search?q=C59824) | Yes |
| U3 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U4 | 1 | 6551 | Rockwell R6551AP |  |  | [Jameco 43318](https://www.jameco.com/z/R6551AP-Rockwell-IC-6551-Asynchronous-Communication-Interface-Adapter-DIP-28-pin_43318.html) | |
| Y1 | 1 | 1.8432 MHz | Abracon LLC AB-1.8432MHZ-B2 | [535-9009-ND](https://www.digikey.com/en/products/filter?keywords=535-9009-ND) | [815-AB-1.8432-B2](https://www.mouser.com/ProductDetail/815-AB-1.8432-B2) |  | |
| U4 | 1 | Socket | IC socket, 28-pin, 0.6 in | [3M5481-ND](https://www.digikey.com/en/products/filter?keywords=3M5481-ND) | [517-4828-6004-CP](https://www.mouser.com/ProductDetail/517-4828-6004-CP) | | |
| J3, J4 | 2 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

- **D1:** A 1N914 also works.
- **U4:** Rockwell R6551AP, out of production. Do not substitute a W65C51.


## Serial Card

### Serial Card Rev 1.1

Drawn, not made yet. **Proven design**: silkscreen text and the bare card edge.

Cart files: [digikey.csv](BOM/Serial%20Card/Rev%201.1/digikey.csv), [mouser.csv](BOM/Serial%20Card/Rev%201.1/mouser.csv), [digikey-through-hole.csv](BOM/Serial%20Card/Rev%201.1/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Serial%20Card/Rev%201.1/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C6, C8 | 3 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| C2–C5 | 4 | 1uF | YAGEO CC0805KKX7R8BB105 | [311-1456-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1456-1-ND) | [603-CC805KKX7R8BB105](https://www.mouser.com/ProductDetail/603-CC805KKX7R8BB105) | LCSC [C28323](https://www.lcsc.com/search?q=C28323) | Yes |
| C7 | 1 | 22pF | Samsung Electro-Mechanics CL21C220JBANNNC | [1276-1047-1-ND](https://www.digikey.com/en/products/filter?keywords=1276-1047-1-ND) | [187-CL21C220JBANNNC](https://www.mouser.com/ProductDetail/187-CL21C220JBANNNC) | LCSC [C1804](https://www.lcsc.com/search?q=C1804) | Yes |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  | |
| J2 | 1 | SERIAL (DCE) | Amphenol D09S33E4GX00LF | [609-1487-ND](https://www.digikey.com/en/products/filter?keywords=609-1487-ND) | [649-D09S33E4GX00LF](https://www.mouser.com/ProductDetail/649-D09S33E4GX00LF) |  | |
| J3 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| J4 | 1 | CTS EN | Pin header 1×3, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| R1 | 1 | 1M | YAGEO RC0805FR-071ML | [311-1.00MCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-1.00MCRCT-ND) | [603-RC0805FR-071ML](https://www.mouser.com/ProductDetail/603-RC0805FR-071ML) | LCSC [C17514](https://www.lcsc.com/search?q=C17514) | Yes |
| U1 | 1 | MAX232 | Texas Instruments MAX232IDR | [296-26141-1-ND](https://www.digikey.com/en/products/filter?keywords=296-26141-1-ND) | [595-MAX232IDR](https://www.mouser.com/ProductDetail/595-MAX232IDR) | LCSC [C59824](https://www.lcsc.com/search?q=C59824) | Yes |
| U2 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U3 | 1 | R6551AP | Rockwell R6551AP |  |  | [Jameco 43318](https://www.jameco.com/z/R6551AP-Rockwell-IC-6551-Asynchronous-Communication-Interface-Adapter-DIP-28-pin_43318.html) | |
| Y1 | 1 | 1.8432 MHz | Abracon LLC AB-1.8432MHZ-B2 | [535-9009-ND](https://www.digikey.com/en/products/filter?keywords=535-9009-ND) | [815-AB-1.8432-B2](https://www.mouser.com/ProductDetail/815-AB-1.8432-B2) |  | |
| U3 | 1 | Socket | IC socket, 28-pin, 0.6 in | [3M5481-ND](https://www.digikey.com/en/products/filter?keywords=3M5481-ND) | [517-4828-6004-CP](https://www.mouser.com/ProductDetail/517-4828-6004-CP) | | |
| J3, J4 | 2 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

- **D1:** A 1N914 also works.
- **U3:** Rockwell R6551AP, out of production. Do not substitute a W65C51.

### Serial Card Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Serial%20Card/Rev%201.0/digikey.csv), [mouser.csv](BOM/Serial%20Card/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/Serial%20Card/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Serial%20Card/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C6, C8 | 3 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| C2–C5 | 4 | 1uF | YAGEO CC0805KKX7R8BB105 | [311-1456-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1456-1-ND) | [603-CC805KKX7R8BB105](https://www.mouser.com/ProductDetail/603-CC805KKX7R8BB105) | LCSC [C28323](https://www.lcsc.com/search?q=C28323) | Yes |
| C7 | 1 | 22pF | Samsung Electro-Mechanics CL21C220JBANNNC | [1276-1047-1-ND](https://www.digikey.com/en/products/filter?keywords=1276-1047-1-ND) | [187-CL21C220JBANNNC](https://www.mouser.com/ProductDetail/187-CL21C220JBANNNC) | LCSC [C1804](https://www.lcsc.com/search?q=C1804) | Yes |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  | |
| J2 | 1 | DB9 FEMALE (DCE) | Amphenol D09S33E4GX00LF | [609-1487-ND](https://www.digikey.com/en/products/filter?keywords=609-1487-ND) | [649-D09S33E4GX00LF](https://www.mouser.com/ProductDetail/649-D09S33E4GX00LF) |  | |
| J3 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| J4 | 1 | CTS EN | Pin header 1×3, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| R1 | 1 | 1M | YAGEO RC0805FR-071ML | [311-1.00MCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-1.00MCRCT-ND) | [603-RC0805FR-071ML](https://www.mouser.com/ProductDetail/603-RC0805FR-071ML) | LCSC [C17514](https://www.lcsc.com/search?q=C17514) | Yes |
| U1 | 1 | MAX232 | Texas Instruments MAX232IDR | [296-26141-1-ND](https://www.digikey.com/en/products/filter?keywords=296-26141-1-ND) | [595-MAX232IDR](https://www.mouser.com/ProductDetail/595-MAX232IDR) | LCSC [C59824](https://www.lcsc.com/search?q=C59824) | Yes |
| U2 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U3 | 1 | 6551 | Rockwell R6551AP |  |  | [Jameco 43318](https://www.jameco.com/z/R6551AP-Rockwell-IC-6551-Asynchronous-Communication-Interface-Adapter-DIP-28-pin_43318.html) | |
| Y1 | 1 | 1.8432 MHz | Abracon LLC AB-1.8432MHZ-B2 | [535-9009-ND](https://www.digikey.com/en/products/filter?keywords=535-9009-ND) | [815-AB-1.8432-B2](https://www.mouser.com/ProductDetail/815-AB-1.8432-B2) |  | |
| U3 | 1 | Socket | IC socket, 28-pin, 0.6 in | [3M5481-ND](https://www.digikey.com/en/products/filter?keywords=3M5481-ND) | [517-4828-6004-CP](https://www.mouser.com/ProductDetail/517-4828-6004-CP) | | |
| J3, J4 | 2 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

- **D1:** A 1N914 also works.
- **U3:** Rockwell R6551AP, out of production. Do not substitute a W65C51.


## Sound Card

### Sound Card Rev 1.1

Drawn, not made yet. **Proven design**: silkscreen text and the bare card edge.

Cart files: [digikey.csv](BOM/Sound%20Card/Rev%201.1/digikey.csv), [mouser.csv](BOM/Sound%20Card/Rev%201.1/mouser.csv), [digikey-through-hole.csv](BOM/Sound%20Card/Rev%201.1/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Sound%20Card/Rev%201.1/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C2 | 2 | 2.2nF | Samsung Electro-Mechanics CL21C222JBFNNNE | [1276-2993-1-ND](https://www.digikey.com/en/products/filter?keywords=1276-2993-1-ND) | [187-CL21C222JBFNNNE](https://www.mouser.com/ProductDetail/187-CL21C222JBFNNNE) | LCSC [C28260](https://www.lcsc.com/search?q=C28260) | Yes |
| C3, C5 | 2 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| C4 | 1 | 1uF | YAGEO CC0805KKX7R8BB105 | [311-1456-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1456-1-ND) | [603-CC805KKX7R8BB105](https://www.mouser.com/ProductDetail/603-CC805KKX7R8BB105) | LCSC [C28323](https://www.lcsc.com/search?q=C28323) | Yes |
| J2 | 1 | SID VDD | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  | |
| J3 | 1 | AUDIO | Switchcraft Inc. PJRAN1X1U02X | [PJRAN1X1U02X-ND](https://www.digikey.com/en/products/filter?keywords=PJRAN1X1U02X-ND) | [502-PJRAN1X1U02X](https://www.mouser.com/ProductDetail/502-PJRAN1X1U02X) |  | |
| J5 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| R1 | 1 | 1k | YAGEO RC0805FR-071KL | [311-1.00KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-1.00KCRCT-ND) | [603-RC0805FR-071KL](https://www.mouser.com/ProductDetail/603-RC0805FR-071KL) | LCSC [C17513](https://www.lcsc.com/search?q=C17513) | Yes |
| U1 | 1 | ARMSID | Retrocomp ARMSID |  |  | [Retrocomp](https://retrocomp.cz/produkt?id=2) | |
| U2 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U1 | 1 | Socket | IC socket, 28-pin, 0.6 in | [3M5481-ND](https://www.digikey.com/en/products/filter?keywords=3M5481-ND) | [517-4828-6004-CP](https://www.mouser.com/ProductDetail/517-4828-6004-CP) | | |
| J5 | 1 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

- **U1:** A modern replacement for the MOS 6581 SID, which is out of production. Every tested build uses one. A real 6581 also needs 12 V at pin 28, which the standard build does not provide.

### Sound Card Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Sound%20Card/Rev%201.0/digikey.csv), [mouser.csv](BOM/Sound%20Card/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/Sound%20Card/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Sound%20Card/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C2 | 2 | 2.2nF | Samsung Electro-Mechanics CL21C222JBFNNNE | [1276-2993-1-ND](https://www.digikey.com/en/products/filter?keywords=1276-2993-1-ND) | [187-CL21C222JBFNNNE](https://www.mouser.com/ProductDetail/187-CL21C222JBFNNNE) | LCSC [C28260](https://www.lcsc.com/search?q=C28260) | Yes |
| C3, C5 | 2 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| C4 | 1 | 1uF | YAGEO CC0805KKX7R8BB105 | [311-1456-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1456-1-ND) | [603-CC805KKX7R8BB105](https://www.mouser.com/ProductDetail/603-CC805KKX7R8BB105) | LCSC [C28323](https://www.lcsc.com/search?q=C28323) | Yes |
| J2 | 1 | VDD | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  | |
| J3 | 1 | AUDIO | Switchcraft Inc. PJRAN1X1U02X | [PJRAN1X1U02X-ND](https://www.digikey.com/en/products/filter?keywords=PJRAN1X1U02X-ND) | [502-PJRAN1X1U02X](https://www.mouser.com/ProductDetail/502-PJRAN1X1U02X) |  | |
| J5 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| R1 | 1 | 1k | YAGEO RC0805FR-071KL | [311-1.00KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-1.00KCRCT-ND) | [603-RC0805FR-071KL](https://www.mouser.com/ProductDetail/603-RC0805FR-071KL) | LCSC [C17513](https://www.lcsc.com/search?q=C17513) | Yes |
| U1 | 1 | 6581 | Retrocomp ARMSID |  |  | [Retrocomp](https://retrocomp.cz/produkt?id=2) | |
| U2 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U1 | 1 | Socket | IC socket, 28-pin, 0.6 in | [3M5481-ND](https://www.digikey.com/en/products/filter?keywords=3M5481-ND) | [517-4828-6004-CP](https://www.mouser.com/ProductDetail/517-4828-6004-CP) | | |
| J5 | 1 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

- **U1:** A modern replacement for the MOS 6581 SID, which is out of production. Every tested build uses one. A real 6581 also needs 12 V at pin 28, which the standard build does not provide.


## Storage Card Pro

### Storage Card Pro Rev 1.1

Drawn, not made yet. **Untested**: silkscreen text and the bare card edge, but Rev 1.0 hasn't been tested.

Cart files: [digikey.csv](BOM/Storage%20Card%20Pro/Rev%201.1/digikey.csv), [mouser.csv](BOM/Storage%20Card%20Pro/Rev%201.1/mouser.csv), [digikey-through-hole.csv](BOM/Storage%20Card%20Pro/Rev%201.1/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Storage%20Card%20Pro/Rev%201.1/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1–C4, C7, C8 | 6 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| C5, C6 | 2 | 20pF | KYOCERA AVX SR151A200JAR | [478-7724-ND](https://www.digikey.com/en/products/filter?keywords=478-7724-ND) | [581-SR151A200JAR](https://www.mouser.com/ProductDetail/581-SR151A200JAR) |  | |
| C9, C10 | 2 | 1uF | YAGEO CC0805KKX7R8BB105 | [311-1456-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1456-1-ND) | [603-CC805KKX7R8BB105](https://www.mouser.com/ProductDetail/603-CC805KKX7R8BB105) | LCSC [C28323](https://www.lcsc.com/search?q=C28323) | Yes |
| D1 | 1 | ACT | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| J1 | 1 | ACT LED | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  | |
| J3 | 1 | SPI | Adam Tech PH1RB-06-UA | [2057-PH1RB-06-UA-ND](https://www.digikey.com/en/products/filter?keywords=2057-PH1RB-06-UA-ND) | [737-PH1RB-06-UA](https://www.mouser.com/ProductDetail/737-PH1RB-06-UA) |  | |
| J4 | 1 | SD CARD | Amphenol 10067847-001RLF | [609-3956-1-ND](https://www.digikey.com/en/products/filter?keywords=609-3956-1-ND) | [649-10067847-001RLF](https://www.mouser.com/ProductDetail/649-10067847-001RLF) | LCSC [C569097](https://www.lcsc.com/search?q=C569097) | Yes |
| J5 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| R1, R2 | 2 | 330 | YAGEO RC0805FR-07330RL | [311-330CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-330CRCT-ND) | [603-RC0805FR-07330RL](https://www.mouser.com/ProductDetail/603-RC0805FR-07330RL) | LCSC [C17630](https://www.lcsc.com/search?q=C17630) | Yes |
| R3, R4 | 2 | 1k | YAGEO RC0805FR-071KL | [311-1.00KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-1.00KCRCT-ND) | [603-RC0805FR-071KL](https://www.mouser.com/ProductDetail/603-RC0805FR-071KL) | LCSC [C17513](https://www.lcsc.com/search?q=C17513) | Yes |
| U1 | 1 | TXS0108EPW | Texas Instruments TXS0108EPWR | [296-23011-1-ND](https://www.digikey.com/en/products/filter?keywords=296-23011-1-ND) | [595-TXS0108EPWR](https://www.mouser.com/ProductDetail/595-TXS0108EPWR) | LCSC [C17206](https://www.lcsc.com/search?q=C17206) | Yes |
| U2 | 1 | ATmega328 | Microchip Technology ATMEGA328P-PU | [ATMEGA328P-PU-ND](https://www.digikey.com/en/products/filter?keywords=ATMEGA328P-PU-ND) | [556-ATMEGA328P-PU](https://www.mouser.com/ProductDetail/556-ATMEGA328P-PU) |  | |
| U3 | 1 | W25Q128JVS | Winbond Electronics W25Q128JVSIQ | [W25Q128JVSIQ-ND](https://www.digikey.com/en/products/filter?keywords=W25Q128JVSIQ-ND) | [454-W25Q128JVSIQ](https://www.mouser.com/ProductDetail/454-W25Q128JVSIQ) | LCSC [C97521](https://www.lcsc.com/search?q=C97521) | Yes |
| U4 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U5 | 1 | LP2985-3.3 | Texas Instruments LP2985-33DBVR | [296-18476-1-ND](https://www.digikey.com/en/products/filter?keywords=296-18476-1-ND) | [595-LP2985-33DBVR](https://www.mouser.com/ProductDetail/595-LP2985-33DBVR) | LCSC [C95414](https://www.lcsc.com/search?q=C95414) | Yes |
| Y1 | 1 | 16 MHz | ECS Inc. ECS-160-20-4X | [X1103-ND](https://www.digikey.com/en/products/filter?keywords=X1103-ND) | [520-HCU1600-20X](https://www.mouser.com/ProductDetail/520-HCU1600-20X) |  | |
| U2 | 1 | Socket | IC socket, 28-pin, 0.3 in | [3M5480-ND](https://www.digikey.com/en/products/filter?keywords=3M5480-ND) | [517-4828-3004-CP](https://www.mouser.com/ProductDetail/517-4828-3004-CP) | | |
| J5 | 1 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

### Storage Card Pro Rev 1.0

Made, not tested yet. **Untested**: made, and not tested yet: the BIOS has no driver for it.

Cart files: [digikey.csv](BOM/Storage%20Card%20Pro/Rev%201.0/digikey.csv), [mouser.csv](BOM/Storage%20Card%20Pro/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/Storage%20Card%20Pro/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Storage%20Card%20Pro/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1–C4, C7, C8 | 6 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| C5, C6 | 2 | 22pF | KYOCERA AVX SR151A200JAR | [478-7724-ND](https://www.digikey.com/en/products/filter?keywords=478-7724-ND) | [581-SR151A200JAR](https://www.mouser.com/ProductDetail/581-SR151A200JAR) |  | |
| C9, C10 | 2 | 1uF | YAGEO CC0805KKX7R8BB105 | [311-1456-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1456-1-ND) | [603-CC805KKX7R8BB105](https://www.mouser.com/ProductDetail/603-CC805KKX7R8BB105) | LCSC [C28323](https://www.lcsc.com/search?q=C28323) | Yes |
| D1 | 1 | ACT | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| J1 | 1 | ACT LED | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  | |
| J3 | 1 | SPI | Adam Tech PH1RB-06-UA | [2057-PH1RB-06-UA-ND](https://www.digikey.com/en/products/filter?keywords=2057-PH1RB-06-UA-ND) | [737-PH1RB-06-UA](https://www.mouser.com/ProductDetail/737-PH1RB-06-UA) |  | |
| J4 | 1 | SD CARD | Amphenol 10067847-001RLF | [609-3956-1-ND](https://www.digikey.com/en/products/filter?keywords=609-3956-1-ND) | [649-10067847-001RLF](https://www.mouser.com/ProductDetail/649-10067847-001RLF) | LCSC [C569097](https://www.lcsc.com/search?q=C569097) | Yes |
| J5 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| R1, R2 | 2 | 330 | YAGEO RC0805FR-07330RL | [311-330CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-330CRCT-ND) | [603-RC0805FR-07330RL](https://www.mouser.com/ProductDetail/603-RC0805FR-07330RL) | LCSC [C17630](https://www.lcsc.com/search?q=C17630) | Yes |
| R3, R4 | 2 | 1k | YAGEO RC0805FR-071KL | [311-1.00KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-1.00KCRCT-ND) | [603-RC0805FR-071KL](https://www.mouser.com/ProductDetail/603-RC0805FR-071KL) | LCSC [C17513](https://www.lcsc.com/search?q=C17513) | Yes |
| U1 | 1 | TXS0108EPW | Texas Instruments TXS0108EPWR | [296-23011-1-ND](https://www.digikey.com/en/products/filter?keywords=296-23011-1-ND) | [595-TXS0108EPWR](https://www.mouser.com/ProductDetail/595-TXS0108EPWR) | LCSC [C17206](https://www.lcsc.com/search?q=C17206) | Yes |
| U2 | 1 | ATmega328 | Microchip Technology ATMEGA328P-PU | [ATMEGA328P-PU-ND](https://www.digikey.com/en/products/filter?keywords=ATMEGA328P-PU-ND) | [556-ATMEGA328P-PU](https://www.mouser.com/ProductDetail/556-ATMEGA328P-PU) |  | |
| U3 | 1 | W25Q128JVS | Winbond Electronics W25Q128JVSIQ | [W25Q128JVSIQ-ND](https://www.digikey.com/en/products/filter?keywords=W25Q128JVSIQ-ND) | [454-W25Q128JVSIQ](https://www.mouser.com/ProductDetail/454-W25Q128JVSIQ) | LCSC [C97521](https://www.lcsc.com/search?q=C97521) | Yes |
| U4 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U5 | 1 | LP2985-3.3 | Texas Instruments LP2985-33DBVR | [296-18476-1-ND](https://www.digikey.com/en/products/filter?keywords=296-18476-1-ND) | [595-LP2985-33DBVR](https://www.mouser.com/ProductDetail/595-LP2985-33DBVR) | LCSC [C95414](https://www.lcsc.com/search?q=C95414) | Yes |
| Y1 | 1 | 16 MHz | ECS Inc. ECS-160-20-4X | [X1103-ND](https://www.digikey.com/en/products/filter?keywords=X1103-ND) | [520-HCU1600-20X](https://www.mouser.com/ProductDetail/520-HCU1600-20X) |  | |
| U2 | 1 | Socket | IC socket, 28-pin, 0.3 in | [3M5480-ND](https://www.digikey.com/en/products/filter?keywords=3M5480-ND) | [517-4828-3004-CP](https://www.mouser.com/ProductDetail/517-4828-3004-CP) | | |
| J5 | 1 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

- **C5, C6:** 16 MHz crystal capacitors: fit 20 pF. Made boards whose silk says 22 pF keep it; a board built with 22 pF is fine. Mouser has none in stock today.


## Storage Card

### Storage Card Rev 1.1

Drawn, not made yet. **Proven design**: the bare card edge only.

Cart files: [digikey.csv](BOM/Storage%20Card/Rev%201.1/digikey.csv), [mouser.csv](BOM/Storage%20Card/Rev%201.1/mouser.csv), [digikey-through-hole.csv](BOM/Storage%20Card/Rev%201.1/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Storage%20Card/Rev%201.1/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C2 | 2 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| D1 | 1 | ACT | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| J2 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| J3 | 1 | Compact Flash | CFH-L3C1LBL01MN0 |  |  | LCSC [C444350](https://www.lcsc.com/search?q=C444350) | Yes |
| J4 | 1 | ACT LED | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  | |
| R1–R4 | 4 | 1k | YAGEO RC0805FR-071KL | [311-1.00KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-1.00KCRCT-ND) | [603-RC0805FR-071KL](https://www.mouser.com/ProductDetail/603-RC0805FR-071KL) | LCSC [C17513](https://www.lcsc.com/search?q=C17513) | Yes |
| R5, R6 | 2 | 330 | YAGEO RC0805FR-07330RL | [311-330CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-330CRCT-ND) | [603-RC0805FR-07330RL](https://www.mouser.com/ProductDetail/603-RC0805FR-07330RL) | LCSC [C17630](https://www.lcsc.com/search?q=C17630) | Yes |
| U1 | 1 | 74HC00 | Nexperia USA Inc. 74HC00D,653 | [1727-2773-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2773-1-ND) | [771-74HC00D-T](https://www.mouser.com/ProductDetail/771-74HC00D-T) | LCSC [C5586](https://www.lcsc.com/search?q=C5586) | Yes |
| U2 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| J2 | 1 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

### Storage Card Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Storage%20Card/Rev%201.0/digikey.csv), [mouser.csv](BOM/Storage%20Card/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/Storage%20Card/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Storage%20Card/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C2 | 2 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| D1 | 1 | ACT | Lite-On Inc. LTST-C170KGKT | [160-1414-1-ND](https://www.digikey.com/en/products/filter?keywords=160-1414-1-ND) | [859-LTST-C170KGKT](https://www.mouser.com/ProductDetail/859-LTST-C170KGKT) | LCSC [C2297](https://www.lcsc.com/search?q=C2297) | Yes |
| J2 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| J3 | 1 | Compact Flash | CFH-L3C1LBL01MN0 |  |  | LCSC [C444350](https://www.lcsc.com/search?q=C444350) | Yes |
| J4 | 1 | ACT LED | JST Sales America Inc. B2B-XH-A | [455-B2B-XH-A-ND](https://www.digikey.com/en/products/filter?keywords=455-B2B-XH-A-ND) |  |  | |
| R1–R4 | 4 | 1k | YAGEO RC0805FR-071KL | [311-1.00KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-1.00KCRCT-ND) | [603-RC0805FR-071KL](https://www.mouser.com/ProductDetail/603-RC0805FR-071KL) | LCSC [C17513](https://www.lcsc.com/search?q=C17513) | Yes |
| R5, R6 | 2 | 330 | YAGEO RC0805FR-07330RL | [311-330CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-330CRCT-ND) | [603-RC0805FR-07330RL](https://www.mouser.com/ProductDetail/603-RC0805FR-07330RL) | LCSC [C17630](https://www.lcsc.com/search?q=C17630) | Yes |
| U1 | 1 | 74HC00 | Nexperia USA Inc. 74HC00D,653 | [1727-2773-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2773-1-ND) | [771-74HC00D-T](https://www.mouser.com/ProductDetail/771-74HC00D-T) | LCSC [C5586](https://www.lcsc.com/search?q=C5586) | Yes |
| U2 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| J2 | 1 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.


## VERA Helper

### VERA Helper Rev 1.1

Drawn, not made yet. **Proven design**: mounting holes, capacitor pitch, JP2 ships open.

Cart files: [digikey.csv](BOM/VERA%20Helper/Rev%201.1/digikey.csv), [mouser.csv](BOM/VERA%20Helper/Rev%201.1/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| C1, C2 | 2 | 100nF | KYOCERA AVX SR205C104KAR | [478-3187-ND](https://www.digikey.com/en/products/filter?keywords=478-3187-ND) | [581-SR205C104KAR](https://www.mouser.com/ProductDetail/581-SR205C104KAR) |  |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  |
| J1 | 1 | 6502 Bus | Würth Elektronik 61204021621 | [732-5401-ND](https://www.digikey.com/en/products/filter?keywords=732-5401-ND) | [710-61204021621](https://www.mouser.com/ProductDetail/710-61204021621) |  |
| J2 | 1 | VERA Module | Pin header 2×12, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  |
| J3 | 1 | Audio L | Switchcraft Inc. PJRAN1X1U02X | [PJRAN1X1U02X-ND](https://www.digikey.com/en/products/filter?keywords=PJRAN1X1U02X-ND) | [502-PJRAN1X1U02X](https://www.mouser.com/ProductDetail/502-PJRAN1X1U02X) |  |
| J4 | 1 | Audio R | Switchcraft Inc. PJRAN1X1U03X | [PJRAN1X1U03X-ND](https://www.digikey.com/en/products/filter?keywords=PJRAN1X1U03X-ND) | [502-PJRAN1X1U03X](https://www.mouser.com/ProductDetail/502-PJRAN1X1U03X) |  |
| J5 | 1 | INT Select | Pin header 1×3, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  |
| J6 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  |
| U1, U2 | 2 | 74HC138 | Texas Instruments SN74HC138N | [296-1575-5-ND](https://www.digikey.com/en/products/filter?keywords=296-1575-5-ND) | [595-SN74HC138N](https://www.mouser.com/ProductDetail/595-SN74HC138N) |  |
| U1, U2 | 2 | Socket | IC socket, 16-pin, 0.3 in | [3M5475-ND](https://www.digikey.com/en/products/filter?keywords=3M5475-ND) | [517-4816-3004-CP](https://www.mouser.com/ProductDetail/517-4816-3004-CP) | |
| J5, J6 | 2 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  |

Pin headers are cut from strips, and the cart files count whole strips.

- **D1:** A 1N914 also works.
- **J1:** Male box header with a keying notch, for a 40-way ribbon cable.

### VERA Helper Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/VERA%20Helper/Rev%201.0/digikey.csv), [mouser.csv](BOM/VERA%20Helper/Rev%201.0/mouser.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other |
|---|---|---|---|---|---|---|
| C1, C2 | 2 | 100nF | KYOCERA AVX SR215C104KAR | [478-3188-ND](https://www.digikey.com/en/products/filter?keywords=478-3188-ND) | [581-SR215C104KAR](https://www.mouser.com/ProductDetail/581-SR215C104KAR) |  |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  |
| J1 | 1 | 6502 Bus | Würth Elektronik 61204021621 | [732-5401-ND](https://www.digikey.com/en/products/filter?keywords=732-5401-ND) | [710-61204021621](https://www.mouser.com/ProductDetail/710-61204021621) |  |
| J2 | 1 | VERA Module | Pin header 2×12, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  |
| J3 | 1 | Audio L | Switchcraft Inc. PJRAN1X1U02X | [PJRAN1X1U02X-ND](https://www.digikey.com/en/products/filter?keywords=PJRAN1X1U02X-ND) | [502-PJRAN1X1U02X](https://www.mouser.com/ProductDetail/502-PJRAN1X1U02X) |  |
| J4 | 1 | Audio R | Switchcraft Inc. PJRAN1X1U03X | [PJRAN1X1U03X-ND](https://www.digikey.com/en/products/filter?keywords=PJRAN1X1U03X-ND) | [502-PJRAN1X1U03X](https://www.mouser.com/ProductDetail/502-PJRAN1X1U03X) |  |
| J5 | 1 | INT Select | Pin header 1×3, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  |
| J6 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  |
| U1, U2 | 2 | 74HC138 | Texas Instruments SN74HC138N | [296-1575-5-ND](https://www.digikey.com/en/products/filter?keywords=296-1575-5-ND) | [595-SN74HC138N](https://www.mouser.com/ProductDetail/595-SN74HC138N) |  |
| U1, U2 | 2 | Socket | IC socket, 16-pin, 0.3 in | [3M5475-ND](https://www.digikey.com/en/products/filter?keywords=3M5475-ND) | [517-4816-3004-CP](https://www.mouser.com/ProductDetail/517-4816-3004-CP) | |
| J5, J6 | 2 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  |

Pin headers are cut from strips, and the cart files count whole strips.

- **D1:** A 1N914 also works.
- **J1:** Male box header with a keying notch, for a 40-way ribbon cable.


## VGA Card Pro

### VGA Card Pro Rev 1.0

Never made. **Untested**: never made.

Cart files: [digikey.csv](BOM/VGA%20Card%20Pro/Rev%201.0/digikey.csv), [mouser.csv](BOM/VGA%20Card%20Pro/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/VGA%20Card%20Pro/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/VGA%20Card%20Pro/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1–C6 | 6 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  | |
| J2 | 1 | VGA | Amphenol ICD15S13E4GX00LF | [609-5181-ND](https://www.digikey.com/en/products/filter?keywords=609-5181-ND) | [649-ICD15S13E4GX00LF](https://www.mouser.com/ProductDetail/649-ICD15S13E4GX00LF) |  | |
| J3 | 1 | INT Select | Pin header 1×3, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| J4 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| Q1 | 1 | BSS138 | onsemi BSS138 | [BSS138CT-ND](https://www.digikey.com/en/products/filter?keywords=BSS138CT-ND) | [512-BSS138](https://www.mouser.com/ProductDetail/512-BSS138) | LCSC [C78284](https://www.lcsc.com/search?q=C78284) | Yes |
| R1, R2, R4, R7 | 4 | 1K | YAGEO RC0805FR-071KL | [311-1.00KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-1.00KCRCT-ND) | [603-RC0805FR-071KL](https://www.mouser.com/ProductDetail/603-RC0805FR-071KL) | LCSC [C17513](https://www.lcsc.com/search?q=C17513) | Yes |
| R3, R6 | 2 | 2.2K | YAGEO RC0805FR-072K2L | [311-2.20KCRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-2.20KCRCT-ND) | [603-RC0805FR-072K2L](https://www.mouser.com/ProductDetail/603-RC0805FR-072K2L) | LCSC [C17520](https://www.lcsc.com/search?q=C17520) | Yes |
| R5, R8 | 2 | 470 | YAGEO RC0805FR-07470RL | [311-470CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-470CRCT-ND) | [603-RC0805FR-07470RL](https://www.mouser.com/ProductDetail/603-RC0805FR-07470RL) | LCSC [C17710](https://www.lcsc.com/search?q=C17710) | Yes |
| R9 | 1 | 820 | YAGEO RC0805FR-07820RL | [311-820CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-820CRCT-ND) | [603-RC0805FR-07820RL](https://www.mouser.com/ProductDetail/603-RC0805FR-07820RL) | LCSC [C17837](https://www.lcsc.com/search?q=C17837) | Yes |
| R10 | 1 | 390 | YAGEO RC0805FR-07390RL | [311-390CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-390CRCT-ND) | [603-RC0805FR-07390RL](https://www.mouser.com/ProductDetail/603-RC0805FR-07390RL) | LCSC [C17655](https://www.lcsc.com/search?q=C17655) | Yes |
| R11, R12 | 2 | 22 | YAGEO RC0805FR-0722RL | [311-22.0CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-22.0CRCT-ND) | [603-RC0805FR-0722RL](https://www.mouser.com/ProductDetail/603-RC0805FR-0722RL) | LCSC [C17561](https://www.lcsc.com/search?q=C17561) | Yes |
| U2 | 1 | 74LVC245 | Texas Instruments SN74LVC245APWR | [296-1233-1-ND](https://www.digikey.com/en/products/filter?keywords=296-1233-1-ND) | [595-SN74LVC245APWR](https://www.mouser.com/ProductDetail/595-SN74LVC245APWR) | LCSC [C6082](https://www.lcsc.com/search?q=C6082) | Yes |
| U3 | 1 | Raspberry Pi Pico | Raspberry Pi SC0915 | [2648-SC0915CT-ND](https://www.digikey.com/en/products/filter?keywords=2648-SC0915CT-ND) | [358-SC0915](https://www.mouser.com/ProductDetail/358-SC0915) |  | |
| U4 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U5 | 1 | 74LVC138 | Nexperia USA Inc. 74LVC138AD,118 | [1727-3093-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-3093-1-ND) | [771-74LVC138AD-T](https://www.mouser.com/ProductDetail/771-74LVC138AD-T) | LCSC [C6061](https://www.lcsc.com/search?q=C6061) | Yes |
| J3, J4 | 2 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

- **D1:** A 1N914 also works.


## VGA Card

### VGA Card Rev 1.1

Drawn, not made yet. **Untested**: the pico9918 turned around, a new outline and jack mount, A1 wired to `MODE1`, and the bare card edge.

Cart files: [digikey.csv](BOM/VGA%20Card/Rev%201.1/digikey.csv), [mouser.csv](BOM/VGA%20Card/Rev%201.1/mouser.csv), [digikey-through-hole.csv](BOM/VGA%20Card/Rev%201.1/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/VGA%20Card/Rev%201.1/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C2 | 2 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  | |
| J2 | 1 | INT Select | Pin header 1×3, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| J3 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| U1 | 1 | Pico9918A | Pico9918A, DIP-40_W15.24mm |  |  | [Tindie](https://www.tindie.com/products/visrealm/pico9918-pro/) | |
| U2, U3 | 2 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U1 | 1 | Socket | IC socket, 40-pin, 0.6 in | [3M5471-ND](https://www.digikey.com/en/products/filter?keywords=3M5471-ND) | [517-4840-6000-CP](https://www.mouser.com/ProductDetail/517-4840-6000-CP) | | |
| J2, J3 | 2 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

### VGA Card Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/VGA%20Card/Rev%201.0/digikey.csv), [mouser.csv](BOM/VGA%20Card/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/VGA%20Card/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/VGA%20Card/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C2 | 2 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  | |
| J2 | 1 | INT Select | Pin header 1×3, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| J3 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| U1 | 1 | Pico9918A | Pico9918A, DIP-40_W15.24mm |  |  | [Tindie](https://www.tindie.com/products/visrealm/pico9918-pro/) | |
| U2, U3 | 2 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| J2, J3 | 2 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

- **D1:** A 1N914 also works.


## Video Card Pro

### Video Card Pro Rev 1.0

Never made. **Untested**: never made.

Cart files: [digikey.csv](BOM/Video%20Card%20Pro/Rev%201.0/digikey.csv), [mouser.csv](BOM/Video%20Card%20Pro/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/Video%20Card%20Pro/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Video%20Card%20Pro/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C2 | 2 | 20pF | KYOCERA AVX SR151A200JAR | [478-7724-ND](https://www.digikey.com/en/products/filter?keywords=478-7724-ND) | [581-SR151A200JAR](https://www.mouser.com/ProductDetail/581-SR151A200JAR) |  | |
| C3–C10 | 8 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  | |
| FB1 | 1 | BLM41PG600SN1L | Murata Electronics BLM41PG600SN1L | [490-1058-1-ND](https://www.digikey.com/en/products/filter?keywords=490-1058-1-ND) | [81-BLM41P600S](https://www.mouser.com/ProductDetail/81-BLM41P600S) | LCSC [C85844](https://www.lcsc.com/search?q=C85844) | Yes |
| J1 | 1 | VIDEO | Switchcraft Inc. PJRAN1X1U04X | [PJRAN1X1U04X-ND](https://www.digikey.com/en/products/filter?keywords=PJRAN1X1U04X-ND) | [502-PJRAN1X1U04X](https://www.mouser.com/ProductDetail/502-PJRAN1X1U04X) |  | |
| J2 | 1 | SERIAL | Pin header 1×4, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| J3 | 1 | INT Select | Pin header 1×3, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| J5 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| Q1 | 1 | 2N4401 | onsemi 2N4401BU | [2N4401-ND](https://www.digikey.com/en/products/filter?keywords=2N4401-ND) | [512-2N4401BU](https://www.mouser.com/ProductDetail/512-2N4401BU) |  | |
| R1, R2 | 2 | 4.7k | YAGEO MFR-12FTF52-4K7 | [13-MFR-12FTF52-4K7CT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-4K7CT-ND) | [603-MFR-12FTF52-4K7](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-4K7) |  | |
| R3 | 1 | 470 | YAGEO RC0805FR-07470RL | [311-470CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-470CRCT-ND) | [603-RC0805FR-07470RL](https://www.mouser.com/ProductDetail/603-RC0805FR-07470RL) | LCSC [C17710](https://www.lcsc.com/search?q=C17710) | Yes |
| R4 | 1 | 75 | YAGEO RC0805FR-0775RL | [311-75.0CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-75.0CRCT-ND) | [603-RC0805FR-0775RL](https://www.mouser.com/ProductDetail/603-RC0805FR-0775RL) | LCSC [C17820](https://www.lcsc.com/search?q=C17820) | Yes |
| R5 | 1 | 1k | YAGEO MFR-12FTF52-1K | [13-MFR-12FTF52-1KCT-ND](https://www.digikey.com/en/products/filter?keywords=13-MFR-12FTF52-1KCT-ND) | [603-MFR-12FTF52-1K](https://www.mouser.com/ProductDetail/603-MFR-12FTF52-1K) |  | |
| U1, U4 | 2 | 74HC157 | Texas Instruments SN74HC157DR | [296-14836-1-ND](https://www.digikey.com/en/products/filter?keywords=296-14836-1-ND) | [595-SN74HC157DR](https://www.mouser.com/ProductDetail/595-SN74HC157DR) | LCSC [C6823](https://www.lcsc.com/search?q=C6823) | Yes |
| U2, U5 | 2 | 74HC166 | Texas Instruments SN74HC166DR | [296-14839-1-ND](https://www.digikey.com/en/products/filter?keywords=296-14839-1-ND) | [595-SN74HC166DR](https://www.mouser.com/ProductDetail/595-SN74HC166DR) | LCSC [C473363](https://www.lcsc.com/search?q=C473363) | Yes |
| U3 | 1 | ATmega1284 | Microchip Technology ATMEGA1284-PU | [ATMEGA1284-PU-ND](https://www.digikey.com/en/products/filter?keywords=ATMEGA1284-PU-ND) | [556-ATMEGA1284-PU](https://www.mouser.com/ProductDetail/556-ATMEGA1284-PU) |  | |
| U6 | 1 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| VR1, VR2 | 2 | 10k | Bourns Inc. 3386F-1-103LF | [3386F-103LF-ND](https://www.digikey.com/en/products/filter?keywords=3386F-103LF-ND) | [652-3386F-1-103LF](https://www.mouser.com/ProductDetail/652-3386F-1-103LF) |  | |
| Y1 | 1 | 14.31818 MHz | ECS Inc. ECS-143-20-4X | [X1081-ND](https://www.digikey.com/en/products/filter?keywords=X1081-ND) | [520-HCU143-20-4X](https://www.mouser.com/ProductDetail/520-HCU143-20-4X) |  | |
| U3 | 1 | Socket | IC socket, 40-pin, 0.6 in | [3M5471-ND](https://www.digikey.com/en/products/filter?keywords=3M5471-ND) | [517-4840-6000-CP](https://www.mouser.com/ProductDetail/517-4840-6000-CP) | | |
| J3, J5 | 2 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

- **D1:** A 1N914 also works.


## Video Card

### Video Card Rev 1.1

Drawn, not made yet. **Proven design**: JP7, a solder jumper, ships bridged (fine with a real TMS9918A's open-drain `/INT`), sockets, silkscreen, the bare card edge.

Cart files: [digikey.csv](BOM/Video%20Card/Rev%201.1/digikey.csv), [mouser.csv](BOM/Video%20Card/Rev%201.1/mouser.csv), [digikey-through-hole.csv](BOM/Video%20Card/Rev%201.1/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Video%20Card/Rev%201.1/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C2 | 2 | 33pF | KYOCERA AVX SR151A330JAR | [478-4849-ND](https://www.digikey.com/en/products/filter?keywords=478-4849-ND) | [581-SR151A330JAR](https://www.mouser.com/ProductDetail/581-SR151A330JAR) |  | |
| C3–C10 | 8 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  | |
| FB1 | 1 | BLM41PG600SN1L | Murata Electronics BLM41PG600SN1L | [490-1058-1-ND](https://www.digikey.com/en/products/filter?keywords=490-1058-1-ND) | [81-BLM41P600S](https://www.mouser.com/ProductDetail/81-BLM41P600S) | LCSC [C85844](https://www.lcsc.com/search?q=C85844) | Yes |
| J1 | 1 | INT Select | Pin header 1×3, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| J3 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| J4 | 1 | VIDEO | Switchcraft Inc. PJRAN1X1U04X | [PJRAN1X1U04X-ND](https://www.digikey.com/en/products/filter?keywords=PJRAN1X1U04X-ND) | [502-PJRAN1X1U04X](https://www.mouser.com/ProductDetail/502-PJRAN1X1U04X) |  | |
| Q1 | 1 | 2N4401 | onsemi 2N4401BU | [2N4401-ND](https://www.digikey.com/en/products/filter?keywords=2N4401-ND) | [512-2N4401BU](https://www.mouser.com/ProductDetail/512-2N4401BU) |  | |
| R1 | 1 | 470 | YAGEO RC0805FR-07470RL | [311-470CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-470CRCT-ND) | [603-RC0805FR-07470RL](https://www.mouser.com/ProductDetail/603-RC0805FR-07470RL) | LCSC [C17710](https://www.lcsc.com/search?q=C17710) | Yes |
| R2 | 1 | 75 | YAGEO RC0805FR-0775RL | [311-75.0CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-75.0CRCT-ND) | [603-RC0805FR-0775RL](https://www.mouser.com/ProductDetail/603-RC0805FR-0775RL) | LCSC [C17820](https://www.lcsc.com/search?q=C17820) | Yes |
| U1 | 1 | TMS9918A | Texas Instruments TMS9918ANL |  |  | eBay | |
| U2, U5, U6 | 3 | 74HCT574 | Nexperia USA Inc. 74HCT574D,653 | [1727-2856-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2856-1-ND) | [771-74HCT574D-T](https://www.mouser.com/ProductDetail/771-74HCT574D-T) | LCSC [C6001](https://www.lcsc.com/search?q=C6001) | Yes |
| U3, U4 | 2 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U7 | 1 | AS6C62256 | Alliance Memory AS6C62256-55PCN | [1450-1033-ND](https://www.digikey.com/en/products/filter?keywords=1450-1033-ND) | [913-AS6C62256-55PCN](https://www.mouser.com/ProductDetail/913-AS6C62256-55PCN) |  | |
| U8 | 1 | 74HCT04 | Nexperia USA Inc. 74HCT04D,653 | [1727-2830-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2830-1-ND) | [771-74HCT04D-T](https://www.mouser.com/ProductDetail/771-74HCT04D-T) | LCSC [C672096](https://www.lcsc.com/search?q=C672096) | Yes |
| Y1 | 1 | 10.738635 MHz | CTS MP107-E | [CTX1443-ND](https://www.digikey.com/en/products/filter?keywords=CTX1443-ND) | [774-MP107-E](https://www.mouser.com/ProductDetail/774-MP107-E) |  | |
| U7 | 1 | Socket | IC socket, 28-pin, 0.6 in | [3M5481-ND](https://www.digikey.com/en/products/filter?keywords=3M5481-ND) | [517-4828-6004-CP](https://www.mouser.com/ProductDetail/517-4828-6004-CP) | | |
| U1 | 1 | Socket | IC socket, 40-pin, 0.6 in | [3M5471-ND](https://www.digikey.com/en/products/filter?keywords=3M5471-ND) | [517-4840-6000-CP](https://www.mouser.com/ProductDetail/517-4840-6000-CP) | | |
| J1, J3 | 2 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

- **C1, C2:** 32 or 33 pF: 33 pF is the standard value and is what the tested Video Card has. The schematic Value changes to 33pF; hidden, so the Gerbers do not change.
- **D1:** A 1N914 also works.
- **U1:** Out of production; eBay is the likely source. Prefer the VGA Card to the Video Card, which needs this chip. Not a TMS9928 or TMS9929, which have no composite output.
- **Y1:** The TMS9918A master clock. The frequency is fixed by the chip.

### Video Card Rev 1.0

Made, tested. **Tested**.

Cart files: [digikey.csv](BOM/Video%20Card/Rev%201.0/digikey.csv), [mouser.csv](BOM/Video%20Card/Rev%201.0/mouser.csv), [digikey-through-hole.csv](BOM/Video%20Card/Rev%201.0/digikey-through-hole.csv), [mouser-through-hole.csv](BOM/Video%20Card/Rev%201.0/mouser-through-hole.csv)

| Reference | Qty | Value | Part | Digi-Key | Mouser | Other | Pre-soldered |
|---|---|---|---|---|---|---|---|
| C1, C2 | 2 | 33pF | KYOCERA AVX SR151A330JAR | [478-4849-ND](https://www.digikey.com/en/products/filter?keywords=478-4849-ND) | [581-SR151A330JAR](https://www.mouser.com/ProductDetail/581-SR151A330JAR) |  | |
| C3–C10 | 8 | 100nF | YAGEO CC0805KRX7R9BB104 | [311-1140-1-ND](https://www.digikey.com/en/products/filter?keywords=311-1140-1-ND) | [603-CC805KRX7R9BB104](https://www.mouser.com/ProductDetail/603-CC805KRX7R9BB104) | LCSC [C49678](https://www.lcsc.com/search?q=C49678) | Yes |
| D1 | 1 | BAT85 | Vishay BAT85S-TR | [BAT85SCT-ND](https://www.digikey.com/en/products/filter?keywords=BAT85SCT-ND) | [78-BAT85S](https://www.mouser.com/ProductDetail/78-BAT85S) |  | |
| FB1 | 1 | BLM41PG600SN1L | Murata Electronics BLM41PG600SN1L | [490-1058-1-ND](https://www.digikey.com/en/products/filter?keywords=490-1058-1-ND) | [81-BLM41P600S](https://www.mouser.com/ProductDetail/81-BLM41P600S) | LCSC [C85844](https://www.lcsc.com/search?q=C85844) | Yes |
| J1 | 1 | INT Select | Pin header 1×3, 2.54 mm, cut from a strip | [S1011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S1011EC-40-ND) | [200-TSW14007TS](https://www.mouser.com/ProductDetail/200-TSW14007TS) |  | |
| J3 | 1 | Conn_02x08_Odd_Even | Pin header 2×8, 2.54 mm, cut from a strip | [S2011EC-40-ND](https://www.digikey.com/en/products/filter?keywords=S2011EC-40-ND) | [649-67996-140HLF](https://www.mouser.com/ProductDetail/649-67996-140HLF) |  | |
| J4 | 1 | Video Out | Switchcraft Inc. PJRAN1X1U04X | [PJRAN1X1U04X-ND](https://www.digikey.com/en/products/filter?keywords=PJRAN1X1U04X-ND) | [502-PJRAN1X1U04X](https://www.mouser.com/ProductDetail/502-PJRAN1X1U04X) |  | |
| Q1 | 1 | 2N4401 | onsemi 2N4401BU | [2N4401-ND](https://www.digikey.com/en/products/filter?keywords=2N4401-ND) | [512-2N4401BU](https://www.mouser.com/ProductDetail/512-2N4401BU) |  | |
| R1 | 1 | 470 | YAGEO RC0805FR-07470RL | [311-470CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-470CRCT-ND) | [603-RC0805FR-07470RL](https://www.mouser.com/ProductDetail/603-RC0805FR-07470RL) | LCSC [C17710](https://www.lcsc.com/search?q=C17710) | Yes |
| R2 | 1 | 75 | YAGEO RC0805FR-0775RL | [311-75.0CRCT-ND](https://www.digikey.com/en/products/filter?keywords=311-75.0CRCT-ND) | [603-RC0805FR-0775RL](https://www.mouser.com/ProductDetail/603-RC0805FR-0775RL) | LCSC [C17820](https://www.lcsc.com/search?q=C17820) | Yes |
| U1 | 1 | TMS9918A | Texas Instruments TMS9918ANL |  |  | eBay | |
| U2, U5, U6 | 3 | 74HCT574 | Nexperia USA Inc. 74HCT574D,653 | [1727-2856-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2856-1-ND) | [771-74HCT574D-T](https://www.mouser.com/ProductDetail/771-74HCT574D-T) | LCSC [C6001](https://www.lcsc.com/search?q=C6001) | Yes |
| U3, U4 | 2 | 74HC138 | Nexperia USA Inc. 74HC138D,653 | [1727-2781-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2781-1-ND) | [771-74HC138D-T](https://www.mouser.com/ProductDetail/771-74HC138D-T) | LCSC [C5602](https://www.lcsc.com/search?q=C5602) | Yes |
| U7 | 1 | AS6C62256 | Alliance Memory AS6C62256-55PCN | [1450-1033-ND](https://www.digikey.com/en/products/filter?keywords=1450-1033-ND) | [913-AS6C62256-55PCN](https://www.mouser.com/ProductDetail/913-AS6C62256-55PCN) |  | |
| U8 | 1 | 74HCT04 | Nexperia USA Inc. 74HCT04D,653 | [1727-2830-1-ND](https://www.digikey.com/en/products/filter?keywords=1727-2830-1-ND) | [771-74HCT04D-T](https://www.mouser.com/ProductDetail/771-74HCT04D-T) | LCSC [C672096](https://www.lcsc.com/search?q=C672096) | Yes |
| Y1 | 1 | 10.738635 MHz | CTS MP107-E | [CTX1443-ND](https://www.digikey.com/en/products/filter?keywords=CTX1443-ND) | [774-MP107-E](https://www.mouser.com/ProductDetail/774-MP107-E) |  | |
| J1, J3 | 2 | | Shunt, 2.54 mm | [S9337-ND](https://www.digikey.com/en/products/filter?keywords=S9337-ND) |  |  | |

Pin headers are cut from strips, and the cart files count whole strips.

- **C1, C2:** 32 or 33 pF: 33 pF is the standard value and is what the tested Video Card has. The schematic Value changes to 33pF; hidden, so the Gerbers do not change.
- **D1:** A 1N914 also works.
- **U1:** Out of production; eBay is the likely source. Prefer the VGA Card to the Video Card, which needs this chip. Not a TMS9928 or TMS9929, which have no composite output.
- **Y1:** The TMS9918A master clock. The frequency is fixed by the chip.
