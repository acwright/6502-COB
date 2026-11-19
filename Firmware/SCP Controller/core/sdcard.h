// The SD card's arithmetic, with no pins: its size from its CSD register, and
// the two checksums of the SD bus in SPI mode. The RP2350 side (rp2350/sd.c)
// talks to the card; the unit tests check these against the SD specification's
// own examples.
#pragma once

#include <stddef.h>
#include <stdint.h>

// The card's size in 512-byte sectors, from its CSD register: the 16 bytes CMD9
// sends, most significant first. 0 for a CSD structure this doesn't know (SDUC's
// 3.0, or the reserved value).
//   CSD 1.0 (SDSC):      (C_SIZE + 1) x 2^(C_SIZE_MULT + 2) blocks of 2^READ_BL_LEN bytes
//   CSD 2.0 (SDHC/SDXC): (C_SIZE + 1) x 512 KB
// A size of 2^32 sectors or more (2 TB) reads as 0xFFFFFFFF.
uint32_t sd_csd_sectors(const uint8_t csd[16]);

// The CSD's version: 1 (SDSC), 2 (SDHC/SDXC) or 3 (SDUC), or 0 for the reserved value.
unsigned sd_csd_version(const uint8_t csd[16]);

// A command's CRC7, over its first five bytes. The frame's last byte is
// (crc << 1) | 1: CMD0's is $95.
uint8_t sd_crc7(const uint8_t *p, size_t len);

// A data block's CRC16 (CCITT, x^16 + x^12 + x^5 + 1, from 0), sent high byte first.
uint16_t sd_crc16(const uint8_t *p, size_t len);
