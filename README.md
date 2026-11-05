6502-COB
========

![6502-COB.png](./Images/6502-COB.png)

An **AC6502** retro-style 8-bit computer based on the **65C02** microprocessor.

> 📖 **Guide:** [AC6502 Documentation](https://acwright.github.io/6502-DOCS/) — the user's and programmer's guide for the whole family.
> See [COB's page in the family appendix](https://acwright.github.io/6502-DOCS/family/cob).

---

**Building one? Every part you need, with supplier numbers and known issues, is in [BOM.md](BOM.md).**

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Systems](#systems)
- [Software](#software)
- [Hardware](#hardware)
  - [Backplanes](#backplanes)
  - [Cards](#cards)
  - [Helpers](#helpers)
- [Firmware](#firmware)
  - [KEH Controller](#keh-controller)
  - [PS2 Keyboard Controller](#ps2-keyboard-controller)
  - [STP Controller](#stp-controller)
- [CAD](#cad)
- [Production](#production)
- [Schematics](#schematics)
- [Checking the schematics](#checking-the-schematics)
- [Libraries](#libraries)
- [Bill of Materials](#bill-of-materials)
  - [Backplane](#backplane)
  - [Backplane Helper](#backplane-helper)
  - [Backplane Pro](#backplane-pro)
  - [Blinkenlights Card](#blinkenlights-card)
  - [Breadboard Helper](#breadboard-helper)
  - [Clock Helper](#clock-helper)
  - [Clock Card](#clock-card)
  - [CPU Card](#cpu-card)
  - [CPU Card Pro](#cpu-card-pro)
  - [DB25 Helper](#db25-helper)
  - [GPIO Breadboard Helper](#gpio-breadboard-helper)
  - [GPIO Card](#gpio-card)
  - [GPIO Helper](#gpio-helper)
  - [Joystick Helper](#joystick-helper)
  - [Keyboard Encoder Helper](#keyboard-encoder-helper)
  - [Keyboard Helper](#keyboard-helper)
  - [LCD Board](#lcd-board)
  - [LCD Card](#lcd-card)
  - [Mega Helper](#mega-helper)
  - [Memory Card](#memory-card)
  - [Prototype Card](#prototype-card)
  - [PS2 Helper](#ps2-helper)
  - [RAM Card](#ram-card)
  - [RTC Card](#rtc-card)
  - [Serial Card](#serial-card)
  - [Serial Card Pro](#serial-card-pro)
  - [Sound Card](#sound-card)
  - [Storage Card](#storage-card)
  - [Storage Card Pro](#storage-card-pro)
  - [VERA Helper](#vera-helper)
  - [VGA Card](#vga-card)
  - [VGA Card Pro](#vga-card-pro)
  - [Video Card](#video-card)
  - [Video Card Pro](#video-card-pro)
- [Purchase](#purchase)
- [License](#license)

---

## Overview

The AC6502 ecosystem is a family of open-source, 65C02-based computers sharing a common architecture, memory map, and [BIOS](https://github.com/acwright/6502-BIOS). Each computer in the family is purpose-built for a different use case but runs the same software and firmware.

The **COB** (Computer on a Backplane) is a full-featured modular desktop computer. It features a real 65C02 CPU, a backplane architecture with expandable card slots, up to 544KB RAM, composite or VGA video output, CompactFlash or SD storage, a real-time clock, and support for PS/2 keyboards, matrix keyboards, and Atari 2600-compatible joysticks.

## Architecture

All AC6502 computers share:

- **CPU**: 65C02 (or accurate emulation)
- **Memory**: 32KB RAM + 32KB ROM, with optional banked RAM expansion
- **Memory Map**: Standardized across the ecosystem — zero page, stack, I/O space ($8000–$9FFF), system ROM, and interrupt vectors at $FFFA–$FFFF
- **Bus**: 16-bit address bus, 8-bit bidirectional data bus, standard 65C02 control signals (RW, PHI2, RESET, IRQ, NMI, RDY, SYNC)
- **BIOS**: A common [BIOS](https://github.com/acwright/6502-BIOS) provides the kernel, monitor, and BASIC interpreter across all systems

## Systems

| Project | Description |
|---------|-------------|
| [6502-ACE](https://github.com/acwright/6502-ACE) | All-in-one Computer Experience — A single board computer |
| [6502-COB](https://github.com/acwright/6502-COB) | Computer On a Backplane — Modular desktop computer with expandable card slots (YOU ARE HERE) |
| [6502-DEV](https://github.com/acwright/6502-DEV) | Development Environment Vehicle — Emulation-based dev system |
| [6502-KIM](https://github.com/acwright/6502-KIM) | Keypad Input Monitor - KIM-1 inspired minimal computer |
| [6502-VCS](https://github.com/acwright/6502-VCS) | Video Computer System — Cartridge-based retro gaming console |

## Software

| Project | Description |
|---------|-------------|
| [6502-BIOS](https://github.com/acwright/6502-BIOS) | The shared BIOS (kernel, monitor, BASIC) for all AC6502 computers |
| [6502-EMULATOR](https://github.com/acwright/6502-EMULATOR) | Emulator for the whole family — desktop app, browser build, and a command line for scripted runs |
| [6502-PRG](https://github.com/acwright/6502-PRG) | Template project for writing assembly language programs |
| [6502-CRT](https://github.com/acwright/6502-CRT) | Template project for writing assembly language cartridges |
| [6502-ASM](https://github.com/acwright/6502-ASM) | Assembly language example programs and demos |
| [6502-BAS](https://github.com/acwright/6502-BAS) | BASIC program listings |
| [6502-WOZMON](https://github.com/acwright/6502-WOZMON) | Wozmon as a standalone ROM |
| [6502-NOP](https://github.com/acwright/6502-NOP) | An all-NOP ROM, for probing a board during bring-up |
| [6502-DOCS](https://github.com/acwright/6502-DOCS) | The documentation site — the guide, the printable reference cards, branding and label artwork |
| [cffs](https://github.com/acwright/cffs) | Builds CompactFlash disk images for the BIOS filesystem |
| [bastok](https://github.com/acwright/bastok) | Tokenizes BASIC listings into `.prg` images, and back |
| [bin2woz](https://github.com/acwright/bin2woz) | Converts a binary into a Wozmon serial upload |

## Hardware

This repository contains KiCad 7.0+ PCB designs for the backplanes, cards, and helpers that make up the COB system.

### Backplanes

**`Hardware/Backplane/`** — Passive backplane providing 5 card slots with full bus interconnect across all slots.

**`Hardware/Backplane Pro/`** — Enhanced backplane with integrated clock generation, reset circuitry, and power distribution plus 5 card slots. Rev 1.1 moves to entirely through-hole components and adds an onboard power switch and DC barrel jack input. Rev 1.2 removes the `RESB` pull-up and adds reverse-polarity protection on the barrel jack.

**`Hardware/Backplane Helper/`** — Adds additional card slots to expand the total backplane configuration up to 12 slots.

### Cards

**`Hardware/Clock Card/`** — The Backplane Pro's clock, reset and power on a card, so a COB can be built on the passive Backplane: a 1 MHz DIP-14 can oscillator to `PHI2` through a clock-enable header (so the Clock Helper's single-step and halt still work), the 555 power-on and push-button reset pulling `RESB` low through an NPN, and a 5 V barrel jack with reverse-polarity protection. *(Ordered, not yet built)*

**`Hardware/CPU Card/`** — Hosts the 65C02 CPU in a card form factor for backplane-based COB systems.

**`Hardware/CPU Card Pro/`** — Hosts a 65816 16-bit CPU (backward-compatible with 65C02). *(Untested)* Its title block credits bahamutkotd, who contributed.

**`Hardware/Memory Card/`** — Provides 32KB SRAM and 32KB EEPROM with address decoding logic for COB systems using the CPU Card.

**`Hardware/RAM Card/`** — 512KB banked RAM expansion organized as two 256KB banks with 256 × 1KB windows each.

**`Hardware/RTC Card/`** — Real-time clock via Dallas DS1511Y with battery backup and 256 bytes of battery-backed SRAM.

**`Hardware/GPIO Card/`** — General-purpose I/O via 65C22 VIA supporting keyboards, joysticks, timers, and custom devices.

**`Hardware/Serial Card/`** — RS-232 serial communication via 65C51 ACIA and MAX232 level shifter.
Female DB-9 wired as **DCE**, so a straight-through cable reaches a PC. `DCD` and `DSR` are tied to
ground; `DTR` is not connected. The `CTS EN` jumper (J4) picks whether the ACIA's `CTS` comes from
ground or from the cable — **ground is the default**, which leaves the transmitter always free to
send.

**`Hardware/Serial Card Pro/`** — Enhanced serial card with full modem control signals (DTR, DCD, DSR).
Male DB-9 wired as **DTE**, like a PC, so reaching a laptop needs a **null-modem** cable — unlike the
plain Serial Card. `CTS`, `DSR` and `DTR` always reach the cable; the `DCD EN` jumper picks ground or
the cable for `DCD` — **ground is the default**.

**The handshake lines are not decoration.** On a real R6551, measured on a KIM in 2026: `CTS` high
stops the transmitter dead, and `DCD` high stops the receiver and the arriving byte is lost. A card
jumpered to take either from the cable, plugged into something that does not assert them, looks like
a dead board — no banner, no echo — until the line comes back. Ground is the default for exactly
that reason.

**`Hardware/VGA Card/`** — VGA 640×480 video output via Raspberry Pi Pico running [Pico9918](https://github.com/visrealm/pico9918) with TMS9918A-compatible graphics modes.

**`Hardware/VGA Card Pro/`** — Fully programmable VGA output using Pi Pico with custom firmware. *(Untested)*

**`Hardware/Video Card/`** — Composite video output via TMS9918A Video Display Processor with 16KB video RAM.

**`Hardware/Video Card Pro/`** — Enhanced composite video card. *(Never made)*

**`Hardware/Sound Card/`** — 3-voice SID audio output via ARMSID module with RCA line-level output.

**`Hardware/Storage Card/`** — CompactFlash storage interface supporting up to 128GB via IDE-compatible protocol.

**`Hardware/Storage Card Pro/`** — SD card (up to 32GB) and 16MB onboard SPI flash storage interface. *(Untested, experimental — the stock BIOS has no driver for it; see [STP Controller](#stp-controller))*

**`Hardware/LCD Card/`** — 16×2 character LCD display via 65C22 VIA in 4-bit or 8-bit mode.

**`Hardware/Blinkenlights Card/`** — Visual bus monitoring with LEDs showing address bus (16), data bus (8), and control signals (8) in real time.

**`Hardware/Prototype Card/`** — Blank prototyping area with integrated breadboard and full bus access headers.

### Helpers

**`Hardware/Keyboard Encoder Helper/`** — ATmega1284p-based dual keyboard encoder supporting PS/2 keyboard and 8×8 matrix keyboard simultaneously via 65C22 VIA.

**`Hardware/PS2 Helper/`** — ATmega328p-based PS/2 keyboard bridge that drives an MT8808 analog crosspoint switch to emulate a matrix keyboard. Its output is a raw 8×8 matrix and feeds the matrix inputs of a Keyboard Encoder Helper, which is what talks to the 65C22 VIA — not the VIA directly.

**`Hardware/Keyboard Helper/`** — 64-key matrix keyboard with Atari 2600-compatible joystick support.

**`Hardware/GPIO Helper/`** — 8 buttons and 8 LEDs for testing and debugging GPIO Card connections.

**`Hardware/GPIO Breadboard Helper/`** — Breadboard interface adapter for the GPIO Card.

**`Hardware/Joystick Helper/`** — Atari 2600-style dual joystick connector and interface board.

**`Hardware/Clock Helper/`** — Manual clock control providing single-step, free-run, and halt modes for debugging real CPU systems.

**`Hardware/DB25 Helper/`** — GPIO to DB25 connector adapter for external device interfacing.

**`Hardware/Breadboard Helper/`** — Exposes the full AC6502 bus to a breadboard for prototyping and experimentation.

**`Hardware/Mega Helper/`** — Arduino Mega 2560 interface adapter for the AC6502 bus.

**`Hardware/LCD Board/`** — 320×240 TFT LCD display (ILI9341) interfaced via 65C22 VIA.

**`Hardware/VERA Helper/`** — VERA FPGA video module adapter for the AC6502 bus.

## Firmware

This repository contains [PlatformIO](https://platformio.org/)-based firmware for the COB system's microcontroller helpers.

### KEH Controller
`Firmware/KEH Controller/`

Firmware for the ATmega1284p on the Keyboard Encoder Helper. Provides:

- Simultaneous PS/2 keyboard and 8×8 matrix keyboard scanning
- ASCII conversion with modifier key support (Shift, Ctrl)
- Buffered, debounced input handling
- Parallel I/O to the AC6502 bus via 65C22 VIA

See [Firmware/KEH Controller/README.md](./Firmware/KEH%20Controller/README.md) for setup and usage instructions.

### PS2 Keyboard Controller
`Firmware/PS2 Keyboard Controller/`

Firmware for the ATmega328p on the PS2 Helper. Provides:

- Interrupt-driven PS/2 keyboard scan code reading
- MT8808 analog crosspoint switch matrix control
- Make/break detection and extended scan code support
- Function key emulation via FN key combinations

The MT8808 closes row/column contacts in place of physical key switches, so this
card connects to the **matrix inputs of a Keyboard Encoder Helper**, not to a
65C22 VIA. The encoder does the scanning and ASCII conversion; wired straight to
a VIA the card produces nothing, as the BIOS has no matrix-scanning code.

See [Firmware/PS2 Keyboard Controller/README.md](./Firmware/PS2%20Keyboard%20Controller/README.md) for setup and usage instructions.

### STP Controller
`Firmware/STP Controller/`

Firmware for the ATmega328p on the Storage Card Pro. Provides:

- Memory-mapped SPI controller for 6502 bus access
- Support for SD card, 16MB SPI flash, and external SPI devices
- Dual-speed SPI (4 MHz normal operation, 400 kHz initialization)
- PHI2-synchronized interface for reliable 6502 communication

⚠️ **Experimental.** The Storage Card Pro is not part of the default I/O set the
BIOS probes for, and no COB machine is built around it today. The BIOS storage
slot expects eight True IDE CompactFlash registers at `$8C00–$8C07`; this card
presents two SPI registers instead, so a stock BIOS reports `NO DEVICE` for every
storage path. Using it needs a modified BIOS or software that drives the two
registers directly.

See [Firmware/STP Controller/README.md](./Firmware/STP%20Controller/README.md) for setup and usage instructions.

## CAD
`CAD/`

3D-printable enclosure parts and laser-cut top panels for the COB system.

**Board images** are in `CAD/Images/<Board>/Rev X/`: `Front.png` and `Back.png` on white, and `Front Transparent.png` and `Back Transparent.png` with no background. Every image is a 3D render at the same size, with the black solder mask and white silkscreen the boards are made with. Bare-board photos may differ, because the renders show parts fitted.

**Top panels, enclosures and jigs are versioned by board revision**, like `Hardware/`: `CAD/Tops/<Board>/Rev X/`, `CAD/Enclosures/<Board>/Rev X/`, `CAD/Jigs/<Board>/Rev X/`. Each revision has its own complete folder, even when two revisions share the same files. `Bases/` holds the parts for a whole computer, not for one board, so it isn't versioned.

Keyboard Encoder Helper Rev 1.0, the board on sale, has the old 88 × 39 mm holes, and the COB's base plate is drilled for Rev 1.1's 88 × 38 mm. To fit a Rev 1.0 board, drill plate holes 9 and 21 (x 296, at y 16 and y 104 on the plate mounting drawing) out to 5 mm. The two screws then sit 1 mm to the left of those holes' centers, and the board moves less than 1 mm into the 10 mm gap beside the Backplane Helper. Drill through all three layers of the plate, and add a washer if a screw head doesn't sit flat. The plate mounting drawing itself shows Rev 1.1.

The Rev 1.0 top panels for the Clock, DB25, GPIO, Joystick and Keyboard Encoder Helpers, and the Rev 1.1 top panel for the PS2 Helper, are derived from the other revision's panel by moving the four mounting holes. None of them has been cut yet.

The **[plate mounting drawing](CAD/Bases/Plate%20Mounting%20Drawing.png)** ([SVG](CAD/Bases/Plate%20Mounting%20Drawing.svg)) shows where the two Backplanes (each a Backplane or a Backplane Pro), the Backplane Helper and the Keyboard Encoder Helper mount on the base plate, with every hole's position and the hardware the build needs. The plate is a stack of three 3 mm acrylic layers.

## Production
`Production/`

[REVISIONS.md](REVISIONS.md) lists every board revision: whether it was made, its JLCPCB order, the commit it was made from, and what fits it.

JLCPCB-ready Gerber files and BOM/CPL for PCB fabrication and assembly.

## Schematics
`Schematics/`

PDF schematics for each board.

## Checking the schematics
`Tests/check-schematics.mjs`

The RAM Card's bank latch decides which kilobyte of its 512 KB each window shows, and a latch that loads on the wrong address corrupts a bank without any sign. The ACE's equivalent latch was wrong twice while its gates looked right on paper, so this script checks the logic instead of reading it. It asks KiCad for the card's netlist, builds the glue logic from the gates it finds there, fits the card's jumpers, and drives every address, as a read and as a write, with PHI2 high and low. That is 262,144 bus states. For each one it compares the RAM's chip select, read and write strobes and A18, and the latch enable, against the memory map, and checks that the card drives the data bus only on a read of its own window. A net that nothing drives counts as a failure, so a missing wire fails too.

It checks the RAM Card Rev 1.0 with both windows jumpered, IO 1 (`$8000`) and IO 2 (`$8400`), which is the only setting Rev 1.0 supports: R1 and R2 pull the window selects to ground, so a window left without a jumper is selected at every address.

Run it after any change to a checked schematic:

```sh
node Tests/check-schematics.mjs
```

It needs Node.js and KiCad's `kicad-cli`, which it finds on the `PATH`, at the macOS default location, or through a `KICAD_CLI` environment variable. It takes a few seconds, prints `ok` or `FAIL` for each check with example bus states for any failure, and exits non-zero on a failure.

## Libraries
`Libraries/`

Shared KiCad symbol and footprint libraries used across all AC6502 hardware projects.

## Bill of Materials

Every part for every board, by revision, is in **[BOM.md](BOM.md)**, with supplier numbers, known issues and files to upload to Digi-Key and Mouser.

### Backplane

#### Revision History

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Backplane/Rev 1.0/` and `Production/Backplane/Rev 1.0/` match the boards JLCPCB made (order Y50). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

Parts list: [BOM.md](BOM.md#backplane).

### Backplane Helper

#### Revision History

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/Backplane Helper/Rev 1.0/` and `Production/Backplane Helper/Rev 1.0/` match the boards JLCPCB made (order Y77). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Backplane Pro

#### Rev 1.2

Drawn, not yet made. Two changes from Rev 1.1:

- **R5 is removed.** It was a 1kΩ pull-up on `RESB`, in parallel with the CPU Card's. The CPU Card's pull-up is the only one a COB needs, and the reset circuit only pulls `RESB` low, through Q1. Without a CPU Card on the bus, `RESB` has no pull-up, so whatever drives the bus instead (a [Mega Helper](#mega-helper), for example) must hold `RESB` high itself.
- **D2, a 1N5819, is added** in series between the barrel jack (J1) and the power switch (SW1), anode at the jack, so a reversed supply can't reach VCC. It drops about 0.3–0.4 V, so VCC sits near 4.6 V.

The backplane carries no decoupling capacitors, as on the other backplanes: every card that plugs in has 100nF on each of its own chips.

Parts list: [BOM.md](BOM.md#backplane-pro).

#### Rev 1.1

- Built and tested. `Hardware/Backplane Pro/Rev 1.1/` and `Production/Backplane Pro/Rev 1.1/` match the boards JLCPCB made (order Y93). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

**Building a Rev 1.1:**

- **Leave R5 unfitted.** R5 is a 1kΩ pull-up on `RESB`, in parallel with the CPU Card's. The CPU Card's pull-up is the only one a COB needs, and the Backplane Pro's reset circuit only pulls `RESB` low, through Q1. Without a CPU Card on the bus, `RESB` then has no pull-up, so whatever drives the bus instead (a [Mega Helper](#mega-helper), for example) must hold `RESB` high itself.
- **Use a centre-positive 5 V supply only.** Rev 1.1 has no reverse-polarity protection on the barrel jack.

#### Rev 1.0

- Initial release, and the board on sale. Built and tested. `Hardware/Backplane Pro/Rev 1.0/` and `Production/Backplane Pro/Rev 1.0/` match the boards JLCPCB made (order Y30). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- This board was called the Backplane when it was ordered, so its silkscreen says `6502 BACKPLANE`. Today's [Backplane](#backplane) is a different board, order Y50.
- The PCB file was restored to that layout on 2026-11-04. A later edit only moved C8, C14, D1 and TP1 slightly, and Rev 1.1 is a full redesign, so that edit has no revision of its own. The schematic and BOM are today's, and they match this copper.

Parts list: [BOM.md](BOM.md#backplane-pro).

**Building a Rev 1.0:** leave R3 unfitted, or remove it from a built board. R3 is a 1kΩ pull-up on `RESB`, in parallel with the CPU Card's, and the CPU Card's pull-up is the only one a COB needs. The Rev 1.1 notes above explain what that means for a machine without a CPU Card.

### Blinkenlights Card

#### Revision History

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Adds `C1`–`C4`, 100nF decoupling capacitors, one beside each chip, with tracks rerouted to reach them. Rev 1.0 has no pads for them.
- The silkscreen spells out `RESB`. Rev 1.0's says `RSB`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Blinkenlights Card/Rev 1.0/` and `Production/Blinkenlights Card/Rev 1.0/` match the boards JLCPCB made (order Y40). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

**Both revisions:** the `IRQB`, `NMIB` and `RESB` LEDs (D25–D27, through R25–R27) hang straight on those lines. While a line is asserted, whatever pulls it low also sinks about 9 mA of LED current, nearly three times the 3.2 mA that the W65C22's and W65C21's IRQ outputs are rated for. The 65C02 may still read the line as low, but nothing guarantees it. Fit the card to watch the bus, not in a machine that relies on its interrupts. A later revision will buffer those three LEDs through the 74HC04's spare gates, as `RDY` and `BE` already are.

Parts list: [BOM.md](BOM.md#blinkenlights-card).

### Breadboard Helper

#### Revision History

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/Breadboard Helper/Rev 1.0/` and `Production/Breadboard Helper/Rev 1.0/` match the boards JLCPCB made (order Y39). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- The PCB file was restored to that layout on 2026-11-04. Later edits only changed pad shapes, when footprints were refreshed, so they don't make a Rev 1.1. The schematic and BOM are today's, and they match this copper.
- This is a different board from the [GPIO Breadboard Helper](#gpio-breadboard-helper): this one breaks out the full 6502 bus, and that one breaks out a VIA's PORT A and PORT B.

Parts list: [BOM.md](BOM.md#breadboard-helper).

### Clock Helper

#### Revision History

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the standard position, 6 mm from each edge. The spacing goes from 39 × 39 mm to 38 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/Clock Helper/` and `CAD/Tops/Clock Helper/`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Clock Helper/Rev 1.0/` and `Production/Clock Helper/Rev 1.0/` match the boards JLCPCB made (order Y74). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

Parts list: [BOM.md](BOM.md#clock-helper).

### Clock Card

Rev 1.0 has been ordered. No card has been built or tested yet. The card's oscillator socket takes any DIP-14 can; it is drawn, labelled and tested with 1 MHz, the AC6502's standard `PHI2`. It has no power switch, and no `RESB` pull-up: the CPU Card's is the only one a COB needs. JP1 is open as made, so the clock reaches `PHI2` only through J3: fit a switch or a jumper there, or bridge JP1 if the clock never needs to stop.

### CPU Card

**Building a Rev 1.0:** fit 10kΩ (0805) for R1–R6, not the 1kΩ in Rev 1.0's files; Rev 1.1 has 10kΩ. With a 1kΩ pull-up, a device that pulls `IRQB` low sinks 5 mA, more than the 3.2 mA that the W65C22's and W65C21's IRQ outputs are rated for.

#### Revision History

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Pull-up resistors changed from 1kΩ to 10kΩ.
- Some tracks are rerouted.
- The silkscreen labels U1 `65C02` and J3 `EXP`, and adds a `6502` label. It drops Rev 1.0's "Jumper J2 for original 6502" note.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/CPU Card/Rev 1.0/` and `Production/CPU Card/Rev 1.0/` match the boards JLCPCB made (order Y18). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### CPU Card Pro

Parts list: [BOM.md](BOM.md#cpu-card-pro).

### DB25 Helper

#### Revision History

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the standard position, 6 mm from each edge. The spacing goes from 88 × 39 mm to 88 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/DB25 Helper/` and `CAD/Tops/DB25 Helper/`.
- The project's name is `DB25 Helper`. The order's Gerbers carry its old name, `GPIO DB25 Helper`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/DB25 Helper/Rev 1.0/` and `Production/DB25 Helper/Rev 1.0/` match the boards JLCPCB made (order Y65). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

Parts list: [BOM.md](BOM.md#db25-helper).

### GPIO Breadboard Helper

#### Revision History

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/GPIO Breadboard Helper/Rev 1.0/` and `Production/GPIO Breadboard Helper/Rev 1.0/` match the boards JLCPCB made (order Y57). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### GPIO Card

#### Revision History

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/GPIO Card/Rev 1.0/` and `Production/GPIO Card/Rev 1.0/` match the boards JLCPCB made (order Y45). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

Parts list: [BOM.md](BOM.md#gpio-card).

### GPIO Helper

#### Revision History

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the standard position, 6 mm from each edge. The spacing goes from 88 × 39 mm to 88 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/GPIO Helper/` and `CAD/Tops/GPIO Helper/`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/GPIO Helper/Rev 1.0/` and `Production/GPIO Helper/Rev 1.0/` match the boards JLCPCB made (order Y66). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

Parts list: [BOM.md](BOM.md#gpio-helper).

### Joystick Helper

#### Revision History

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the standard position, 6 mm from each edge. The spacing goes from 39 × 39 mm to 38 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/Joystick Helper/` and `CAD/Tops/Joystick Helper/`. The holes' courtyards now overlap the courtyard of J2, the DB9 connector. That has been reviewed and is fine, so the project excludes it from DRC.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Joystick Helper/Rev 1.0/` and `Production/Joystick Helper/Rev 1.0/` match the boards JLCPCB made (order Y73). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

Parts list: [BOM.md](BOM.md#joystick-helper).

### Keyboard Encoder Helper

#### Revision History

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the standard position, 6 mm from each edge. The spacing goes from 88 × 39 mm to 88 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/Keyboard Encoder Helper/` and `CAD/Tops/Keyboard Encoder Helper/`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Keyboard Encoder Helper/Rev 1.0/` and `Production/Keyboard Encoder Helper/Rev 1.0/` match the boards JLCPCB made (order Y72). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- To mount it on the COB's base plate, two plate holes have to be drilled wider: see [CAD](#cad).

Parts list: [BOM.md](BOM.md#keyboard-encoder-helper).

### Keyboard Helper

#### Revision History

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Keyboard Helper/Rev 1.0/` and `Production/Keyboard Helper/Rev 1.0/` match the boards JLCPCB made (order Y70). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### LCD Board

#### Revision History

**Rev 1.0**

- Initial release. Built and tested. `Hardware/LCD Board/Rev 1.0/` and `Production/LCD Board/Rev 1.0/` match the boards JLCPCB made (order Y80). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- The PCB file was restored to that layout on 2026-11-04. Later edits only changed pad shapes, when footprints were refreshed, so they don't make a Rev 1.1. The schematic and BOM are today's, and they match this copper.

Parts list: [BOM.md](BOM.md#lcd-board).

### LCD Card

#### Revision History

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- `JP1` is open as made. On Rev 1.0 it is bridged.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/LCD Card/Rev 1.0/` and `Production/LCD Card/Rev 1.0/` match the boards JLCPCB made (order Y27). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

Parts list: [BOM.md](BOM.md#lcd-card).

### Mega Helper

#### Revision History

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/Mega Helper/Rev 1.0/` and `Production/Mega Helper/Rev 1.0/` match the boards JLCPCB made (order Y81). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

**Writing firmware for it:** the Mega's D2, D3, D4, D9 and D10 connect straight to `IRQB`, `NMIB`, `RESB`, `RDY` and `BE`, which every other device on the bus shares. Drive those pins open-drain. To assert a line, call `digitalWrite(pin, LOW)` and then `pinMode(pin, OUTPUT)`, in that order: after `INPUT_PULLUP` the pin's output latch is high, so switching to `OUTPUT` first would drive the line high for a moment. To release a line, call `pinMode(pin, INPUT)`. Never drive one of these pins high, because a pin driven high holds its line high against every other device that pulls it low. The pull-ups are on the CPU Card; in a machine without a CPU Card, release `RESB` with `pinMode(pin, INPUT_PULLUP)` so that it rises.

### Memory Card

#### Revision History

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/Memory Card/Rev 1.0/` and `Production/Memory Card/Rev 1.0/` match the boards JLCPCB made (order Y20). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- The PCB file was restored to that layout on 2026-11-04. Later edits only changed pad shapes, when footprints were refreshed, so they don't make a Rev 1.1. The schematic and BOM are today's, and they match this copper.

Parts list: [BOM.md](BOM.md#memory-card).

### Prototype Card

#### Revision History

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Prototype Card/Rev 1.0/` and `Production/Prototype Card/Rev 1.0/` match the boards JLCPCB made (order Y22). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### PS2 Helper

#### Revision History

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the resistors `R2`–`R9` and reroutes the tracks around them.
- Moves the four mounting holes (`H1`–`H4`) to the standard position, 6 mm from each edge. The spacing goes from 88 × 39 mm to 88 × 38 mm. Each revision has its own enclosure and top panel, in `CAD/Enclosures/PS2 Helper/` and `CAD/Tops/PS2 Helper/`.
- Drops the `R2-R9` silkscreen label.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/PS2 Helper/Rev 1.0/` and `Production/PS2 Helper/Rev 1.0/` match the boards JLCPCB made (order Y61). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

Parts list: [BOM.md](BOM.md#ps2-helper).

### RAM Card

#### Revision History

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/RAM Card/Rev 1.0/` and `Production/RAM Card/Rev 1.0/` match the boards JLCPCB made (order Y69). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

**Rev 1.0 is deprecated, and still works with the BIOS and BASIC.** Before fitting one:

- **Jumper both windows on J3, and nothing else:** 1–2 for IO 1 (`$8000`) and 3–4 for IO 2 (`$8400`), the setting the BIOS expects. R1 and R2 pull the window selects low, and the selects are active low, so a window left without a jumper is selected at every address: the card then drives the data bus on every read, against the system RAM and ROM. J3's other positions connect the same two windows to other addresses, so a third jumper puts two 74HC138 outputs on one window's select and ties them together.
- **One bank latch serves both windows.** A write to `$83FF` and a write to `$87FF` load the same 74HC573, so both windows always show the same bank number, each in its own half of the AS6C4008. A program can't point one window at one bank and the other window at another, so copying between banks through the two windows doesn't work on this card.
- **The data bus reaches the latch bit-reversed** (`D0` drives the latch's `D7`). That only renumbers the banks, and no program can tell.

A Rev 1.1, with a latch per window and window selects that read as not selected when a jumper is missing, is planned.

Parts list: [BOM.md](BOM.md#ram-card).

### RTC Card

#### Revision History

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/RTC Card/Rev 1.0/` and `Production/RTC Card/Rev 1.0/` match the boards JLCPCB made (order Y62). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Serial Card

#### Revision History

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Serial Card/Rev 1.0/` and `Production/Serial Card/Rev 1.0/` match the boards JLCPCB made (order Y67). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

Parts list: [BOM.md](BOM.md#serial-card).

### Serial Card Pro

#### Revision History

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- `J2` uses KiCad's standard DB-9 footprint, in a new position, in place of Rev 1.0's own. Its pin spacing and mounting lugs are the same, so the same connector fits both revisions.
- The silkscreen says `SERIAL (DTE)`. Rev 1.0's says `DB9 Male (DTE)`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Serial Card Pro/Rev 1.0/` and `Production/Serial Card Pro/Rev 1.0/` match the boards JLCPCB made (order Y36). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

Parts list: [BOM.md](BOM.md#serial-card-pro).

### Sound Card

#### Revision History

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Sound Card/Rev 1.0/` and `Production/Sound Card/Rev 1.0/` match the boards JLCPCB made (order Y84). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### Storage Card

#### Revision History

**Rev 1.0**

- Initial release, and the board on sale. Built and tested. `Hardware/Storage Card/Rev 1.0/` and `Production/Storage Card/Rev 1.0/` match the boards JLCPCB made (order Y47). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.
- The PCB file was restored to that layout on 2026-11-04. Later edits only changed pad shapes, when footprints were refreshed, so they don't make a Rev 1.1. The schematic and BOM are today's, and they match this copper.

Parts list: [BOM.md](BOM.md#storage-card).

### Storage Card Pro

#### Revision History

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Storage Card Pro/Rev 1.0/` and `Production/Storage Card Pro/Rev 1.0/` match the boards JLCPCB made (order Y78). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

### VERA Helper

#### Revision History

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- Moves the four mounting holes (`H1`–`H4`) to the standard position, 6 mm from each edge. The spacing goes from 88 × 69 mm to 88 × 68 mm.

**Rev 1.0**

- Initial release, and the board on sale. Its mounting holes are off the standard: 5.75 and 6.25 mm from the long sides' ends, and 5.32 and 5.68 mm from the top and bottom.
- Built and tested. `Hardware/VERA Helper/Rev 1.0/` and `Production/VERA Helper/Rev 1.0/` match the boards JLCPCB made (order Y71). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

Parts list: [BOM.md](BOM.md#vera-helper).

### VGA Card

#### Revision History

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- `A1` reaches U1 pin 11, the pico9918's `MODE1`, as on the ACE Rev 1.1. A PICO9918 PRO takes it through a header pin soldered into its `MDE1` pad.
- JP1 is open as made, so the pico9918's `/INT` reaches `IRQB` (or `NMIB`, through J2) only through D1.
- D1 is named in its value field: a BAT85, cathode toward the pico9918.
- U1, the pico9918, is turned around, and the board's outline around its VGA jack changes. The two mounting holes move, and the tracks are rerouted to suit.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/VGA Card/Rev 1.0/` and `Production/VGA Card/Rev 1.0/` match the boards JLCPCB made (order Y64). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

**Building a Rev 1.0: cut JP1.** The pico9918 drives its `/INT` (U1 pin 16) high as well as low. D1 is meant to let it only pull `IRQB` (or `NMIB`, through J2) low, but JP1, a solder jumper bridged on the board as made, shorts across D1. With JP1 bridged, the pico9918 holds `IRQB` high against every other interrupt source, and the keyboard and serial input stop working. Cut the trace between JP1's pads, and check with a meter that they no longer connect. The COB Video Card's JP7 is a different case: a real TMS9918A's `/INT` is open-drain, so it doesn't matter whether JP7 is open or bridged.

Parts list: [BOM.md](BOM.md#vga-card).

### VGA Card Pro

### Video Card

#### Revision History

**Rev 1.1** (drawn, not yet made; Rev 1.0 is sold first)

- `JP7` is bridged as made, which shorts across D1. On Rev 1.0 it is open, so `/INT` reaches `IRQB` or `NMIB` through D1. Both work, because a real TMS9918A's `/INT` is open-drain.
- U1 and U7 use socket footprints (`Socket_LongPads`) in place of Rev 1.0's `LongPads`.
- Adds the OSHW and A.C. Wright logos to the silkscreen.
- The silkscreen labels `J4` as `VIDEO`. Rev 1.0's says `Video Out`.

**Rev 1.0**

- Initial release, and the board on sale. `Hardware/Video Card/Rev 1.0/` and `Production/Video Card/Rev 1.0/` match the boards JLCPCB made (order Y53). The Gerbers and drill files in the production zip are byte-for-byte what JLCPCB received.

Parts list: [BOM.md](BOM.md#video-card).

### Video Card Pro

## Purchase

I have a few PCBs available on Tindie for those interested in building their own AC6502 system without ordering from a fab directly.

<a href="https://www.tindie.com/stores/acwrightdesign/?ref=offsite_badges&utm_source=sellers_acwrightdesign&utm_medium=badges&utm_campaign=badge_medium"><img src="https://static.tindie.com/badges/tindie-mediums.png" alt="I sell on Tindie" width="150" height="78"></a>

## License

Hardware designs are released under the [CERN Open Hardware Licence Version 2 – Permissive](https://ohwr.org/cern_ohl_p_v2.txt).  
Firmware is released under the MIT License — [KEH Controller](./Firmware/KEH%20Controller/LICENSE), [PS2 Keyboard Controller](./Firmware/PS2%20Keyboard%20Controller/LICENSE), [STP Controller](./Firmware/STP%20Controller/LICENSE).
