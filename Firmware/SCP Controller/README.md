# SCP Controller

Firmware for the RP2350A on the **Storage Card Pro 1.1**. The card answers on the 6502 bus as the Storage Card's
CompactFlash card does, at `$8C00–$8C07` by default, so the stock BIOS's `LOAD`, `SAVE`, `DIR` and `FORMAT` work
unchanged. The disks are on an SD card when one is in the slot, and on the card's built-in flash drive when not.

> **Not finished.** The firmware is being written, and nothing here has run on a Storage Card Pro yet: no Rev 1.1
> board has been made. So far the controller's logic is tested on the Mac, against the stock BIOS in an emulator, and
> its bus is tested on a Pico 2 wired to time itself (`tests/bench/`, where the measured times are). The board's build
> doesn't answer on the bus yet: it waits for the SD card and flash drivers. Don't fit it to a board expecting storage
> to work.

The ACE SD Adapter 1.1 in [6502-ACE](https://github.com/acwright/6502-ACE) has the same circuit. Its firmware, the
**ASDA Controller**, is a copy of this one: the two are the same, file for file, except `product.h` (the board's name)
and this README. `Tools/firmware/twins.py --check --all` checks that.

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
| `pico2-breadboard` | A Pico 2 on a breadboard copy of the board, on the ACE's `STORAGE` header |

The Pico 2 builds are for testing the firmware before a board exists. Each one's wiring is at the top of its header in
`rp2350/boards/`.

## Folders

| Folder | What it holds |
|---|---|
| `core/` | The controller's logic in plain C, with no Pico SDK, so the unit tests run it on the Mac |
| `rp2350/` | The RP2350 side: start-up, and the header for each build's pins in `boards/` |
| `tests/unit/` | The unit tests |
| `tests/bench/` | The Pico 2 test rigs: the wiring, and `loopback.py`, which drives the loopback build's test console |
| `tests/bios/` | The stock BIOS 1.7 and 2.1.0 running against the core in a 65C02 emulator, with `cffs` checking the disk format; see its README |
| `cmake/` | The SDK's fetch, and the source hash the build stamps into the firmware |

## License

MIT; see [LICENSE](LICENSE). The board's header, `rp2350/boards/ac6502_sd.h`, is derived from the Pico SDK's
`pico2.h`, under the SDK's BSD-3-Clause licence, as it says. The tests carry two things from elsewhere, both MIT:
Troy Schrapel's vrEmu6502 in `tests/bios/vrEmu6502/`, with its licence, and the BIOS ROMs from 6502-BIOS in
`tests/bios/roms/`.
