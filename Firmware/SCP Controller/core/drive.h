// The worker side of the controller: it takes the job the bus side posts
// (ata.h), does it on a medium, and hands it back. It chooses the medium when a
// command starts: the SD card if one is in and ready, else the built-in drive.
// A command keeps its medium to the end; if the medium goes mid-command, or is
// a different card by the next sector, the command ends with ERR and ABRT.
//
// It also keeps what the bench reads back (the longest busy times, the error
// count), says what the LEDs show, and decides when power-on is over.
#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "ata.h"
#include "media.h"

typedef struct {
    uint32_t reads, writes, errors;
    uint32_t longest_read_us, longest_write_us;
} drive_medium_stats_t;

typedef struct {
    drive_medium_stats_t sd, flash;
    uint32_t longest_busy_us;       // the longest any one job kept BSY set
    uint32_t errors;
} drive_stats_t;

typedef struct {
    ata_t *ata;
    medium_t *sd;                   // NULL on a build with no SD card
    medium_t *flash;                // NULL on a build with no built-in drive
    medium_t *current;              // the running command's medium
    uint32_t current_generation;    // ... and which start of it
    uint32_t (*now_us)(void *clock);
    void *clock;
    const char *model, *serial, *firmware;     // for IDENTIFY
    drive_stats_t stats;
    bool busy;                      // a job is being done
    bool active;                    // a job has been done since power-on
    uint32_t last_end_us;           // when the last one finished
} drive_t;

void drive_init(drive_t *d, ata_t *ata, medium_t *sd, medium_t *flash,
                uint32_t (*now_us)(void *clock), void *clock,
                const char *model, const char *serial, const char *firmware);

// The medium a command starting now would use, or NULL if none is ready.
medium_t *drive_choose(drive_t *d);

// Does the posted job, if there is one. Returns whether there was.
bool drive_service(drive_t *d);

// Power-on is over, and the controller should start answering, when there's no
// SD card in the slot, or the card in it has started or failed to, or the wait
// for it has run out. Until then reads answer $80 (BSY), which the BIOS's boot
// probe waits through: 1.5 s at 2 MHz, 3.0 s at 1 MHz.
#define DRIVE_BOOT_SD_WAIT_MS 1200
bool drive_boot_settled(bool card_in, bool sd_ready, bool sd_failed, uint32_t elapsed_ms);

// The LEDs: sd (green, D2) while the SD card is the medium a command would use;
// act (red, D1) while a job is being done and for DRIVE_ACT_HOLD_US after, so a
// single sector shows.
#define DRIVE_ACT_HOLD_US 50000u
typedef struct {
    bool sd, act;
} drive_leds_t;
drive_leds_t drive_leds(const drive_t *d, uint32_t now_us);
