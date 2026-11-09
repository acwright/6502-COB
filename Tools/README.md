# Tools

The scripts that keep this repository's files consistent: the BOMs, the revision register, the generated README
sections, the board images and the checks that hold it all together. They are the same in all five AC6502 KiCad
repositories ([6502-ACE](https://github.com/acwright/6502-ACE), [6502-COB](https://github.com/acwright/6502-COB),
[6502-DEV](https://github.com/acwright/6502-DEV), [6502-KIM](https://github.com/acwright/6502-KIM) and
[6502-VCS](https://github.com/acwright/6502-VCS)).

They need Python 3, KiCad 10 in `/Applications/KiCad`, Node.js for the repository's `Tests/`, and Pillow for the
board images. They are written for macOS.

## This repository, or all five

A tool works on this repository by default. Add `--all` to work on all five, which must then be cloned side by side
in one folder:

```text
Kicad/
  6502-ACE/  6502-COB/  6502-DEV/  6502-KIM/  6502-VCS/
```

## After any schematic or PCB edit

```sh
python3 Tools/regen.py "Board" REV        # production files, schematic PDF, STEP and images for one revision
python3 Tools/bom/gen_bom.py              # BOM.md and the Digi-Key and Mouser carts
python3 Tools/revision-audit/register.py  # REVISIONS.md and the README's "Which revision to make"
python3 Tools/derived-check.py            # everything derived from the KiCad files is current: 0 faults
```

`derived-check.py` runs the revision audit and every other check, and lists anything out of date. Slow results are
cached in `Tools/work/cache.json`, keyed by the bytes of every file they depend on; `--no-cache` recomputes them.

## What's here

| Folder | What it does |
|---|---|
| `bom/` | `gen_bom.py` writes `BOM.md` and the carts; `apply.py` writes the parts catalogue (`catalogue.json`) into the KiCad files; `check.py` checks they all agree. `digikey.py` and `mouser.py` look parts up, with API keys from `Tools/.env`, which git ignores. |
| `revision-audit/` | `audit.py` checks every revision against the family's standard; `register.py` writes `REVISIONS.md`; `labels.py` gives each revision its label; `newrev.py` starts a new revision; `gproof.py` compares two revisions' Gerbers (`--no-fill` without the pours' fills); `cadcheck.py` checks the top panels fit their boards. |
| `jumpers/` | Writes the README's *Jumpers* section, and checks every jumper on every revision is in it. |
| `offboard/` | Writes the README's *Off-board headers* section from the newest PCBs. |
| `schematic/` | Draws and checks the 6502 bus, cart and card connectors (`busfix.py`, `check.py`), and sets each global label's shape from the signal's flow (`flow.py`). |
| `library/` | Checks the KiCad libraries are the same in all five repositories, and renames parts across them. |
| `board-images/` | Renders the board images in `CAD/Images/`. |
| `cad/` | Reads each machine's `CAD/Assembly.json`, which places its boards on the plate, and checks it against the PCBs and today's plate. The family's standards for plates and tops are in its README. |
| `consistency/` | `table.py --all` prints every board's newest revision against the family's rules. |
| `cardedge/` | `standard.json` is the one card edge every card and cart shares: the outline, a cart's shell holes, no mask on the tab and no paste on the fingers. `cardedge.py` applies it to a revision not yet made, and checks every newest revision against it; revisions still waiting for their fix are listed in `Tools/data/cardedge.json`. |

## Data

`Tools/data/` holds this repository's own records, and is the one part of `Tools/` that differs between the
repositories:

| File | What it holds |
|---|---|
| `orders.json` | Each revision's order, status, test result and label. |
| `assignment.json` | Which catalogue part each reference on each revision is. |
| `jumpers.json` | What each jumper is for, how it's shipped and what to do with it. |
| `offboard.json` | Exceptions to the off-board header rules. |
| `rendered.json` | What each PCB looked like when its images were rendered. |
| `tindie.json` | Stock on each board's Tindie listing, as last read. |
| `cardedge.json` | Newest revisions that don't meet the card edge standard yet, and the item that fixes each. Only in the repositories with cards or carts. |

A change to one board's records is a commit to this repository only. `Tools/work/` holds generated files, such as
the audit and the cache, and git ignores it.

## Changing a tool

Everything else in `Tools/` is shared. Edit it in any repository, then copy it to the other four and commit all five:

```sh
python3 Tools/sync.py           # copy this repository's shared files to the four beside it
python3 Tools/sync.py --check   # are all five the same? derived-check.py runs this
```

`build-notes/`, in 6502-ACE only, builds that repository's ACE Board build notes PDF.
