# Production files

Every board's production files (`Production/<Board>/Rev X/`: the Gerber zip, `bom.csv`, `positions.csv`,
`designators.csv` and `netlist.ipc`) are made by one tool, the **Fabrication Toolkit** (bennymeg's JLC plugin for
KiCad), with one set of settings. They're made in one of two ways, and both must give the same files:

- **In KiCad's PCB editor**, from the plugin's button. The plugin reads its settings from
  `fabrication-toolkit-options.json` in the revision's folder.
- **Headlessly**, by `Tools/regen.py`, which runs `toolkit.py` on a scratch copy of the revision.

`options.json` here is the one set of settings. `production.py --sync` writes it, byte for byte, as every
revision's `fabrication-toolkit-options.json`, and `toolkit.py` reads it directly. `plugin.json` pins the plugin
itself. `production.py --check`, run by `derived-check.py`, fails if any of them drift.

Why it matters: until 2026-11-13 (`KICAD.md` K38) the headless runner hard-coded **AUTO TRANSLATE** off while the
window had it on. The placement files of 22 unmade revisions came out with their surface-mount chips rotated 90° to
180° from what JLCPCB's assembly needs. No board was made from them.

## The settings

| Setting (key in the file) | Value | What it does, and why this value |
|---|---|---|
| `AUTO TRANSLATE` | `true` | Adds the plugin's `transformations.csv` corrections to `positions.csv`: rotations for SOIC, SOT-23, TSSOP and other packages whose zero angle in KiCad differs from JLCPCB's. **Must be on.** Every made board's placement file was written with it on (checked against the plugin on 2026-11-13: 999 of 1,002 placed parts agree; the three that don't are below). |
| `AUTO FILL` | `false` | Off: the plugin exports the zone fills saved in the board. Refill before making production files: `kicad-cli pcb drc --refill-zones --save-board`. Then the saved board and the Gerbers always agree. |
| `EXCLUDE DNP` | `true` | Leaves parts marked *Do not populate* out of `bom.csv`. They're left out of `positions.csv` either way. |
| `ALL_ACTIVE_LAYERS` | `false` | Off: the zip holds what JLCPCB uses, namely copper, mask, paste, silkscreen, the outline and the drill files. On, it also adds Fab, Courtyard, User and Adhesive layers, which JLCPCB ignores. Some older made zips have them. |
| `EXTRA_LAYERS` | `""` | No extra layers. |
| `EXTEND_EDGE_CUT` | `false` | Would send User.1 as a V-cut layer. No board is panelised. |
| `ALTERNATIVE_EDGE_CUT` | `false` | Would send User.2 as the outline instead of Edge.Cuts. The outline is Edge.Cuts. |
| `ARCHIVE_NAME` | `""` | Empty: the plugin names the zip `<title>_<rev>.zip` from the title block, with spaces as `_`, and the CSVs plainly. This is the name the window and `regen.py` both give. When the title changes (`KICAD.md` K35: `AC6502 <Board>`), a regenerated revision's zip takes the new name, and `regen.py` removes the old one. A made revision's zip is never regenerated. |
| `BACKUP_OPT` | `true` | In plugin 5.3.0 the logic is inverted: it makes a timestamped backup zip when this is **false** (`thread.py`, `if not self.options[BACKUP_OPT]`). `true` means no backups. The git history keeps every version. |
| `OPEN BROWSER` | `true` | Opens the output folder after a run from the window. It changes no file, and `toolkit.py` never opens one. |

The window rewrites the file every time it runs, with Python's `json.dump`, in the same form `options.json` is
written in. A run that changes nothing leaves the file unchanged. If you untick a box in the window, the file
changes and `production.py --check` fails: put it back with `production.py --sync`, or change the standard here
for every board.

## The plugin

`plugin.json` records the plugin's version (5.3.0) and a SHA-256 of each of its files, in the copy KiCad 10's
window runs: `~/Documents/KiCad/10.0/3rdparty/plugins/com_github_bennymeg_JLC-Plugin-for-KiCad/`. The 8.0 and 9.0
folders hold older copies with different code. Nothing uses them.

KiCad's Plugin and Content Manager can update the plugin on its own. Pin it there (*Pin* on the installed
package), so it stays at the version recorded here.

### Updating the plugin

1. Update it in the Plugin and Content Manager.
2. Read its changes, especially `process.py` (`generate_tables`, `generate_positions`), `thread.py` and
   `transformations.csv`.
3. Regenerate one surface-mount card with `regen.py`, and compare its `positions.csv` with the last one. Then
   regenerate every revision that isn't made, and run `production.py --all --check`.
4. Record it: `python3 Tools/production/production.py --pin VERSION` rewrites `plugin.json` from the installed
   files. Change this README if a setting changed meaning. Then sync and commit all five repositories.

Steps 3 and 4 go in that order on purpose: `toolkit.py` refuses an unpinned plugin. For step 3, pin it in a scratch
checkout first, or compare by running the plugin's window on one board.

## The check

`production.py --check` (`--all` for the five repositories):
- every revision folder's `fabrication-toolkit-options.json` is `options.json`, byte for byte;
- the plugin's files match `plugin.json`;
- every revision not yet made has a `positions.csv` whose parts and rotations are what the plugin gives. The check
  recomputes them from the PCB and the pinned `transformations.csv`, following the plugin's own rules: a part is
  placed unless it's `exclude_from_pos_files` or DNP, or its designator contains `**`. Its rotation is the
  footprint's (`180 - r` on the bottom) plus the first matching row of the table. A per-part offset field
  (`FT Rotation Offset` and the like) fails the check, because it isn't modelled; no board uses one.

Made and ordered revisions keep what JLCPCB received, so the check doesn't compare them.

## Made boards whose placement file differs from the standard

The MAX232 (U1) on the Serial Card 1.0, and both MAX232s (U1, U2) on the Serial Card Pro 1.0, were sent at 0°. The
standard gives 270°. Their footprint was then `6502 Parts:MAX232D`, which no row of the table matches. The library
rename to `6502 Parts:SOIC-16` (by shape, not part number) now matches `^SOIC-`. The footprint has KiCad's SOIC-16
orientation (pin 1 top left, pads within 0.02 mm of `Package_SO:SOIC-16_3.9x9.9mm_P1.27mm`). So 270°, which is what
the 74HC138 beside it on the same cards was sent at, is right for it. Both cards are tested, so the 0° was corrected
at JLCPCB's review or the chip was fitted by hand. The unmade Rev 1.1s carry 270°.
