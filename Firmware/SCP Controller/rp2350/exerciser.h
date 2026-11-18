// The loopback rig's bus exerciser (exerciser.pio): 6502 bus cycles, built as a
// stream of timed phases and played by PIO1 through the jumper wires.
//
// A cycle is timed from PHI2 as a W65C02 and the card's front end make it, with
// PHI2 high for 45% of the period:
//   - the strobes (RB or WB) rise 30 ns after PHI2 falls, and the address and CS
//     hold for 30 ns more;
//   - the new address and CS then hold until the strobe falls, 30 ns after PHI2
//     rises (the 74HCT00's delay);
//   - the strobe stays low until 30 ns after PHI2 falls.
// Every cycle strobes RB or WB, as the bus does whichever card it's for; only
// the controller's own cycles pull CS low.
#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef enum {
    CYCLE_READ,             // another card's, or memory's: CS high
    CYCLE_WRITE,
    CYCLE_OUR_READ,         // the controller's register `reg`
    CYCLE_OUR_WRITE,
} cycle_t;

typedef struct {
    uint32_t *words;
    size_t count, cap;
    uint32_t pins;          // the pins after the last phase
    uint32_t samples;       // phases that sample
    bool marker;            // the next phase samples, as a marker
    double mhz;
    double ns_per_clock;
} stream_t;

void stream_init(stream_t *s, uint32_t *words, size_t cap, double mhz);

// One bus cycle. For CYCLE_OUR_READ, sample_ns >= 0 reads D0-D7 that long after RB
// falls (the real 6502 latches 10 ns before PHI2 falls: H - 40 ns after RB falls).
// For CYCLE_OUR_WRITE, marker makes the next phase sample, so the CPU knows the
// write is over and may change the data.
void stream_cycle(stream_t *s, cycle_t kind, unsigned reg, double sample_ns, bool marker);

// Holds RESB low (true) or releases it for `ns`, the other pins idle.
void stream_resb(stream_t *s, bool low, double ns);

// When the 6502 latches read data, in ns after RB falls.
double stream_latch_ns(const stream_t *s);

// The exerciser on PIO1, the player and the sampler.
void exerciser_init(void);

// Leaves the seven control pins at `pins` (bit 0 RESB ... bit 6 A0) and returns
// what GPIO8-14 read back through the wires, in the same order.
uint32_t exerciser_wires(uint32_t pins);

// Plays a stream to the end. Samples land in `samples` (s->samples of them).
// `idle` is called while it waits. Returns false if the stream ran late, which
// means the DMA couldn't keep the player fed and the timing can't be trusted.
bool exerciser_play(const stream_t *s, uint8_t *samples, void (*idle)(void));

// The same, but calling `on_sample` with each sample as it comes, so the CPU
// can act between cycles (the write loop changes D0-D7 after each marker).
bool exerciser_play_live(const stream_t *s, void (*on_sample)(uint32_t index, uint8_t value), void (*idle)(void));

// D0-D7 driven by the CPU, through the pads' overrides, for the 6502's writes.
void exerciser_drive_data(uint8_t value);
void exerciser_release_data(void);

// The sampler: arms it to read `delay_clocks` after RB, takes up to `max` samples
// while `s` plays, and returns how many it took.
size_t exerciser_sample_play(const stream_t *s, uint32_t delay_clocks, uint8_t *samples, size_t max, void (*idle)(void));
