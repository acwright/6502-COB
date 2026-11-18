// A medium: the SD card or the built-in flash drive, as 512-byte sectors.
//
// The BIOS sees 256 disks of 1 MB (2048 sectors) each. A medium holds N whole
// disks, its sectors / 2048, and any part-disk left over is unused. A smaller
// medium repeats its disks, as a board's registers repeat across an I/O window:
// LBA n goes to sector n mod (N x 2048). So on a 16 MB chip DISK 16 is DISK 0,
// and below the end of the medium LBA n is still sector n.
#pragma once

#include <stdbool.h>
#include <stdint.h>

#define MEDIA_DISK_SECTORS 2048u

typedef enum {
    MEDIUM_OK = 0,
    MEDIUM_FAILED,          // the medium couldn't read or write the sector
    MEDIUM_GONE,            // the medium has gone (the SD card was pulled)
} medium_result_t;

typedef struct medium medium_t;
struct medium {
    const char *name;
    uint32_t generation;    // the medium adds 1 each time it starts: a card pulled and another put in is a new one
    bool (*ready)(medium_t *m);                                     // present, started and usable
    uint32_t (*sectors)(medium_t *m);                               // its size in 512-byte sectors
    medium_result_t (*read)(medium_t *m, uint32_t sector, uint8_t *buf);
    medium_result_t (*write)(medium_t *m, uint32_t sector, const uint8_t *buf);
    void *ctx;
};

// N: the whole disks a medium of this many sectors holds.
uint32_t media_disks(uint32_t sectors);

// The sector LBA lba reaches on a medium of this many sectors. False when the
// medium holds no whole disk.
bool media_map(uint32_t sectors, uint32_t lba, uint32_t *sector);
