# Bench tests on a Pico 2

The firmware can be tested on a Raspberry Pi Pico 2 before a board exists. Each rig has its own build (a preset), and
`loopback.py` talks to the firmware's test console over the Pico 2's USB serial port.

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
python3 tests/bench/loopback.py wires "sweep 2" "bsy 2" "soak 2 3600"
```

`loopback.py` sends each command and prints the answer; its exit status is 1 if any answer reports a failure. The
commands are listed at the top of `rp2350/loopback.c`. `wires` first: it checks each jumper both ways.

### Measured on the loopback rig

Firmware 0.1.0 at 150 MHz, measured on 18 November 2026. Each result held at both 1 MHz and 2 MHz.

| What | Measured | Needed |
|---|---|---|
| Read data on D0–D7 after the controller sees RB fall | Right in 2,048 of 2,048 samples from 4 clocks (26.7 ns); wrong at 3 | By the 6502's latch: H − 40 ns after RB, 185 ns at 2 MHz |
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

The `pico2-media` build takes an SD card breakout and a W25Q flash breakout. Its wiring is at the top of
`rp2350/boards/pico2_media.h`.
