# The stock BIOS against the controller

These tests run the real BIOS ROMs on a 65C02 emulator on the Mac, with the controller's core answering at IO 4
(`$8C00`), as the Storage Card's CompactFlash card does on a real machine. The BIOS boots, probes for storage, and
takes BASIC commands typed at its serial console: `SAVE`, `LOAD`, `DIR`, `DEL`, `DISK`, `FORMAT`, `BSAVE` and
`BLOAD`. Nothing in the BIOS is changed or stubbed.

```sh
cmake --preset host && cmake --build --preset host && ctest --preset host
ctest --preset host -R bios -V      # with the table of busy times
```

## The machine

`machine.c` is an AC6502 just big enough for the BIOS:

- a W65C02 (vrEmu6502);
- 32 KB of RAM and the 32 KB ROM;
- an R6551 serial card at IO 5 (`$9000`) for the console, which sends typed bytes only while the BIOS holds RTS
  low, at 19,200 baud;
- the controller at IO 4.

Every other slot is empty and reads as open bus, the last byte on the bus, as a real board's does. The BIOS's probe
relies on that to tell an empty slot from a card.

The controller is the firmware's own `core/` code, on models of its media: an SD card in RAM, and a NOR chip that
keeps the chip's rules (programming only clears bits, erasing a 4 KB sector sets it to `$FF`). A job's cost on a
medium is in microseconds, and the machine counts it in 6502 cycles at its clock, 1 or 2 MHz. So the BIOS's
timeouts, which are counted in cycles, run out when they would on a real machine.

| Media timing | Read a sector | Write a sector | Page program | 4 KB erase |
|---|---|---|---|---|
| SD typical | 0.8 ms | 3 ms | | |
| SDHC worst (the SD specification's limits) | 100 ms | 250 ms | | |
| SDXC worst | 100 ms | 500 ms | | |
| Flash typical (W25Q128JV datasheet) | about 0.21 µs a byte | | 0.4 ms | 45 ms |
| Flash worst | about 0.21 µs a byte | | 3 ms | 400 ms |

Power-on is 250 ms for the RP2350's start, plus the time an SD card in the slot takes to start, up to the
firmware's 1.2 s wait.

## The tests

- `test_bios` runs every case on one ROM, at 1 MHz and 2 MHz, and ends with the table of busy times against the
  BIOS's wait. That wait is 65,536 polls of 13 cycles: 852 ms at 1 MHz and 426 ms at 2 MHz. CTest runs it on
  both ROMs (`bios_1.7`, `bios_2.1.0`).
- `cffs_interop.py` checks the disk format against [cffs](https://github.com/acwright/cffs), whose images are the
  format's reference. An image cffs writes is read through the BIOS, and files the BIOS saves, on the SD card and
  on the built-in drive, list and extract with cffs. CTest runs it when `cffs` and Python 3 are on the PATH
  (`cffs_1.7`, `cffs_2.1.0`).
- `bios_cli` runs the machine from the command line, for trying things by hand:

  ```sh
  build/host/tests/bios/bios_cli tests/bios/roms/BIOS-2.1.0.bin '10 PRINT "HI"' 'SAVE "HI"' 'DIR'
  ```

## The ROMs

The two BIOS versions the boards run, copied from [6502-BIOS](https://github.com/acwright/6502-BIOS) (MIT). Each
was rebuilt from its tag with `make` and matched the binary tracked there byte for byte.

| File | For | Tag | Commit | SHA-256 |
|---|---|---|---|---|
| `roms/BIOS-1.7.bin` | the COB (Storage Card Pro) | `v1.7` | `387d29d` | `49be5865bde74220f37ad10bd773619b17f052b37c89f79c1a3564b7da51d799` |
| `roms/BIOS-2.1.0.bin` | the ACE (ACE SD Adapter) | `v2.1.0` | `6f9e137` | `991ba3c258caec56824ef46ed9dbae5224d824f292cc6a41de9c9e4bf79e8543` |

To take a new BIOS, copy its `BIOS.bin` here under its version and add it to the `foreach` in `CMakeLists.txt`.

## vrEmu6502

`vrEmu6502/` is Troy Schrapel's [vrEmu6502](https://github.com/visrealm/vrEmu6502), under its MIT licence
(`vrEmu6502/LICENSE`), copied unchanged from [6502-PICOCALC](https://github.com/acwright/6502-PICOCALC)'s
`src/cpu/vrEmu6502/`. It is built as it comes, without this firmware's warning flags.
