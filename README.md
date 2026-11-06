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
- [Shared lines](#shared-lines)
- [Checking the schematics](#checking-the-schematics)
- [Libraries](#libraries)
- [Bill of Materials](#bill-of-materials)
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

**`Hardware/Serial Card/`** — RS-232 serial communication via R6551AP ACIA and MAX232 level shifter.
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

**`Hardware/Keyboard Encoder Helper/`** — ATmega1284-based dual keyboard encoder supporting PS/2 keyboard and 8×8 matrix keyboard simultaneously via 65C22 VIA.

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

Firmware for the ATmega1284 on the Keyboard Encoder Helper. Provides:

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

## Shared lines

Five lines of the 6502 bus are shared by every board on it: `RESB`, `IRQB`, `NMIB`, `RDY` and `BE`. A board may pull one of these lines low, and nothing drives one high. Each line is held high by one 10kΩ pull-up resistor to VCC, on the board with the CPU: the ACE Board, the KIM Board, the VCS Main Board, the COB CPU Card or CPU Card Pro, or the DEV Board. No other board has one. Two pull-ups on the same line would sit in parallel and lower its resistance, so a card that adds its own pull-up changes the machine for every other board. The VIAs and PIAs in the BOMs, the W65C22N and W65C21N, have open-drain interrupt outputs for this reason. A W65C22S drives `IRQB` high as well as low, so it can't share the line without a diode.

The same holds where a board has its own reset circuit. A reset switch, its timer and the transistor that pulls `RESB` low can be on any board, such as the COB Backplane Pro or the Clock Card, but the `RESB` pull-up is only ever on the board with the CPU. Each of those boards draws its pull-ups together, in one group on its schematic.

`SOB` is a CPU pin that isn't on the bus. It is tied to VCC, directly or through a 10kΩ resistor.

A few chips have a pull-up of their own inside the chip, such as an ATmega's reset pin. Where such a pin is wired to `RESB`, its pull-up of 30–60kΩ sits in parallel with the 10kΩ one. That's harmless, because whatever pulls `RESB` low can sink the extra current many times over.

A revision that doesn't follow this yet says so in its known issues in [BOM.md](BOM.md), with what to fit or remove.

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

Shared KiCad symbol and footprint libraries used across all AC6502 hardware projects, with their 3D models in `Models/`. A part is named for what it is and its shape, such as `RJ45 Jack LED` or `CR2032 Holder`, never for a manufacturer's part number, so a replacement part with the same footprint fits without renaming anything. The part numbers to buy are in [BOM.md](BOM.md). Every AC6502 repository carries the same copy of each part.

## Bill of Materials

Every part for every board, by revision, is in **[BOM.md](BOM.md)**, with supplier numbers, known issues, build notes and files to upload to Digi-Key and Mouser. What changed in each revision, and what is known about each one, is in **[REVISIONS.md](REVISIONS.md)**.

## Purchase

I have a few PCBs available on Tindie for those interested in building their own AC6502 system without ordering from a fab directly.

<a href="https://www.tindie.com/stores/acwrightdesign/?ref=offsite_badges&utm_source=sellers_acwrightdesign&utm_medium=badges&utm_campaign=badge_medium"><img src="https://static.tindie.com/badges/tindie-mediums.png" alt="I sell on Tindie" width="150" height="78"></a>

## License

Hardware designs are released under the [CERN Open Hardware Licence Version 2 – Permissive](https://ohwr.org/cern_ohl_p_v2.txt).  
Firmware is released under the MIT License — [KEH Controller](./Firmware/KEH%20Controller/LICENSE), [PS2 Keyboard Controller](./Firmware/PS2%20Keyboard%20Controller/LICENSE), [STP Controller](./Firmware/STP%20Controller/LICENSE).
