# KEH Controller

## Overview

The KEH (Keyboard Encoder Helper) Controller is firmware for the ATMega1284P microcontroller that provides dual keyboard input support for 6502-based computer systems. It can simultaneously handle both PS/2 keyboard input and custom keyboard matrix input, converting keypresses to ASCII codes and outputting them through a 6522 VIA (Versatile Interface Adapter) interface.

## Features

- **Dual Input Support**: Handles both PS/2 keyboards and 8x8 keyboard matrix simultaneously
- **ASCII Conversion**: Converts PS/2 scancodes and matrix keypresses to ASCII characters
- **Always Uppercase Letters**: Letters are always output as uppercase ASCII regardless of modifiers
- **Modifier Keys**: Shift (symbols/numbers only) and Ctrl (control codes)
- **Buffered Input**: Uses circular buffers to prevent data loss during rapid typing
- **Debounced Matrix Scanning**: Hardware debouncing for reliable matrix keyboard operation
- **Enable/Disable Control**: Independent enable signals for PS/2 and matrix inputs
- **Shared Joystick Ports**: Releases PORT A / PORT B when disabled so the 6502 can read the two Atari 2600-compatible joysticks that share those ports

## Hardware Connections

### ATMega1284P Pin Assignments

#### VIA PORT A (Pins 24-31)
Used for row scanning (matrix mode) or ASCII output (PS/2 mode):
- PA0 (Pin 24) - VIA_PA0 / Row 0 / Data Bit 0
- PA1 (Pin 25) - VIA_PA1 / Row 1 / Data Bit 1
- PA2 (Pin 26) - VIA_PA2 / Row 2 / Data Bit 2
- PA3 (Pin 27) - VIA_PA3 / Row 3 / Data Bit 3
- PA4 (Pin 28) - VIA_PA4 / Row 4 / Data Bit 4
- PA5 (Pin 29) - VIA_PA5 / Row 5 / Data Bit 5
- PA6 (Pin 30) - VIA_PA6 / Row 6 / Data Bit 6
- PA7 (Pin 31) - VIA_PA7 / Row 7 / Data Bit 7

#### VIA PORT B (Pins 0-7)
Used for column scanning (matrix mode) or ASCII output (matrix output):
- PB0 (Pin 0) - VIA_PB0 / Column 0 / Data Bit 0
- PB1 (Pin 1) - VIA_PB1 / Column 1 / Data Bit 1
- PB2 (Pin 2) - VIA_PB2 / Column 2 / Data Bit 2
- PB3 (Pin 3) - VIA_PB3 / Column 3 / Data Bit 3
- PB4 (Pin 4) - VIA_PB4 / Column 4 / Data Bit 4
- PB5 (Pin 5) - VIA_PB5 / Column 5 / Data Bit 5
- PB6 (Pin 6) - VIA_PB6 / Column 6 / Data Bit 6
- PB7 (Pin 7) - VIA_PB7 / Column 7 / Data Bit 7

#### Control Signals
- Pin 8 (VIA_CA1) - PS/2 Data Ready strobe (output)
- Pin 9 (VIA_CA2) - PS/2 Enable (input, active low)
- Pin 10 (PS2CLK) - PS/2 Clock input
- Pin 11 (PS2DATA) - PS/2 Data input
- Pin 12 (VIA_CB1) - Matrix Data Ready strobe (output)
- Pin 13 (VIA_CB2) - Matrix Enable (input, active low)

### PS/2 Keyboard Interface

Connect a PS/2 keyboard to:
- **CLK**: Pin 10 (PS2CLK)
- **DATA**: Pin 11 (PS2DATA)
- **VCC**: +5V
- **GND**: Ground

### Keyboard Matrix Interface

The firmware supports an 8x8 keyboard matrix (64 keys maximum):
- **Rows**: Connected to PA0-PA7 (Pins 24-31)
- **Columns**: Connected to PB0-PB7 (Pins 0-7)

Each key connects a row to a column when pressed. The matrix is scanned with rows driven low and columns read with pull-ups.

