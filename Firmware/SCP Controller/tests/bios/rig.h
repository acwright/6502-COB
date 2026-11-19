// A rig on the USB serial port, in serve mode (rp2350/serve_protocol.h): the
// controller's registers played from the Mac, answered by the core on the media
// rig's real SD card and flash, or through the loopback rig's PIO bus.
//
// Writes are buffered and sent in order ahead of the next read, so a run of them
// costs no round trips. Any fault on the link (no answer in RIG_TIMEOUT_S) ends
// the program: a test can't go on without its controller.
#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "../../rp2350/serve_protocol.h"

#define RIG_TIMEOUT_S 10

typedef struct rig rig_t;

// Opens the port (NULL: the first /dev/cu.usbmodem*), and puts the rig in serve
// mode. bus_mhz is the loopback rig's bus timing, 1 or 2; the media rig ignores it.
rig_t *rig_open(const char *port, double bus_mhz);
void rig_close(rig_t *r);

uint8_t rig_read(rig_t *r, unsigned reg);
void rig_write(rig_t *r, unsigned reg, uint8_t value);

// Reads the data register up to max times, stopping after the read that ends
// the sector. Returns how many it read.
size_t rig_data(rig_t *r, uint8_t *buf, size_t max);

void rig_power_on(rig_t *r, bool card);
void rig_card(rig_t *r, bool in);
void rig_stats(rig_t *r, uint32_t words[SERVE_STAT_COUNT]);

// Read Sectors and Write Sectors of one sector, as the BIOS sends them, through
// the controller: wait for BSY to clear, set the count and LBA, the command, wait
// for DRQ, move the 512 bytes. False on ERR, or no answer in RIG_TIMEOUT_S.
bool rig_sector_read(rig_t *r, uint32_t lba, uint8_t buf[512]);
bool rig_sector_write(rig_t *r, uint32_t lba, const uint8_t buf[512]);

// Waits for BSY to clear after a power-on. False if no medium answers (status $00).
bool rig_wait_ready(rig_t *r);

// Round trips so far: each read, data run, or command waited on.
uint64_t rig_round_trips(const rig_t *r);
