#!/usr/bin/env python3
"""cffs is the oracle for the disk format: images it writes load in the BIOS, and
files the BIOS saves through the controller list and extract with it.

  cffs_interop.py --cli BIOS_CLI --rom ROM [--rig PORT]

  1. cffs makes an SD card image with a file on it; the BIOS BLOADs the file
     through the controller and sums its bytes in BASIC.
  2. The BIOS BSAVEs 1000 bytes of ROM and SAVEs a program onto that card;
     cffs lists the image and extracts both, which must match.
  3. The same on the built-in drive, read back as the 6502 sees its sectors.

With --rig (PORT, or "auto"), the controller is the media rig's, on its real SD
card and flash: the image is put on the card through the controller and read
back the same way, disk 0 of each medium.

Needs cffs on the PATH (6502's cffs-image-tool)."""
import argparse
import os
import re
import subprocess
import sys
import tempfile


def sh(*args, **kw):
    r = subprocess.run(args, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"{' '.join(args)} failed ({r.returncode}):\n{r.stdout}{r.stderr}")
    return r.stdout


def listed(image):
    """The file names cffs lists on disk 0."""
    out = sh('cffs', 'list', image)
    return {line.split()[0] for line in out.splitlines()[3:] if line.strip()}


def extract(image, name, tmp):
    path = os.path.join(tmp, name + '.out')
    sh('cffs', 'extract', image, name, path)
    return open(path, 'rb').read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cli', required=True)
    ap.add_argument('--rom', required=True)
    ap.add_argument('--rig')
    a = ap.parse_args()
    rom = open(a.rom, 'rb').read()
    rom_part = rom[0x2000:0x2000 + 1000]            # $A000, where the ROM file comes from
    faults = []

    with tempfile.TemporaryDirectory() as tmp:
        data = bytes((i * 37 + 11) & 255 for i in range(1000))
        open(os.path.join(tmp, 'data.bin'), 'wb').write(data)
        sd, out = os.path.join(tmp, 'sd.img'), os.path.join(tmp, 'out.img')
        sh('cffs', 'create', sd, '--disks', '4')
        sh('cffs', 'add', sd, os.path.join(tmp, 'data.bin'))

        media = (['--rig', a.rig, '--put', sd, '--get', out] if a.rig else ['--sd', sd, '--sd-out', out])
        console = sh(a.cli, a.rom, *media,
                     'BLOAD 8192,"DATA.BIN"',
                     'S=0:FOR I=0 TO 999:S=S+PEEK(8192+I):NEXT:PRINT S',
                     'BSAVE 40960,1000,"ROM.BIN"',
                     '10 PRINT "HELLO FROM THE BIOS"',
                     'SAVE "PROG"')
        if '?LOAD ERROR' in console or '?SAVE ERROR' in console:
            faults.append('the BIOS reported an error:\n' + console)
        sums = re.findall(r'^ (\d+)$', console, re.M)     # text mode has turned CR LF into LF
        if not sums or int(sums[0]) != sum(data):
            faults.append(f'cffs file through the BIOS: summed {sums[:1]}, want {sum(data)}')

        names = listed(out)
        for want in ('DATA.BIN', 'ROM.BIN', 'PROG'):
            if want not in names:
                faults.append(f'SD card: cffs lists {sorted(names)}, no {want}')
        if 'ROM.BIN' in names and extract(out, 'ROM.BIN', tmp) != rom_part:
            faults.append('SD card: ROM.BIN as cffs extracts it is not the ROM bytes BSAVEd')
        if 'PROG' in names and b'HELLO FROM THE BIOS' not in extract(out, 'PROG', tmp):
            faults.append('SD card: PROG as cffs extracts it lacks the program text')

        flash = os.path.join(tmp, 'flash.img')
        media = (['--rig', a.rig, '--no-card', '--get', flash] if a.rig else ['--flash', '16', '--flash-out', flash])
        console = sh(a.cli, a.rom, *media, 'BSAVE 40960,1000,"ROM.BIN"')
        names = listed(flash)
        if 'ROM.BIN' not in names:
            faults.append(f'built-in drive: cffs lists {sorted(names)}, no ROM.BIN')
        elif extract(flash, 'ROM.BIN', tmp) != rom_part:
            faults.append('built-in drive: ROM.BIN as cffs extracts it is not the ROM bytes BSAVEd')

    for f in faults:
        print('FAIL', f)
    where = ' on the media rig' if a.rig else ''
    print(f'{os.path.basename(a.rom)}: cffs interop{where}, {len(faults)} faults')
    return 1 if faults else 0


if __name__ == '__main__':
    sys.exit(main())