### Joystick Interface

PORT A and PORT B are shared between this encoder and two Atari 2600-compatible
joysticks. The Keyboard Encoder Helper has no DB-9 connectors of its own — the
sticks arrive on the same 2×6 box headers that carry the VIA ports (`J1` PORT B,
`J2` PORT A), or across the `J4` DB-25 keyboard cable. Three helper boards reach
those lines:

- **Keyboard Helper** — the usual path. Its `J7` DB-25 takes the whole keyboard
  cable from KEH's `J4`, and the two DB-9s it carries (`J1` JOYSTICK A, `J2`
  JOYSTICK B) are those same port lines brought back out, with the 1kΩ pull-ups
  (`R1`–`R16`) fitted. Its `J3`/`J4` 2×6 headers are the same two sticks again.
- **Joystick Helper** — converts a single port header to a DB-9 with the 1kΩ
  pull-ups fitted, which is where Atari 2600 compatibility comes from.
- **GPIO Helper** — not a stick, but its `J1` PORT A side is eight push buttons
  to ground behind 1kΩ pull-ups, so it stands in for one electrically while
  testing.

The BIOS reads the two sticks through those same ports:

| BIOS routine | BASIC | VIA port | KEH header | Encoder released by |
|---|---|---|---|---|
| `ReadJoystick1` (`$A048`) | `JOY(1)` | PORT B | `J1` | `CB2` high — matrix encoder off |
| `ReadJoystick2` (`$A04B`) | `JOY(2)` | PORT A | `J2` | `CA2` high — PS/2 encoder off |

> Note the naming trap: the Keyboard Helper's *JOYSTICK A* connector is PORT A,
> which is `JOY(2)`, and *JOYSTICK B* is PORT B, which is `JOY(1)`.

Each read returns the port raw, as a bitmask:

```
Bit:  7   6   5   4   3   2   1   0
      R   L   D   U   Y   X   B   A
```

The ports are **active low** — every line is pulled high and grounded by the
stick's switch — so a held button reads `0` and an untouched stick reads `$FF`.

This is the firmware's obligation in the joystick path: when `CA2` or `CB2`
goes high, it releases the corresponding port within 100 µs so the 6502 can
read the stick directly — the same arrangement a C64 has with a CIA port.
`disablePS2()` releases PORT A and `disableMatrix()` releases PORT B, both by
returning the pins to `INPUT_PULLUP` rather than bare `INPUT`. That matters
here in particular, since a KEH port can legitimately have no external
pull-ups fitted at all — see the helper board list above.

