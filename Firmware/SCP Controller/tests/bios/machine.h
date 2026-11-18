// An AC6502 just big enough to run the stock BIOS against the controller's
// core: a 65C02 (vrEmu6502), 32 KB of RAM, the 32 KB ROM, a serial card for the
// console at IO 5 ($9000), and the controller at IO 4 ($8C00). Every other I/O
// slot is empty and reads as open bus, the last byte on the bus, as a real
// board's does.
//
// The controller is the firmware's own core (ata.c, drive.c, flashdisk.c) on
// models of its media: a RAM SD card and a NOR chip. Their busy times are taken
// in microseconds and turned into 6502 cycles at the machine's clock, so the
// BIOS's own timeouts, counted in cycles, are the real ones.
#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "../unit/fakes.h"
#include "vrEmu6502/vrEmu6502.h"

// What a medium costs, in microseconds.
typedef struct {
    const char *name;
    uint32_t read_us, write_us;             // the SD card: one sector
    uint32_t program_us, erase_us;          // the NOR chip: one 256-byte page, one 4 KB erase
    uint32_t byte_us_x100;                  // the NOR chip: reading, per byte, in hundredths of a microsecond
} media_timing_t;

extern const media_timing_t SD_TYPICAL, SD_SDHC_WORST, SD_SDXC_WORST;
extern const media_timing_t FLASH_TYPICAL, FLASH_WORST;

// One job the controller did, as the bench would log it.
typedef struct {
    uint8_t op;                 // ata_op_t
    bool sd;                    // on the SD card, else the built-in drive
    uint8_t error;
    uint32_t busy_us;
} job_log_t;

typedef struct {
    double mhz;
    const uint8_t *rom;                     // 32 KB, from $8000
    uint32_t sd_sectors;                    // 0: no card in the slot
    const media_timing_t *sd_timing, *flash_timing;
    uint32_t flash_bytes;                   // 0: no chip
    uint32_t boot_us;                       // the RP2350's start, before the controller answers
    uint32_t sd_start_us;                   // starting a card already in at power-on
    bool sd_start_fails;
} machine_config_t;

typedef struct {
    machine_config_t cfg;
    VrEmu6502 *cpu;
    uint8_t ram[0x8000];
    uint8_t bus;                            // the last byte on the bus
    uint64_t cycles;

    // The serial card (an R6551 with every modem line at ground).
    uint8_t acia_cmd, acia_ctrl, acia_rx;
    bool acia_rx_full, acia_irq;
    const char *input;                      // typed, a byte at a time, while RTS is low
    size_t input_pos;
    uint64_t next_rx;
    char out[1 << 16];
    size_t out_len;

    // The controller.
    fake_clock_t clock;
    ata_t ata;
    drive_t drive;
    ram_medium_t sd;
    fake_nor_t chip;
    flashdisk_t flash;
    bool present;                           // power-on is over
    uint64_t present_at;                    // the cycle it ends on
    bool job_out;                           // the worker has done a job the bus side hasn't picked up
    uint64_t job_ready;                     // the cycle the bus side may see it
    job_log_t jobs[4096];
    size_t job_count;
} machine_t;

// Powers the machine on. The SD card's image, if any, starts as sd_image (sd_sectors x 512 bytes) or blank.
machine_t *machine_new(const machine_config_t *cfg, const uint8_t *sd_image);
void machine_free(machine_t *m);

uint64_t machine_cycles_for_us(const machine_t *m, uint64_t us);
double machine_us(const machine_t *m);

// Runs until `want` appears in the console output after `from`, or `seconds` of
// machine time pass. Returns the offset just past it, or 0 if it never came.
size_t machine_wait(machine_t *m, size_t from, const char *want, double seconds);

// Types `text` at the serial console (\r for Return). It goes in a byte at a
// time as the BIOS takes it; machine_wait() runs the machine meanwhile.
void machine_type(machine_t *m, const char *text);

// Types a line and waits for the BASIC prompt after it. Returns what the
// machine printed in between, in buf.
bool machine_command(machine_t *m, const char *line, char *buf, size_t size, double seconds);

uint8_t machine_peek(const machine_t *m, uint16_t addr);

// The longest busy time logged since job index `from`, for ops matching `op` (0: any).
uint32_t machine_longest(const machine_t *m, size_t from, uint8_t op);

// The BIOS's wait for BSY (StWaitReady, StWaitDrq): 65536 passes of 13 cycles.
#define BIOS_WAIT_CYCLES (65536.0 * 13.0)
// The BIOS's boot probe (StProbeWait): CF_PROBE_LIMIT 30000 polls of 100 cycles.
#define BIOS_PROBE_CYCLES (30000.0 * 100.0)
