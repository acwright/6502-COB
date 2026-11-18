// A NOR flash chip, the built-in drive, as the flash disk needs it. The RP2350
// side drives a W25Q over SPI1; the unit tests use a model of one.
//
// Programming can only turn bits from 1 to 0; erasing a 4 KB sector sets it all
// to $FF.
#pragma once

#include <stdbool.h>
#include <stdint.h>

#define NOR_PAGE   256u
#define NOR_SECTOR 4096u

typedef struct nor nor_t;
struct nor {
    uint32_t size;                                                          // bytes; 0 if no chip answered
    bool (*read)(nor_t *n, uint32_t addr, uint8_t *buf, uint32_t len);
    bool (*program)(nor_t *n, uint32_t addr, const uint8_t *buf, uint32_t len);   // within one page
    bool (*erase)(nor_t *n, uint32_t addr);                                 // the 4 KB sector at addr
    void *ctx;
};

// The size a JEDEC ID (manufacturer, type, capacity) gives, in bytes, for the
// Winbond W25Q...JV family from 1 MB (W25Q80, $14) to 128 MB (W25Q01, $21).
// The capacity byte is the size's power of 2 up to $19 (32 MB); Winbond then
// goes on at $20 (64 MB). 0 for anything else.
uint32_t nor_size_from_jedec(const uint8_t id[3]);

// Whether a chip of this size needs 4-byte addresses: above 16 MB.
bool nor_needs_4byte(uint32_t size);
