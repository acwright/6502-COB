# Bench tests on a Pico 2

The firmware can be tested on a Raspberry Pi Pico 2 before a board exists. Each rig has its own build (a preset), and
`rig.py` talks to the firmware's test console over the Pico 2's USB serial port.

## The loopback rig

The `pico2-loopback` build tests the bus with nothing but seven jumper wires. The controller answers on GPIO0–14,
as on the board, and a bus exerciser on the RP2350's second PIO block plays a 6502's side of the bus into it:

| Exerciser | Pin | → | Controller | Pin | Signal |
|---|---|---|---|---|---|
| GP15 | 20 | → | GP8 | 11 | RESB |
| GP16 | 21 | → | GP9 | 12 | RB |
| GP17 | 22 | → | GP10 | 14 | WB |
| GP18 | 24 | → | GP11 | 15 | CS |
| GP19 | 25 | → | GP12 | 16 | A2 |
| GP20 | 26 | → | GP13 | 17 | A1 |
| GP21 | 27 | → | GP14 | 19 | A0 |

No wires on GP0–7 (D0–D7): the exerciser reads them straight off the pads, and drives them for the 6502's writes
through the pads' overrides. With no 4.7k resistors on a bare Pico 2, the pads' own pulls make an undriven read
`$80`, as on the board.

The exerciser times each cycle as a W65C02 at 1 or 2 MHz and the card's front end would. PHI2 is high for 45% of the
cycle, and the strobes fall 30 ns after PHI2 rises. Every cycle strobes RB or WB, whichever card it's for, and only
the controller's own cycles pull CS low. The controller runs as on the board: the bus on PIO0 and core 1, the worker
on core 0, here with a pattern disk in place of the SD card and flash.

```sh
cmake --preset pico2-loopback && cmake --build --preset pico2-loopback
picotool load -f -x build/pico2-loopback/rp2350/*.uf2
python3 tests/bench/rig.py wires "sweep 2" "bsy 2" "soak 2 3600"
```

`rig.py` sends each command and prints the answer; its exit status is 1 if any answer reports a failure. The
commands are listed at the top of `rp2350/loopback.c`. `wires` first: it checks each jumper both ways.

### Measured on the loopback rig

Firmware 0.1.0 at 150 MHz, measured on 18 November 2026. Each result held at both 1 MHz and 2 MHz.

| What | Measured | Needed |
|---|---|---|
| Read data on D0–D7 after the controller sees RB fall | Right in 1,000,064 of 1,000,064 samples at each delay from 4 clocks (26.7 ns); wrong at 3 (`sweep MHZ 7813`) | By the 6502's latch: H − 40 ns after RB, 185 ns at 2 MHz |
| BSY in status, read 4 cycles after a command or after a sector's last byte is written | `$80` | `$80` |
| DRQ clear in status, read 4 cycles after a sector's last byte is read | `$50` | `$50` |
| Data reads 4 cycles apart, as an unrolled `lda` loop makes them | 284,160 bytes, none wrong | None wrong |
| Read and Write Sectors, data 15 cycles apart as the BIOS loops, an hour at each speed | 194,463 sectors, none wrong, no failed command | None wrong |
| Core 1, from taking an access to the register copy being current | 97% of 101.6 million accesses under 1 µs, all reads under 1.8 µs, one write at 2.0 µs | Before our next access: at least 4 cycles later, 2 µs at 2 MHz |

The data's 26.7 ns adds to the board's own delays: the 74LVC541 on the way in, the input synchroniser, and the
74LVC4245A on the way out. By the parts' data sheets that comes to about 82 ns after RB falls, still well inside
the 6502's latch.

