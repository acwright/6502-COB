# Revisions

Every revision of every board in this repository, and what is known about each. The audit date is at the end.

**Status** says what has happened to a revision:

- **Made, matches order:** JLCPCB's own copy of the order is byte-identical to the production zip here, and the PCB file regenerates the same copper, mask, outline and holes. This compares files with the order. It says nothing about whether the board works: that's **Tested**.
- **Made, not compared:** the board exists, but its files haven't been compared with an order.
- **Ordered:** placed, and not yet arrived.
- **Drawn:** the files are complete, and the board hasn't been ordered.
- **Never made**, or **To confirm** where nothing on record says either way.

**Holes** is how far the corner mounting holes sit from the board's edges. The standard is 6 mm, and 5 mm on the ACE Board, the CF Adapter and the Keyboard Helper. A dash means a card or cart, which has no corner holes.

| Board | Rev | Status | Tested | Order | Ordered | Made from | Tindie stock | Size (mm) | Holes | Top panel | Enclosure | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Backplane | 1.0 | Made, matches order | Yes | Y50 | 2024-07-03 | `3e494e3` | 3 | 100×100 | 6 mm | yes | — |  |
| Backplane Helper | 1.0 | Made, matches order | Yes | Y77 | 2025-12-02 | `4115600` | 3 | 50×100 | 6 mm | yes | — |  |
| Backplane Pro | 1.0 | Made, matches order | Yes | Y30 | 2024-04-30 | `305dab8` | 4 | 100×100 | 6 mm | yes | — | symbol has pins the footprint lacks: J2 shield pin; the board's silk says 6502 BACKPLANE, its name when ordered |
| Backplane Pro | 1.1 | Made, matches order | Yes | Y93 | 2026-06-21 | `7486bd6` | 4 | 100×100 | 6 mm | yes | — |  |
| Backplane Pro | 1.2 | Drawn | — |  |  |  | — | 100×100 | 6 mm | yes | — |  |
| Blinkenlights Card | 1.0 | Made, matches order | Yes | Y40 | 2024-06-08 | `7d050b0` | 4 | 100×57.62 | — | — | — |  |
| Blinkenlights Card | 1.1 | Drawn | — |  |  |  | — | 100×57.62 | — | — | — |  |
| Breadboard Helper | 1.0 | Made, matches order | Yes | Y39 | 2024-06-08 | `7d050b0` | 3 | 75×55 | — | — | — |  |
| CPU Card | 1.0 | Made, matches order | Yes | Y18 | 2024-04-03 | `da975a6` | 4 | 100×57.62 | — | — | — |  |
| CPU Card | 1.1 | Drawn | — |  |  |  | — | 100×57.62 | — | — | — |  |
| CPU Card Pro | 1.0 | Never made | — |  |  |  | — | 100×57.62 | — | — | — | title block credits bahamutkotd, who contributed |
| Clock Card | 1.0 | Ordered | — |  |  |  | — | 100×57.62 | — | — | — | Order 1, placed 2026-11-02 |
| Clock Helper | 1.0 | Made, matches order | Yes | Y74 | 2025-11-21 | `65a5e49` | 4 | 50×50 | 5.32–5.68 mm | SVG only | yes |  |
| Clock Helper | 1.1 | Drawn | — |  |  |  | — | 50×50 | 6 mm | yes | yes |  |
| DB25 Helper | 1.0 | Made, matches order | Yes | Y65 | 2025-10-06 | `013b131` | — | 100×50 | 5.32–6.25 mm | SVG only | yes |  |
| DB25 Helper | 1.1 | Drawn | — |  |  |  | — | 100×50 | 6 mm | yes | yes |  |
| GPIO Breadboard Helper | 1.0 | Made, matches order | Yes | Y57 | 2025-10-06 | `0dd90c8` | 4 | 58.83×55 | — | — | — |  |
| GPIO Card | 1.0 | Made, matches order | Yes | Y45 | 2024-06-19 | `390cb17` | 3 | 100×57.62 | — | — | — |  |
| GPIO Helper | 1.0 | Made, matches order | Yes | Y66 | 2025-10-06 | `013b131` | 4 | 100×50 | 5.32–6.25 mm | SVG only | yes |  |
| GPIO Helper | 1.1 | Drawn | — |  |  |  | — | 100×50 | 6 mm | yes | yes |  |
| Joystick Helper | 1.0 | Made, matches order | Yes | Y73 | 2025-11-16 | `4f73288` | 4 | 50×50 | 5.32–5.68 mm | SVG only | yes |  |
| Joystick Helper | 1.1 | Drawn | — |  |  |  | — | 50×50 | 6 mm | yes | yes |  |
| Keyboard Encoder Helper | 1.0 | Made, matches order | Yes | Y72 | 2025-11-14 | `4470a4f` | 4 | 100×50 | 5.32–6.25 mm | SVG only | yes | to fit the COB plate, drill plate holes 9 and 21 out to 5 mm: see the README |
| Keyboard Encoder Helper | 1.1 | Drawn | — |  |  |  | — | 100×50 | 6 mm | yes | yes |  |
| Keyboard Helper | 1.0 | Made, matches order | Yes | Y70 | 2025-10-27 | `3b654ed` | 4 | 335×125 | 5 mm | — | yes |  |
| LCD Board | 1.0 | Made, matches order | Yes | Y80 | 2026-01-13 | `2a232e3` | — | 100×100 | 6 mm | yes | — |  |
| LCD Card | 1.0 | Made, matches order | Yes | Y27 | 2024-04-22 | `f77fc20` | 4 | 100×57.62 | — | — | — |  |
| LCD Card | 1.1 | Drawn | — |  |  |  | — | 100×57.62 | — | — | — |  |
| Mega Helper | 1.0 | Made, matches order | Yes | Y81 | 2026-01-10 | `affcc47` | 3 | in footprint | — | — | — | symbol has pins the footprint lacks: Arduino header pins |
| Memory Card | 1.0 | Made, matches order | Yes | Y20 | 2024-04-03 | `da975a6` | 4 | 100×57.62 | — | — | — |  |
| PS2 Helper | 1.0 | Made, matches order | Yes | Y61 | 2025-10-06 | `0969243` | 4 | 100×50 | 5.32–6.25 mm | yes | yes |  |
| PS2 Helper | 1.1 | Drawn | — |  |  |  | — | 100×50 | 6 mm | SVG only | yes |  |
| Prototype Card | 1.0 | Made, matches order | Yes | Y22 | 2024-04-03 | `da975a6` | 4 | 100×57.62 | — | — | — |  |
| RAM Card | 1.0 | Made, matches order | Yes | Y69 | 2025-10-28 | `9b9e95d` | 4 | 100×57.62 | — | — | — |  |
| RTC Card | 1.0 | Made, matches order | Yes | Y62 | 2025-10-06 | `0969243` | 4 | 100×57.62 | — | — | — |  |
| Serial Card | 1.0 | Made, matches order | Yes | Y67 | 2025-10-06 | `013b131` | 3 | 100×57.62 | — | — | — |  |
| Serial Card Pro | 1.0 | Made, matches order | Yes | Y36 | 2024-05-20 | `ffafeba` | 4 | 100×57.62 | — | — | — |  |
| Serial Card Pro | 1.1 | Drawn | — |  |  |  | — | 100×57.62 | — | — | — |  |
| Sound Card | 1.0 | Made, matches order | Yes | Y84 | 2026-01-13 | `3b4c7bb` | 4 | 100×57.62 | — | — | — |  |
| Storage Card | 1.0 | Made, matches order | Yes | Y47 | 2024-06-22 | `b8f89eb` | 4 | 100×57.62 | — | — | — |  |
| Storage Card Pro | 1.0 | Made, matches order | Not yet | Y78 | 2025-12-11 | `b89a4a4` | — | 100×57.62 | — | — | — |  |
| VERA Helper | 1.0 | Made, matches order | Yes | Y71 | 2025-11-04 | `e74f44e` | 4 | 100×80 | 5.32–6.25 mm | — | — |  |
| VERA Helper | 1.1 | Drawn | — |  |  |  | — | 100×80 | 6 mm | — | — |  |
| VGA Card | 1.0 | Made, matches order | Yes | Y64 | 2025-10-06 | `0dd90c8` | 4 | 100×57.62 | — | — | — |  |
| VGA Card | 1.1 | Drawn | — |  |  |  | — | 100×57.62 | — | — | — |  |
| VGA Card Pro | 1.0 | Never made | — |  |  |  | — | 100×57.62 | — | — | — | symbol has pins the footprint lacks: Pico pins 41-43 |
| Video Card | 1.0 | Made, matches order | Yes | Y53 | 2024-07-09 | `f890f21` | 2 | 100×57.62 | — | — | — |  |
| Video Card | 1.1 | Drawn | — |  |  |  | — | 100×57.62 | — | — | — |  |
| Video Card Pro | 1.0 | Never made | — |  |  |  | — | 100×57.62 | — | — | — |  |

The audit last ran on 2026-11-04. Each production zip marked *Made, matches order* was compared byte for byte with JLCPCB's copy, and its PCB regenerated to the same copper, mask, outline and holes. Tindie stock is from the listings as saved on 2026-10-23.
