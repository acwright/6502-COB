# SCP Controller

Firmware for the Raspberry Pi Pico 2 on the **Storage Card Pro 1.1**. The card answers on the 6502 bus as the Storage
Card's CompactFlash card does, at `$8C00–$8C07` with its window jumper J5 on `$8C00`, so the stock BIOS's `LOAD`,
`SAVE`, `DIR` and `FORMAT` work unchanged. The disks are on an SD card when one is in the slot, and on the card's
built-in flash drive when not.

Version 1.0.0. `SCP Controller.uf2`, in this folder, is the build to flash.

> **Untested on a card.** No Storage Card Pro 1.1 has been made yet, so this firmware hasn't answered a real 6502.
> The controller's logic is tested on the Mac, against the stock BIOS 1.8 and 2.2.0 in an emulator. On Pico 2 test
> rigs its bus is timed, its SD card and flash drivers run on real media, and the stock BIOS runs against it, both
> on real media and through its bus (`tests/bench/`, where the measured times are).

The ACE SD Adapter 1.1 in [6502-ACE](https://github.com/acwright/6502-ACE) has the same circuit. Its firmware, the
**ASDA Controller**, is a copy of this one: the two are the same, file for file, except `product.h` (the board's name)
and this README. `Tools/firmware/twins.py --check --all` checks that.

## What it does

The Pico 2 answers the eight registers of a CompactFlash card in 8-bit True IDE mode, as the BIOS uses them:

| Address | Read | Write |
|---|---|---|
| `$8C00` | Data | Data |
| `$8C01` | Error | Features |
| `$8C02` | Sector count | Sector count |
| `$8C03`–`$8C05` | LBA bits 0–23 | LBA bits 0–23 |
| `$8C06` | LBA bits 24–27 | LBA bits 24–27 |
| `$8C07` | Status | Command |

The commands are Read Sectors (`$20`, `$21`), Write Sectors (`$30`, `$31`), IDENTIFY (`$EC`), Set Features (`$EF`),
Erase Sectors (`$C0`) and Flush (`$E7`). Any other command answers with an error (`ABRT`). IDENTIFY gives the model
"AC6502 Storage Card Pro", the firmware version, the Pico's own serial number and the medium's size. Its words
128–137 carry the longest busy times, the medium answering, its *N* and the error count since power-on, for a 6502
program to read (`core/identify.h` lists them).

**The medium.** The controller chooses the medium as each command starts: the SD card if one is in and ready,
otherwise the built-in drive. A card can go in or come out between commands, and the next command uses whichever
medium is there. A card pulled during a command ends that command with an error.

**The disks.** The BIOS divides a medium into 1 MB disks, `DISK 0` to `DISK 255`. A medium of *N* whole megabytes
holds *N* disks, and a higher disk number reaches disk number mod *N*. On the 16 MB built-in drive, `DISK 16` is
`DISK 0` and `DISK 20` is `DISK 4`, so a `SAVE` to a higher disk lands on the lower one. An SD card of 256 MB or more
holds all 256 disks. Sector *n* on the SD card is the BIOS's sector *n*, as on a CompactFlash card, so an image of a
CompactFlash card written to an SD card works unchanged, and [cffs](https://github.com/acwright/cffs) reads and
writes either on a computer. A computer can't open the card as a drive: it holds the BIOS's own file system, not FAT.

**The built-in drive.** A W25Q128JVFIQ, 16 MB. It stores each byte inverted, so a blank chip reads as zeros rather
than `$FF`. A sector written finishes on the chip before the BIOS sees the command done, so turning the machine off
straight after a `SAVE` loses nothing. Each `SAVE` rewrites the disk's directory sector, and the chip's sectors last
about 100,000 erases, so a disk's directory wears out after some 100,000 `SAVE`s.

**Power-on and reset.** From power-on, every read answers `$80` (busy) until a medium is ready. With a card in, the
controller waits up to 1.2 s for the card to start, then answers from the built-in drive if the card hasn't. The
Pico 2 starts in about 55 ms, so even a card that never starts leaves the controller answering inside the stock
BIOS's wait for storage. A reset (`RESB`) ends any command, and the controller stays busy until a flash erase or
write in progress has finished.

## SD cards

Use an SDHC card (4–32 GB). SDXC cards work too. Tested: a SanDisk 16 GB SDHC and a Samsung EVO 64 GB SDXC, every
sector of all 256 disks written and read back. SDSC cards (2 GB and smaller) are supported but untested on a real
card. The SD card runs at 12.5 MHz.

**At 2 MHz.** The BIOS waits about 0.85 s for a command to finish at 1 MHz, and half that, 0.43 s, at 2 MHz. Every
medium fits inside the 1 MHz wait. At 2 MHz the slowest writes can take longer: the SD specification allows an SDXC
card up to 0.5 s, and the flash chip's data sheet allows the built-in drive's erase and write together 0.45 s. The
cards tested took at most 190 ms (the SDHC card) and 89 ms (the SDXC card), and the built-in drive's chip 50 ms.
If a write does overrun the wait, the BIOS reports an error for a write that then finishes. A `?DEL ERROR` has still
deleted the file. A `?SAVE ERROR` leaves the data written but no directory entry for it, so `SAVE` again.

## The LEDs

| LED | Pin | Lit |
|---|---|---|
| D2, green | GPIO21 | While the SD card is the medium answering |
| D1, red, and the case LED on J1 | GPIO22 | While a medium is busy, and for 50 ms after each command |

Both LEDs light together for a quarter of a second at power-on.

## The pins

| GPIO | 0–7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 26 | 27 | 28 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Net | D0–D7 | RESB | RB | WB | CS | A2 | A1 | A0 | FLASH_CS | SD DAT0 | SD DAT3 | SD CLK | SD CMD | SD CD | LED_SD | LED_ACT | FLASH_CLK | FLASH_DI | FLASH_DO |

D0–D7 come through the 74LVC4245A, and `RESB`, `RB`, `WB`, `CS` and A0–A2 through the 74LVC541. `CS` is the select
from the window jumper J5. The SD card is on SPI0 and the built-in drive on SPI1. `rp2350/boards/ac6502_sd_pico2.h`
holds the map.

## Flashing it

The Pico 2 needs flashing once, when it's first fitted, and again for each new version.

1. Either leave the machine switched on, or take the card out of the machine. Never power the machine from the
   Pico 2's USB: the module's USB 5 V reaches the card's 5 V, and so the bus's, through the module's diode.
2. Hold the Pico 2's BOOTSEL button and plug a micro-USB cable from a computer into the Pico 2. Let go of BOOTSEL.
   A drive named `RP2350` appears.
3. Copy `SCP Controller.uf2` onto that drive. The Pico 2 restarts with the firmware, and the drive goes away.

`picotool load -x "SCP Controller.uf2"` does the same from a terminal, with `-f` if the Pico 2 is already running
this firmware. A Pico 2 bought on its own may come with another bootloader and partition table, which can make the
firmware vanish after it's copied. `picotool erase` and then `picotool reboot -u` clear them; then copy the `.uf2`
again.

## The USB port

The Pico 2's USB is a serial port for diagnostics. Open it in any terminal, at any speed. The firmware prints its
banner when the port opens (the source hash differs from build to build):

```
SCP Controller 1.0.0 (source 0123456789ab), Storage Card Pro 1.1 / ACE SD Adapter 1.1
Copyright (c) 2026 A.C. Wright Design
```

Press any key for a report. One looks like this, with an SD card in; the numbers are an example:

```
Answering since 209 ms after start: a medium is ready
Medium now: SD card, N = 15193
SD card: ready, 31116288 sectors, N = 15193
Built-in drive: 16 MB, N = 16
Jobs: SD 12 reads, 3 writes; built-in 0 reads, 0 writes; 0 errors
Longest busy: 21100 us (SD write 21100, built-in write 0)
Bus: 6650 reads, 1580 writes, 1 resets; longest handling 1160 ns
```

*N* is the number of 1 MB disks the medium holds; above 256 the BIOS reaches only the first 256. The longest busy
time is the one to compare with the BIOS's waits under *At 2 MHz*.

## Building it

It needs CMake 3.25 or newer, Ninja, the Arm GNU Toolchain (`arm-none-eabi-gcc`) and `picotool`. On macOS:

```sh
brew install cmake ninja picotool
brew install --cask gcc-arm-embedded
```

The Raspberry Pi Pico SDK 2.1.1 is cloned into `build/` the first time an RP2350 build is configured, with only the
TinyUSB submodule. To use an SDK already on disk instead, set `PICO_SDK_PATH`; it must be release 2.1.1.

```sh
cmake --preset board && cmake --build --preset board    # build/board/rp2350/SCP Controller.uf2
cmake --preset host && cmake --build --preset host && ctest --preset host
```

| Preset | What it builds |
|---|---|
| `board` | The firmware for the Storage Card Pro 1.1 and the ACE SD Adapter 1.1 |
| `host`, `host-asan` | The controller's core, its unit tests and the BIOS tests, on the Mac; `host-asan` adds AddressSanitizer and UBSan |
| `pico2-loopback` | A Pico 2 that times its own bus: GPIO15–21 wired to GPIO8–14 |
| `pico2-media` | A Pico 2 with an SD card breakout and a W25Q flash breakout, driven over USB |
| `pico2-breadboard` | The boards' firmware on a Pico 2 with the media rig's breakouts, whose card detect is the other way up |

The Pico 2 builds are for testing the firmware without a board. Each one's wiring is at the top of its header in
`rp2350/boards/`.

The build stamps the version and a hash of the sources into the `.uf2`. After changing the firmware, copy the
`board` build over `SCP Controller.uf2` in this folder, and in the ASDA Controller's folder its own build over
`ASDA Controller.uf2`. `Tools/firmware/twins.py --check` fails while a tracked `.uf2` was built from other sources.

## Folders

| Folder | What it holds |
|---|---|
| `core/` | The controller's logic in plain C, with no Pico SDK, so the unit tests run it on the Mac |
| `rp2350/` | The RP2350 side: the bus program, the SD card and flash drivers, start-up, and the header for each build's pins in `boards/` |
| `tests/unit/` | The unit tests |
| `tests/bench/` | The Pico 2 test rigs: the wiring, the measured times, and `rig.py`, which drives the rig builds' test consoles |
| `tests/bios/` | The stock BIOS 1.8 and 2.2.0 running against the core in a 65C02 emulator, with `cffs` checking the disk format; see its README |
| `cmake/` | The SDK's fetch, and the source hash the build stamps into the firmware |

## License

MIT; see [LICENSE](LICENSE). The board headers in `rp2350/boards/` include the Pico SDK's `pico2.h`,
which is under the SDK's BSD-3-Clause licence. The tests carry two things from elsewhere, both MIT:
Troy Schrapel's vrEmu6502 in `tests/bios/vrEmu6502/`, with its licence, and the BIOS ROMs from 6502-BIOS in
`tests/bios/roms/`.