The one 2.0 µs write is at the edge of the 2 µs at 2 MHz, and which register it went to wasn't recorded. A write
that makes the controller busy (a command, or a sector's last byte) puts BSY in the copy before anything else, so
a status read that soon still sees BSY: that's the BSY row above.

## The media rig

The `pico2-media` build tests the SD card and the flash chip on breakouts, with no bus. The SD card is on the
board's own pins. The flash can't be: a Pico 2 doesn't bring out GPIO24 and 25. Pin numbers are the Pico 2's header.

| Breakout pin | Pico 2 | Pin | Board signal |
|---|---|---|---|
| microSD 5V | VBUS | 40 | (5 V from USB; the breakout makes its own 3.3 V) |
| microSD GND | GND | 23 | |
| microSD DO | GP16 | 21 | SD DAT0 |
| microSD CS | GP17 | 22 | SD DAT3 |
| microSD CLK | GP18 | 24 | SD CLK |
| microSD DI | GP19 | 25 | SD CMD |
| microSD CD | GP20 | 26 | SD_CD |
| flash VCC | 3V3(OUT) | 36 | |
| flash GND | GND | 38 | |
| flash CS | GP15 | 20 | |
| flash CLK | GP14 | 19 | |
| flash DI | GP27 | 32 | |
| flash DO | GP28 | 34 | |
| green LED, through 330 Ω to GND | GP21 | 27 | LED_SD |
| red LED, through 330 Ω to GND | GP22 | 29 | LED_ACT |

The microSD breakout is Adafruit's "5V ready" one. Leave its 3v pin unconnected: it's the output of its own
regulator. Its CD is the other way up from the board's: the socket's switch grounds it with no card in, so the rig
reads a card as high, with the pad's pull-up (`FW_SD_CD_CARD_IN`). Its level shifter also delays the card's replies
too much for 25 MHz, so the rig runs the card at 12.5 MHz (`FW_SD_HZ`). The flash breakout is a W25Q64JVSIQ; its pins
are labelled D0 (the chip's DO) and D1 (its DI). The flash clock is on GP14, not the SPI1 clock on GP26, because the
first rig's Pico 2 has a GP26 that can't drive low.

```sh
cmake --preset pico2-media && cmake --build --preset pico2-media
picotool load -f -x build/pico2-media/rp2350/*.uf2
python3 tests/bench/rig.py pins info "test flash" "test sd"
```

Run `pins` first, on any Pico 2 not used on a rig before. It drives each pad both ways and reads it back, and reads
each pin against the pad's pull-up and pull-down. A pad that can't drive is a fault in the Pico 2, and nothing on
that pin will work. `adc` measures GP26 to GP28 in volts; `flashprobe` and `flashwires` find a flash wire that's
swapped or doesn't reach. The commands are listed at the top of `rp2350/mediarig.c`.

`test flash` and `test sd` write every sector of each disk the medium holds, up to the 256 the BIOS can reach, read
them back, and compare them byte by byte and by checksum. Then they read one sector of each disk above the medium's
N, to check the mirroring. On the flash, the same data is written a second time, and every sector should be
skipped as unchanged.

### Measured on the media rig

Firmware 0.1.0, measured on 19 November 2026.

| What | Measured | Needed |
|---|---|---|
| W25Q64JVSIQ: JEDEC ID, at 25 MHz | `EF 40 17`: 8 MB, N = 8 | |
| Flash: all 16,384 sectors written, read back and compared, twice | 0 wrong, checksums equal | None wrong |
| Flash: disks 8–255, one sector each | All mirror disks 0–7 | All |
| Flash: the same data written again | 16,384 of 16,384 skipped as unchanged | All |
| Flash: longest write of a sector, erasing its 4 KB (16,384 writes) | 50.4 ms; the chip's longest erase 41.0 ms, longest page program 373 µs | Inside the BIOS's wait: 426 ms at 2 MHz |
| Flash: a sector written into blank space, with no erase | 2.8 ms | |
| Flash: a sector read | 217 µs (2.40 MB/s) | |
| SD card: a SanDisk 16 GB SDHC (SU16G, 2010), started | 31,116,288 sectors from its CSD, as macOS counts them; N = 15,193 | |
| SD card: all 524,288 sectors of disks 0–255 written, read back and compared, at 12.5 MHz | 0 wrong, checksums equal; no CRC retries, no write retried | None wrong |
| SD card: longest write of a sector | 190 ms (2.0 ms on average) | Inside the BIOS's wait: 426 ms at 2 MHz |
| SD card: longest read of a sector | 1.5 ms (0.76 ms on average) | |
| SD card: the same test over disks 0–3, at each clock | 25 MHz: 518 of about 4,100 data responses misread, 17 writes failed. 18.75 MHz and 12.5 MHz: none wrong | |
| SD card: at power-on | Started in 21–23 ms: 1 CMD0, 5–6 ACMD41s | Inside the 1.2 s the firmware waits |
| SD card: put in while powered, 11 times | Started every time, in 244–649 ms; it took 10–91 CMD0s, 5 ms apart, to answer | Within the 1 s allowed |
| Card detect | Each insertion and removal seen, 50 ms debounce; the green LED and the medium followed | |
