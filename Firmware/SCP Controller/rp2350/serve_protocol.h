// The rigs' "serve" protocol: a Mac plays the 6502's side of the controller's
// registers over the USB serial port, as bytes, with no line endings. The Mac's
// BIOS harness (tests/bios/rig.c) speaks it to the media rig, which answers from
// the core on the real media, and to the loopback rig, which plays each access
// as a bus cycle through the PIO bus. Plain C: the Mac includes it too.
//
// The rig prints SERVE_HELLO when it enters the mode (the console's "serve"),
// then reads commands. Each is a byte, then its arguments:
//
//   SERVE_READ reg              -> the register's value                (1 byte)
//   SERVE_WRITE reg value       -> nothing: writes stream, in order
//   SERVE_DATA count_lo count_hi
//                               -> reads the data register up to count times,
//                                  stopping after the read that ends the
//                                  transfer: n_lo n_hi, then n bytes
//   SERVE_POWER card            -> power-on, as at a reset of the whole board;
//                                  card 0 starts with the slot reading empty: SERVE_OK
//   SERVE_CARD in               -> the card shown (1) or hidden (0), as if pulled: SERVE_OK
//   SERVE_RESB low              -> RESB's level: SERVE_OK
//   SERVE_STATS                 -> a count n, then n 32-bit words, low byte first (serve_stat_t)
//   SERVE_QUIT                  -> SERVE_OK, and back to the console
#pragma once

#define SERVE_HELLO "SERVE 1\r\n"

enum {
    SERVE_READ = 'r',
    SERVE_WRITE = 'w',
    SERVE_DATA = 'd',
    SERVE_POWER = 'p',
    SERVE_CARD = 'c',
    SERVE_RESB = 'b',
    SERVE_STATS = 's',
    SERVE_QUIT = 'q',
};

#define SERVE_OK 0x4B       // 'K'

// SERVE_STATS's words, in order.
typedef enum {
    SERVE_STAT_SD_READS,
    SERVE_STAT_SD_WRITES,
    SERVE_STAT_SD_ERRORS,
    SERVE_STAT_SD_LONGEST_READ_US,
    SERVE_STAT_SD_LONGEST_WRITE_US,
    SERVE_STAT_FLASH_READS,
    SERVE_STAT_FLASH_WRITES,
    SERVE_STAT_FLASH_ERRORS,
    SERVE_STAT_FLASH_LONGEST_READ_US,
    SERVE_STAT_FLASH_LONGEST_WRITE_US,
    SERVE_STAT_LONGEST_BUSY_US,
    SERVE_STAT_ERRORS,
    SERVE_STAT_SETTLE_MS,           // power-on: from SERVE_POWER to answering
    SERVE_STAT_SD_DISKS,            // N of the card, 0 with none started
    SERVE_STAT_FLASH_DISKS,
    SERVE_STAT_SD_LED,              // the green LED: the card is the medium a command would use
    SERVE_STAT_HAS_SD,              // the rig has an SD card slot (the loopback rig has only a RAM disk)
    SERVE_STAT_LATE,                // loopback: bus cycles played late, whose timing can't be trusted
    SERVE_STAT_COUNT
} serve_stat_t;
