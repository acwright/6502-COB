// The 6502 bus: three PIO programs on PIO0 (bus.pio) and the bus side of the
// controller (core/ata.c) on core 1. Core 1 takes each access the programs
// report, applies it to the registers, and rewrites the register copy the
// read program serves from. It polls, from SRAM, with no interrupts.
#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "ata.h"

typedef struct {
    uint32_t reads, writes;         // accesses of ours seen
    uint32_t resets;                // RESB falling edges
    uint32_t longest_ns;            // the longest from taking an access off a FIFO to the copy being current
    uint32_t longest_read_ns, longest_write_ns;
    uint32_t histogram[8];          // accesses handled in under 0.25, 0.5, 1, 2, 4, 8, 16 us, and longer
    uint32_t section_cycles[3];     // the longest, in core 1 cycles: the access, the checks and ata_poll, publish
} bus_stats_t;

// Starts the bus: the programs, then core 1 running `a`. Until bus_set_present()
// every read answers BSY ($80).
void bus_start(ata_t *a);

// From core 0: power-on is over; a medium can answer (or none can).
void bus_set_present(bool present);

// A copy of core 1's counts.
bus_stats_t bus_stats(void);

// Diagnostics, run on the calling core: cycles for 1000 rounds of the 8 peeks,
// of 4 writes to the read program's FIFO words, and of 4 writes to plain RAM.
void bus_bench(uint32_t cycles[3]);
