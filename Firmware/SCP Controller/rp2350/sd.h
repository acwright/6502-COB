// The SD card, on SPI0: card detect, start-up, and its sectors as a medium
// (media.h).
//
// Start-up runs in steps from sd_poll(), a few hundred microseconds each, so the
// worker on core 0 goes on answering from the built-in drive while a card
// starts. Card detect is debounced for SD_DEBOUNCE_MS; a card is read at power-on
// without waiting. CRC checking is on, both ways: a block that arrives damaged is
// read again, and one the card got damaged is sent again, up to SD_TRIES times.
#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "media.h"

#define SD_DEBOUNCE_MS 50
#define SD_TRIES       3

typedef enum {
    SD_EMPTY,               // no card in the slot
    SD_STARTING,            // a card is in, and starting
    SD_READY,               // started: its sectors can be read and written
    SD_FAILED,              // a card is in, but didn't start; it stays failed until it's taken out
} sd_state_t;

typedef struct {
    sd_state_t state;
    bool card_in;           // card detect, debounced
    bool high_capacity;     // SDHC or SDXC: block addresses
    uint32_t sectors;       // from the CSD
    uint8_t csd[16], cid[16];
    uint32_t ocr;
    const char *failed_at;  // the step a start failed at, for the console
    uint32_t start_ms;      // how long the last start took
    uint32_t hz;            // the clock after start-up, as set
    uint32_t reads, writes;
    uint32_t crc_retries;   // blocks sent or read again after a CRC error
    uint32_t failures;      // reads and writes that failed after every try
} sd_info_t;

// Sets up the pins and SPI0 and reads card detect. hz is the clock after start-up.
void sd_init(uint32_t hz);

// Card detect and start-up. Call it often from core 0.
void sd_poll(void);

// Forgets the card and starts it again (the console's "sd"), printing each step
// if verbose.
void sd_restart(bool verbose);

// Sets the clock after start-up, now if a card is started. Returns the clock set.
uint32_t sd_set_hz(uint32_t hz);

bool sd_card_detect_raw(void);  // the pin, now: true with a card in
const sd_info_t *sd_info(void);
medium_t *sd_medium(void);