The BIOS reads a stick as `KBDisable` → settle → read the port directly →
`KBEnable`. Nothing is transmitted over the shared lines, so there is nothing
for one stick to corrupt on the other's behalf — **both sticks read correctly
even when held at the same time.** An earlier design had the encoder push
joystick state to the 6502 as control bytes over the keyboard channel instead;
that could not report a held button on the port it was reporting over, and was
abandoned. See
[BIOS `PLAN.md` §2](https://github.com/acwright/6502-BIOS/blob/main/PLAN.md)
for the full account.

**Measured release latency: to be measured later.** This is the figure the
BIOS's `KBDisable` settle wait is sized against. Cycle-counting the compiled
firmware puts the worst-case code path at ~17 µs against a 100 µs budget, but
that excludes a PS/2 interrupt landing in the window and says nothing about how
long the bus takes to charge through a pull-up, so the published number comes
from a scope. See [PLAN.md](../../PLAN.md).

## Keyboard Matrix Layout

```
       PB0    PB1    PB2    PB3    PB4    PB5    PB6    PB7
PA0:    `      1      2      3      4      5      6      7
PA1:    8      9      0      -      =      BS     ESC    TAB
PA2:    Q      W      E      R      T      Y      U      I
PA3:    O      P      [      ]      \      INS    CAPS   A
PA4:    S      D      F      G      H      J      K      L
PA5:    ;      '    ENTER   DEL   SHIFT    Z      X      C
PA6:    V      B      N      M      ,      .      /      UP
PA7:  CTRL   MENU    ALT   SPACE   FN    LEFT   DOWN  RIGHT
```

**Special Keys:**
- BS = Backspace (0x08)
- ESC = Escape (0x1B)
- TAB = Tab (0x09)
- INS = Insert (0x1A)
- DEL = Delete (0x7F)
- ENTER = Enter (0x0D)
- Arrow keys: UP (0x1E), LEFT (0x1C), DOWN (0x1F), RIGHT (0x1D)

**Ignored Keys:**
- Caps Lock, Menu/GUI, Alt, Fn — produce no output and track no state

## Operation Modes

### PS/2 Mode
When VIA_CA2 (Pin 9) is pulled LOW:
- PS/2 keyboard is enabled
- Scancodes are converted to ASCII
- Output appears on PORT A (PA0-PA7)
- VIA_CA1 pulses low when data is ready

### Matrix Mode
When VIA_CB2 (Pin 13) is pulled LOW:
- Matrix keyboard is enabled
- Matrix is scanned every 10ms
- Keys are debounced (stable for 2 scans)
- Output appears on PORT B (PB0-PB7)
- VIA_CB1 pulses low when data is ready

### Dual Mode
Both keyboards can operate simultaneously if both enable signals are active.

### Joystick Reads
When an enable signal goes HIGH the firmware releases that port so the joystick
sharing it can be read by the 6502 — see [Joystick Interface](#joystick-interface).

## ASCII Character Mapping

### Modifier Priority

1. **Ctrl** — If held, produce control code. Shift is ignored.
2. **Shift** — If held (no Ctrl), produce shifted symbol. Letters unaffected.
3. **Base** — No modifier: produce base ASCII (letters always uppercase).

### Control Characters (Ctrl+Key)

- Ctrl+2 = 0x00 (NUL)
- Ctrl+A-Z = 0x01-0x1A
- Ctrl+[ = 0x1B (ESC)
- Ctrl+\ = 0x1C (FS)
- Ctrl+] = 0x1D (GS)
- Ctrl+6 = 0x1E (RS)
- Ctrl+- = 0x1F (US)

### Shifted Symbols

Shift only affects number and symbol keys (not letters):

| Base | Shifted | | Base | Shifted |
|------|---------|-|------|---------|
| 1 → ! | 2 → @ | | 3 → # | 4 → $ |
| 5 → % | 6 → ^ | | 7 → & | 8 → * |
| 9 → ( | 0 → ) | | - → _ | = → + |
| [ → { | ] → } | | \ → \| | ; → : |
| ' → " | , → < | | . → > | / → ? |
| ` → ~ | | | | |

### Printable Characters

Letters are always uppercase (A-Z). Numbers, symbols, space, and navigation keys follow standard ASCII.

## Build Instructions

### Prerequisites

1. **Install PlatformIO**
   ```bash
   # Using pip
   pip install platformio
   
   # Or install PlatformIO IDE extension for VS Code
   ```

2. **Install MiniPro Programmer Software** (for uploading)
   ```bash
   # macOS (using Homebrew)
   brew install minipro
   
   # Linux
   sudo apt-get install minipro
   
   # Or build from source: https://gitlab.com/DavidGriffith/minipro
   ```

### Building the Firmware

1. **Navigate to the project directory:**
   ```bash
   cd "Firmware/KEH Controller"
   ```

2. **Build the firmware:**
   ```bash
   # Build for ATMega1284P (default)
   pio run -e atmega1284p
   
   # Or build for ATMega1284
   pio run -e atmega1284
   ```

3. **Build output:**
   The compiled firmware will be located at:
   ```
   .pio/build/atmega1284p/firmware.hex
   ```

### Uploading the Firmware

The project uses a MiniPro TL866 programmer for uploading.

1. **Connect the MiniPro programmer** to your ATMega1284P chip

2. **Upload firmware and fuses:**
   ```bash
   # Upload to ATMega1284P
   pio run -e atmega1284p -t upload
   
   # Or upload to ATMega1284
   pio run -e atmega1284 -t upload
   ```

3. **Manual upload (if needed):**
   ```bash
   # Flash the program
   minipro -p "ATMEGA1284P@DIP40" -c code -w .pio/build/atmega1284p/firmware.hex
   
   # Flash the fuses
   minipro -p "ATMEGA1284P@DIP40" -c config -w fuses.cfg --fuses
   ```

## Fuse Configuration

The `fuses.cfg` file contains the ATMega1284P fuse settings:

```properties
lfuse = 0xff   # Low fuse
hfuse = 0xff   # High fuse  
efuse = 0xff   # Extended fuse
lock = 0xff    # Lock bits (unprogrammed, not written)
```

**Fuse Settings:**
- **Low Fuse (0xFF)**: Low power crystal oscillator (8.0–16.0 MHz) for the
  on-board 16 MHz crystal (`Y1`), slowly-rising-power start-up (16K CK + 65 ms),
  no clock divide (CKDIV8 off), clock output disabled
- **High Fuse (0xFF)**: Default settings
- **Extended Fuse (0xFF)**: Default settings
- **Lock Bits (0xFF)**: No memory lock protection

> **Note**: The low fuse selects a *crystal* oscillator, which is what this board
> needs — the Keyboard Encoder Helper carries a 16 MHz HC49-U crystal across
> XTAL1/XTAL2. Full Swing is a different setting (`CKSEL3:1 = 011`) and is not
> used here. The ACE board's `AB Controller` runs from a full-can oscillator
> module instead and therefore uses the *external clock* setting
> (`lfuse = 0xE0`); the two are not interchangeable.

> **Note**: Lock bits are left unprogrammed on all of these boards. The upload
> command writes fuses only (`--fuses`, no `--lock`), so the `lock` line above is
> recorded for reference and never programmed.

⚠️ **Warning**: Incorrect fuse settings can brick your microcontroller. Verify fuse values are appropriate for your hardware configuration before programming.

## Dependencies

The firmware requires the following library (automatically installed by PlatformIO):

- **CircularBuffer** (v1.4.0+) by Roberto Lo Giacco
  - Provides interrupt-safe circular buffers for keyboard data

## Project Structure

```
KEH Controller/
├── platformio.ini          # PlatformIO configuration
├── fuses.cfg              # AVR fuse configuration
├── src/
│   └── main.cpp           # Main firmware source code
├── include/               # Header files (if any)
├── lib/                   # Local libraries
└── test/                  # Unit tests
```

## Troubleshooting

### Build Issues

**Problem**: PlatformIO not found
```bash
# Solution: Install or update PlatformIO
pip install -U platformio
```

**Problem**: Library dependency errors
```bash
# Solution: Clean and rebuild
pio run -t clean
pio run
```

### Upload Issues

**Problem**: MiniPro not found
```bash
# Solution: Ensure minipro is installed and in PATH
which minipro
```

**Problem**: Chip not detected
- Check that the chip is properly seated in the programmer
- Verify you're using the correct chip model (ATMEGA1284P vs ATMEGA1284)
- Check for proper power supply to the programmer

### Runtime Issues

**Problem**: No keyboard response
- Verify enable signals (CA2/CB2) are at correct logic levels
- Check PS/2 clock and data connections
- Verify matrix keyboard connections
- Ensure VIA interface connections are correct

**Problem**: `JOY(1)`/`JOY(2)` return keystrokes or a stuck value
- Confirm the BIOS is v1.5 or later — older BIOS reads the port before the
  encoder has released it (see [Joystick Interface](#joystick-interface))
- Verify the stick's pull-ups are present (the Keyboard Helper and Joystick
  Helper carry them; a bare box-header connection does not)

**Problem**: Incorrect characters output
- Check for proper pull-up resistors on PS/2 lines
- Verify keyboard matrix wiring matches the defined layout
- Test with a known-good PS/2 keyboard

## License

See the main repository LICENSE file for licensing information.

## Contributing

This firmware is part of the 6502 computer project. Contributions and improvements are welcome through the main repository.

