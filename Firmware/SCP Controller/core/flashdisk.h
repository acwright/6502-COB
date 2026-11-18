// The built-in drive: a medium (media.h) on a NOR flash chip (nor.h).
//
// Every byte is stored inverted, so a blank chip, all $FF, reads as zeros: an
// empty directory, ready to use. A 512-byte write lands in a 4 KB erase sector:
//   - if nothing changes, nothing is written;
//   - if the new bytes only need bits turned from 1 to 0 (space never written
//     since the chip was erased, for one), the two pages are programmed as they
//     stand, with no erase;
//   - otherwise the 4 KB sector is read, erased and programmed again with the
//     new 512 bytes in it, skipping pages left blank.
// Every write is read back and compared.
#pragma once

#include <stdint.h>

#include "media.h"
#include "nor.h"

typedef struct {
    uint32_t writes;        // sectors written
    uint32_t unchanged;     // ... of which changed nothing, so were skipped
    uint32_t in_place;      // ... programmed with no erase
    uint32_t erases;        // ... needing a 4 KB erase
    uint32_t failed;        // reads or writes the chip failed
} flashdisk_stats_t;

typedef struct {
    medium_t medium;        // first, so a medium_t * is a flashdisk_t *
    nor_t *nor;
    flashdisk_stats_t stats;
    uint8_t scratch[NOR_SECTOR];
} flashdisk_t;

void flashdisk_init(flashdisk_t *f, nor_t *nor);
