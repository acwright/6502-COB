// The built-in drive's chip: a Winbond W25Q on SPI1, as the flash disk's nor_t
// (core/nor.h). Its JEDEC ID sets the size. A chip above 16 MB gets Winbond's
// 4-byte-address commands ($13, $12, $21), which work whatever mode it's in.
#pragma once

#include <stdint.h>

#include "nor.h"

typedef struct {
    uint8_t jedec[3];           // manufacturer, type, capacity
    uint8_t status[3];          // status registers 1-3, as read at start-up
    uint32_t hz;                // the clock, as set
    uint32_t programs, erases;  // since start-up
    uint32_t longest_program_us, longest_erase_us;
    uint32_t timeouts;          // programs or erases still busy past the data sheet's maximum
    uint32_t wel_failures;      // Write Enables the chip didn't take
} flash_info_t;

// Sets up SPI1, resets the chip, and reads its ID. The nor_t's size is 0 if no
// chip this knows answered.
nor_t *flash_init(uint32_t hz);

uint32_t flash_set_hz(uint32_t hz);
const flash_info_t *flash_info(void);
