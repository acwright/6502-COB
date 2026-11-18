// The IDENTIFY DEVICE ($EC) data: 256 16-bit words, laid out as a CompactFlash
// card's. Read through the 8-bit data register, each word comes low byte
// first, and each word of a string holds two characters, the first in the high
// byte: "AC6502" reads as 'C','A','5','6','2','0'.
//
// Words this controller fills:
//     0      $848A: a CompactFlash card
//     1,3,6  default cylinders, heads (16) and sectors per track (63)
//     7-8    sectors on the medium, high word first (CFA)
//     10-19  serial number, 20 characters
//     23-26  firmware version, 8 characters
//     27-46  model, 40 characters
//     47     $8001: one sector per Read/Write Multiple
//     49     $0200: LBA
//     51     $0200: PIO mode 2 timing
//     53     $0001: words 54-58 are valid
//     54-56  current cylinders, heads, sectors per track
//     57-58  current capacity in sectors, low word first
//     60-61  sectors in LBA mode, low word first
// and, in the vendor-specific words, what the bench reads back:
//     128-129  the longest a command has kept BSY set since power-on, in us
//     130-131  the longest SD card sector write, in us
//     132-133  the longest built-in drive sector write, in us
//     134      the medium answering this command: 1 the SD card, 2 the built-in drive
//     135      N, the whole 1 MB disks on that medium
//     136-137  errors since power-on
//
// "Sectors on the medium" is N x 2048: the disks the BIOS can reach without
// mirroring.
#pragma once

#include <stdint.h>

#define IDENTIFY_MEDIUM_SD    1
#define IDENTIFY_MEDIUM_FLASH 2

typedef struct {
    const char *model;      // up to 40 characters
    const char *serial;     // up to 20
    const char *firmware;   // up to 8
    uint32_t sectors;       // N x 2048
    uint32_t longest_busy_us;
    uint32_t longest_sd_write_us;
    uint32_t longest_flash_write_us;
    uint16_t medium;        // IDENTIFY_MEDIUM_*
    uint16_t disks;
    uint32_t errors;
} identify_t;

void identify_build(uint8_t buf[512], const identify_t *id);

// Word w of an IDENTIFY sector, as the 6502 reads it (for tests and tools).
static inline uint16_t identify_word(const uint8_t buf[512], unsigned w)
{
    return (uint16_t)(buf[2 * w] | (buf[2 * w + 1] << 8));
}
