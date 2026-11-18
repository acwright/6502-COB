// The loopback rig's medium: 16 MB, every sector a pattern made from its
// number, with the last eight sectors written kept in RAM so they read back.
// It takes `read_us` and `write_us` to answer, so the controller shows BSY.
#pragma once

#include <stdint.h>

#include "media.h"

#define PATTERNDISK_SLOTS 8

typedef struct {
    medium_t medium;        // first, so a medium_t * is a patterndisk_t *
    uint32_t sectors;
    uint32_t read_us, write_us;
    struct {
        uint32_t sector;
        uint8_t used;
        uint8_t data[512];
    } slot[PATTERNDISK_SLOTS];
    unsigned next;
} patterndisk_t;

void patterndisk_init(patterndisk_t *d, uint32_t sectors);

// Byte i of an unwritten sector.
static inline uint8_t patterndisk_byte(uint32_t sector, unsigned i)
{
    return (uint8_t)(sector * 7u + i * 13u + (sector >> 8) * 3u + (i >> 8) * 101u);
}
